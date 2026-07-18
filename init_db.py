"""数据库初始化脚本 - 创建数据库和表"""
import pymysql
pymysql.install_as_MySQLdb()

from app import create_app
from models import db

app = create_app()

with app.app_context():
    # 数据库表由 create_app() 中的 db.create_all() 自动创建，此处仅初始化数据
    print("[OK] 数据库表创建成功！")

    # 检查是否有测试用户，如果没有则创建一个
    from models import User
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', email='admin@example.com', role='admin')
        admin_user.set_password('123456')
        db.session.add(admin_user)
        print("[OK] 已创建管理员账号: admin / 123456")
    elif admin_user.role != 'admin':
        admin_user.role = 'admin'
        db.session.add(admin_user)
        print("[OK] 已将 admin 账号升级为管理员")

    # 初始化默认分类
    from models import Category
    default_categories = ['技术', '生活', '学习', '分享', '其他']
    for cat_name in default_categories:
        if not Category.query.filter_by(name=cat_name).first():
            db.session.add(Category(name=cat_name))
            print(f"[OK] 已创建分类: {cat_name}")

    db.session.commit()
