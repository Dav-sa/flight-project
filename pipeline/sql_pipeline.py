import json
import psycopg2
from psycopg2.extras import Json
import pandas as pd

with open("results/airfranceinfo.json", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data, index=[0])
df.to_csv("output.csv", index=False)

conn_string = "postgresql://postgres:JobiJobaùùùazê12!@db.ezcppwnavhquepnbdzap.supabase.co:5432/postgres"


conn = psycopg2.connect(conn_string)
cur = conn.cursor()

# Commit the transaction


cur.close()
conn.close()
