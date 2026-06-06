"""
后端服务验证脚本
检查所有依赖和数据库连接
"""
import sys
import os


def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("✗ Python 版本过低，需要 Python 3.6+")
        return False
    return True


def check_dependencies():
    """检查依赖包"""
    required = ['flask', 'flask_cors', 'flask_sqlalchemy', 'werkzeug']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (未安装)")
            missing.append(package)
    
    if missing:
        print(f"\n请先安装缺失的依赖: pip install -r requirements.txt")
        return False
    return True


def check_database():
    """检查数据库"""
    try:
        from app import app
        from models import db
        
        with app.app_context():
            # 尝试查询用户表
            from models import User
            count = User.query.count()
            print(f"✓ 数据库连接成功 (用户数: {count})")
            
            # 验证默认用户
            users = User.query.all()
            print("\n默认用户:")
            for user in users:
                print(f"  - {user.username} ({user.role})")
            
            return True
    except Exception as e:
        print(f"✗ 数据库错误: {e}")
        print("\n请先初始化数据库: python init_db.py")
        return False


def main():
    print("="*50)
    print("后端服务验证")
    print("="*50)
    
    checks = [
        ("Python 版本", check_python_version),
        ("依赖包", check_dependencies),
        ("数据库连接", check_database)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n检查 {name}...")
        results.append(check_func())
    
    print("\n" + "="*50)
    if all(results):
        print("✓ 所有检查通过！后端服务已准备就绪。")
        print("\n启动服务: python app.py")
    else:
        print("✗ 部分检查未通过，请修复上述问题。")
    print("="*50)


if __name__ == '__main__':
    main()
