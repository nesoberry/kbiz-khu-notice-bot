import requests
from bs4 import BeautifulSoup
import os

TOKEN = '8666105720:AAHpmLyz3PW8d9IpJSNZBpX-RpNQE6OCkNM'
CHAT_ID = '6511348560'

# 봇의 기억을 저장할 메모장 파일 이름
FILE_PATH = 'last_post_id.txt'

# 1. 이전 기억(메모장) 읽어오기
last_post_id = ""
if os.path.exists(FILE_PATH): # 만약 메모장 파일이 있다면
    with open(FILE_PATH, 'r') as f:
        last_post_id = f.read().strip() # 파일에 적힌 번호를 읽어옴

# 2. 학교 장학게시판 접속
url = "https://kbiz.khu.ac.kr/biz_kor/user/bbs/BMSR00040/list.do?menuNo=14500160"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
notices = soup.find_all('td', class_='tal')

if notices:
    latest_notice = notices[0]
    a_tag = latest_notice.find('a')
    
    if a_tag:
        clean_title = ' '.join(a_tag.text.split())
        raw_link = a_tag['href']
        current_post_id = raw_link.split("'")[1] # 현재 게시판의 최신 글 번호
        
        # 3. 기억과 현재 비교하기!
        if current_post_id != last_post_id:
            print(f"✨ 새로운 글 발견! ({current_post_id}) 텔레그램으로 전송합니다.")
            
            message = f"🚨 [경영대학 정보 알림봇]\n\n새로운 공지가 올라왔어!\n📌 제목: {clean_title}\n🔗 확인하기: {url}"
            tg_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
            requests.post(tg_url, data={'chat_id': CHAT_ID, 'text': message})
            
            # 4. 메모장 업데이트 (새로운 글 번호로 덮어쓰기)
            with open(FILE_PATH, 'w') as f:
                f.write(current_post_id)
                
        else:
            print(f"💤 새로운 공지사항이 없어. (마지막 확인 글 번호: {last_post_id})")
