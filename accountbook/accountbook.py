import streamlit as st
from firebase_admin import firestore

def init_accountbook_sessions(db):
    if "pages" not in st.session_state:
        st.session_state.pages = []
        docs = db.collection("pages") \
                .order_by("date", direction = firestore.Query.DESCENDING) \
                .stream()
        
        for doc in docs:
            data = doc.to_dict()
            st.session_state.pages.append(data["page_name"])
    
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = None

    if "selected_page_type" not in st.session_state:
        st.session_state.selected_page_type = None

    if "expense_type" not in st.session_state:
        docs = db.collection("category").where("type", "==", "expense").stream()
        st.session_state.expense_type = [doc.to_dict().get("value") for doc in docs]

    if "payment_type" not in st.session_state:
        docs = db.collection("category").where("type", "==", "payment").stream()
        st.session_state.payment_type = [doc.to_dict().get("value") for doc in docs]