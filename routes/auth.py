import re
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from flask_jwt_extended import create_access_token
from models import db, User, Post

auth_bp = Blueprint('auth', __name__)
LOGIN_ATTEMPTS = {}
MAX_LOGIN_ATTEMPTS = 20
LOGIN_WINDOW = timedelta(minutes=10)

# 邮箱正则
EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def login_key(username):
    return f"{request.remote_addr or 'local'}:{username.lower()}"


def login_is_limited(username):
    now = datetime.now(timezone.utc)
    key = login_key(username)
    attempts = [ts for ts in LOGIN_ATTEMPTS.get(key, []) if now - ts < LOGIN_WINDOW]
    LOGIN_ATTEMPTS[key] = attempts
    return len(attempts) >= MAX_LOGIN_ATTEMPTS


def record_failed_login(username):
    LOGIN_ATTEMPTS.setdefault(login_key(username), []).append(datetime.now(timezone.utc))


def clear_failed_logins(username):
    LOGIN_ATTEMPTS.pop(login_key(username), None)


# ========== API 路由 ==========

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    """
    用户注册
    ---
    tags:
      - 认证
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [username, email, password]
          properties:
            username:
              type: string
              description: 用户名
              example: newuser
            email:
              type: string
              description: 邮箱
              example: user@example.com
            password:
              type: string
              description: 密码（至少6位）
              example: 123456
    responses:
      201:
        description: 注册成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: 注册成功
            user:
              type: object
      400:
        description: 参数错误或用户已存在
    """
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not all([username, email, password]):
        return jsonify({'success': False, 'message': '请填写完整信息'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少6位'}), 400

    if not EMAIL_RE.match(email):
        return jsonify({'success': False, 'message': '邮箱格式不正确'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': '邮箱已注册'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'success': True, 'message': '注册成功', 'user': user.to_dict()}), 201


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """
    用户登录
    ---
    tags:
      - 认证
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [username, password]
          properties:
            username:
              type: string
              description: 用户名
              example: admin
            password:
              type: string
              description: 密码
              example: 123456
    responses:
      200:
        description: 登录成功，返回 JWT Token
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            token:
              type: string
              description: JWT Token
            user:
              type: object
      401:
        description: 用户名或密码错误
    """
    data = request.get_json(silent=True) or {}
    username = data.get('username', '')
    password = data.get('password', '')

    if login_is_limited(username):
        return jsonify({'success': False, 'message': '登录尝试过多，请稍后再试'}), 429

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        clear_failed_logins(username)
        token = create_access_token(identity=str(user.id))
        # 清除旧session，防止 Session Fixation
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': token,
            'user': user.to_dict()
        }), 200

    record_failed_login(username)
    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401


# ========== 网页路由 ==========

@auth_bp.route('/register')
def register_page():
    return render_template('register.html')


@auth_bp.route('/login')
def login_page():
    return render_template('login.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    reset_url = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.create_reset_token()
            db.session.commit()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
        flash('如果邮箱存在，系统已生成重置链接。', 'success')
    return render_template('forgot_password.html', reset_url=reset_url)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_is_valid(token):
        flash('重置链接无效或已过期', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if len(password) < 6:
            flash('密码至少 6 位', 'error')
        elif password != confirm:
            flash('两次密码输入不一致', 'error')
        else:
            user.set_password(password)
            user.clear_reset_token()
            db.session.commit()
            flash('密码已重置，请重新登录', 'success')
            return redirect(url_for('auth.login_page'))
    return render_template('reset_password.html', token=token)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('posts.index'))


@auth_bp.route('/user/<username>')
def user_profile(username):
    from models import User
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id, status='published').order_by(Post.created_at.desc()).all()
    return render_template('user_profile.html', profile_user=user, posts=posts)
