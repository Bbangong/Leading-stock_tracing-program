import streamlit as st
import pandas as pd
import time

# 화면 설정
st.set_page_config(page_title="실시간 주도주", page_icon="🔥", layout="centered")

# 전체 배경 아이보리 설정
st.markdown("""
<style>
.stApp {
    background-color: #FDFBF0;
}
</style>
""", unsafe_allow_html=True)

# 제목에 불꽃 하나 더 추가! 🔥
st.markdown("### 🔥 거래대금 상위 주도섹터 🔥")
st.caption("거래대금 상위 & 4% 이상 상승종목 (3분 자동 갱신)")
st.divider()

# ⭐ 사용자님의 구글 엑셀 CSV 링크
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQygCBp6noqOTPG2tKVFDrB_PrZsRoDSHQQt9bwF8ZRi-pwiBzVrpKClIPLBBOFCnNWJwHabzkrUzgF/pub?gid=0&single=true&output=csv"

try:
    df = pd.read_csv(CSV_URL)

    if df.empty:
        st.info("📉 데이터 대기 중... 본체 PC에서 수집 중입니다.")
    else:
        if '거래대금' in df.columns:
            df['거래대금'] = pd.to_numeric(df['거래대금'], errors='coerce').fillna(0)
            df = df.sort_values(by='거래대금', ascending=False)

        html_content = ""
        for index, row in df.iterrows():
            name = row.get('종목명', '종목미상')
            sector = row.get('섹터명', '섹터미상')
            
            price = pd.to_numeric(row.get('현재가격', 0), errors='coerce')
            price = 0 if pd.isna(price) else price
            
            volume = row.get('거래대금', 0)
            
            # 시가총액 데이터 가져오기 (단위: 억)
            market_cap = pd.to_numeric(row.get('시가총액', 0), errors='coerce')
            market_cap = 0 if pd.isna(market_cap) else market_cap
            
            rate = pd.to_numeric(str(row.get('등락률', 0)).replace('%', ''), errors='coerce')
            rate = 0 if pd.isna(rate) else rate

            color = "#ff4d4d" if rate > 0 else "#64b5f6" if rate < 0 else "#ffffff"
            bg_color = "rgba(255, 77, 77, 0.15)" if rate > 0 else "rgba(100, 181, 246, 0.15)" if rate < 0 else "rgba(255,255,255,0.1)"
            sign = "+" if rate > 0 else ""

            # 🔥 요청하신 디자인 수정 반영
            # 1. 종목명 옆 시가총액 표기 (색상: 주황색 #FF9800)
            # 2. 거래대금 색상 (진한 갈색 #5D4037)
            # 3. 박스 배경 남색 (#15202B), 현재가 빨간색 (#ff4d4d) 유지
            
            html_content += f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 10px; margin-bottom: 8px; border-radius: 10px; border: 1px solid #0f171e; background-color: #15202B; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                <div style="flex: 1.5; text-align: left;">
                    <div style="font-size: 16px; font-weight: 900; color: #ffffff;">
                        {name} <span style="font-size: 12px; color: #FF9800; margin-left: 4px;">{market_cap:,.0f}억</span>
                    </div>
                    <div style="font-size: 12px; font-weight: 700; color: #00E676; margin-top: 3px;">{sector}</div>
                </div>
                <div style="flex: 1; text-align: right; font-size: 16px; font-weight: 800; color: #ff4d4d;">
                    {price:,.0f}
                </div>
                <div style="flex: 1; text-align