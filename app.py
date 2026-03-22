import streamlit as st
import pandas as pd

# 1. 화면 기본 설정
st.set_page_config(page_title="실시간 주도주", page_icon="📈", layout="centered")

st.header("🎯 오늘의 주도주 포착")
st.write("거래대금 500억 이상 & 4% 이상 상승 종목 (구글 엑셀 실시간 연동)")
st.divider()

# ⭐ 2. 아까 구글 엑셀에서 복사한 CSV 링크를 아래 따옴표 안에 붙여넣으세요!
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQygCBp6noqOTPG2tKVFDrB_PrZsRoDSHQQt9bwF8ZRi-pwiBzVrpKClIPLBBOFCnNWJwHabzkrUzgF/pub?gid=0&single=true&output=csv"

try:
    # 파이썬이 구글 엑셀 데이터를 실시간으로 읽어옵니다.
    df = pd.read_csv(CSV_URL)

    # 데이터가 비어있을 경우
    if df.empty:
        st.info("📉 아직 포착된 주도주가 없습니다.")
    else:
        # 3. 엑셀의 각 줄(종목)을 돌면서 예쁜 카드로 만들기
        for index, row in df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    # 엑셀의 A1, B1, C1, D1 이름표와 똑같이 적어줍니다.
                    st.subheader(f"✅ {row['종목명']}")
                    st.caption(f"⏱️ 포착: {row['포착시간']}")
                with col2:
                    st.metric(label="등락률", value=str(row['등락률']))
                with col3:
                    st.metric(label="거래대금", value=str(row['거래대금']))
                    
                st.divider()

except Exception as e:
    st.error("엑셀 주소를 다시 확인해 주세요! (웹에 게시 -> CSV 링크)")