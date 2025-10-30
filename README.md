create postgres database
database name: lwp

```bash
git clone https://github.com/pc8521/erb7_hw.git
python manage.py makemigrations
python manage.py migrate
python django_data_management_tool.py
```
--- Django 數據管理工具 ---
1. 清理數據庫
2. 生成樣本數據
3. 匯出數據到 CSV
4. 從 CSV 匯入數據 (會先清空現有數據)
5. 離開
請選擇操作 (1-5): 
