import os
import markdown
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash, current_app
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from utils import login_required_web, login_required_api
from models import db, User, Post, Category, Like
from sqlalchemy.orm import joinedload

posts_bp = Blueprint('posts', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_categories():
    return Category.query.order_by(Category.name).all()


# ========== API 路由 ==========

@posts_bp.route('/api/posts', methods=['GET'])
def api_get_posts():
    """
    获取文章列表（支持分页、搜索、分类筛选）
    ---
    tags:
      - 文章
    parameters:
      - in: query
        name: page
        type: integer
        description: 页码（默认1）
        required: false
      - in: query
        name: per_page
        type: integer
        description: 每页条数（默认10）
        required: false
      - in: query
        name: keyword
        type: string
        description: 搜索关键词
        required: false
      - in: query
        name: category_id
        type: integer
        description: 分类ID
        required: false
    responses:
      200:
        description: 文章列表
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            posts:
              type: array
              items:
                type: object
            total:
              type: integer
            page:
              type: integer
            pages:
              type: integer
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id', type=int)

    query = Post.query.options(
        joinedload(Post.author),
        joinedload(Post.category)
    )
    if keyword:
        query = query.filter(Post.title.contains(keyword) | Post.content.contains(keyword))
    if category_id:
        query = query.filter(Post.category_id == category_id)

    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'posts': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages
    })


@posts_bp.route('/api/posts/<int:post_id>', methods=['GET'])
def api_get_post(post_id):
    """
    获取文章详情
    ---
    tags:
      - 文章
    parameters:
      - in: path
        name: post_id
        type: integer
        required: true
        description: 文章ID
    responses:
      200:
        description: 文章详情
        schema:
          type: object
          properties:
            success:
              type: boolean
            post:
              type: object
      404:
        description: 文章不存在
    """
    post = Post.query.get_or_404(post_id)
    return jsonify({'success': True, 'post': post.to_dict()})


@posts_bp.route('/api/posts', methods=['POST'])
@login_required_api
def api_create_post():
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()

    if not title or not content:
        return jsonify({'success': False, 'message': '标题和内容不能为空'}), 400

    post = Post(title=title, content=content, user_id=int(get_jwt_identity()),
                category_id=data.get('category_id'))
    db.session.add(post)
    db.session.commit()

    return jsonify({'success': True, 'message': '发布成功', 'post': post.to_dict()}), 201


@posts_bp.route('/api/posts/<int:post_id>', methods=['PUT'])
@login_required_api
def api_update_post(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = int(get_jwt_identity())

    # 检查所有权：只有作者或管理员可以编辑
    if post.user_id != user_id:
        user = db.session.get(User, user_id)
        if not user or user.role != 'admin':
            return jsonify({'success': False, 'message': '无权修改他人文章'}), 403

    data = request.get_json()

    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    if 'category_id' in data:
        post.category_id = data['category_id']
    db.session.commit()

    return jsonify({'success': True, 'message': '更新成功', 'post': post.to_dict()})


@posts_bp.route('/api/posts/<int:post_id>', methods=['DELETE'])
@login_required_api
def api_delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = int(get_jwt_identity())

    # 检查所有权：只有作者或管理员可以删除
    if post.user_id != user_id:
        user = db.session.get(User, user_id)
        if not user or user.role != 'admin':
            return jsonify({'success': False, 'message': '无权删除他人文章'}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({'success': True, 'message': '删除成功'})


# ---------- 点赞 ----------

@posts_bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
@login_required_api
def api_toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = int(get_jwt_identity())

    existing = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
        post.likes -= 1
        liked = False
    else:
        like = Like(user_id=user_id, post_id=post_id)
        db.session.add(like)
        post.likes += 1
        liked = True
    db.session.commit()

    return jsonify({'success': True, 'liked': liked, 'likes': post.likes})


# ---------- 分类 ----------

@posts_bp.route('/api/categories', methods=['GET'])
def api_get_categories():
    return jsonify({'success': True, 'categories': [c.to_dict() for c in get_categories()]})


@posts_bp.route('/api/categories', methods=['POST'])
@login_required_api
def api_create_category():
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'message': '分类名称不能为空'}), 400
    if Category.query.filter_by(name=name).first():
        return jsonify({'success': False, 'message': '分类已存在'}), 400

    cat = Category(name=name)
    db.session.add(cat)
    db.session.commit()
    return jsonify({'success': True, 'category': cat.to_dict()}), 201


# ---------- 图片上传 ----------

@posts_bp.route('/api/upload', methods=['POST'])
@login_required_api
def api_upload():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '未选择文件'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'success': False, 'message': '不支持的文件类型'}), 400

    # 确保上传目录存在
    upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)

    filename = secure_filename(file.filename)
    # 加时间戳防止重名
    name, ext = os.path.splitext(filename)
    filename = f"{name}_{int(datetime.now(timezone.utc).timestamp())}{ext}"
    file.save(os.path.join(upload_path, filename))

    url = f"/{UPLOAD_FOLDER}/{filename}"
    return jsonify({'success': True, 'url': url, 'filename': filename})


# ========== 网页路由 ==========

@posts_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id', type=int)

    query = Post.query.options(
        joinedload(Post.author),
        joinedload(Post.category)
    )
    if keyword:
        query = query.filter(Post.title.contains(keyword) | Post.content.contains(keyword))
    if category_id:
        query = query.filter(Post.category_id == category_id)

    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        'index.html',
        posts=pagination.items,
        pagination=pagination,
        keyword=keyword,
        category_id=category_id,
        categories=get_categories()
    )


@posts_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.options(
        joinedload(Post.author),
        joinedload(Post.category),
        joinedload(Post.comments).joinedload(Comment.author)
    ).get_or_404(post_id)
    # 增加阅读量
    post.views += 1
    db.session.commit()

    # 渲染 Markdown
    post.html_content = markdown.markdown(
        post.content,
        extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
    )

    # 当前用户是否点赞
    liked = False
    if 'user_id' in session:
        liked = Like.query.filter_by(user_id=session['user_id'], post_id=post_id).first() is not None

    return render_template('post_detail.html', post=post, liked=liked)


@posts_bp.route('/write')
@login_required_web
def write_post():
    return render_template('write_post.html', categories=get_categories())


@posts_bp.route('/publish', methods=['POST'])
@login_required_web
def publish_post():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()

    if not title or not content:
        flash('标题和内容不能为空', 'error')
        return redirect(url_for('posts.write_post'))

    category_id = request.form.get('category_id', type=int) or None
    post = Post(title=title, content=content, user_id=session['user_id'],
                category_id=category_id)
    db.session.add(post)
    db.session.commit()

    flash('发布成功！', 'success')
    return redirect(url_for('posts.index'))


@posts_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required_web
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    # 检查所有权：只有作者或管理员可以编辑
    if post.user_id != session['user_id']:
        user = db.session.get(User, session['user_id'])
        if not user or user.role != 'admin':
            flash('无权编辑他人文章', 'error')
            return redirect(url_for('posts.index'))

    if request.method == 'POST':
        post.title = request.form.get('title', post.title).strip()
        post.content = request.form.get('content', post.content).strip()
        post.category_id = request.form.get('category_id', type=int) or None
        db.session.commit()
        flash('更新成功！', 'success')
        return redirect(url_for('posts.post_detail', post_id=post_id))

    return render_template('write_post.html', post=post, editing=True, categories=get_categories())


# ========== 个人中心 ==========

@posts_bp.route('/dashboard')
@login_required_web
def dashboard():
    """个人中心：查看自己的文章和统计数据"""
    user = db.session.get(User, session['user_id'])
    posts = Post.query.options(
        joinedload(Post.category)
    ).filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()

    stats = {
        'post_count': len(posts),
        'total_views': sum(p.views for p in posts),
        'total_likes': sum(p.likes for p in posts),
        'total_comments': sum(p.comment_count for p in posts),
    }

    categories = Category.query.order_by(Category.name).all()

    return render_template('dashboard.html', user=user, posts=posts, stats=stats, categories=categories)


@posts_bp.route('/dashboard/password', methods=['GET', 'POST'])
@login_required_web
def change_password():
    """修改密码"""
    user = db.session.get(User, session['user_id'])

    if request.method == 'POST':
        old_pw = request.form.get('old_password', '')
        new_pw = request.form.get('new_password', '')
        confirm_pw = request.form.get('confirm_password', '')

        if not user.check_password(old_pw):
            flash('当前密码错误', 'error')
        elif len(new_pw) < 6:
            flash('新密码至少6位', 'error')
        elif new_pw != confirm_pw:
            flash('两次密码输入不一致', 'error')
        else:
            user.set_password(new_pw)
            db.session.commit()
            flash('密码修改成功！', 'success')
            return redirect(url_for('posts.dashboard'))

    return render_template('change_password.html', user=user)


@posts_bp.route('/dashboard/post/<int:post_id>/delete', methods=['POST'])
@login_required_web
def dashboard_delete_post(post_id):
    """从个人中心删除自己的文章"""
    post = Post.query.get_or_404(post_id)

    # 检查所有权：只有作者或管理员可以删除
    if post.user_id != session['user_id']:
        user = db.session.get(User, session['user_id'])
        if not user or user.role != 'admin':
            flash('无权删除他人文章', 'error')
            return redirect(url_for('posts.dashboard'))

    db.session.delete(post)
    db.session.commit()
    flash('文章已删除', 'success')
    return redirect(url_for('posts.dashboard'))


