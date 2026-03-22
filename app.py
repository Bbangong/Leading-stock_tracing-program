import streamlit as st
import pandas as pd
import time

# 1. 화면 설정
st.set_page_config(page_title="실시간 주도주", page_icon="🔥", layout="centered")

# 2. 전체 배경 아이보리 설정 (CSS가 확실히 먹히도록 수정)
st.markdown("""
<style>
    .stApp { background-color: #FDFBF0; }
    /* 스트림릿 기본 마진 제거 */
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
</style>
""", unsafe_allow_html=True)

# 3. 제목
st.markdown("<h2 style='text-align: center;'>🔥 거래대금 상위 주도섹터 🔥</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>거래대금 상위 & 4% 이상 상승종목 (3분 자동 갱신)</p>", unsafe_allow_html=True)
st.divider()

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQygCBp6noqOTPG2tKVFDrB_PrZsRoDSHQQt9bwF8ZRi-pwiBzVrpKClIPLBBOFCnNWJwHabzkrUzgF/pub?gid=0&single=true&output=csv"

try:
    # 🚨 데이터 불러오기 (캐시 방지를 위해 랜덤값 추가는 생략, 기본 충실)
    df = pd.read_csv(CSV_URL)

    if df.empty:
        st.info("📉 데이터 대기 중... 본체 PC에서 수집 중입니다.")
    else:
        # 데이터 전처리 및 정렬
        if '거래대금' in df.columns:
            df['거래대금'] = pd.to_numeric(df['거래대금'], errors='coerce').fillna(0)
            df = df.sort_values(by='거래대금', ascending=False)

        # 🚨 여기서부터 카드를 하나씩 직접 그립니다 (더 안정적임)
        for index, row in df.iterrows():
            name = str(row.get('종목명', '종목미상'))
            sector = str(row.get('섹터명', '섹터미상'))
            price = pd.to_numeric(row.get('현재가격', 0), errors='coerce')
            volume = pd.to_numeric(row.get('거래대금', 0), errors='coerce')
            market_cap = pd.to_numeric(row.get('시가총액', 0), errors='coerce')
            rate_str = str(row.get('등락률', '0')).replace('%', '')
            rate = pd.to_numeric(rate_str, errors='coerce') or 0

            color = "#ff4d4d" if rate > 0 else "#64b5f6" if rate < 0 else "#ffffff"
            bg_color = "rgba(255, 77, 77, 0.15)" if rate > 0 else "rgba(100, 181, 246, 0.15)" if rate < 0 else "rgba(255,255,255,0.1)"
            sign = "+" if rate > 0 else ""

            # 🎯 [한 줄 고정 + 디자인 강제 적용]
            card_html = f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 10px; margin-bottom: 10px; border-radius: 12px; background-color: #15202B; border: 1px solid #2A3644; box-shadow: 0px 4px 6px rgba(0,0,0,0.2);">
                <div style="flex: 2; text-align: left; min-width: 0; overflow: hidden;">
                    <div style="font-size: 15px; font-weight: 800; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {name} <span style="font-size: 11px; color: #FF9800; font-weight: 700;">{market_cap:,.0f}억</span>
                    </div>
                    <div style="font-size: 11px; color: #00E676; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{sector}</div>
                </div>
                <div style="flex: 0.8; text-align: right; font-size: 15px; font-weight: 700; color: #ff4d4d;">
                    {price:,.0f}
                </div>
                <div style="flex: 1; text-align: right;">
                    <span style="color: {color}; background-color: {bg_color}; padding: 3px 8px; border-radius: 6px; font-size: 12px; font-weight: bold; white-space: nowrap;">
                        {sign}{rate:.2f}%
                    </span>
                </div>
                <div style="flex: 0.8; text-align: right; font-size: 13px; color: #A1887F; font-weight: 700;">
                    {volume:,.0f}억
                </div>
            </div>
            """
            # 루프 안에서 즉시 렌더링
            st.markdown(card_html, unsafe_allow_html=True)

    # 3분 자동 갱신
    time.sleep(180)
    st.rerun()

except Exception as e:
    st.error(f"⚠️ 앱 실행 중 오류: {e}")