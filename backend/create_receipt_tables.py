"""
创建收货记录表
"""
from app import create_app
from models import db, PurchaseReceipt, PurchaseReceiptItem

app = create_app()

with app.app_context():
    # 创建表（如果不存在）
    db.create_all()
    print("收货记录表创建成功！")