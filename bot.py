import requests
from bs4 import BeautifulSoup
import os
import json

# 1. 내 텔레그램 마스터키와 주소 
TOKEN = '여기에_토큰_붙여넣기'
CHAT_ID = '여기에_채팅ID_붙여넣기'

# 봇의 기억을 저장할 파일 이름
FILE_PATH = 'last_post_id.txt'

# 2. 감시할 게시판 이름과 주소 목록 (원하는 이름으로 마음대로 바꿔도 돼!)
BOARDS = {
    "경영대 장학": "https://kbiz.khu.ac.kr/biz_kor/user/bbs/BMSR00040/list.do?menuNo=14500160",
    "본관 일반공지": "https://www.khu.ac.kr/kor/user/bbs/BMSR00040/list.do?menuNo=200316",
    "본관 학사안내": "https://www.khu.ac.kr/kor/user/bbs/BMSR00040/list.do?menuNo=200317",
    "본관 장학안내": "https://www.khu.ac.kr/kor/user/bbs/BMSR00040/list.do?menuNo=200318",
    "본관 행사안내": "https://www.khu.ac.kr/kor/user/bbs/BMSR00040/list.do?menuNo=200361"
}

# 3. 이전 기억(메모장) 읽어오기
last_post_ids = {}
if os.path.exists(FILE_PATH):
    with open(FILE_PATH, 'r') as f:
        content = f.read().strip()
        if content:
            try:
                # 메모장이 딕셔너리(사물함) 형태인지 확인하고 불러오기
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    last_post_ids = parsed
            except:
                pass # 예전 방식의 숫자만 적혀있으면 그냥 무시하고 새로 사물함을 짬

headers = {'User-Agent': 'Mozilla/5.0'}
updated = False # 새 글이 하나라도 있었는지 체크

# 4. 등록된 게시판을 하나씩 순회하며 확인하기
for board_name, url in BOARDS.items():
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    notices = soup.find_all('td', class_='tal')

    if notices:
        latest_notice = notices[0]
        a_tag = latest_notice.find('a')
        
        if a_tag:
            clean_title = ' '.join(a_tag.text.split())
            raw_link = a_tag['href']
            
            # 새 글 번호 추출
            current_post_id = raw_link.split("'")[1]
            
            # 해당 게시판의 이전 기억 꺼내오기 (처음 확인하는 게시판이면 '0'으로 설정)
            last_id_for_this_board = last_post_ids.get(board_name, "0")
            
            # 현재 번호와 기억된 번호가 다르면 알림 전송!
            if current_post_id != last_id_for_this_board:
                print(f"✨ [{board_name}] 새로운 글 발견! 텔레그램으로 전송합니다.")
                
                message = f"🚨 [{board_name}]\n\n새로운 공지가 올라왔어!\n📌 제목: {clean_title}\n🔗 확인하기: {url}"
                tg_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
                requests.post(tg_url, data={'chat_id': CHAT_ID, 'text': message})
                
                # 기억 업데이트
                last_post_ids[board_name] = current_post_id
                updated = True
            else:
                print(f"💤 [{board_name}] 새로운 공지사항 없음.")

# 5. 메모장에 새 사물함(딕셔너리) 구조로 덮어쓰기 (새 글이 있었을 때만)
if updated:
    with open(FILE_PATH, 'w') as f:
        # json.dumps를 써서 파이썬 딕셔너리를 텍스트 형태로 예쁘게 변환해서 저장
        f.write(json.dumps(last_post_ids))
