import json
with open("firebase-auth.json", "r") as f:
    data = json.load(f)

print("[firebase_auth]")
for k, v in data.items():
    if k == "private_key":
        # private_key는 TOML에서 멀티라인 문자열로 변환
        print(f'{k} = """{v}"""')
    else:
        print(f'{k} = "{v}"')
