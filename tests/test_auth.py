"""认证 API 测试"""


class TestAuth:
    """用户注册与登录测试"""

    def test_register_success(self, client):
        """注册成功"""
        resp = client.post('/api/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': '123456'
        })
        data = resp.get_json()
        assert resp.status_code == 201
        assert data['success'] is True
        assert data['user']['username'] == 'newuser'

    def test_register_missing_fields(self, client):
        """注册缺少必填字段"""
        resp = client.post('/api/register', json={
            'username': 'newuser'
        })
        assert resp.status_code == 400
        assert resp.get_json()['success'] is False

    def test_register_short_password(self, client):
        """注册密码太短"""
        resp = client.post('/api/register', json={
            'username': 'newuser2',
            'email': 'new2@example.com',
            'password': '123'
        })
        assert resp.status_code == 400

    def test_register_duplicate_username(self, client):
        """重复用户名注册"""
        client.post('/api/register', json={
            'username': 'dupuser',
            'email': 'dup1@example.com',
            'password': '123456'
        })
        resp = client.post('/api/register', json={
            'username': 'dupuser',
            'email': 'dup2@example.com',
            'password': '123456'
        })
        assert resp.status_code == 400
        assert '已存在' in resp.get_json()['message']

    def test_login_success(self, client):
        """登录成功"""
        client.post('/api/register', json={
            'username': 'loginuser',
            'email': 'login@example.com',
            'password': '123456'
        })
        resp = client.post('/api/login', json={
            'username': 'loginuser',
            'password': '123456'
        })
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
        assert 'token' in data
        assert data['user']['username'] == 'loginuser'

    def test_login_wrong_password(self, client):
        """密码错误"""
        client.post('/api/register', json={
            'username': 'wrongpw',
            'email': 'wrong@example.com',
            'password': '123456'
        })
        resp = client.post('/api/login', json={
            'username': 'wrongpw',
            'password': 'wrongpassword'
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        """登录不存在的用户"""
        resp = client.post('/api/login', json={
            'username': 'nonexistent',
            'password': '123456'
        })
        assert resp.status_code == 401

    def test_password_reset_flow(self, client, db):
        """找回密码可以生成 token 并重置密码"""
        from models import User

        client.post('/api/register', json={
            'username': 'resetuser',
            'email': 'reset@example.com',
            'password': '123456'
        })
        with client.session_transaction() as sess:
            sess['_csrf_token'] = 'test-csrf'

        resp = client.post('/forgot-password', data={
            '_csrf_token': 'test-csrf',
            'email': 'reset@example.com'
        })
        assert resp.status_code == 200

        user = User.query.filter_by(email='reset@example.com').first()
        token = user.reset_token
        assert token

        resp = client.post(f'/reset-password/{token}', data={
            '_csrf_token': 'test-csrf',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        }, follow_redirects=False)
        assert resp.status_code == 302

        login = client.post('/api/login', json={
            'username': 'resetuser',
            'password': 'newpass123'
        })
        assert login.status_code == 200
