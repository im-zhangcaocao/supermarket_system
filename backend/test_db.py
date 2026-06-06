import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import app
from models import db, User

with app.app_context():
    users = User.query.all()
    print(f'=== Users in Database ===')
    print(f'Total users: {len(users)}')
    if users:
        for u in users[:5]:
            print(f'User: {u.username}, Role: {u.role}, Status: {u.status}')
    else:
        print('No users found!')
