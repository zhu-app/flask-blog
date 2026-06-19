from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from flask_jwt_extended import create_access_token
from models import db, User, Post

auth_bp = Blueprint('auth', __name__)


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
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not all([username, email, password]):
        return jsonify({'success': False, 'message': '请填写完整信息'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少6位'}), 400

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
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
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

    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401


# ========== 网页路由 ==========

@auth_bp.route('/register')
def register_page():
    return render_template('register.html')


@auth_bp.route('/login')
def login_page():
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@auth_bp.route('/user/<username>')
def user_profile(username):
    from models import User
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    return render_template('user_profile.html', profile_user=user, posts=posts)
