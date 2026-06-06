"""
创建补货建议表
"""
from app import create_app
from models import db, ReplenishmentAdvice

app = create_app()

with app.app_context():
    # 创建表（如果不存在）
    db.create_all()
    print("补货建议表创建成功！")