import sqlite3
import csv

from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
db_path = '/opt/1panel/apps/gotify/gotify/data/gotify.db'
output_csv = project_root / "data" / "Wechat_payments.csv"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, message FROM messages
    WHERE message LIKE '%微信支付: 已支付%';
""")
rows = cursor.fetchall()

# 原始 CSV（id,message）
with open(output_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'message'])
    writer.writerows(rows)
print(f"提取完成，共 {len(rows)} 条记录，已保存至 {output_csv}")