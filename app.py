import streamlit as st
import pandas as pd
import time

# 화면 꽉 차게 쓰기 위한 설정
st.set_page_config(page_title="실시간 주도주", page_icon="🔥", layout="centered")

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

            color = "#d32f2f" if rate > 0 else "#1976d2" if rate < 0 else "#333"
            bg_color = "#ffebee" if rate > 0 else "#e3f2fd" if rate < 0 else "#f5f5f5"
            sign = "+" if rate > 0 else ""

            # 🔥 요청하신 디자인