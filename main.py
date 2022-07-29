from re import X
from tkinter import Y
from selenium import webdriver
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import clipboard
import schedule
import os
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap
import urllib.request

data = {
    # 카카오아이디
    'kakaoid': '아이디',
    # 카카오비밀번호
    'kakaopassword': '비밀번호',
    # 구글아이디
    'googleid': '아이디',
    # 구글비밀번호
    'googlepassword': '비밀번호',
    # 로그인후 리턴페이지
    'returnpage':'https://partners.newspic.kr/main/index#2',
    # 메뉴에서 스크롤 횟수
    'repeatnum':1
    }

def start_browser():
    global driver
    global wait
    global action
    chrome_driver_dir = "./chromedriver.exe"
    options = webdriver.ChromeOptions() 
    # 시크릿모드
    # options.add_argument("--incognito")
    # 백그라운드 실행 에러남 고쳐야해~
    # options.add_argument("--headless")
    # 대부분의 리소스에 대한 액세스를 방지??잘 모르겠는데 필수옵션이라함
    options.add_argument("--no-sandbox")
    # 크롬 드라이버에 setuid를 하지 않음으로써 크롬의 충돌을 막아줌
    options.add_argument("--disable-setuid-sandbox")
    # 메모리가 부족해서 에러가 발생하는 것을 막아줌
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # 윈도우 사이즈조정
    options.add_argument('window-size=500,900')
    driver = webdriver.Chrome(options=options, executable_path=chrome_driver_dir)
    action = ActionChains(driver)
    # 대기시간설정
    driver.implicitly_wait(0.1)
    wait = WebDriverWait(driver, 10)

# 구글 로그인용 브라우저
def start_browser_google():
    global upload_browser
    upload_options = uc.ChromeOptions()
    # 백그라운드
    # upload_options.headless=True
    # upload_options.add_argument('--headless')
    upload_browser = uc.Chrome(options = upload_options)
    
# 카카오로그인
def kakao_login():
    driver.get('https://accounts.kakao.com/login?continue=https%3A%2F%2Fcs.kakao.com%2F')
    driver.find_element(By.NAME, 'email').send_keys(data['kakaoid'])
    driver.find_element(By.NAME, 'password').send_keys(data['kakaopassword'])
    driver.find_element(By.CLASS_NAME, 'btn_g.btn_confirm.submit').click()

# 뉴스픽로그인
def newspic_login(returnpage, num):
    driver.get('https://partners.newspic.kr/login')
    driver.find_element(By.CLASS_NAME, 'btn-kakao').click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tab_30"]')))
    driver.get(returnpage)
    for c in range(num * 7):
        # 스크롤로하면 왜 그런지 모르겠는데 에러가 나서
        # 일단 data의 스크롤 1번당 pagedown 7번누른거로 처리
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tabBlockBig"]')))
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            


def find_news():
    global mynews
    newsdata = {}
    mynews = {}
    # li태그 전부 긁어서 저장
    news = driver.find_elements(By.XPATH, '//*[@id="channelList"]/li/div[2]')
    # 오늘날자랑 비교해서 오늘 날자만 저장
    for i in range(len(news)):
        if datetime.today().strftime("%Y.%m.%d") == news[i].find_element(By.CSS_SELECTOR, 'div > span').get_attribute('textContent'):
            newsdata[news[i].find_element(By.CSS_SELECTOR, 'a').get_attribute('href')] = news[i].find_element(By.CSS_SELECTOR, 'div > span').get_attribute('textContent')
    # 한페이지씩들어가서 타이틀: [공유주소, 이미지주소]로 저장
    for url in newsdata:
        driver.get(url)
        driver.find_element(By.XPATH, '//*[@id="partners-link-copy"]/ul/li[1]').click()
        mynewsurl = clipboard.paste()
        mynewstitle = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[1]/div[2]/h3').text
        medialink = driver.find_element(By.CLASS_NAME, 'article_view')
        try:
            medialink = medialink.find_element(By.TAG_NAME, 'img')
            medialink = medialink.get_attribute('src')
            mynews[mynewstitle] = [mynewsurl, medialink]
        except:
            medialink = medialink.find_element(By.TAG_NAME, 'video')
            medialink = medialink.get_attribute('poster')
            mynews[mynewstitle] = [mynewsurl, medialink]
    driver.quit()

def make_image(message):

    # Image size
    W = 640
    H = 640
    bg_color = 'rgb(247, 133, 98)' # One Shot 120L Coral
    
    # font setting
    font = ImageFont.truetype('NanumSquareRoundR.ttf', size=30)
    font_color = 'rgb(245, 245, 220)' # or just 'black'
		# 원래 윈도우에 설치된 폰트는 아래와 같이 사용 가능하나,
		# 아무리 해도 한글 폰트가 사용이 안 되어.. 같은 폴더에 다운받아 놓고 사용함.
		# font = ImageFont.truetype("arial.ttf", size=28)
    
    image =Image.new('RGB', (W, H), color = bg_color)
    draw = ImageDraw.Draw(image)
    
    # Text wraper to handle long text
	# 40자를 넘어갈 경우 여러 줄로 나눔
    lines = textwrap.wrap(message, width=15)
  
 
    y_text = 0
    # 각 줄의 내용을 적음
    for line in lines:
        width, height = font.getsize(line)
        draw.text(((W-width)/2,(H-height)/2+y_text), line, font=font, fill=font_color)
        y_text += height
        # height는 글씨의 높이로, 한 줄 적고 나서 height만큼 아래에 다음 줄을 적음
        
    # 안에 적은 내용을 파일 이름으로 저장
    image.save('main.png')
    


def upload():
    print('업로드 시작')
    # for news in mynews:
    start_browser_google()
    upload_browser.get('http://accounts.google.com/')
    time.sleep(2)
    upload_browser.find_element(By.NAME, 'identifier').send_keys(data['googleid'])
    upload_browser.find_element(By.ID, 'identifierNext').click()
    time.sleep(5)
    upload_browser.find_element(By. NAME, 'password').send_keys(data['googlepassword'])
    upload_browser.find_element(By.ID, 'passwordNext').click()
    time.sleep(2)
    upload_browser.get('https://www.youtube.com/')
    time.sleep(2)
    upload_browser.find_element(By.XPATH, '//*[@id="contents"]/ytd-account-item-renderer[2]').click()
    time.sleep(1)
    num =0
    for i in mynews:
        starttime = datetime.today().strftime("%H")
        
        writing = i + "더 보러가기 =====>>>" + mynews[i][0]
        make_image(i)
        urllib.request.urlretrieve(mynews[i][1], 'media.png')
        upload_browser.get('https://www.youtube.com/channel/UCl4_MlpLYtVEuL48iXJDFJg/community')
        time.sleep(1)
        upload_browser.find_element(By. ID, "commentbox-placeholder").click()
        time.sleep(1)
        upload_browser.execute_script(f"document.getElementById('contenteditable-root').innerHTML='{writing}'")
        time.sleep(1)
        # upload_browser.find_element(By.XPATH, '//*[@id="commentbox"]').set_attribute('added-attachment', 'image')
        upload_browser.execute_script("document.getElementById('commentbox').setAttribute('added-attachment','image')")
        time.sleep(1)
        upload_browser.find_element(By.XPATH, '//*[@id="dropzone"]/input').send_keys(os.getcwd()+"/main.png")
        time.sleep(1)
        upload_browser.find_element(By.XPATH, '//*[@id="add-image-button-container"]/input').send_keys(os.getcwd()+"/media.png")
        time.sleep(1)
        upload_browser.find_element(By.XPATH, '//*[@id="submit-button"]/a').click()
        num += 1
        if num == 5:
            while True:
                endtime = datetime.today().strftime("%H")
                if endtime != starttime:
                    break
            num = 0

    finishtime = datetime.today().strftime("%Y.%m.%d/%H.%M.%S")
    print('업로드 끝')
def step():
    print('자료확인 시작')
    start_browser()
    kakao_login()
    newspic_login(data['returnpage'], data['repeatnum'])
    find_news()
    print('자료 다운로드 끝')


if __name__ == "__main__":   
    global finishtime
    finishtime = "실행전"
    clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

    schedule.every().day.at("10:00").do(step)
    schedule.every().day.at("15:00").do(upload)
    # step()
    # upload()
    while True:
        clearConsole()   
        schedule.run_pending()
        print('스케쥴 실행중.....' + datetime.today().strftime("%Y.%m.%d/%H.%M.%S"))
        print('마지막 업로드 종료 시간' + finishtime)
        time.sleep(1)
    