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

# --- [2. 키움 토큰 발급] ---
def get_access_token():
    url = "https://api.kiwoom.com/oauth2/token"
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    data = {"grant_type": "client_credentials", "appkey": APP_KEY, "secretkey": APP_SECRET}
    res = requests.post(url, data=json.dumps(data), headers=headers)
    if res.status_code == 200:
        return res.json().get("token")
    return None

# --- [3. 데이터 조회 및 정확한 단위 필터링] ---
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
    
    # 아까 디버깅으로 확인한 정확한 리스트 위치
    stock_list = response_data.get("trde_prica_upper", [])
    leading_stocks = []

    for s in stock_list:
        name = s.get("stk_nm", "알수없음")
        raw_amount = str(s.get("trde_prica", "0")).replace(',', '')
        raw_rate = str(s.get("flu_rt", "0")).replace(',', '')
        
        try:
            amount = float(raw_amount)
            rate = float(raw_rate)
        except ValueError:
            continue

        # 🔥 단위 수정 완료! (단위: 100만원)
        # 500억은 100만원 단위로 '50000' 입니다.
        if amount >= 50000 and rate >= 4.0:
            amount_100m = int(amount // 100)  # 보기 편하게 억 단위로 변환
            leading_stocks.append(f"✅ {name}\n   📈 등락률: +{rate}%\n   💰 거래대금: {amount_100m}억")

    return leading_stocks

# --- [4. 텔레그램 전송] ---
async def send_telegram(text):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)

# --- [5. 메인 실행] ---
async def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 실전 주도주 데이터 분석 시작!")
    token = get_access_token()
    
    if token:
        stocks = get_real_leading_stocks(token)
        
        if stocks:
            print(f"🎯 500억/4% 이상 주도주 {len(stocks)}개 포착 완료!")
            msg = f"🔔 [오늘의 주도주 포착!]\n\n" + "\n\n".join(stocks)
            await send_telegram(msg)
            print("📢 텔레그램을 확인하세요!")
        else:
            msg = "📉 오늘은 500억 이상 터지면서 4% 이상 오른 종목이 없습니다."
            await send_telegram(msg)
            print(msg)
    else:
        print("❌ 인증 실패.")

if __name__ == "__main__":
    asyncio.run(main())