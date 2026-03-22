import requests
import json
import telegram
import asyncio
from datetime import datetime

# --- [1. 기본 설정] ---
APP_KEY = "Wrd4IrS8qZpjSlCCqHZoU6CqJjMFh3oEZEku1YfwUPg"
APP_SECRET = "hMNTmhhswR39zHD-Tj8rbqgXyiLNbhucgxnkcsO387E"
TELEGRAM_TOKEN = "8787017558:AAH-CboDNE7QziHnB1RRDRK5F6XBcEKh-6M"
CHAT_ID = "5524071246"

# ⭐ 방금 만든 구글 시트 웹 앱 URL을 여기에 넣습니다!
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbxNIek3U-nDYigfRILqK8GP8AnF2zeh1cq4sNiDkdM6ICnYRAnch2mEc_K9UB2ttQ-g/exec"

# --- [2. 키움 토큰 발급] ---
def get_access_token():
    url = "https://api.kiwoom.com/oauth2/token"
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    data = {"grant_type": "client_credentials", "appkey": APP_KEY, "secretkey": APP_SECRET}
    res = requests.post(url, data=json.dumps(data), headers=headers)
    if res.status_code == 200:
        return res.json().get("token")
    return None

# --- [3. 데이터 조회 및 구글 엑셀 전송] ---
def get_real_leading_stocks(token):
    url = "https://api.kiwoom.com/api/dostk/rkinfo" 
    headers = {
        "authorization": f"Bearer {token}",
        "api-id": "ka10032",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "Content-Type": "application/json;charset=UTF-8"
    }
    data = {"mrkt_tp": "000", "mang_stk_incls": "0", "stex_tp": "1"}

    res = requests.post(url, headers=headers, data=json.dumps(data))
    response_data = res.json()
    
    stock_list = response_data.get("trde_prica_upper", [])
    leading_stocks = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    for s in stock_list:
        name = s.get("stk_nm", "알수없음")
        raw_amount = str(s.get("trde_prica", "0")).replace(',', '')
        raw_rate = str(s.get("flu_rt", "0")).replace(',', '')
        
        try:
            amount = float(raw_amount)
            rate = float(raw_rate)
        except ValueError:
            continue

        # 500억 이상 & 4% 이상 조건
        if amount >= 50000 and rate >= 4.0:
            amount_100m = int(amount // 100)
            rate_str = f"+{rate}%" if rate > 0 else f"{rate}%"
            
            # 1. 텔레그램용 텍스트 조립
            leading_stocks.append(f"✅ {name}\n   📈 등락률: {rate_str}\n   💰 거래대금: {amount_100m}억")
            
            # 2. 구글 엑셀로 쏠 데이터 조립 (아까 우리가 정한 A, B, C, D 열 이름표)
            sheet_data = {
                "time": current_time,
                "name": name,
                "rate": rate_str,
                "amount": f"{amount_100m}억"
            }
            
            # 3. 구글 엑셀로 전송! (POST 방식)
            try:
                requests.post(GOOGLE_SHEET_URL, json=sheet_data)
            except Exception as e:
                print(f"엑셀 전송 에러 ({name}): {e}")

    return leading_stocks

# --- [4. 텔레그램 전송] ---
async def send_telegram(text):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)

# --- [5. 메인 실행] ---
async def main():
    print("🚀 실전 주도주 수집 및 구글 시트 전송 시작!")
    token = get_access_token()
    
    if token:
        stocks = get_real_leading_stocks(token)
        
        if stocks:
            print(f"🎯 500억/4% 이상 주도주 {len(stocks)}개 포착! (엑셀 기록 완료)")
            msg = f"🔔 [오늘의 주도주 포착!]\n\n" + "\n\n".join(stocks)
            await send_telegram(msg)
            print("📢 텔레그램 알림도 발송했습니다!")
        else:
            print("📉 조건에 맞는 종목이 없습니다.")
    else:
        print("❌ 인증 실패.")

if __name__ == "__main__":
    asyncio.run(main())