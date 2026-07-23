from functools import wraps
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from utils import login_required_web
from models import db, User, Post, Comment, Category

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
ADMIN_PER_PAGE = 20


def admin_required(f):
    """管理员权限检查"""
    @wraps(f)
    @login_required_web
    def decorated(*args, **kwargs):
        user = db.session.get(User, session.get('user_id'))
        if not user or user.role != 'admin':
            flash('无权限访问', 'error')
            return redirect(url_for('posts.index'))
        return f(*args, **kwargs)
    return decorated


# ========== 数据统计 ==========

def get_stats():
    return {
        'user_count': User.query.count(),
        'post_count': Post.query.count(),
        'comment_count': Comment.query.count(),
        'category_count': Category.query.count(),
        'recent_posts': Post.query.order_by(Post.created_at.desc()).limit(5).all(),
        'recent_users': User.query.order_by(User.created_at.desc()).limit(5).all(),
    }


# ========== 页面路由 ==========

@admin_bp.route('/')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html', stats=get_stats())


@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    return render_template('admin/users.html', users=pagination.items, pagination=pagination)


@admin_bp.route('/posts')
@admin_required
def posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    return render_template('admin/posts.html', posts=pagination.items, pagination=pagination)


@admin_bp.route('/comments')
@admin_required
def comments():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '').strip()
    query = Comment.query
    if status in {'pending', 'approved', 'hidden'}:
        query = query.filter_by(status=status)
    pagination = query.order_by(Comment.created_at.desc()).paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    return render_template('admin/comments.html', comments=pagination.items, pagination=pagination, status=status)


@admin_bp.route('/categories')
@admin_required
def categories():
    return render_template('admin/categories.html', categories=Category.query.order_by(Category.name).all())


# ========== 操作接口 ==========

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == session['user_id']:
        flash('不能取消自己的管理员权限', 'error')
    else:
        user.role = 'user' if user.role == 'admin' else 'admin'
        db.session.commit()
        flash(f'已切换 {user.username} 的管理员权限', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == session['user_id']:
        flash('不能删除自己', 'error')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'已删除用户 {user.username}', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@admin_required
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    db.session.delete(post)
    db.session.commit()
    flash('文章已删除', 'success')
    return redirect(url_for('admin.posts'))


@admin_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@admin_required
def delete_comment(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect(url_for('admin.comments'))


@admin_bp.route('/comments/<int:comment_id>/status', methods=['POST'])
@admin_required
def update_comment_status(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    status = request.form.get('status')
    if status not in {'pending', 'approved', 'hidden'}:
        flash('无效的评论状态', 'error')
    else:
        comment.status = status
        db.session.commit()
        flash('评论状态已更新', 'success')
    return redirect(url_for('admin.comments'))


@admin_bp.route('/categories/create', methods=['POST'])
@admin_required
def create_category():
    name = request.form.get('name', '').strip()
    if not name:
        flash('分类名称不能为空', 'error')
    elif Category.query.filter_by(name=name).first():
        flash('分类已存在', 'error')
    else:
        db.session.add(Category(name=name))
        db.session.commit()
        flash(f'已创建分类: {name}', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@admin_required
def delete_category(cat_id):
    cat = db.get_or_404(Category, cat_id)
    # 先清空该分类下所有文章的 category_id，避免外键约束错误
    Post.query.filter_by(category_id=cat.id).update({'category_id': None})
    db.session.delete(cat)
    db.session.commit()
    flash(f'已删除分类: {cat.name}（关联文章已转为无分类）', 'success')
    return redirect(url_for('admin.categories'))
