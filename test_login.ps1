# 测试脚本
cd backend
python -c "
from app import app
app.app_context().push()
from models import User

# 检查用户数据
users = User.query.all()
print(f'用户数量: {len(users)}')

# 查找 admin 用户
admin = User.query.filter_by(username='admin').first()
if admin:
    print(f'admin 用户存在: {admin.username}, 密码: {admin.password}, 角色: {admin.role}')
else:
    print('admin 用户不存在')
"
