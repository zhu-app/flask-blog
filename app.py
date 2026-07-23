import os
import logging
import traceback
import hmac
from secrets import token_urlsafe
from flask import Flask, render_template, redirect, url_for, flash, session, send_from_directory, jsonify, request
from config import Config
from models import db
from routes.auth import auth_bp
from routes.posts import posts_bp
from routes.comments import comments_bp
from routes.admin import admin_bp
from flask_jwt_extended import JWTManager                                              # noqa: F401 (init)
from flask_migrate import Migrate                                                      # noqa: F401 (init)
from flasgger import Swagger                                                           # noqa: F401 (init)


def setup_logging(app: Flask) -> None:
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # 文件日志（仅生产环境）
    if not app.debug:
        file_handler = logging.FileHandler('app.log', encoding='utf-8')
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        ))
        app.logger.addHandler(file_handler)


def register_error_handlers(app: Flask) -> None:
    """注册统一错误处理"""

    @app.errorhandler(400)
    def bad_request(e):
        app.logger.warning(f'400 Bad Request: {request.path}')
        if request.is_json:
            return jsonify({'success': False, 'message': '请求参数错误'}), 400
        flash('请求参数错误', 'error')
        return redirect(url_for('posts.index'))

    @app.errorhandler(403)
    def forbidden(e):
        app.logger.warning(f'403 Forbidden: {request.path}')
        if request.is_json:
            return jsonify({'success': False, 'message': '无权限访问'}), 403
        flash('无权限访问', 'error')
        return redirect(url_for('posts.index'))

    @app.errorhandler(404)
    def not_found(e):
        app.logger.info(f'404 Not Found: {request.path}')
        if request.is_json:
            return jsonify({'success': False, 'message': '资源不存在'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        app.logger.warning(f'405 Method Not Allowed: {request.method} {request.path}')
        if request.is_json:
            return jsonify({'success': False, 'message': '请求方法不允许'}), 405
        flash('请求方法不允许', 'error')
        return redirect(url_for('posts.index'))

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f'500 Internal Error: {request.path}\n{traceback.format_exc()}')
        if request.is_json:
            return jsonify({'success': False, 'message': '服务器内部错误'}), 500
        return render_template('500.html'), 500


def register_csrf_protection(app: Flask) -> None:
    """Protect session-backed HTML forms from cross-site request forgery."""

    def csrf_token() -> str:
        token = session.get('_csrf_token')
        if not token:
            token = token_urlsafe(32)
            session['_csrf_token'] = token
        return token

    @app.before_request
    def validate_csrf_token():
        if request.method not in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            return None
        if request.path.startswith('/api/'):
            return None

        token = session.get('_csrf_token')
        submitted = request.form.get('_csrf_token') or request.headers.get('X-CSRFToken')
        if not token or not submitted or not hmac.compare_digest(token, submitted):
            app.logger.warning(f'CSRF validation failed: {request.method} {request.path}')
            if request.is_json:
                return jsonify({'success': False, 'message': 'CSRF token invalid'}), 400
            flash('请求已过期，请刷新页面后重试', 'error')
            return redirect(url_for('posts.index'))
        return None

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=csrf_token)


def create_app(config_class=None) -> Flask:
    if config_class is None:
        config_class = Config
    config_class.check_secrets()
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 配置日志
    setup_logging(app)

    # 初始化扩展
    db.init_app(app)
    JWTManager(app)
    Migrate(app, db)

    # Swagger 配置
    Swagger(app, template={
        'info': {
            'title': 'Ink & Code API',
            'description': 'Flask + MySQL 博客系统 RESTful API 文档',
            'version': '1.0.0',
            'contact': {
                'name': '开发者',
                'email': 'admin@example.com'
            }
        },
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT Token，格式: Bearer <token>'
            }
        },
        'security': [{'Bearer': []}],
        'tags': [
            {'name': '认证', 'description': '用户注册与登录'},
            {'name': '文章', 'description': '文章 CRUD、搜索、点赞'},
            {'name': '评论', 'description': '文章评论'},
            {'name': '分类', 'description': '文章分类管理'},
            {'name': '文件', 'description': '图片上传'},
        ]
    })

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(admin_bp)

    # 注册错误处理
    register_error_handlers(app)
    register_csrf_protection(app)

    # 全局变量
    @app.context_processor
    def inject_user():
        user_id = session.get('user_id')
        user = None
        if user_id:
            from models import User
            user = db.session.get(User, int(user_id))
        return dict(current_user=user)

    # 提供上传目录的静态文件
    upload_dir = os.path.join(app.root_path, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(upload_dir, filename)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5000)
