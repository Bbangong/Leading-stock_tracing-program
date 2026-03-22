import streamlit as st
import pandas as pd
import time

# 1. 화면 설정
st.set_page_config(page_title="실시간 주도주", page_icon="🔥", layout="centered")

# 2. 전체 배경 아이보리 설정
st.markdown("""
<style>
    .stApp { background-color: #FDFBF0; }
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
</style>
""", unsafe_allow_html=True)

# 3. 제목 (HTML로 직접 쏴서 디자인 고정)
st.markdown("<h2 style='text-align: center;'>🔥 실시간 거래대금 주도주 🔥</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>3,000억 이상 & 4% 이상 상승 (3분 자동 갱신)</p>", unsafe_allow_html=True)
st.divider()

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQygCBp6noqOTPG2tKVFDrB_PrZsRoDSHQQt9bwF8ZRi-pwiBzVrpKClIPLBBOFCnNWJwHabzkrUzgF/pub?gid=0&single=true&output=csv"

try:
    df = pd.read_csv(CSV_URL)

    if df.empty:
        st.info("📉 데이터 대기 중... 장 시작 후 종목이 포착되면 나타납니다.")
    else:
        # 데이터 정렬 (거래대금 순)
        if '거래대금' in df.columns:
            df['거래대금'] = pd.to_numeric(df['거래대금'], errors='coerce').fillna(0)
            df = df.sort_values(by='거래대금', ascending=False)

        # 🚨 [핵심] HTML을 하나로 묶어서 한 번에 출력 (글자로 나오는 현상 방지)
        final_html = ""
        
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

            # 🎯 [거래대금 노란색 + 한 줄 고정 레이아웃]
            card = f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 10px