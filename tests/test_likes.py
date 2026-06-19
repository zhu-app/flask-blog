"""点赞 API 测试"""


class TestLikes:
    """点赞功能测试"""

    def test_like_post(self, client, auth_headers, sample_post):
        """点赞文章"""
        resp = client.post(f'/api/posts/{sample_post}/like', headers=auth_headers)
        data = resp.get_json()
        assert data['success'] is True
        assert data['liked'] is True
        assert data['likes'] == 1

    def test_unlike_post(self, client, auth_headers, sample_post):
        """取消点赞"""
        # 先点赞
        client.post(f'/api/posts/{sample_post}/like', headers=auth_headers)
        # 再取消点赞
        resp = client.post(f'/api/posts/{sample_post}/like', headers=auth_headers)
        data = resp.get_json()
        assert data['liked'] is False
        assert data['likes'] == 0

    def test_like_without_auth(self, client, sample_post):
        """未登录点赞失败"""
        resp = client.post(f'/api/posts/{sample_post}/like')
        assert resp.status_code == 401

    def test_multiple_likes_count(self, client, auth_headers, admin_headers, sample_post):
        """多个用户点赞统计"""
        # 用户1点赞
        client.post(f'/api/posts/{sample_post}/like', headers=auth_headers)
        # 用户2点赞
        client.post(f'/api/posts/{sample_post}/like', headers=admin_headers)

        resp = client.get(f'/api/posts/{sample_post}')
        assert resp.get_json()['post']['likes'] == 2
