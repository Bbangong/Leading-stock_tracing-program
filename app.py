import streamlit as st
import pandas as pd
import time

# 1. 화면 설정
st.set_page_config(page_title="실시간 주도주", page_icon="🔥", layout="centered")

# 2. 전체 배경 아이보리 설정
st.markdown("""
<style>
.stApp {
    background-color: #FDFBF0;
}
</style>
""", unsafe_allow_html=True)

# 3. 제목
st.markdown("### 🔥 거래대금 상위 주도섹터 🔥")
st.caption("거래대금 상위 & 4% 이상 상승종목 (3분 자동 갱신)")
st.divider()

# ⭐ 사용자님의 구글 엑셀 CSV 링크
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQygCBp6noqOTPG2tKVFDrB_PrZsRoDSHQQt9bwF8ZRi-pwiBzVrpKClIPLBBOFCnNWJwHabzkrUzgF/pub?gid=0&single=true&output=csv"

try:
    # 캐시 방지를 위해 랜덤 쿼리 파라미터 추가 (선택사항)
    df = pd.read_csv(CSV_URL)

    if df.empty:
        st.info("📉 데이터 대기 중... 본체 PC에서 수집 중입니다.")
    else:
        # 거래대금 기준 정렬
        if '거래대금' in df.columns:
            df['거래대금'] = pd.to_numeric(df['거래대금'], errors='coerce').fillna(0)
            df = df.sort_values(by='거래대금', ascending=False)

        html_content = ""
        for index, row in df.iterrows():
            # 🚨 [수정] 엑셀 헤더 '섹터명'과 일치 확인됨
            name = row.get('종목명', '종목미상')
            sector = row.get('섹터명', '섹터미상')
            price = pd.to_numeric(row.get('현재가격', 0), errors='coerce')
            price = 0 if pd.isna(price) else price
            volume = row.get('거래대금', 0)
            market_cap = pd.to_numeric(row.get('시가총액', 0), errors='coerce')
            market_cap = 0 if pd.isna(market_cap) else market_cap
            rate = pd.to_numeric(str(row.get('등락률', 0)).replace('%', ''), errors='coerce')
            rate = 0 if pd.isna(rate) else rate

            color = "#ff4d4d" if rate > 0 else "#64b5f6" if rate < 0 else "#ffffff"
            bg_color = "rgba(255, 77, 77, 0.15)" if rate > 0 else "rgba(100, 181, 246, 0.15)" if rate < 0 else "rgba(255,255,255,0.1)"
            sign = "+" if rate > 0 else ""

            # 🚨 [최종 레이아웃] 한 줄 고정 및 말줄임 처리 적용
            card = f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 10px; margin-bottom: 8px; border-radius: 10px; border: 1px solid #0f171e; background-color: #15202B; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); overflow: hidden;">
                <div style="flex: 2; text-align: left; min-width: 0;">
                    <div style="font-size: 15px; font-weight: 900; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {name} <span style="font-size: 11px; color: #FF9800; margin-left: 2px; font-weight: 700;">{market_cap:,.0f}억</span>
                    </div>
                    <div style="font-size: 11px; font-weight: 700; color: #00E676; margin-top: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{sector}</div>
                </div>
                
                <div style="flex: 0.8; text-align: right; font-size: 15px; font-weight: 800; color: #ff4d4d; white-space: nowrap;">
                    {price:,.0f}
                </div>
                
                <div style="flex: 1; text-align: right; white-space: nowrap;">
                    <span style="color: {color}; background-color: {bg_color}; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: bold;">
                        {sign}{rate:.2f}%
                    </span>
                </div>
                
                <div style="flex: 0.9; text-align: right; font-size: 13px; color: #A1887F; font-weight: 700; white-space: nowrap;">
                    {volume:,.0f}억
                </div>
            </div>
            """
            html_content += card
        
        st.markdown(html_content, unsafe_allow_html=True)

    # 3분 대기 후 자동 리런
    time.sleep(180)
    st.rerun()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")