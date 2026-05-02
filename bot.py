import requests
from bs4 import BeautifulSoup
import os
import json

# 1. 내 텔레그램 마스터키와 주소 (여기에 본인 정보 입력!)
TOKEN = '8666105720:AAHpmLyz3PW8d9IpJSNZBpX-RpNQE6OCkNM'
CHAT_ID = '6511348560'
FILE_PATH = 'last_post_id.txt'

# 2. 감시할 게시판 이름과 주소 목록
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
                last_post_ids = json.loads(content)
            except:
                pass

headers = {'User-Agent': 'Mozilla/5.0'}
updated = False # 메모장을 덮어쓸지 말지 결정하는 스위치

# 4. 각 게시판 순회하며 여러 개의 새 글 찾기 (버전 3.0 핵심 로직!)
for board_name, url in BOARDS.items():
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 해당 게시판의 글 목록 쫙 다 가져오기
    notices = soup.find_all('td', class_='tal')
    
    # 봇이 해당 게시판에서 마지막으로 기억하고 있는 글 번호 (없으면 '0')
    last_id_for_this_board = last_post_ids.get(board_name, "0")
    
    # 새롭게 발견한 공지들을 담을 빈 바구니
    new_notices_found = []
    
    # 이번에 확인한 가장 큰(최신) 번호를 임시로 저장할 변수
    max_id_this_time = int(last_id_for_this_board)
    
    for notice in notices:
        a_tag = notice.find('a')
        if a_tag:
            clean_title = ' '.join(a_tag.text.split())
            raw_link = a_tag['href']
            
            # 주소에서 글 번호만 빼내기 (숫자로 변환하여 비교)
            try:
                current_post_id_str = raw_link.split("'")[1]
                current_post_id = int(current_post_id_str)
            except:
                continue # 번호를 못 찾으면 에러 내지 말고 다음 글로 넘어가
                
            # 만약 글 번호가 내가 기억하는 마지막 번호보다 크면 = 이건 무조건 새 글이다!
            if current_post_id > int(last_id_for_this_board):
                new_notices_found.append({'id': current_post_id_str, 'title': clean_title})
                
                # 확인한 번호 중 가장 큰 번호 갱신
                if current_post_id > max_id_this_time:
                    max_id_this_time = current_post_id

    # 바구니에 담긴 새 글이 있다면 알림 보내기
    if new_notices_found:
        print(f"✨ [{board_name}] 새로운 글 {len(new_notices_found)}개 발견!")
        
        # 메시지 텍스트 조립 (여러 개면 한 메시지에 깔끔하게 모아서 보냄)
        message = f"🚨 [{board_name}] 새 공지 {len(new_notices_found)}건\n\n"
        for idx, item in enumerate(new_notices_found, 1):
            message += f"{idx}. {item['title']}\n"
        message += f"\n🔗 확인하기: {url}"
        
        # 텔레그램으로 쏘기
        tg_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
        requests.post(tg_url, data={'chat_id': CHAT_ID, 'text': message})
        
        # 메모장에 가장 최신 번호(제일 큰 번호)로 업데이트
        last_post_ids[board_name] = str(max_id_this_time)
        updated = True
    else:
        print(f"💤 [{board_name}] 새로운 공지사항 없음.")

# 5. 메모장에 변경된 사물함 덮어쓰기
if updated:
    with open(FILE_PATH, 'w') as f:
        f.write(json.dumps(last_post_ids))
