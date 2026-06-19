"""文章 API 测试"""


class TestPosts:
    """文章 CRUD 测试"""

    def test_create_post_success(self, client, auth_headers):
        """创建文章成功"""
        resp = client.post('/api/posts', json={
            'title': '我的第一篇文章',
            'content': '这是文章内容'
        }, headers=auth_headers)
        data = resp.get_json()
        assert resp.status_code == 201
        assert data['success'] is True
        assert data['post']['title'] == '我的第一篇文章'

    def test_create_post_without_auth(self, client):
        """未登录创建文章失败"""
        resp = client.post('/api/posts', json={
            'title': '测试',
            'content': '内容'
        })
        assert resp.status_code == 401

    def test_create_post_empty_title(self, client, auth_headers):
        """标题为空创建失败"""
        resp = client.post('/api/posts', json={
            'title': '',
            'content': '内容'
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_get_posts_list(self, client, auth_headers, sample_post):
        """获取文章列表"""
        resp = client.get('/api/posts')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
        assert len(data['posts']) >= 1
        assert data['total'] >= 1

    def test_get_posts_pagination(self, client, auth_headers):
        """文章列表分页"""
        # 创建 3 篇文章
        for i in range(3):
            client.post('/api/posts', json={
                'title': f'文章{i}',
                'content': f'内容{i}'
            }, headers=auth_headers)

        resp = client.get('/api/posts?page=1&per_page=2')
        data = resp.get_json()
        assert len(data['posts']) <= 2
        assert data['page'] == 1
        assert data['total'] >= 3

    def test_get_posts_search(self, client, auth_headers):
        """文章搜索"""
        client.post('/api/posts', json={
            'title': 'Python 入门教程',
            'content': '学习 Python 编程'
        }, headers=auth_headers)

        resp = client.get('/api/posts?keyword=Python')
        data = resp.get_json()
        assert data['total'] >= 1

    def test_get_post_detail(self, client, sample_post):
        """获取文章详情"""
        resp = client.get(f'/api/posts/{sample_post}')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['post']['id'] == sample_post
        assert data['post']['title'] == '测试文章'

    def test_get_post_not_found(self, client):
        """获取不存在的文章"""
        resp = client.get('/api/posts/99999')
        assert resp.status_code == 404

    def test_update_post(self, client, auth_headers, sample_post):
        """更新文章"""
        resp = client.put(f'/api/posts/{sample_post}', json={
            'title': '更新后的标题',
            'content': '更新后的内容'
        }, headers=auth_headers)
        data = resp.get_json()
        assert data['success'] is True
        assert data['post']['title'] == '更新后的标题'

    def test_delete_post(self, client, auth_headers, sample_post):
        """删除文章"""
        resp = client.delete(f'/api/posts/{sample_post}', headers=auth_headers)
        assert resp.get_json()['success'] is True

        # 确认已删除
        resp = client.get(f'/api/posts/{sample_post}')
        assert resp.status_code == 404
