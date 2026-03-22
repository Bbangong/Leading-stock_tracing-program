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
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbyF-8dUfzJKoP6yeFCHvonpAk9eVegprXcu_lQeWdy1lITGBQdD5TImH2seWfbli1I/exec"

# --- [2. 키움 토큰 발급] ---
def get_access_token():
    url = "https://api.kiwoom.com/oauth2/token"
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    data = {"grant_type": "client_credentials", "appkey": APP_KEY, "secretkey": APP_SECRET}
    res = requests.post(url, data=json.dumps(data), headers=headers)
    return res.json().get("token") if res.status_code == 200 else None

def get_stock_detail(token, stock_code):
    """종목코드 하나를 받아서 현재가, 시총, 업종명을 가져오는 함수"""
    url = "https://api.kiwoom.com/api/dostk/rkinfo"
    headers = {
        "authorization": f"Bearer {token}",
        "api-id": "ka10001", # 주식기본정보요청 API
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "Content-Type": "application/json;charset=UTF-8"
    }
    data = {"stk_cd": stock_code}
    
    try:
        res = requests.post(url, headers=headers, data=json.dumps(data))
        detail = res.json()
        # 키움 응답 필드에서 데이터 추출 (abs는 마이너스 기호 제거)
        price = abs(int(float(detail.get("cur_prc", "0")))) # 현재가
        mkt_cap = int(float(detail.get("hts_avls", "0"))) # 시가총액(억 단위)
        sector = detail.get("bstp_nm", "섹터미상") # 업종명
        return price, mkt_cap, sector
    except:
        return 0, 0, "섹터미상"

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
            code = s.get("stk_cd", "") # 상세조회를 위해 종목코드가 꼭 필요함!
            amount = float(str(s.get("trde_prica", "0")).replace(',', ''))
            rate = float(str(s.get("flu_rt", "0")).replace(',', ''))

            # 🎯 테스트를 위해 기준을 100(100억)으로 낮춰서 확인해보세요!
            # 실전에서는 300000(3000억)으로 다시 고치면 됩니다.
            if amount >= 100 and rate >= 4.0:
                # 🚨 [중요] 여기서 위에서 만든 상세조회 함수를 호출합니다!
                price, mkt_cap, sector = get_stock_detail(token, code)
                
                amount_100m = int(amount // 100)
                valid_stocks.append({
                    "name": name,
                    "price": price,
                    "rate": rate,
                    "amount": amount_100m,
                    "cap": mkt_cap,
                    "sector": sector,
                    "time": current_time
                })
        except Exception as e:
            print(f"오류 발생({name}): {e}")
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

# --- [4. 실행 메인 루프 (테스트 모드)] ---
async def main():
    print(f"🔥 실전 주도주 엔진 가동! (지금은 테스트 모드입니다)")
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        now = datetime.now()
        
        # 🚨 [시간 체크 해제] 장 시간이 아니어도 무조건 실행되게 설정함!
        if True: 
            print(f"\n[ {now.strftime('%H:%M:%S')} ] 데이터 수집 중...")
            token = get_access_token()
            
            if token:
                # 3천억 필터가 너무 빡빡해서 종목이 안 나올 수 있으니, 
                # 테스트 시에는 3,000억 기준을 잠시 낮춰서 확인해보는 것도 좋습니다!
                stocks = process_leading_stocks(token)
                
                if stocks:
                    msg = f"🔔 [주도주 TOP {len(stocks)} 포착]\n"
                    for s in stocks:
                        msg += f"\n✅ {s['name']} ({s['sector']})\n💰 {s['amount']}억 | 📈 {s['rate']}%"
                    
                    await bot.send_message(chat_id=CHAT_ID, text=msg)
                    print(f"🎯 {len(stocks)}개 종목 포착 및 전송 완료!")
                else:
                    print("📉 조건(3천억/4%)에 맞는 대어가 지금은 없습니다.")
                    print("💡 확인 팁: main.py 위쪽에서 300000 숫자를 100 정도로 낮추면 바로 데이터가 뜹니다!")
            else:
                print("❌ 키움 토큰 발급 실패")

        # 🎯 3분(180초) 대기
        print("⏳ 3분 뒤 다시 시작합니다...")
        await asyncio.sleep(180)

if __name__ == "__main__":
    asyncio.run(main())