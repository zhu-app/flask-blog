import os
import warnings


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:123456@localhost:3306/blog_db?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 3600 * 24  # 24小时
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))
    COMMENT_REQUIRE_APPROVAL = os.getenv('COMMENT_REQUIRE_APPROVAL', 'false').lower() == 'true'

    @classmethod
    def check_secrets(cls):
        """检查是否使用了默认密钥，生产环境必须替换"""
        defaults = {
            'SECRET_KEY': 'your-secret-key-change-in-production',
            'JWT_SECRET_KEY': 'jwt-secret-key-change-in-production',
        }
        for name, default in defaults.items():
            if getattr(cls, name) == default:
                warnings.warn(
                    f"⚠️ {name} 使用了不安全的默认值，请通过环境变量设置！"
                )
