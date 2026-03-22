import requests
import json
import telegram
import asyncio
import time
from datetime import datetime

# --- [1. 기본 설정] ---
APP_KEY = "Wrd4IrS8qZpjSlCCqHZoU6CqJjMFh3oEZEku1YfwUPg"
APP_SECRET = "hMNTmhhswR39zHD-Tj8rbqgXyiLNbhucgxnkcsO387E"
TELEGRAM_TOKEN = "8787017558:AAH-CboDNE7QziHnB1RRDRK5F6XBcEKh-6M"
CHAT_ID = "5524071246"

# 구글 시트 웹 앱 URL (사용자님 링크 유지)
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbxNIek3U-nDYigfRILqK8GP8AnF2zeh1cq4sNiDkdM6ICnYRAnch2mEc_K9UB2ttQ-g/exec"

# --- [2. 키움 토큰 발급] ---
def get_access_token():
    url = "https://api.kiwoom.com/oauth2/token"
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    data = {"grant_type": "client_credentials", "appkey": APP_KEY, "secretkey": APP_SECRET}
    res = requests.post(url, data=json.dumps(data), headers=headers)
    return res.json().get("token") if res.status_code == 200 else None

# --- [3. 데이터 수집 및 전송 핵심 로직] ---
def process_leading_stocks(token):
    url = "https://api.kiwoom.com/api/dostk/rkinfo" 
    headers = {
        "authorization": f"Bearer {token}",
        "api-id": "ka10032",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "Content-Type": "application/json;charset=UTF-8"
    }
    # 거래대금 상위 조회 파라미터
    data = {"mrkt_tp": "000", "mang_stk_incls": "0", "stex_tp": "1"}
    
    res = requests.post(url, headers=headers, data=json.dumps(data))
    response_data = res.json()
    stock_list = response_data.get("trde_prica_upper", [])
    
    current_time = datetime.now().strftime("%H:%M:%S")
    valid_stocks = []

    for s in stock_list:
        try:
            name = s.get("stk_nm", "알수없음")
            amount = float(str(s.get("trde_prica", "0")).replace(',', '')) # 거래대금(단위: 백만)
            rate = float(str(s.get("flu_rt", "0")).replace(',', ''))      # 등락률
            price = int(float(str(s.get("stk_prc", "0")).replace(',', ''))) # 현재가
            mkt_cap = float(str(s.get("mkt_cap", "0")).replace(',', ''))  # 시총(단위: 억)
            sector = s.get("theme_nm", "섹터미상") # 섹터명(테마명)

            # 🎯 실전 조건: 거래대금 3,000억(300,000백만) 이상 & 4% 이상
            if amount >= 300000 and rate >= 4.0:
                amount_100m = int(amount // 100) # 억 단위 변환
                valid_stocks.append({
                    "name": name,
                    "price": price,
                    "rate": rate,
                    "amount": amount_100m,
                    "cap": int(mkt_cap),
                    "sector": sector,
                    "time": current_time
                })
        except:
            continue

    # 🎯 거래대금 순으로 정렬 후 상위 20개만 컷
    valid_stocks = sorted(valid_stocks, key=lambda x: x['amount'], reverse=True)[:20]

    # 구글 시트로 데이터 쏘기 (한꺼번에 보내는 것이 좋으나, 기존 시트 구조 유지)
    for stock in valid_stocks:
        sheet_data = {
            "time": stock["time"],
            "name": stock["name"],
            "rate": f"{stock['rate']}%",
            "amount": stock["amount"],
            "price": stock["price"],
            "cap": stock["cap"],
            "sector": stock["sector"]
        }
        try:
            requests.post(GOOGLE_SHEET_URL, json=sheet_data)
        except:
            pass

    return valid_stocks

# --- [4. 실행 메인 루프] ---
async def main():
    print(f"🔥 실전 주도주 무한 엔진 가동! (3,000억/4% 기준)")
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        now = datetime.now()
        # 장중 시간(09:00~15:35) 체크 (테스트 시에는 이 조건 주석 처리 가능)
        if (now.hour == 9 and now.minute >= 0) or (10 <= now.hour < 15) or (now.hour == 15 and now.minute <= 35):
            print(f"\n[ {now.strftime('%H:%M:%S')} ] 데이터 수집 중...")
            token = get_access_token()
            
            if token:
                stocks = process_leading_stocks(token)
                
                if stocks:
                    msg = f"🔔 [주도주 TOP {len(stocks)} 포착]\n"
                    for s in stocks:
                        msg += f"\n✅ {s['name']} ({s['sector']})\n💰 {s['amount']}억 | 📈 {s['rate']}%"
                    
                    await bot.send_message(chat_id=CHAT_ID, text=msg)
                    print(f"🎯 {len(stocks)}개 종목 포착 및 전송 완료!")
                else:
                    print("📉 조건에 맞는 대어가 없습니다.")
            else:
                print("❌ 키움 토큰 발급 실패")
        else:
            print(f"💤 현재 시간 {now.strftime('%H:%M')}, 장 운영 시간이 아닙니다.")

        # 🎯 3분(180초) 대기
        print("⏳ 3분 뒤 다시 시작합니다...")
        await asyncio.sleep(180)

if __name__ == "__main__":
    asyncio.run(main())