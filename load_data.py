import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import FieldFilter
import datetime

# Firebase 서비스 계정 키 경로
cred = credentials.Certificate("firebase-key.json")

firebase_admin.initialize_app(cred)

# Firestore 클라이언트 생성
db = firestore.client()

def load_expense_csv(page_name):
    df = pd.read_csv(f"~/Downloads/가계부/{page_name}_expense.csv")
    df["page_name"] = page_name

    for idx, row in df.iterrows():
        date_str = row["Date"]
        date = datetime.datetime.strptime(date_str, "%Y. %m. %d")
        category = row["Category"]
        detail = row["Detail"]
        amount = row["Amount"]
        amount = float(amount.replace(",", "").replace("$", ""))
        payment = row["Card"] if "Card" in row else ""
        
        db.collection("expense_data").add({
            "page_name" : page_name,
            "Date" : date,
            "Category" : category,
            "Detail" : detail,
            "Amount" : amount,
            "Payment" : payment
        })
    print(f"'{page_name}' 페이지를 지출 데이터 로드를 완료했습니다.")

def load_income_csv(page_name):
    df = pd.read_csv(f"~/Downloads/가계부/{page_name}_income.csv")
    df["page_name"] = page_name

    for idx, row in df.iterrows():
        date_str = row["Date"]
        date = datetime.datetime.strptime(date_str, "%Y. %m. %d")
        detail = row["Category"]
        amount = row["Amount"]
        amount = float(amount.replace(",", "").replace("$", ""))
        
        db.collection("income_data").add({
            "page_name" : page_name,
            "Date" : date,
            "Detail" : detail,
            "Amount" : amount,
        })
    print(f"'{page_name}' 페이지를 수입 데이터 로드를 완료했습니다.")
    
def load_data(page_name):
    # 1. pages 컬렉션에서 같은 이름 존재 여부 확인
    docs = db.collection("pages").where(
        filter=FieldFilter("page_name", "==", page_name)
        ).stream()
    docs_list = list(docs)

    if len(docs_list) > 0:
        print(f"'{page_name}' 페이지는 이미 존재합니다.")
    else:
        tnow = datetime.datetime.now()

        # 2. 없으면 새 문서 추가
        db.collection("pages").add({
            "page_name" : page_name,
            "user_name" : "admin",
            "date": tnow
        })
        
        print(f"'{page_name}' 페이지를 새로 추가했습니다.")

        # Expense Data Load
        load_expense_csv(page_name)

        # Income Data Load
        load_income_csv(page_name)

pages = ['202501', '202502', '202503', '202504', '202505', '202506', '202507', '202508', '202509']
for page in pages:
    load_data(page)

