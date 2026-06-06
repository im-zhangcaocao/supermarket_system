import sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    print('Importing app...')
    from app import app
    print('App imported successfully')
    
    print('Getting config...')
    print(f'Database URI: {app.config.get("SQLALCHEMY_DATABASE_URI")}')
    
    print('Creating app context...')
    with app.app_context():
        print('App context created')
        
        print('Importing models...')
        from models import db, User
        
        print('Querying users...')
        users = User.query.all()
        print(f'Found {len(users)} users')
        
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
