from flask import Blueprint, request, jsonify, redirect, url_for, session, flash
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.orm import joinedload
from utils import login_required_web, login_required_api
from models import db, User, Comment, Post

comments_bp = Blueprint('comments', __name__)


# ========== API 路由 ==========

@comments_bp.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def api_get_comments(post_id):
    """
    获取文章评论列表
    ---
    tags:
      - 评论
    parameters:
      - in: path
        name: post_id
        type: integer
        required: true
        description: 文章ID
    responses:
      200:
        description: 评论列表
        schema:
          type: object
          properties:
            success:
              type: boolean
            comments:
              type: array
              items:
                type: object
    """
    comments = Comment.query.options(
        joinedload(Comment.author)
    ).filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    return jsonify({'success': True, 'comments': [c.to_dict() for c in comments]})


@comments_bp.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@login_required_api
def api_create_comment(post_id):
    data = request.get_json()
    content = data.get('content', '').strip()

    if not content:
        return jsonify({'success': False, 'message': '评论内容不能为空'}), 400

    comment = Comment(content=content, post_id=post_id, user_id=int(get_jwt_identity()))
    db.session.add(comment)
    db.session.commit()

    return jsonify({'success': True, 'message': '评论成功', 'comment': comment.to_dict()}), 201


# ========== 网页路由 ==========

@comments_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required_web
def add_comment(post_id):
    content = request.form.get('content', '').strip()

    if not content:
        flash('评论内容不能为空', 'error')
        return redirect(url_for('posts.post_detail', post_id=post_id))

    comment = Comment(content=content, post_id=post_id, user_id=session['user_id'])
    db.session.add(comment)
    db.session.commit()

    flash('评论成功！', 'success')
    return redirect(url_for('posts.post_detail', post_id=post_id))


@comments_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required_web
def delete_comment(comment_id):
    """删除评论：评论作者、文章作者、管理员均可删除"""
    comment = Comment.query.get_or_404(comment_id)
    post = db.session.get(Post, comment.post_id)

    user_id = session['user_id']
    is_comment_author = comment.user_id == user_id
    is_post_author = post and post.user_id == user_id
    user = db.session.get(User, user_id)
    is_admin = user and user.role == 'admin'

    if not (is_comment_author or is_post_author or is_admin):
        flash('无权删除此评论', 'error')
        return redirect(url_for('posts.post_detail', post_id=comment.post_id))

    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect(url_for('posts.post_detail', post_id=comment.post_id))
