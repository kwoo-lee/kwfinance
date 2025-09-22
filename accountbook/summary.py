import streamlit as st
from google.cloud.firestore import FieldFilter
import pandas as pd
import datetime, calendar
import myutil

def render_summary_page(db, page_name):
    # 수입 데이터 가져오기
    docs = db.collection("income_data").where(
        filter=FieldFilter("page_name", "==", page_name)
    ).stream()
    income_df = myutil.doc_to_df(docs)

    # 지출 데이터 가져오기
    docs = db.collection("expense_data").where(
        filter=FieldFilter("page_name", "==", page_name)
    ).stream()
    expense_df = myutil.doc_to_df(docs)

    # 지출/수입 표
    left_col, right_col = st.columns([1, 2])

    with left_col:
        render_income_expense_total_summary(income_df, expense_df)

    with right_col:
        render_expense_calendar(expense_df)

def render_expense_calendar(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Day"] = df["Date"].dt.strftime("%Y-%m-%d")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    # ───────────────────────────────
    # ② 월 선택 UI
    # ───────────────────────────────
    months = sorted(df["Date"].dt.strftime("%Y-%m").unique())
    selected_month = st.selectbox("📅 볼 달을 선택하세요", months)

    year, month = map(int, selected_month.split("-"))

    # ───────────────────────────────
    # ③ 선택 월 데이터 요약
    # ───────────────────────────────
    month_df = df[(df["Year"] == year) & (df["Month"] == month)]

    # 날짜별 총합
    sum_df = month_df.groupby("Day")["Amount"].sum().reset_index(name="총 지출")

    # 날짜별 가장 큰 지출
    idx = month_df.groupby("Day")["Amount"].idxmax()
    max_detail_df = month_df.loc[idx, ["Day", "Detail"]].rename(columns={"Detail": "가장 큰 지출"})

    # 병합
    day_info = pd.merge(sum_df, max_detail_df, on="Day")

    # dict 형태로 빠르게 접근
    info_map = {
        row["Day"]: f"{pd.to_datetime(row['Day']).strftime('%m.%d')}<br>{row['가장 큰 지출']}<br>{row['총 지출']:.0f}"
        for _, row in day_info.iterrows()
    }

    # ───────────────────────────────
    # ④ 달력 그리기
    # ───────────────────────────────
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)  # 주 단위 리스트

    st.subheader(f"📆 {year}년 {month}월")

    # 요일 헤더
    cols = st.columns(7)
    for i, day in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
        cols[i].markdown(f"**{day}**", unsafe_allow_html=True)

    # 날짜 출력
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].markdown(" ", unsafe_allow_html=True)
            else:
                d_str = f"{year}-{month:02d}-{day:02d}"
                if d_str in info_map:
                    content = info_map[d_str]  # 날짜/상세/금액
                else:
                    # 🔹 지출 없는 날: 날짜 + "-"
                    content = f"{month:02d}.{day:02d}<br>-"

                cols[i].markdown(
                    f"""
                    <div style='
                        border:1px solid #ddd;
                        border-radius:8px;
                        padding:6px;
                        min-height:100px;
                        text-align:center;
                        display:flex;
                        flex-direction:column;
                        justify-content:center;
                    '>{content}</div>
                    """,
                    unsafe_allow_html=True
                )

def render_income_expense_total_summary(income_df, expense_df):
    st.markdown("##### 💸💰 총 입출")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.write(" - ")
            st.write("**Income**")
            st.write("**Expense**")
        with c2:
            st.write("**Total**")
            total_income = income_df["Amount"].sum()
            total_expense = expense_df["Amount"].sum()
            st.write(f"${total_income:.2f}")
            st.write(f"${total_expense:.2f}")
    
    st.divider()

    st.markdown("##### 💸 유형 별 지출")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Category**")
        with c2:
            st.write("**Total**")

        categories = st.session_state.expense_type
        for cat in categories:
            filtered_df = expense_df[expense_df["Category"] == cat]
            with c1:
                st.write(cat)
            with c2:
                sum_amount = filtered_df["Amount"].sum()
                st.write(f"${sum_amount:.2f}")


