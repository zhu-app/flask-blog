import os
import markdown
import bleach
from datetime import timezone
from secrets import token_urlsafe
from feedgen.feed import FeedGenerator
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash, current_app, abort
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from utils import login_required_web, login_required_api
from models import db, User, Post, Category, Like, Comment, Tag
from sqlalchemy import select
from sqlalchemy.orm import joinedload

posts_bp = Blueprint('posts', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}
MAX_PER_PAGE = 50
DEFAULT_PER_PAGE = 10

MARKDOWN_TAGS = {
    'a', 'abbr', 'blockquote', 'br', 'code', 'del', 'div', 'em', 'h1', 'h2', 'h3',
    'h4', 'h5', 'h6', 'hr', 'img', 'li', 'ol', 'p', 'pre', 'span', 'strong',
    'table', 'tbody', 'td', 'th', 'thead', 'tr', 'ul'
}
MARKDOWN_ATTRIBUTES = {
    'a': ['href', 'title'],
    'code': ['class'],
    'div': ['class'],
    'img': ['alt', 'src', 'title'],
    'pre': ['class'],
    'span': ['class'],
    'td': ['align'],
    'th': ['align'],
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def render_markdown(content):
    raw_html = markdown.markdown(
        content,
        extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
    )
    return bleach.clean(
        raw_html,
        tags=MARKDOWN_TAGS,
        attributes=MARKDOWN_ATTRIBUTES,
        protocols=['http', 'https', 'mailto'],
        strip=True
    )


def get_per_page(default=DEFAULT_PER_PAGE):
    per_page = request.args.get('per_page', default, type=int)
    if per_page < 1:
        return default
    return min(per_page, MAX_PER_PAGE)


def get_categories():
    return Category.query.order_by(Category.name).all()


def get_tag_names(value):
    if not value:
        return []
    if isinstance(value, (list, tuple, set)):
        value = ','.join(str(item) for item in value)
    names = []
    for raw in value.replace('，', ',').split(','):
        name = raw.strip().lower()
        if name and name not in names:
            names.append(name[:40])
    return names[:8]


def set_post_tags(post, tag_text):
    tags = []
    for name in get_tag_names(tag_text):
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
        tags.append(tag)
    post.tags = tags


def summarize(content, limit=150):
    text = bleach.clean(markdown.markdown(content), tags=[], strip=True).strip()
    return text[:limit]


def can_manage_post(post):
    if 'user_id' not in session:
        return False
    if post.user_id == session['user_id']:
        return True
    user = db.session.get(User, session['user_id'])
    return bool(user and user.role == 'admin')


def published_posts_query():
    return Post.query.filter_by(status='published')


def as_utc(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


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
    per_page = get_per_page()
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id', type=int)
    tag = request.args.get('tag', '').strip().lower()

    query = published_posts_query().options(
        joinedload(Post.author),
        joinedload(Post.category)
    )
    if keyword:
        query = query.filter(Post.title.contains(keyword) | Post.content.contains(keyword))
    if category_id:
        query = query.filter(Post.category_id == category_id)
    if tag:
        query = query.join(Post.tags).filter(Tag.name == tag)

    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'posts': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages,
        'tag': tag
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
    post = db.get_or_404(Post, post_id)
    if post.status != 'published' and not can_manage_post(post):
        abort(404)
    return jsonify({'success': True, 'post': post.to_dict()})


@posts_bp.route('/api/posts', methods=['POST'])
@login_required_api
def api_create_post():
    data = request.get_json(silent=True) or {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()

    if not title or not content:
        return jsonify({'success': False, 'message': '标题和内容不能为空'}), 400

    status = data.get('status', 'published')
    if status not in {'draft', 'published'}:
        status = 'published'

    post = Post(
        title=title,
        content=content,
        user_id=int(get_jwt_identity()),
        category_id=data.get('category_id'),
        status=status,
        cover_image=data.get('cover_image'),
        seo_description=data.get('seo_description') or summarize(content)
    )
    set_post_tags(post, data.get('tags', ''))
    db.session.add(post)
    db.session.commit()

    return jsonify({'success': True, 'message': '发布成功', 'post': post.to_dict()}), 201


@posts_bp.route('/api/posts/<int:post_id>', methods=['PUT'])
@login_required_api
def api_update_post(post_id):
    post = db.get_or_404(Post, post_id)
    user_id = int(get_jwt_identity())

    # 检查所有权：只有作者或管理员可以编辑
    if post.user_id != user_id:
        user = db.session.get(User, user_id)
        if not user or user.role != 'admin':
            return jsonify({'success': False, 'message': '无权修改他人文章'}), 403

    data = request.get_json(silent=True) or {}

    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    post.cover_image = data.get('cover_image', post.cover_image)
    post.seo_description = data.get('seo_description', post.seo_description) or summarize(post.content)
    if data.get('status') in {'draft', 'published'}:
        post.status = data['status']
    if 'category_id' in data:
        post.category_id = data['category_id']
    if 'tags' in data:
        set_post_tags(post, data.get('tags', ''))
    db.session.commit()

    return jsonify({'success': True, 'message': '更新成功', 'post': post.to_dict()})


@posts_bp.route('/api/posts/<int:post_id>', methods=['DELETE'])
@login_required_api
def api_delete_post(post_id):
    post = db.get_or_404(Post, post_id)
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
    post = db.get_or_404(Post, post_id)
    user_id = int(get_jwt_identity())

    existing = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
        post.likes = max(0, post.likes - 1)
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
    data = request.get_json(silent=True) or {}
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
    if file.mimetype not in ALLOWED_MIME_TYPES:
        return jsonify({'success': False, 'message': '不支持的文件类型'}), 400

    # 确保上传目录存在
    upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)

    filename = secure_filename(file.filename)
    _, ext = os.path.splitext(filename)
    filename = f"{token_urlsafe(16)}{ext.lower()}"
    file.save(os.path.join(upload_path, filename))

    url = f"/{UPLOAD_FOLDER}/{filename}"
    return jsonify({'success': True, 'url': url, 'filename': filename})


# ========== 网页路由 ==========

@posts_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = DEFAULT_PER_PAGE
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id', type=int)
    tag = request.args.get('tag', '').strip().lower()

    query = published_posts_query().options(
        joinedload(Post.author),
        joinedload(Post.category)
    )
    if keyword:
        query = query.filter(Post.title.contains(keyword) | Post.content.contains(keyword))
    if category_id:
        query = query.filter(Post.category_id == category_id)
    if tag:
        query = query.join(Post.tags).filter(Tag.name == tag)

    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        'index.html',
        posts=pagination.items,
        pagination=pagination,
        keyword=keyword,
        category_id=category_id,
        tag=tag,
        categories=get_categories(),
        tags=Tag.query.order_by(Tag.name).all()
    )


@posts_bp.route('/rss.xml')
def rss_feed():
    fg = FeedGenerator()
    fg.title('Ink & Code')
    fg.link(href=url_for('posts.index', _external=True), rel='alternate')
    fg.link(href=url_for('posts.rss_feed', _external=True), rel='self')
    fg.description('Ink & Code 最新文章')
    fg.language('zh-CN')

    posts = published_posts_query().options(joinedload(Post.author)).order_by(Post.created_at.desc()).limit(20).all()
    for post in posts:
        fe = fg.add_entry()
        fe.id(url_for('posts.post_detail', post_id=post.id, _external=True))
        fe.title(post.title)
        fe.link(href=url_for('posts.post_detail', post_id=post.id, _external=True))
        fe.author(name=post.author.username if post.author else 'Ink & Code')
        fe.description(post.seo_description or summarize(post.content))
        fe.published(as_utc(post.created_at))
        fe.updated(as_utc(post.updated_at))

    return current_app.response_class(fg.rss_str(pretty=True), mimetype='application/rss+xml')


@posts_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post = db.first_or_404(
        select(Post).options(
            joinedload(Post.author),
            joinedload(Post.category),
            joinedload(Post.comments).joinedload(Comment.author)
        ).where(Post.id == post_id)
    )
    if post.status != 'published' and not can_manage_post(post):
        abort(404)
    # 增加阅读量
    post.views += 1
    db.session.commit()

    # 渲染 Markdown
    post.html_content = render_markdown(post.content)

    # 当前用户是否点赞
    liked = False
    if 'user_id' in session:
        liked = Like.query.filter_by(user_id=session['user_id'], post_id=post_id).first() is not None

    can_moderate_comments = can_manage_post(post)
    visible_comments = [
        comment for comment in post.comments
        if comment.status == 'approved' or can_moderate_comments or comment.user_id == session.get('user_id')
    ]

    return render_template(
        'post_detail.html',
        post=post,
        liked=liked,
        comments=visible_comments,
        can_moderate_comments=can_moderate_comments
    )


@posts_bp.route('/write')
@login_required_web
def write_post():
    return render_template('write_post.html', categories=get_categories(), all_tags=Tag.query.order_by(Tag.name).all())


@posts_bp.route('/publish', methods=['POST'])
@login_required_web
def publish_post():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    status = 'draft' if request.form.get('action') == 'draft' else 'published'

    if not title or not content:
        flash('标题和内容不能为空', 'error')
        return redirect(url_for('posts.write_post'))

    category_id = request.form.get('category_id', type=int) or None
    post = Post(
        title=title,
        content=content,
        user_id=session['user_id'],
        category_id=category_id,
        status=status,
        cover_image=request.form.get('cover_image', '').strip() or None,
        seo_description=request.form.get('seo_description', '').strip() or summarize(content)
    )
    set_post_tags(post, request.form.get('tags', ''))
    db.session.add(post)
    db.session.commit()

    flash('草稿已保存' if status == 'draft' else '发布成功！', 'success')
    if status == 'draft':
        return redirect(url_for('posts.dashboard'))
    return redirect(url_for('posts.index'))


@posts_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required_web
def edit_post(post_id):
    post = db.get_or_404(Post, post_id)

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
        post.status = 'draft' if request.form.get('action') == 'draft' else 'published'
        post.cover_image = request.form.get('cover_image', '').strip() or None
        post.seo_description = request.form.get('seo_description', '').strip() or summarize(post.content)
        set_post_tags(post, request.form.get('tags', ''))
        db.session.commit()
        flash('草稿已保存' if post.status == 'draft' else '更新成功！', 'success')
        if post.status == 'draft':
            return redirect(url_for('posts.dashboard'))
        return redirect(url_for('posts.post_detail', post_id=post_id))

    return render_template('write_post.html', post=post, editing=True, categories=get_categories(), all_tags=Tag.query.order_by(Tag.name).all())


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
        'published_count': sum(1 for p in posts if p.status == 'published'),
        'draft_count': sum(1 for p in posts if p.status == 'draft'),
        'total_views': sum(p.views for p in posts),
        'total_likes': sum(p.likes for p in posts),
        'total_comments': sum(p.comment_count for p in posts),
    }

    categories = Category.query.order_by(Category.name).all()

    return render_template('dashboard.html', user=user, posts=posts, stats=stats, categories=categories)


@posts_bp.route('/dashboard/profile', methods=['POST'])
@login_required_web
def update_profile():
    user = db.session.get(User, session['user_id'])
    user.avatar_url = request.form.get('avatar_url', '').strip() or None
    db.session.commit()
    flash('资料已更新', 'success')
    return redirect(url_for('posts.dashboard'))


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
    post = db.get_or_404(Post, post_id)

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
