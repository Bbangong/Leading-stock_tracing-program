import streamlit as st
import pandas as pd
import time

# 1. 화면 기본 설정 (실전용으로 깔끔하게)
st.set_page_config(page_title="실전 주도주 포착", page_icon="🔥", layout="centered")

st.header("🔥 실시간 주도주 포착 (TOP 20)")
st.write("조건: 거래대금 3천억 & 4% 이상 상승 (3분 자동 갱신)")
st.divider()

# ⭐ 사용자님의 구글 엑셀 CSV 링크를 아래에 꼭 넣으세요!
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQygCBp6noqOTPG2tKVFDrB_PrZsRoDSHQQt9bwF8ZRi-pwiBzVrpKClIPLBBOFCnNWJwHabzkrUzgF/pub?gid=0&single=true&output=csv"

try:
    df = pd.read_csv(CSV_URL)

    if not df.empty:
        # 데이터 전처리: 엑셀 데이터를 계산 가능한 숫자로 강제 변환
        df['거래대금'] = pd.to_numeric(df['거래대금'], errors='coerce')
        df['등락률'] = pd.to_numeric(df['등락률'].astype(str).str.replace('%', ''), errors='coerce')

        # 1. 필터링: 거래대금 3000억 이상 & 등락률 4% 이상
        df = df[(df['거래대금'] >= 3000) & (df['등락률'] >= 4.0)]

        # 4. 정렬 & 자르기: 거래대금 기준 내림차순 정렬 후 상위 20개만 컷!
        df = df.sort_values(by='거래대금', ascending=False).head(20)

    if df.empty:
        st.info("📉 현재 조건(3천억/4% 이상)에 맞는 주도주가 없습니다.")
    else:
        # 3 & 5. UI: 종목별 깔끔한 카드 형태 출력
        for index, row in df.iterrows():
            # 키움 API에서 아직 데이터를 안 쏴줄 경우를 대비한 안전장치 (에러 방지)
            sector = row.get('섹터명', '섹터미상')
            price = row.get('현재가격', 0)
            market_cap = row.get('시가총액', 0)
            capture_time = row.get('포착시간', '00:00:00')

            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    # 종목명과 섹터명을 세련되게 배치
                    st.markdown(f"### 🎯 {row['종목명']} <span style='font-size:14px; color:gray;'>{sector}</span>", unsafe_allow_html=True)
                    # 포착시간과 시총을 작은 글씨로 배치
                    st.caption(f"⏱️ {capture_time} 포착 | 💰 시총: {market_cap:,}억")
                
                with col2:
                    # 등락률을 증권앱처럼 위아래 화살표 색상과 함께 표시
                    st.metric(label="현재가", value=f"{price:,}원", delta=f"{row['등락률']}%")
                
                with col3:
                    st.metric(label="거래대금", value=f"{row['거래대금']:,.0f}억")
                    
                st.divider()

    # 2. 3분(180초) 대기 후 자동 새로고침 (9시부터 돌아가는 건 컴퓨터 코드에서 제어)
    st.caption("🔄 3분마다 최신 데이터로 자동 갱신됩니다...")
    time.sleep(180)
    st.rerun()

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다. 엑셀 주소를 확인해주세요.")