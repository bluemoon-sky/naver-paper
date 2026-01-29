import os
import sys

def restore_cookies():
    # 저장할 쿠키 파일명 (예: goodman6999.json)
    # 여기서는 GitHub Secrets 이름을 COOKIE_JSON_{USER_ID} 형태로 가정
    # 예: NAVER_ID가 goodman6999이면 COOKIE_JSON_GOODMAN6999 환경변수에서 읽어옴
    
    naver_ids = os.environ.get('NAVER_ID', '').split('|')
    
    for nid in naver_ids:
        nid = nid.strip()
        if not nid:
            continue
            
        env_var_name = f"COOKIE_JSON_{nid.upper()}"
        cookie_content = os.environ.get(env_var_name)
        
        if cookie_content:
            file_path = f"{nid}.json"
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cookie_content)
                print(f"Succees: Restored cookie file for {nid}")
            except Exception as e:
                print(f"Error: Failed to restore cookie file for {nid} - {e}")
        else:
            print(f"Warning: No secret found for {env_var_name}")

if __name__ == "__main__":
    restore_cookies()
