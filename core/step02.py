import csv
import json
import os

from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
STATE_FILE = project_root / "data" / "balance_state.json"
CSV_FILE = project_root / "data" / "parsed_payments.csv"

def load_state():
    """
    加载状态文件，如果不存在则提示用户输入初始余额并初始化状态。
    返回：(last_id, balance)
    """
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        return state.get('last_id', 0), state.get('balance', 0.0)
    else:
        while True:
            try:
                initial_balance = float(input("请输入初始余额："))
                break
            except ValueError:
                print("输入无效，请重新输入数字。")
        return 0, initial_balance


def save_state(last_id, balance):
    """保存状态到JSON文件"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump({'last_id': last_id, 'balance': balance}, f, indent=2)


def read_payments_from_csv(csv_file):
    """
    读取CSV文件，返回列表，每个元素为 (db_id, amount)
    假设CSV有表头：db_id,amount
    """
    payments = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                db_id = int(row['db_id'])
                amount = float(row['amount'])
                payments.append((db_id, amount))
            except (KeyError, ValueError) as e:
                print(f"跳过无效行: {row}，错误: {e}")
    # 按db_id排序，确保处理顺序
    payments.sort(key=lambda x: x[0])
    return payments


def process_new_payments(payments, last_id):
    """
    过滤出 db_id > last_id 的记录，并累加金额。
    返回：(新记录的列表, 总金额, 本次处理的最大ID)
    """
    new_payments = [(db_id, amt) for db_id, amt in payments if db_id > last_id]
    if not new_payments:
        return [], 0.0, last_id
    total = sum(amt for _, amt in new_payments)
    max_id = max(db_id for db_id, _ in new_payments)
    return new_payments, total, max_id


def main():
    # 1. 加载状态
    last_id, current_balance = load_state()
    print(f"当前状态：last_id={last_id}, 余额={current_balance:.2f}")

    # 2. 读取CSV数据
    if not os.path.exists(CSV_FILE):
        print(f"错误：找不到文件 {CSV_FILE}，请先运行提取脚本生成此文件。")
        return
    payments = read_payments_from_csv(CSV_FILE)

    # 3. 过滤新记录
    new_payments, total_expense, new_last_id = process_new_payments(payments, last_id)

    if not new_payments:
        print("没有新的支付记录需要处理。")
        return

    # 4. 显示本次处理的记录
    print("\n本次处理的新记录：")
    for db_id, amt in new_payments:
        print(f"  ID: {db_id}, 金额: {amt:.2f}")

    # 5. 更新余额
    new_balance = current_balance - total_expense

    # 6. 保存新状态
    save_state(new_last_id, new_balance)

    # 7. 输出汇总
    print(f"\n本次总支出: {total_expense:.2f}")
    print(f"原余额: {current_balance:.2f}")
    print(f"新余额: {new_balance:.2f}")
    print(f"已处理到ID: {new_last_id}")

if __name__ == '__main__':
    main()