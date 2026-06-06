"""
迁移补货建议表（删除旧表并重新创建）
"""
from app import create_app
from models import db, ReplenishmentAdvice

app = create_app()

with app.app_context():
    # 删除旧表
    ReplenishmentAdvice.__table__.drop(db.engine)
    print("旧表已删除")
    
    # 创建新表
    db.create_all()
    print("新表创建成功！")