"""测试 fixtures"""
import pytest
from app import create_app
from config import Config
from models import db as _db


class TestConfig(Config):
    """测试用配置（SQLite 内存数据库）"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key-32-bytes-long-for-security!!'
    JWT_SECRET_KEY = 'test-jwt-secret-key-32-bytes-long-for-test'


@pytest.fixture(scope='session')
def app():
    """创建测试用 Flask 应用"""
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """测试客户端"""
    return app.test_client()


@pytest.fixture(scope='function')
def db(app):
    """数据库实例"""
    with app.app_context():
        yield _db
        _db.session.rollback()


@pytest.fixture(scope='function')
def auth_headers(client):
    """登录并返回 JWT 认证头"""
    from models import User
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(username='testuser', email='test@example.com')
            user.set_password('123456')
            _db.session.add(user)
            _db.session.commit()

    resp = client.post('/api/login', json={
        'username': 'testuser',
        'password': '123456'
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def admin_headers(client):
    """登录管理员账号并返回 JWT 认证头"""
    from models import User
    with client.application.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin', email='admin@example.com', role='admin'
            )
            admin.set_password('123456')
            _db.session.add(admin)
            _db.session.commit()

    resp = client.post('/api/login', json={
        'username': 'admin',
        'password': '123456'
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def sample_post(client, auth_headers):
    """创建一个示例文章并返回其 ID"""
    resp = client.post('/api/posts', json={
        'title': '测试文章',
        'content': '这是测试文章的内容'
    }, headers=auth_headers)
    data = resp.get_json()
    assert data['success'], f"创建文章失败: {data}"
    return data['post']['id']
