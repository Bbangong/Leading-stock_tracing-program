import streamlit as st
import pandas as pd
import time

# 화면 꽉 차게 쓰기 위한 설정
st.set_page_config(page_title="실시간 주도주", page_icon="🔥", layout="centered")

# 🔥 전체 앱 배경색을 연한 아이보리(#FDFBF0)로 덮어버리는 특수 코드
st.markdown("""
<style>
.stApp {
    background-color: #FDFBF0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("### 🔥 거래대금 상위 주도섹터")
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
            
            rate = pd.to_numeric(str(row.get('등락률', 0)).replace('%', ''), errors='coerce')
            rate = 0 if pd.isna(rate) else rate

            # 남색 배경에 맞춰 등락률 박스 색상도 밝고 세련되게 조정
            color = "#ff4d4d" if rate > 0 else "#64b5f6" if rate < 0 else "#ffffff"
            bg_color = "rgba(255, 77, 77, 0.15)" if rate > 0 else "rgba(100, 181, 246, 0.15)" if rate < 0 else "rgba(255,255,255,0.1)"
            sign = "+" if rate > 0 else ""

            # 🔥 디자인 구역: 진한 남색 바탕(#15202B), 흰색 글씨, 밝은 초록색/빨간색 포인트
            html_content += f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 10px; margin-bottom: 8px; border-radius: 10px; border: 1px solid #0f171e; background-color: #15202B; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                <div style="flex: 1.5; text-align: left;">
                    <div style="font-size: 16px; font-weight: 900; color: #ffffff;">{name}</div>
                    <div style="font-size: 12px; font-weight: 700; color: #00E676; margin-top: 3px;">{sector}</div>
                </div>
                <div style="flex: 1; text-align: right; font-size: 16px; font-weight: 800; color: #ff4d4d;">
                    {price:,.0f}
                </div>
                <div style="flex: 1; text-align: right;">
                    <span style="color: {color}; background-color: {bg_color}; padding: 4px 8px; border-radius: 6px; font-size: 13px; font-weight: bold;">
                        {sign}{rate:.2f}%
                    </span>
                </div>
                <div style="flex: 1; text-align: right; font-size: 14px; color: #b0bec5; font-weight: 700;">
                    {volume:,.0f}억
                </div>
            </div>
            """
        
        st.markdown(html_content, unsafe_allow_html=True)

    time.sleep(180)
    st.rerun()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")