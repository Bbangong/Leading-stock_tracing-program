import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
import html

# 1. 화면 설정
st.set_page_config(page_title="실시간 주도주", page_icon="🔥", layout="centered")

# 2. 전체 배경
st.markdown("""
<style>
    .stApp { background-color: #FDFBF0; }
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
</style>
""", unsafe_allow_html=True)

# 3. 제목
st.markdown("<h2 style='text-align: center;'>🔥 실시간 거래대금 주도주 🔥</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>3,000억 이상 & 4% 이상 상승 (3분 자동 갱신)</p>", unsafe_allow_html=True)
st.divider()

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQygCBp6noqOTPG2tKVFDrB_PrZsRoDSHQQt9bwF8ZRi-pwiBzVrpKClIPLBBOFCnNWJwHabzkrUzgF/pub?gid=0&single=true&output=csv"


def to_number(value, default=0):
    num = pd.to_numeric(value, errors="coerce")
    return default if pd.isna(num) else num


def clean_stock_code(value):
    if pd.isna(value):
        return ""
    code = str(value).strip()
    if code.endswith(".0"):
        code = code[:-2]
    return code.zfill(6) if code.isdigit() else code


try:
    df = pd.read_csv(CSV_URL, dtype={"종목코드": str})

    if df.empty:
        st.info("📉 데이터 대기 중... 장 시작 후 종목이 포착되면 나타납니다.")
    else:
        if "거래대금" in df.columns:
            df["거래대금"] = pd.to_numeric(df["거래대금"], errors="coerce").fillna(0)
            df = df.sort_values(by="거래대금", ascending=False)

        card_list = []

        for _, row in df.iterrows():
            name = html.escape(str(row.get("종목명", "종목미상")))
            code = html.escape(clean_stock_code(row.get("종목코드", "")))
            sector = html.escape(str(row.get("섹터명", "섹터미상")))
            price = to_number(row.get("현재가격", 0))
            volume = to_number(row.get("거래대금", 0))
            market_cap = to_number(row.get("시가총액", 0))

            rate_val = str(row.get("등락률", "0")).replace("%", "")
            rate = to_number(rate_val)

            color = "#ff4d4d" if rate > 0 else "#64b5f6" if rate < 0 else "#ffffff"
            bg_color = (
                "rgba(255, 77, 77, 0.15)" if rate > 0
                else "rgba(100, 181, 246, 0.15)" if rate < 0
                else "rgba(255,255,255,0.1)"
            )
            sign = "+" if rate > 0 else ""

            code_display = (
                f'<span style="font-size:12px; color:#B0BEC5; font-weight:600;">({code})</span>'
                if code else ""
            )

            card_html = f"""
<div style="display:flex; justify-content:space-between; align-items:center; padding:12px 14px; border-radius:12px; background-color:#15202B; border:1px solid #2A3644; box-shadow:0px 4px 6px rgba(0,0,0,0.2);">
    <div style="flex:1.65; min-width:0;">
        <div style="font-size:15px; font-weight:800; color:#ffffff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
            {name} {code_display}
        </div>
        <div style="display:flex; align-items:center; gap:8px; margin-top:4px; font-size:11px; white-space:nowrap; overflow:hidden;">
            <div style="color:#FF9800; font-weight:700; flex-shrink:0;">시총 {market_cap:,.0f}억</div>
            <div style="color:#00E676; overflow:hidden; text-overflow:ellipsis;">{sector}</div>
        </div>
    </div>

    <div style="flex:1.55; display:flex; justify-content:flex-end; align-items:center; gap:14px; margin-left:12px; padding-right:4px;">
        <div style="display:flex; flex-direction:column; align-items:flex-end; justify-content:center;">
            <div style="font-size:11px; color:#ff4d4d; font-weight:600; line-height:1; margin-bottom:4px;">현재가</div>
            <div style="display:flex; align-items:center; justify-content:flex-end; gap:6px;">
                <div style="font-size:15px; font-weight:700; color:#ff4d4d; white-space:nowrap; line-height:1;">{price:,.0f}</div>
                <div style="color:{color}; background-color:{bg_color}; padding:2px 7px; border-radius:6px; font-size:11px; font-weight:bold; white-space:nowrap; line-height:1.1;">
                    {sign}{rate:.2f}%
                </div>
            </div>
        </div>

        <div style="text-align:right; min-width:78px;">
            <div style="font-size:11px; color:#FFFF00; font-weight:600; margin-bottom:2px;">거래대금</div>
            <div style="font-size:13px; color:#FFFF00; font-weight:700; white-space:nowrap;">{volume:,.0f}억</div>
        </div>
    </div>
</div>
"""
            card_list.append(card_html)

        final_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body style="margin:0; padding:0; background:transparent;">
    <div style="display:flex; flex-direction:column; gap:10px;">
        {''.join(card_list)}
    </div>
</body>
</html>
"""

        components.html(
            final_html,
            height=max(120, len(df) * 92 + 20),
            scrolling=False
        )

    time.sleep(180)
    st.rerun()

except Exception as e:
    st.error(f"⚠️ 앱 실행 오류: {e}")