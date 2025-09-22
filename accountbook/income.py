import streamlit as st
from google.cloud.firestore import FieldFilter
import pandas as pd
import datetime

@st.dialog("새 수입 추가")
def add_income_dialog(db):
    today = datetime.date.today()
    date = st.date_input("일자", key="new_income_date_name", value=today)
    detail = st.text_input("상세", key="new_income_detail_name")
    amount = st.number_input("금액", min_value=0)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("저장", type="primary", width='stretch', key="save_new_button"):
            date_as_datetime = datetime.datetime.combine(date, datetime.datetime.min.time())
            db.collection("income_data").add({
                "page_name" : st.session_state.selected_page,
                "Date" : date_as_datetime,
                "Detail" : detail,
                "Amount" : amount
            })

            st.rerun()  # 즉시 목록에 반영
    with c2:
        if st.button("취소", width='stretch', key="cancel_new_button"):
            st.rerun()


def render_income_page(db, page_name):
    if st.button("➕ 추가", type="secondary", width='content', key="add_income_button"):
        add_income_dialog(db)  # 모달 열기

    # DB에서 값 가져오기
    docs = db.collection("income_data").where(
        filter=FieldFilter("page_name", "==", page_name)
    ).stream()

    # list로 변경
    data = []
    for doc in docs:
        dict = doc.to_dict()
        dict["ID"] = doc.id  
        data.append(dict)

    if data:
        # 원하는 필드 순서 지정
        desired_order = ["ID", "Date",  "Detail", "Amount"]

        # pandas DataFrame으로 변환 + 열 순서 지정
        df = pd.DataFrame(data)[desired_order]

        # Date 컬럼을 datetime으로 확실히 변환 (안전)
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

        # 날짜 순으로 내림차순 정렬 (최신 정보 위로 올라오게)
        df = df[desired_order].sort_values("Date", ascending=False)

        # Header
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
        with c1:
            st.write("Date")
        with c2:
            st.write("Detail")
        with c3:
            st.write("Amount")
        with c4:
            st.write("Delete")

        # 표로 출력
        for i, row in df.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                with c1:
                    st.write(row["Date"])
                with c2:
                    st.write(row["Detail"])
                with c3:
                    st.write(row["Amount"])
                with c4:
                    if st.button("🗑️", key=f"delete_income_{i}"):
                        db.collection("income_data").document(row["ID"]).delete()
                        st.toast(f"'{row['Detail']}' 삭제", icon="✅")
                        st.rerun()

        # st.dataframe(df, width='stretch')
    else:
        st.warning("데이터가 없습니다.")