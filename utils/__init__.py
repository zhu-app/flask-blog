from functools import wraps
from flask import session, redirect, url_for, flash
from flask_jwt_extended import jwt_required


def login_required_web(f):
    """网页版登录检查（Session）"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'error')
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


def login_required_api(f):
    """API版登录检查（JWT Token）"""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated
