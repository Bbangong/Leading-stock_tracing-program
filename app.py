import streamlit as st
import pandas as pd
import time
import html

# 1. 화면 설정
st.set_page_config(page_title="실시간 주도주", page_icon="🔥", layout="centered")

# 2. 전체 배경 아이보리 설정
st.markdown("""
<style>
    .stApp { background-color: #FDFBF0; }
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
</style>
""", unsafe_allow_html=True)

# 3. 제목
st.markdown("<h2 style='text-align: center;'>🔥 실시간 거래대금 주도주 🔥</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>3,000억 이상 & 4% 이상 상승 (3분 자동 갱신)</p>", unsafe_allow_html=True)
st.divider()

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQygCBp6noqOTPG2tKVFDrB_PrZsRoDSHQQt9bwF8ZRi-pwiBzVrpKClIPLBBOFCnNWJwHabzkrUzgF/pub?gid=0&single=true&output=csv"

def to_number(value, default=0):
    num = pd.to_numeric(value, errors='coerce')
    return default if pd.isna(num) else num

def clean_stock_code(value):
    if pd.isna(value): return ""
    code = str(value).strip()
    if code.endswith(".0"): code = code[:-2]
    return code.isdigit() and code.zfill(6) or code

try:
    # 🚨 캐시 방지를 위해 랜덤 파라미터 추가 (선택사항)
    df = pd.read_csv(CSV_URL, dtype={"종목코드": str})

    if df.empty:
        st.info("📉 데이터 대기 중... 장 시작 후 종목이 포착되면 나타납니다.")
    else:
        # 데이터 정렬 (거래대금 순)
        if '거래대금' in df.columns:
            df['거래대금'] = pd.to_numeric(df['거래대금'], errors='coerce').fillna(0)
            df = df.sort_values(by='거래대금', ascending=False)

        # 🚨 [수정] 반복문 안에서 각각 렌더링 (들여쓰기 영향 최소화)
        for _, row in df.iterrows():
            name = html.escape(str(row.get('종목명', '종목미상')))
            code = html.escape(clean_stock_code(row.get('종목코드', '')))
            sector = html.escape(str(row.get('섹터명', '섹터미상')))
            price = to_number(row.get('현재가격', 0))
            volume = to_number(row.get('거래대금', 0))
            market_cap = to_number(row.get('시가총액', 0))
            rate_val = str(row.get('등락률', '0')).replace('%', '')
            rate = to_number(rate_val)

            color = "#ff4d4d" if rate > 0 else "#64b5f6" if rate < 0 else "#ffffff"
            bg_color = "rgba(255, 77, 77, 0.15)" if rate > 0 else "rgba(100, 181, 246, 0.15)" if rate < 0 else "rgba(255,255,255,0.1)"
            sign = "+" if rate > 0 else ""
            code_display = f'<span style="font-size: 12px; color: #B0BEC5; font-weight: 600;">({code})</span>' if code else ""

            # 🎯 [카드 레이아웃] 문자열 앞에 공백이 없도록 바짝 붙여서 작성
            card_html = f"""<div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 10px; margin-bottom: 10px; border-radius: 12px; background-color: #15202B; border: 1px solid #2A3644; box-shadow: 0px 4px 6px rgba(0,0,0,0.2); overflow: hidden;">
<div style="flex: 2; text-align: left; min-width: 0;">
<div style="font-size: 15px; font-weight: 800; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
{name} {code_display}
</div>
<div style="display: flex; align-items: center; gap: 8px; margin-top: 3px; min-width: 0; font-size: 11px; white-space: nowrap; overflow: hidden;">
<span style="color: #FF9800; font-weight: 700; flex-shrink: 0;">시총 {market_cap:,.0f}억</span>
<span style="color: #00E676; overflow: hidden; text-overflow: ellipsis;">{sector}</span>
</div>
</div>
<div style="flex: 0.8; text-align: right; font-size: 15px; font-weight: 700; color: #ff4d4d;">{price:,.0f}</div>
<div style="flex: 1; text-align: right;">
<span style="color: {color}; background-color: {bg_color}; padding: 3px 8px; border-radius: 6px; font-size: 12px; font-weight: bold;">{sign}{rate:.2f}%</span>
</div>
<div style="flex: 0.8; text-align: right; font-size: 13px; color: #FFFF00; font-weight: 700;">{volume:,.0f}억</div>
</div>"""
            # 루프 안에서 즉시 렌더링 (공백 에러 방지)
            st.markdown(card_html, unsafe_allow_html=True)

    # 3분 자동 새로고침
    time.sleep(180)
    st.rerun()

except Exception as e:
    st.error(f"⚠️ 앱 실행 오류: {e}")