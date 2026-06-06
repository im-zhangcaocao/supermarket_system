"""
快速启动脚本
一键启动后端服务
"""
import os
import sys
import subprocess


def print_banner():
    """打印横幅"""
    print("="*60)
    print("  家电超市管理系统 - 后端服务")
    print("="*60)
    print()


def check_python():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("✗ Python 版本过低，需要 Python 3.6+")
        return False
    return True


def check_dependencies():
    """检查依赖"""
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
        print(f"\n请先安装依赖: pip install -r requirements.txt")
        return False
    return True


def check_database():
    """检查数据库"""
    db_file = 'database.db'
    if not os.path.exists(db_file):
        print(f"✗ 数据库文件不存在: {db_file}")
        print("正在初始化数据库...")
        try:
            subprocess.run([sys.executable, 'init_db.py'], check=True)
            print("✓ 数据库初始化完成")
            return True
        except subprocess.CalledProcessError:
            print("✗ 数据库初始化失败")
            return False
    else:
        print(f"✓ 数据库文件存在: {db_file}")
        return True


def main():
    """主函数"""
    print_banner()
    
    # 检查 Python 版本
    if not check_python():
        sys.exit(1)
    
    print()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    print()
    
    # 检查数据库
    if not check_database():
        sys.exit(1)
    
    print()
    print("="*60)
    print("✓ 所有检查通过，正在启动服务...")
    print("="*60)
    print()
    print("后端服务地址: http://127.0.0.1:5000")
    print()
    print("可用 API:")
    print("  - 产品管理:   /api/products")
    print("  - 库存管理:   /api/stock")
    print("  - 供应商管理: /api/suppliers")
    print()
    print("按 Ctrl+C 停止服务")
    print("="*60)
    print()
    
    # 启动 Flask 服务
    try:
        from app import app
        app.run(debug=False, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"\n✗ 启动失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
