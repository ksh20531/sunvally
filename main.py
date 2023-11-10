import config
import pymysql
import datetime
import ssl
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time


# 필드 데이터를 객체화
class Target(object):

    def __init__(self, obj):
        self.id = obj[0]
        self.name = obj[1]
        self.code = obj[2]
        self.time = obj[3]
        self.teeup_time = obj[4]

    def getTime(self):
        return self.teeup_time.time()


# 시간에 맞는 필드 선택
def selectField():
    now = datetime.datetime.now().time()
    check = datetime.time(8, 0, 0)
    sulak = datetime.time(9, 0, 0)
    iljuk = datetime.time(9, 30, 0)
    yeoju = datetime.time(10, 30, 0)

    # return '테스트'  # for test
    if datetime.datetime.today().weekday() != 0:
        # return '테스트'
        return '설악'
    else:
        if now < check:
            return '체크'
        elif check < now < sulak:
            return '설악'
        elif sulak < now < iljuk:
            return '일죽'
        elif iljuk < now < yeoju:
            return '여주'
        else:
            return '체크'


# 필드 데이터 가져오기
def getData(field):
    try:
        conn = pymysql.connect(host=config.db_host, user=config.db_user, password=config.db_pw, db=config.db_database)

        cursor = conn.cursor()
        sql = 'SELECT reservation.id,name,code,time,reservation_time,reservation.deleted ' \
              'FROM golf_reservations AS reservation ' \
              'JOIN golf_fields AS field ' \
              'ON reservation.field_id = field.id WHERE name="'+field+'" ' \
              'AND reservation.deleted = 0 ' \
              'ORDER BY reservation.id desc;'
        cursor.execute(sql)
        row = cursor.fetchone()
        conn.close()

        return row
    except:
        result['message'] = 'DB 에러'
        print(result['message'])
        endProgram()


# 날짜 선택
def makeDate(date):
    selected_month = date.month
    now_month = datetime.datetime.now().month

    if selected_month == now_month:
        date = 'A'+date.strftime('%Y%m%d')
    elif selected_month > now_month:
        date = 'B'+date.strftime('%Y%m%d')
    else:
        date = 'A'+date.strftime('%Y%m%d')

    result['message'] = '선택한 날짜 : ' + date
    print(result['message'])

    return date


# 크롬 드라이버 다운로드
def getChromeDriver():
    print('크롬 드라이버 로드')
    # ssl 오류 발생 방지
    ssl._create_default_https_context = ssl.create_default_context()

    # 크롬 브라우저 꺼짐 방지 옵션
    chrome_options = Options()
    # chrome_options.add_argument("headless")  # 백그라운드 처리
    chrome_options.add_experimental_option("detach", True)  # 꺼짐 방지 옵션
    try:
        # https://chromedriver.chromium.org/downloads
        chrome_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        result['message'] = '크롬 드라이버 자동 로드 성공'
    except:
        chrome_driver = webdriver.Chrome(options=chrome_options)
        # result['message'] = '크롬 드라이버 로드 실패, 수동 다운로드 필요'
        # path = os.getcwd()
        # os.startfile(path)
        # webbrowser.open("https://googlechromelabs.github.io/chrome-for-testing/")

    chrome_driver.maximize_window()  # 창 최대화 옵션
    chrome_driver.implicitly_wait(10)  # 페이지 로드 시간 옵션

    return chrome_driver


# 예약 시작
def makeReservation():
    selected_date = makeDate(target.teeup_time)
    cnt = 0

    now = datetime.datetime.now()
    hour = target.time.split(":")[0]
    minute = target.time.split(":")[1]
    reservation_time = datetime.datetime(now.year, now.month, now.day, int(hour), int(minute))

    result['message'] = '예약 대기'
    print(result['message'])
    while True:
        # print('cnt : ', cnt)
        if cnt == 2:
            break

        second = reservation_time - datetime.datetime.now()
        if cnt == 1 or second.total_seconds() < 0.01:
            driver.refresh()
            result['message'] = "예약 시작"
            print(result['message'])

            try:
                wait.until(EC.visibility_of_element_located((By.ID, selected_date)))
                date = driver.find_element(By.ID, selected_date)
                date_title = date.find_element(By.TAG_NAME, 'a')

                if date_title.get_attribute('title') == "오픈전입니다.":
                    driver.refresh()
                elif date_title.get_attribute('title') == "마감되었습니다.":
                    result['message'] = "예약 마감"
                else:
                    date.click()
                    wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, '#tabCourseALL > div > div > table > tbody > tr')))
                    elements = driver.find_elements(By.CSS_SELECTOR, '#tabCourseALL > div > div > table > tbody > tr')

                    if elements[0].get_attribute('innerHTML').find('Tee-off') > -1:
                        result['message'] = '예약 오픈 전, 다시 시도'
                        print(result['message'])
                    else:
                        teeup_time = target.teeup_time

                        for elem in elements:
                            if elem.text.find('마감') < 0:
                                target_time = datetime.datetime.strptime(
                                    str(teeup_time.date()) + ' ' + elem.text.split(' ')[3], '%Y-%m-%d %H:%M'
                                )
                                diff = target_time - teeup_time  # second
                                diff = int(diff.seconds / 60)  # second to minute

                                # 예약시간 이상이고, 범위 안에 들었을 경우
                                if teeup_time <= target_time and diff <= config.timeRange:
                                    elem.find_element(By.CLASS_NAME, 'btn-res').click()
                                    result['message'] = "예약 페이지로 이동"
                                    break
                            else:
                                result['message'] = '풀 부킹'
                        try:
                            btn = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'btn-res03')))
                            btn.click()
                            result['success'] = 'success'
                            result['message'] = '예약 성공'
                            print(result)
                            break
                        except:
                            result['message'] = '중복 예약으로 실패'

                cnt = cnt + 1
            except:
                result['message'] = "날짜 선택 오류"
                endProgram()
        else:
            result['message'] = '예약 시간이 아닙니다'

    return None


# 매크로 종료
def endProgram():
    print('매크로 종료 시작')
    try:
        driver.close()
    except:
        pass

    result_id = data[0]
    if result['success'] == 'success':
        result_success = 1
    else:
        result_success = 0
    result_time = data[4]

    try:
        conn = pymysql.connect(host=config.db_host, user=config.db_user, password=config.db_pw, db=config.db_database)
        cursor = conn.cursor()
        sql = 'INSERT INTO golf_results (reservation_id, is_booked, booked_time) VALUES (%s,%s,%s);'
        val = (result_id, result_success, result_time)

        cursor.execute(sql, val)
        conn.commit()
        conn.close()
    except:
        print('DB 에러')

    print('매크로 종료')
    exit()


# 매크로 시작
result = {'success': 'fail', 'message': ''}
data = getData(selectField())

target = Target(data)
result['message'] = '골프장 선택 완료'
print(
    '골프장 : ', target.name,
    '\n예약 시간 : ', target.time,
    '\n티업 시간 : ', target.teeup_time
)

# 로그인 페이지 이동 후 아이디,비밀번호 입력 후 로그인 클릭
driver = getChromeDriver()
wait = WebDriverWait(driver, 10)
driver.get(config.url_login)
driver.find_element(By.ID, "usrId").send_keys(config.my_id)
driver.find_element(By.ID, "usrPwd").send_keys(config.my_pw)
driver.find_element(By.ID, "fnLogin").click()

# alert 창처리
try:
    wait.until(EC.alert_is_present())
    alert = driver.switch_to.alert
    alert.accept()
    result['message'] = '비밀번호 변경 알림창 OK'
except:
    wait.until(EC.alert_is_present())
    alert = driver.switch_to.alert
    alert.dismiss()
    result['message'] = '비밀번호 변경 알림창 에러'
    pass
time.sleep(1)
print(result['message'])

# 예약 페이지로 이동
driver.get(config.url_reservation)
driver.find_element(By.ID, 'selectCoId' + target.code).click()
result['message'] = target.name + ' 선택'
print(result['message'])

# 예약 시작
makeReservation()
# 매크로 종료
endProgram()
