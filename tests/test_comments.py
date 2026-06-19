"""评论 API 测试"""


class TestComments:
    """评论功能测试"""

    def test_create_comment(self, client, auth_headers, sample_post):
        """发表评论成功"""
        resp = client.post(f'/api/posts/{sample_post}/comments', json={
            'content': '这是一条测试评论'
        }, headers=auth_headers)
        data = resp.get_json()
        assert resp.status_code == 201
        assert data['success'] is True
        assert data['comment']['content'] == '这是一条测试评论'

    def test_create_comment_without_auth(self, client, sample_post):
        """未登录发表评论失败"""
        resp = client.post(f'/api/posts/{sample_post}/comments', json={
            'content': '评论内容'
        })
        assert resp.status_code == 401

    def test_create_comment_empty_content(self, client, auth_headers, sample_post):
        """空评论内容失败"""
        resp = client.post(f'/api/posts/{sample_post}/comments', json={
            'content': ''
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_get_comments(self, client, auth_headers, sample_post):
        """获取评论列表"""
        # 先创建一条评论
        client.post(f'/api/posts/{sample_post}/comments', json={
            'content': '测试评论'
        }, headers=auth_headers)

        resp = client.get(f'/api/posts/{sample_post}/comments')
        data = resp.get_json()
        assert resp.status_code == 200
        assert len(data['comments']) >= 1
        assert data['comments'][0]['content'] == '测试评论'
