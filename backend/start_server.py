import sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    from app import app
    print('App imported successfully')
    print('Starting Flask server...')
    app.run(host='127.0.0.1', port=5000, debug=False)
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
    input('Press Enter to exit...')
