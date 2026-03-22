import streamlit as st
import pandas as pd
import time

# 1. 화면 기본 설정
st.set_page_config(page_title="실전 주도주 포착", page_icon="🔥", layout="centered")

st.header("🔥 실시간 주도주 포착 (TOP 20)")
st.write("본체 PC에서 쏴주는 실시간 주도주 데이터를 그대로 보여줍니다.")
st.divider()

# ⭐ 사용자님의 구글 엑셀 CSV 링크
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQygCBp6noqOTPG2tKVFDrB_PrZsRoDSHQQt9bwF8ZRi-pwiBzVrpKClIPLBBOFCnNWJwHabzkrUzgF/pub?gid=0&single=true&output=csv"

try:
    df = pd.read_csv(CSV_URL)

    if df.empty:
        st.info("📉 대기 중... 본체 PC에서 데이터를 수집하고 있습니다.")
    else:
        # 엑셀에 있는 데이터를 거래대금 순으로만 깔끔하게 정렬
        if '거래대금' in df.columns:
            df['거래대금'] = pd.to_numeric(df['거래대금'], errors='coerce')
            df = df.sort_values(by='거래대금', ascending=False)

        # UI: 종목별 깔끔한 카드 형태 출력 (조건 필터링 없이 엑셀 내용 100% 출력)
        for index, row in df.iterrows():
            sector = row.get('섹터명', '섹터미상')
            price = row.get('현재가격', 0)
            market_cap = row.get('시가총액', 0)
            capture_time = row.get('포착시간', '00:00:00')

            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"### 🎯 {row['종목명']} <span style='font-size:14px; color:gray;'>{sector}</span>", unsafe_allow_html=True)
                    st.caption(f"⏱️ {capture_time} 포착 | 💰 시총: {market_cap:,}억")
                
                with col2:
                    st.metric(label="현재가", value=f"{price:,}원", delta=f"{row['등락률']}%")
                
                with col3:
                    st.metric(label="거래대금", value=f"{row['거래대금']:,.0f}억")
                    
                st.divider()

    # 3분(180초) 대기 후 자동 새로고침 
    st.caption("🔄 3분마다 최신 데이터로 자동 갱신됩니다...")
    time.sleep(180)
    st.rerun()

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다. 엑셀 주소를 확인해주세요.")