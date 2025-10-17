#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Django Sample Data Generator Script
Author: Raymond
Purpose: Generate and import sample data into the database.
"""

import os
import random
from datetime import timedelta
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.utils import timezone

# 設定DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # 替換為你的專案名稱
application = get_wsgi_application()

from data_import.models import Person, Category, Transaction

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
        # 使用 get_or_create 確保唯一性，但我們在清空後執行，所以不會重複
        obj = Category(name=cat, description=f"Category: {cat}")
        category_objs.append(obj)
    Category.objects.bulk_create(category_objs)

    # 創建人員 (不指定ID)
    person_objs = []
    for i in range(20):  # 20個人
        first = random.choice(first_names)
        last = random.choice(last_names)
        email = f"{first.lower()}.{last.lower()}.{random.randint(1,100)}@erb7.com" # 避免重複
        phone = f"+1-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
        # 創建對象，但不賦予ID
        obj = Person(first_name=first, last_name=last, email=email, phone=phone)
        person_objs.append(obj)
    Person.objects.bulk_create(person_objs)

    # 重新從數據庫獲取創建後的對象，以確保它們有正確的ID
    # 這是為了在創建 Transaction 時能引用正確的 person 和 category ID
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
        # 創建 Transaction 對象，引用已保存的 person 和 category 對象
        trans = Transaction(
            person=person, # 使用已保存的對象實例
            category=category, # 使用已保存的對象實例
            amount=amount,
            date=date,
            notes=notes
        )
        transactions.append(trans)

    Transaction.objects.bulk_create(transactions)

    print(f"✅ 成功生成並匯入 {len(person_objs)} 位人物, {len(category_objs)} 個分類, {len(transactions)} 筆交易。")

if __name__ == "__main__":
    print("開始執行樣本數據生成腳本...")
    generate_sample_data()
    print("樣本數據生成完畢。")