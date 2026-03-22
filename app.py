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
        # 거래대금이 문자로 꼬여있을 경우 에러 방지용 (nan은 0으로 처리)
        if '거래대금' in df.columns:
            df['거래대금'] = pd.to_numeric(df['거래대금'], errors='coerce').fillna(0)
            df = df.sort_values(by='거래대금', ascending=False)

        # HTML/CSS를 활용해 올려주신 이미지처럼 완벽한 1줄 디자인 구현
        html_content = ""
        for index, row in df.iterrows():
            name = row.get('종목명', '종목미상')
            sector = row.get('섹터명', '섹터미상')
            
            # 숫자 데이터 안전하게 가져오기
            price = pd.to_numeric(row.get('현재가격', 0), errors='coerce')
            price = 0 if pd.isna(price) else price
            
            volume = row.get('거래대금', 0)
            
            rate = pd.to_numeric(str(row.get('등락률', 0)).replace('%', ''), errors='coerce')
            rate = 0 if pd.isna(rate) else rate

            # 한국 주식 시장 색상 룰 (상승은 빨강, 하락은 파랑)
            color = "#d32f2f" if rate > 0 else "#1976d2" if rate < 0 else "#333"
            bg_color = "#ffebee" if rate > 0 else "#e3f2fd" if rate < 0 else "#f5f5f5"
            sign = "+" if rate > 0 else ""

            # 한 줄 카드 UI 생성
            html_content += f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 10px; margin-bottom: 8px; border-radius: 10px; border: 1px solid #e0e0e0; background-color: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                <div style="flex: 1.5; font-size: 16px; font-weight: 800; color: #222;">
                    {name} <span style="font-size: 11px; font-weight: normal; color: #777; background: #f0f0f0; padding: 2px 6px; border-radius: 10px; margin-left: 5px;">{sector}</span>
                </div>
                <div style="flex: 1; text-align: right; font-size: 15px; font-weight: 700; color: #111;">
                    {price:,.0f}
                </div>
                <div style="flex: 1; text-align: right;">
                    <span style="color: {color}; background-color: {bg_color}; padding: 4px 8px; border-radius: 6px; font-size: 13px; font-weight: bold;">
                        {sign}{rate:.2f}%
                    </span>
                </div>
                <div style="flex: 1; text-align: right; font-size: 14px; color: #555; font-weight: 700;">
                    {volume:,.0f}억
                </div>
            </div>
            """
        
        # 만들어진 HTML 화면에 쏘기
        st.markdown(html_content, unsafe_allow_html=True)

    # 3분 대기 후 자동 새로고침
    time.sleep(180)
    st.rerun()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")