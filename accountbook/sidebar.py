import streamlit as st

# 모달 다이얼로그: 새 버튼 추가
@st.dialog("새 페이지 추가")
def add_page_dialog(db):
    st.write("추가할 페이지의 이름을 입력하세요.")
    new_name = st.text_input("페이지 이름", key="new_page_name", placeholder="예) 202509")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("저장", type="primary", width='stretch', key="save_new_button"):
            name = (new_name or "").strip()
            if not name:
                st.error("이름을 입력해주세요.")
                st.stop()
            if name in st.session_state["pages"]:
                st.warning("같은 이름의 버튼이 이미 있습니다.")
                st.stop()

            db.collection("pages").add({
                "user_name" : "admin",
                "page_name" : name
            })

            st.session_state.pages.append(name)
            st.rerun()  # 즉시 목록에 반영
    with c2:
        if st.button("취소", width='stretch', key="cancel_new_button"):
            st.rerun()
            
def render_sidebar(db):
    with st.sidebar:
        st.title("📒 가계부 프로그램")
        
        # 페이지 추가 버튼
        if st.button("➕ 가계부 추가", type="secondary", width='stretch', key="add_page_button"):
            add_page_dialog(db)  # 외부에서 전달된 함수 실행

        st.divider()
        st.subheader("🧾 가계부 목록")

        if len(st.session_state.get("pages", [])) == 0:
            st.caption("아직 생성된 버튼이 없습니다. '➕ 추가'를 눌러 만들어보세요.")
        else:
            # 생성된 버튼들을 사이드바에 그리기
            for idx, name in enumerate(st.session_state["pages"]):
                if st.button(name, width='stretch', key=f"dyn_btn_{idx}"):
                    st.toast(f"'{name}' 버튼을 눌렀습니다!", icon="✅")
                    st.session_state.selected_page = name