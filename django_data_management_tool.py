#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Django Data Management Tool
Author: Raymond
Purpose: A unified tool for cleaning, generating, exporting, and importing data.
"""

import os
import csv
import random
from datetime import timedelta
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.utils import timezone

# 設定DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # 替換為你的專案名稱
application = get_wsgi_application()

from data_import.models import Person, Category, Transaction

def clean_database():
    """清理數據庫中的所有數據"""
    print("正在清理數據庫...")
    # 重要：按正確順序刪除，先刪關聯表
    Transaction.objects.all().delete()
    Person.objects.all().delete()
    Category.objects.all().delete()
    print("✅ 數據庫已清理完畢。")

def generate_sample_data():
    """生成20+筆樣本數據並存入數據庫"""
    categories = [
        "Food", "Transport", "Entertainment", "Utilities", "Health",
        "Education", "Shopping", "Travel", "Gifts", "Savings",
        "Clothing", "Insurance", "Dining Out", "Groceries", "Car",
        "Pet", "Household", "Electronics", "Subscriptions", "Miscellaneous"
    ]

    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Iris", "Jack"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

    print("正在清理現有數據...")
    # 重要：按正確順序刪除，先刪關聯表
    Transaction.objects.all().delete()
    Person.objects.all().delete()
    Category.objects.all().delete()

    print("正在生成樣本數據...")

    # 創建分類 (不指定ID)
    category_objs = []
    for cat in categories:
        obj = Category(name=cat, description=f"Category: {cat}")
        category_objs.append(obj)
    Category.objects.bulk_create(category_objs)

    # 創建人員 (不指定ID)
    person_objs = []
    for i in range(20):  # 20個人
        first = random.choice(first_names)
        last = random.choice(last_names)
        email = f"{first.lower()}.{last.lower()}.{random.randint(1,100)}@erb7.com" # 避免重複
        phone = f"+852-{random.randint(1000,9999)} {random.randint(1000,9999)}"
        obj = Person(first_name=first, last_name=last, email=email, phone=phone)
        person_objs.append(obj)
    Person.objects.bulk_create(person_objs)

    # 重新從數據庫獲取創建後的對象，以確保它們有正確的ID
    person_objs = list(Person.objects.all())
    category_objs = list(Category.objects.all())

    # 創建交易記錄 (至少20筆，這裡設為25筆)
    transactions = []
    start_date = timezone.now().date() - timedelta(days=60)  # 近兩個月內
    for _ in range(25):  # 25筆交易，滿足至少20筆的要求
        person = random.choice(person_objs)
        category = random.choice(category_objs) if random.random() > 0.2 else None  # 20%無分類
        amount = round(random.uniform(10.0, 500.0), 2)
        days_ago = random.randint(0, 60)
        date = start_date + timedelta(days=days_ago)
        notes = f"Sample transaction for {person.first_name} on {date}"
        trans = Transaction(
            person=person,
            category=category,
            amount=amount,
            date=date,
            notes=notes
        )
        transactions.append(trans)

    Transaction.objects.bulk_create(transactions)

    print(f"✅ 成功生成並匯入 {len(person_objs)} 位人物, {len(category_objs)} 個分類, {len(transactions)} 筆交易。")

def export_to_csv():
    """從數據庫匯出數據到CSV文件"""
    print("正在匯出數據到CSV文件...")

    # 匯出Person (不包含ID)
    with open('exported_persons.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Phone'])
        for p in Person.objects.all():
            writer.writerow([p.first_name, p.last_name, p.email, p.phone])

    # 匯出Category (不包含ID)
    with open('exported_categories.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Description'])
        for c in Category.objects.all():
            writer.writerow([c.name, c.description])

    # 匯出Transaction (不包含ID，使用 Person 的 Email 和 Category 的 Name 進行關聯)
    with open('exported_transactions.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 修正：將 Person Name 改為 Person Email，這樣匯入時更容易查找
        writer.writerow(['Person Email', 'Person Full Name', 'Category Name', 'Amount', 'Date', 'Notes'])
        for t in Transaction.objects.all():
            person_email = t.person.email
            person_full_name = f"{t.person.first_name} {t.person.last_name}"
            category_name = t.category.name if t.category else ""
            writer.writerow([
                person_email, # 使用 Email 作為唯一標識符
                person_full_name, # 保留原名稱供參考
                category_name, # 使用 Name 作為唯一標識符
                t.amount,
                t.date,
                t.notes
            ])

    print("✅ 數據已成功匯出至 CSV 文件 (exported_persons.csv, exported_categories.csv, exported_transactions.csv)。")

def import_from_csv():
    """從CSV文件匯入數據到數據庫，先清理舊數據"""
    print("正在清理舊數據...")
    # 刪除現有數據 (注意順序)
    Transaction.objects.all().delete()
    Person.objects.all().delete()
    Category.objects.all().delete()
    print("✅ 舊數據已清理完畢。")

    print("正在從CSV文件匯入新數據...")

    # 匯入Category (根據唯一字段 name)
    category_map = {} # 用於建立 name -> 對象 的映射
    try:
        with open('exported_categories.csv', 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 使用 name 作為唯一標識符，避免重複
                obj, created = Category.objects.get_or_create(
                    name=row['Name'],
                    defaults={'description': row['Description']}
                )
                category_map[row['Name']] = obj # 建立映射
    except FileNotFoundError:
        print("錯誤: 找不到 exported_categories.csv 文件。")
        return
    except KeyError as e:
        print(f"錯誤: CSV 文件 exported_categories.csv 中缺少必要的欄位 {e}。")
        return

    # 匯入Person (根據唯一字段 email)
    person_map = {} # 用於建立 email -> 對象 的映射
    try:
        with open('exported_persons.csv', 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 使用 email 作為唯一標識符，避免重複
                obj, created = Person.objects.get_or_create(
                    email=row['Email'],
                    defaults={
                        'first_name': row['First Name'],
                        'last_name': row['Last Name'],
                        'phone': row['Phone']
                    }
                )
                person_map[row['Email']] = obj # 建立映射
    except FileNotFoundError:
        print("錯誤: 找不到 exported_persons.csv 文件。")
        return
    except KeyError as e:
        print(f"錯誤: CSV 文件 exported_persons.csv 中缺少必要的欄位 {e}。")
        return

    # 匯入Transaction (根據 person_email 和 category_name 關聯)
    try:
        with open('exported_transactions.csv', 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # 動態獲取標題
            fieldnames = reader.fieldnames
            print(f"CSV 標題: {fieldnames}") # 除錯：打印標題

            transactions_to_create = []
            for row in reader:
                try:
                    # 使用動態標題鍵
                    person_email = row['Person Email'] # 假設標題是 'Person Email'
                    person_obj = person_map.get(person_email)
                    if not person_obj:
                        print(f"警告: 找不到 Person Email {person_email}，跳過此筆交易。")
                        continue # 跳過這筆記錄

                    category_name = row['Category Name'] # 假設標題是 'Category Name'
                    category_obj = category_map.get(category_name)
                    if category_name and not category_obj:
                        print(f"警告: 找不到 Category Name {category_name}，跳過此筆交易。")
                        continue # 跳過這筆記錄

                    transactions_to_create.append(
                        Transaction(
                            # 不指定ID
                            person=person_obj, # 使用查找到的對象
                            category=category_obj, # 使用查找到的對象
                            amount=row['Amount'],
                            date=row['Date'],
                            notes=row['Notes']
                        )
                    )
                except KeyError as e: # 捕獲鍵不存在的錯誤
                    print(f"警告: CSV 標題中找不到鍵 {e}。當前行: {row}")
                    continue
                except Exception as e: # 捕獲可能的其他異常
                    print(f"警告: 處理交易記錄時發生其他錯誤: {e}, 當前行: {row}")
                    continue
            if transactions_to_create:
                Transaction.objects.bulk_create(transactions_to_create)
    except FileNotFoundError:
        print("錯誤: 找不到 exported_transactions.csv 文件。")
        return
    except KeyError as e:
        print(f"錯誤: CSV 文件 exported_transactions.csv 中缺少必要的欄位 {e}。")
        return

    print("✅ 新數據已成功從 CSV 文件匯入到數據庫。")

def main_menu():
    """顯示主選單並處理用戶選擇"""
    while True:
        print("\n--- Django 數據管理工具 ---")
        print("1. 清理數據庫")
        print("2. 生成樣本數據")
        print("3. 匯出數據到 CSV")
        print("4. 從 CSV 匯入數據 (會先清空現有數據)")
        print("5. 離開")
        choice = input("請選擇操作 (1-5): ").strip()

        if choice == '1':
            confirm = input("此操作將清空數據庫中所有數據，確定要繼續嗎？(y/N): ").strip().lower()
            if confirm == 'y':
                clean_database()
            else:
                print("操作已取消。")
        elif choice == '2':
            generate_sample_data()
        elif choice == '3':
            export_to_csv()
        elif choice == '4':
            confirm = input("此操作將清空現有數據，然後從CSV匯入，確定要繼續嗎？(y/N): ").strip().lower()
            if confirm == 'y':
                import_from_csv()
            else:
                print("操作已取消。")
        elif choice == '5':
            print("再見！")
            break
        else:
            print("無效的選擇，請輸入 1 到 5 之間的數字。")

if __name__ == "__main__":
    main_menu()