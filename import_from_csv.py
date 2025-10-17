#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Django Data Import from CSV Script
Author: Raymond
Purpose: Import data from CSV files into the database after clearing old data.
"""

import os
import csv
from django.conf import settings
from django.core.wsgi import get_wsgi_application

# 設定DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # 替換為你的專案名稱
application = get_wsgi_application()

from data_import.models import Person, Category, Transaction

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
    with open('exported_categories.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 使用 name 作為唯一標識符，避免重複
            obj, created = Category.objects.get_or_create(
                name=row['Name'],
                defaults={'description': row['Description']}
            )
            category_map[row['Name']] = obj # 建立映射

    # 匯入Person (根據唯一字段 email)
    person_map = {} # 用於建立 email -> 對象 的映射
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

    # 匯入Transaction (根據 person_email 和 category_name 關聯)
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

    print("✅ 新數據已成功從 CSV 文件匯入到數據庫。")

if __name__ == "__main__":
    print("開始執行數據匯入腳本 (包含清理舊數據)...")
    import_from_csv()
    print("數據匯入完畢。")