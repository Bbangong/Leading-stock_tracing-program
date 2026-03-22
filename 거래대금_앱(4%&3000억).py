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
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbzUJzNWl4vUxVmIJN1zA4HhHIVKo0aeo_PO7uyL_GYRKUR6FS8dBpLl2dXzRBe9UBEd/exec"

# --- [2. 키움 토큰 발급] ---
def get_access_token():
    url = "https://api.kiwoom.com/oauth2/token"
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    data = {"grant_type": "client_credentials", "appkey": APP_KEY, "secretkey": APP_SECRET}
    res = requests.post(url, data=json.dumps(data), headers=headers)
    return res.json().get("token") if res.status_code == 200 else None

# --- [기존 27번 줄부터 시작] ---

def get_stock_detail(token, stock_code):
    headers = {
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "Content-Type": "application/json;charset=UTF-8"
    }
    data = {"stk_cd": str(stock_code).zfill(6)}
    
    price, mkt_cap, sector = 0, 0, "섹터미상"

    try:
        # --- [1. ka10001 호출: 현재가와 시가총액] ---
        headers["api-id"] = "ka10001"
        res1 = requests.post("https://api.kiwoom.com/api/dostk/stkinfo", 
                             headers=headers, data=json.dumps(data))
        out1 = res1.json().get("output", res1.json())
        
        def clean(v): return str(v).replace(',', '').strip()
        
        # 사용자님 제보: ka10001에서 현재가는 cur_prc, 시총은 mac
        price = abs(int(float(clean(out1.get("cur_prc", "0")))))
        mkt_cap = int(float(clean(out1.get("mac", "0"))))

        # --- [2. ka10100 호출: 업종명] ---
        headers["api-id"] = "ka10100"
        # ka10100은 이미지 4번의 규격을 따름
        res2 = requests.post("https://api.kiwoom.com/api/dostk/stkinfo", 
                             headers=headers, data=json.dumps(data))
        out2 = res2.json().get("output") or res2.json().get("body") or res2.json()
        
        # 사용자님 제보: ka10100에서 업종명은 upName (대문자 N 주의!)
        sector = out2.get("upName") or "섹터미상"

    except Exception as e:
        print(f"❌ {stock_code} 조회 실패: {e}")

    return price, mkt_cap, sector
    

# --- [3. 데이터 수집 및 전송 핵심 로직] ---

def process_leading_stocks(token):
    url = "https://api.kiwoom.com/api/dostk/rkinfo" 
    headers = {
        "authorization": f"Bearer {token}",
        "api-id": "ka10032", # 거래대금상위
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "Content-Type": "application/json;charset=UTF-8"
    }
    data = {"mrkt_tp": "000", "mang_stk_incls": "0", "stex_tp": "1"}
    
    res = requests.post(url, headers=headers, data=json.dumps(data))
    response_data = res.json()
    stock_list = response_data.get("trde_prica_upper", [])
    
    current_time = datetime.now().strftime("%H:%M:%S")
    valid_stocks = []

    for s in stock_list:
        try:
            name = s.get("stk_nm", "알수없음")
            code = s.get("stk_cd", "")
            
            # 거래대금 안전하게 정수화
            amount_raw = str(s.get("trde_prica", "0")).replace(',', '').strip()
            amount = float(amount_raw)
            
            # 🚨 [등락률 1818% 살인 진압 로직]
            rate_raw = str(s.get("flu_rt", "0")).replace(',', '').strip()
            rate = float(rate_raw)
            
            # 한국 주식 상한가는 30%입니다. 이 원칙 하나만 지킵니다.
            # 1818 -> 18.18 / 181.8 -> 18.18
            while abs(rate) > 30.0:
                rate = rate / 10.0 
            
            # 최종 소수점 둘째자리 고정
            rate = round(rate, 2)

            # 테스트용 100억 기준
            if amount >= 200000 and rate >= 4.0:
                price, mkt_cap, sector = get_stock_detail(token, code)
                
                # 시총이 0이면 리스트 API 데이터에서 한 번 더 시도
                if mkt_cap == 0:
                    cap_raw = s.get("mkt_cap") or s.get("hts_avls") or "0"
                    mkt_cap = int(float(str(cap_raw).replace(',', '')))

                if price == 0:
                    price = abs(int(float(str(s.get("cur_prc", "0")).replace(',', ''))))

                valid_stocks.append({
                    "name": name,
                    "price": price,
                    "rate": rate,
                    "amount": int(amount // 100),
                    "cap": mkt_cap,
                    "sector": sector,
                    "time": current_time
                })
        except Exception as e:
            print(f"⚠️ {name} 파싱 에러: {e}")
            continue

    # 거래대금 순 정렬 및 상위 20개
    valid_stocks = sorted(valid_stocks, key=lambda x: x['amount'], reverse=True)[:20]

    # 구글 시트 전송
       # 종목을 하나씩 보내지 않고, 'stocks'라는 이름의 리스트로 묶어서 한 번에 전송!
    payload = {"stocks": valid_stocks}
    
    try:
        response = requests.post(GOOGLE_SHEET_URL, json=payload)
        if response.status_code == 200:
            print(f"✅ 엑셀 초기화 및 최신 주도주 {len(valid_stocks)}개 동기화 완료!")
    except Exception as e:
        print(f"❌ 엑셀 전송 중 오류 발생: {e}")

    return valid_stocks

# --- [여기까지 교체 완료] ---

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