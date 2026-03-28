import sqlite3
import csv
import re

from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
db_path = '/opt/1panel/apps/gotify/gotify/data/gotify.db'
output_csv = project_root / "data" / "parsed_payments.csv"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, message FROM messages
    WHERE message LIKE '%微信支付: 已支付%';
""")
rows = cursor.fetchall()

pattern_id = re.compile(r'\[(\d+)条\]')
pattern_amount = re.compile(r'¥([\d.]+)')

parsed_results = []
for db_id, msg in rows:
    match_id = pattern_id.search(msg)
    match_amount = pattern_amount.search(msg)
    custom_id = match_id.group(1) if match_id else None
    amount = float(match_amount.group(1)) if match_amount else None

    parsed_results.append({
        'db_id': db_id,
        'amount': amount
    })

with open(output_csv, 'w', newline='', encoding='utf-8') as f2:
    writer2 = csv.writer(f2)
    writer2.writerow(['db_id', 'amount'])
    for r in parsed_results:
        writer2.writerow([r['db_id'], r['amount']])

print("解析结果已保存至 output_csv（仅 db_id, amount）")
conn.close()