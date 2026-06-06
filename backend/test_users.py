import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import app
from models import db, User

app.app_context().push()

users = User.query.all()
if users:
    print(f'Found {len(users)} users')
    for u in users[:5]:
        print(f'  {u.username} - {u.role} - password length: {len(u.password)}')
else:
    print('No users found')
