#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Django Data Export to CSV Script
Author: Raymond
Purpose: Export data from the database to CSV files.
"""

import os
import csv
from django.conf import settings
from django.core.wsgi import get_wsgi_application

# 設定DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # 替換為你的專案名稱
application = get_wsgi_application()

from data_import.models import Person, Category, Transaction

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

if __name__ == "__main__":
    print("開始執行數據匯出腳本...")
    export_to_csv()
    print("數據匯出完畢。")