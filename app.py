import firebase_admin
import os, sys, json
from firebase_admin import credentials, firestore
import streamlit as st
import accountbook
import pyrebase

def init_firebase():
    try:
        # --- Firestore 연결 (앱 최초 실행 시만 초기화) ---
        if os.path.exists(".streamlit/secrets.toml"):
            firebase_config = dict(st.secrets["firebase"])
            cred = credentials.Certificate(firebase_config)
        else:
            # Streamlit Cloud의 Secrets 사용
            if "firebase" in st.secrets:
                firebase_config = dict(st.secrets["firebase"])

                # 🔥 private_key 줄바꿈 문제 해결
                if "\\n" in firebase_config["private_key"]:
                    firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")

                cred = credentials.Certificate(firebase_config)
            else:
                print("cannot find secrets")
                sys.stdout.flush()
                # Render/Railway 환경변수 사용 (환경변수에 JSON 문자열 넣어둠)
                firebase_config = json.loads(os.environ["FIREBASE_KEY"])
                cred = credentials.Certificate(firebase_config)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    except Exception as e:
        # 화면에 에러 메시지 출력 후 앱 중단
        st.markdown(
            "<h2 style='text-align: center; color: red;'>Connection이 안되었습니다.</h2>",
            unsafe_allow_html=True
        )
        print(e)
        sys.stdout.flush()
        st.stop()  # 앱 실행 중단
        return 0

def init_auth():
    # ===== 로그인 상태 저장 =====
    if "user" not in st.session_state:
        st.session_state.user = None

    # ===== Firebase Auth 초기화 =====
    auth_config = st.secrets["firebase_auth"]
    firebase = pyrebase.initialize_app(auth_config)
    auth = firebase.auth()
    return auth

# Firebase초기화 시도
db = init_firebase()
auth = init_auth()

# 로그인 후만 접근 가능한 영역
if st.session_state.user:

    # --- 세션 상태 초기화 ---
    accountbook.init_accountbook_sessions(db)

    # --- 사이드바---
    accountbook.render_sidebar(db)

    # --- 메인영역 ---
    st.set_page_config(layout="wide")

    if st.session_state.selected_page is None:
        st.info("페이지를 선택하세요.")
    else:
        page_name = st.session_state.selected_page
        st.title(f"📒 가계부 - {page_name} ")
        c1, c2, c3 = st.columns([3, 3, 8]) 
        with c1:
            if st.button("입출금 기록", type="secondary", width='stretch', key="inout_button"):
                st.session_state.selected_page_type = "InOut"
                st.rerun()
        with c2:
            if st.button("요약", type="secondary", width='stretch', key="summary_button"):
                st.session_state.selected_page_type = "Summary"
                st.rerun()

        page_type = st.session_state.selected_page_type
        if page_type == "InOut":
            # 지출/수입 표
            left_col, right_col = st.columns(2)

            with left_col:
                st.markdown("#### 💸 지출")
                accountbook.render_expense_page(db, page_name)

            with right_col:
                st.markdown("#### 💰 수입")
                accountbook.render_income_page(db, page_name)
        elif page_type == "Summary":
            accountbook.render_summary_page(db, page_name)
else:
    st.title(f"📒 관우 가계부 ")
    email = st.text_input("이메일")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.user = user
            st.success(f"환영합니다 {email} 님!")
            st.rerun()
        except Exception as e:
            st.error(f"로그인 실패: {e}")
