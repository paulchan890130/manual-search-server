import os
import subprocess
import time

WATCH_DIR = r"C:/Users/윤찬/내 드라이브/한우리 현행업무/프로그램/manual-search-server"
INTERVAL = 10  # 초 단위 (10초마다 검사)

def get_status():
    result = subprocess.run(["git", "status", "--porcelain"], cwd=WATCH_DIR, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def auto_push():
    print(f"👀 폴더 변경 감지 중... ({WATCH_DIR})")
    while True:
        status = get_status()
        if status:
            print("📌 변경사항 감지! Git Push 진행합니다...")
            subprocess.run(["git", "add", "."], cwd=WATCH_DIR)
            subprocess.run(["git", "commit", "-m", "chore: 자동 감지 커밋"], cwd=WATCH_DIR)
            subprocess.run(["git", "push"], cwd=WATCH_DIR)
            print("✅ Push 완료!")
        else:
            print("⏳ 변경 없음. 대기 중...")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    auto_push()
