import pandas as pd

def doc_to_df(docs):
    data = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        data.append(d)

    # DataFrame으로 변환
    df = pd.DataFrame(data)
    return df