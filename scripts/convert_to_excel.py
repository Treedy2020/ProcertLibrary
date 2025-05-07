import pandas as pd
import jsonlines

with jsonlines.open("data/procert_format.jsonl", 'r') as f:
    data = [l for l in f]

df = pd.DataFrame(data)
df.to_excel("data/procert_format.xlsx", index=False)
