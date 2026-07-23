"""文章 API 测试"""
from io import BytesIO


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

    def test_post_detail_page_renders(self, client, sample_post):
        """网页文章详情页可正常渲染"""
        resp = client.get(f'/post/{sample_post}')
        assert resp.status_code == 200
        assert b'post-detail' in resp.data

    def test_post_detail_sanitizes_markdown_html(self, client, auth_headers):
        """Markdown 渲染会清理危险 HTML"""
        resp = client.post('/api/posts', json={
            'title': 'XSS 测试',
            'content': '**安全内容** <script>alert(1)</script>'
        }, headers=auth_headers)
        post_id = resp.get_json()['post']['id']

        detail = client.get(f'/post/{post_id}')
        body = detail.data.decode('utf-8')
        assert detail.status_code == 200
        assert '<strong>安全内容</strong>' in body
        assert '<script>alert(1)</script>' not in body
        assert 'alert(1)' in body

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

    def test_posts_per_page_is_capped(self, client):
        """文章列表分页大小有上限"""
        resp = client.get('/api/posts?per_page=999')
        assert resp.status_code == 200
        assert len(resp.get_json()['posts']) <= 50

    def test_upload_rejects_svg(self, client, auth_headers):
        """上传接口拒绝 SVG 文件"""
        resp = client.post('/api/upload', data={
            'file': (BytesIO(b'<svg></svg>'), 'bad.svg')
        }, headers=auth_headers, content_type='multipart/form-data')
        assert resp.status_code == 400

    def test_publish_requires_csrf_token(self, client, auth_headers):
        """网页发文表单需要 CSRF token"""
        resp = client.post('/publish', data={
            'title': '无 CSRF',
            'content': '应被拦截'
        }, follow_redirects=False)
        assert resp.status_code == 302

    def test_draft_post_is_not_public(self, client, auth_headers):
        """草稿不会出现在公开列表和公开详情里"""
        resp = client.post('/api/posts', json={
            'title': '草稿文章',
            'content': '暂时不公开',
            'status': 'draft'
        }, headers=auth_headers)
        post_id = resp.get_json()['post']['id']

        listing = client.get('/api/posts')
        titles = [item['title'] for item in listing.get_json()['posts']]
        assert '草稿文章' not in titles

        public_client = client.application.test_client()
        detail = public_client.get(f'/api/posts/{post_id}')
        assert detail.status_code == 404

    def test_tag_filtering(self, client, auth_headers):
        """文章支持标签并可按标签筛选"""
        resp = client.post('/api/posts', json={
            'title': 'Flask 标签文章',
            'content': 'tagged',
            'tags': 'flask, python'
        }, headers=auth_headers)
        assert resp.status_code == 201

        filtered = client.get('/api/posts?tag=flask')
        titles = [item['title'] for item in filtered.get_json()['posts']]
        assert 'Flask 标签文章' in titles

    def test_rss_feed(self, client, sample_post):
        """RSS feed 可访问"""
        resp = client.get('/rss.xml')
        assert resp.status_code == 200
        assert resp.mimetype == 'application/rss+xml'
        assert b'<rss' in resp.data
