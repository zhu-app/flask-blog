# 📝 Flask Blog — 全栈博客系统

> 一个完整的 Flask + MySQL 博客系统，支持文章管理、用户认证、评论点赞、分类搜索、管理员后台和 Docker 部署。

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)](https://mysql.com)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ✨ 功能特性

### 👤 用户端
| 功能 | 说明 |
|------|------|
| 📝 文章发布/编辑/删除 | 支持 Markdown 写作，实时预览 |
| 🔍 文章搜索 + 分类筛选 | 按关键词和分类快速定位 |
| 💬 评论系统 | 登录后可发表评论 |
| ❤️ 点赞功能 | 支持点赞/取消点赞 |
| 📡 RSS 订阅 | 支持 RSS 订阅最新文章 |
| 🖼️ 图片上传 | 支持在文章中插入图片 |
| 👤 个人主页 | 查看作者所有文章 |
| 🔐 双认证体系 | 网页用 Session，API 用 JWT Token |

### 🔧 管理后台
| 功能 | 说明 |
|------|------|
| 📊 数据概览 | 用户数、文章数、评论数统计 |
| 👥 用户管理 | 查看用户、切换管理员、删除用户 |
| 📰 文章管理 | 查看、删除所有文章 |
| 💬 评论管理 | 查看、删除评论 |
| 🏷️ 分类管理 | 创建、删除分类 |

### 🛡️ 安全特性
- ✅ 密码 bcrypt 加密存储（Werkzeug）
- ✅ JWT Token 认证（API 接口）
- ✅ Session 认证（网页端）
- ✅ 邮箱格式校验
- ✅ 文章所有权校验（仅作者或管理员可编辑/删除）
- ✅ 防止 Session Fixation（登录时重置 session）
- ✅ 文件上传安全过滤（白名单扩展名 + 重命名）
- ✅ 统一的错误处理（JSON + HTML 双模式）

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.10+, Flask 3.0, Flask-JWT-Extended |
| **数据库** | MySQL 8.0+, SQLAlchemy ORM |
| **前端** | HTML5, CSS3, JavaScript (Fetch API), Jinja2 |
| **Markdown** | Python-Markdown (代码高亮 + 表格 + 任务列表) |
| **RSS** | feedgen |
| **API 文档** | Swagger UI (flasgger) |
| **数据库迁移** | Flask-Migrate (Alembic) |
| **容器化** | Docker, Docker Compose |
| **测试** | pytest, pytest-flask (SQLite 内存数据库) |

---

## 🚀 快速开始

### 方式一：本地运行

#### 1. 安装依赖

```bash
pip install -r requirements.txt

# 开发依赖（可选）
pip install pytest pytest-flask
```

#### 2. 配置数据库

修改 `config.py` 中的数据库连接，或通过环境变量覆盖：

```bash
# Windows (PowerShell)
$env:DATABASE_URL="mysql+pymysql://root:your_password@localhost:3306/blog_db?charset=utf8mb4"

# Linux/Mac
export DATABASE_URL="mysql+pymysql://root:your_password@localhost:3306/blog_db?charset=utf8mb4"
```

#### 3. 创建数据库

```sql
CREATE DATABASE blog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 4. 设置密钥（生产环境必改！）

```bash
# Windows (PowerShell)
$env:SECRET_KEY="your-strong-secret-key-here"
$env:JWT_SECRET_KEY="your-strong-jwt-secret-key-here"

# Linux/Mac
export SECRET_KEY="your-strong-secret-key-here"
export JWT_SECRET_KEY="your-strong-jwt-secret-key-here"
```

#### 5. 初始化并运行

```bash
# 初始化数据库（创建表 + 默认管理员账号）
python init_db.py

# 启动服务
python app.py
```

访问 **http://localhost:5000** 🎉

### 方式二：Docker 部署（推荐）

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 中的密钥

# 2. 启动服务
docker-compose up -d

# 3. 初始化数据库
docker-compose exec web python init_db.py

# 4. 查看日志
docker-compose logs -f
```

---

## 🔑 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 👑 管理员 | `admin` | `123456` |

> ⚠️ 生产环境请立即修改密码和密钥！

---

## 📖 使用指南

### 首页访问
- **博客首页**: http://localhost:5000
- **管理员后台**: http://localhost:5000/admin
- **API 文档**: http://localhost:5000/apidocs
- **RSS 订阅**: http://localhost:5000/feed

### 写文章
1. 注册/登录账号
2. 点击导航栏「写文章」
3. 使用 Markdown 编写内容
4. 选择分类，点击发布

### 管理后台
1. 使用管理员账号登录（admin / 123456）
2. 访问 http://localhost:5000/admin
3. 管理用户、文章、评论、分类

---

## 🔌 API 接口

### 认证
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/register` | 用户注册 | - |
| POST | `/api/login` | 用户登录（返回 JWT Token） | - |

### 文章
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/posts` | 文章列表（分页/搜索/分类） | - |
| GET | `/api/posts/<id>` | 文章详情 | - |
| POST | `/api/posts` | 创建文章 | ✅ JWT |
| PUT | `/api/posts/<id>` | 更新文章（仅作者/管理员） | ✅ JWT |
| DELETE | `/api/posts/<id>` | 删除文章（仅作者/管理员） | ✅ JWT |
| POST | `/api/posts/<id>/like` | 点赞/取消点赞 | ✅ JWT |

### 评论 & 分类
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/posts/<id>/comments` | 获取评论列表 | - |
| POST | `/api/posts/<id>/comments` | 发表评论 | ✅ JWT |
| GET | `/api/categories` | 获取所有分类 | - |
| POST | `/api/categories` | 创建分类 | ✅ JWT |
| POST | `/api/upload` | 上传图片 | ✅ JWT |

---

## 📁 项目结构

```
flask-blog/
├── app.py                 # 应用工厂 + 错误处理
├── config.py              # 配置（环境变量 + 默认值）
├── init_db.py             # 数据库初始化脚本
├── pyproject.toml         # 项目元数据 + 依赖声明
├── requirements.txt       # Python 依赖
├── Dockerfile             # 多阶段构建镜像
├── docker-compose.yml     # Docker 编排（Web + MySQL）
├── .env.example           # 环境变量模板
├── models/                # 数据模型层
│   ├── user.py            #   用户模型
│   ├── post.py            #   文章模型
│   ├── comment.py         #   评论模型
│   ├── category.py        #   分类模型
│   └── like.py            #   点赞模型
├── routes/                # 路由层（蓝图）
│   ├── auth.py            #   认证（注册/登录/登出）
│   ├── posts.py           #   文章（CRUD/搜索/点赞/RSS）
│   ├── comments.py        #   评论
│   └── admin.py           #   管理员后台
├── utils/                 # 工具函数
│   └── __init__.py        #   权限装饰器
├── templates/             # Jinja2 模板
│   ├── index.html         #   首页
│   ├── post_detail.html   #   文章详情
│   ├── write_post.html    #   写文章/编辑
│   ├── login.html         #   登录
│   ├── register.html      #   注册
│   ├── user_profile.html  #   用户主页
│   ├── 404.html           #   404 页面
│   ├── 500.html           #   500 页面
│   └── admin/             #   管理后台模板
├── static/                # 静态资源
│   └── css/               #   样式文件
└── tests/                 # 测试（25 个测试用例）
    ├── conftest.py        #   Fixtures
    ├── test_auth.py       #   认证测试
    ├── test_posts.py      #   文章测试
    ├── test_comments.py   #   评论测试
    └── test_likes.py      #   点赞测试
```

---

## 🧪 测试

```bash
# 运行全部测试（25 个用例）
python -m pytest tests/ -v

# 运行测试 + 覆盖率
python -m pytest tests/ -v --cov=.

# 运行特定测试文件
python -m pytest tests/test_auth.py -v
```

---

## 🐳 Docker 常用命令

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 进入容器
docker-compose exec web bash

# 查看数据库
docker-compose exec db mysql -u root -p blog_db

# 重建镜像
docker-compose build --no-cache
```

---

## 🔒 安全注意事项

生产环境部署前，请务必完成以下操作：

- [ ] 修改 `SECRET_KEY` 和 `JWT_SECRET_KEY` 为强随机字符串
- [ ] 修改 MySQL root 密码
- [ ] 启用 HTTPS（推荐使用 Nginx + Let's Encrypt）
- [ ] 配置防火墙，限制数据库端口（3306）仅内网访问
- [ ] 禁用 `/apidocs` 路由或添加认证（生产环境）
- [ ] 添加 CSRF 保护（推荐 Flask-WTF）
- [ ] 配置日志轮转（避免日志文件无限增长）
- [ ] 定期备份数据库

---

## 📄 许可证

[MIT License](LICENSE)

---

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) — 轻量级 Web 框架
- [SQLAlchemy](https://www.sqlalchemy.org/) — 强大的 ORM
- [MySQL](https://www.mysql.com/) — 数据库
- [Docker](https://www.docker.com/) — 容器化

---

<p align="center">
  <sub>Built with ❤️ using Flask & MySQL</sub>
</p>
