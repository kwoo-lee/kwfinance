import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 서비스 계정 키 경로
cred = credentials.Certificate("firebase-key.json")

firebase_admin.initialize_app(cred)

# Firestore 클라이언트 생성
db = firestore.client()

# 

exp = [
"Stock"
,"House"
,"Food"
,"Transport"
,"Taxi"
,"Shopping"
,"Coffee"
,"EatOut"
,"Travel"
,"ETC"
,"Lesson"
,"Alcohol"
,"Household"
,"Phone"]

payment = ["Cash", "DBS", "Citi"]

print("hh")
for i in exp:
    db.collection("category").add({
        "type" : "expense",
        "value" : i
    })


for i in payment:
    db.collection("category").add({
        "type" : "payment",
        "value" : i
    })
