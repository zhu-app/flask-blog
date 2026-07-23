# Ink & Code

一个基于 Flask + MySQL 的个人博客系统，覆盖写作、分类、标签、评论、点赞、后台管理、RSS、SEO 和基础安全防护。适合作为个人作品集、课程项目或 Flask 全栈实践项目。

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)
![Tests](https://img.shields.io/badge/tests-35%20passed-brightgreen)

## 功能亮点

### 用户端

| 功能 | 说明 |
| --- | --- |
| 用户认证 | 注册、登录、退出、修改密码、找回密码 |
| 文章写作 | Markdown 写作、实时预览、发布、编辑、删除 |
| 草稿箱 | 支持保存草稿，草稿不会公开展示 |
| 分类与标签 | 支持分类筛选、标签筛选和文章标签管理 |
| 文章封面 | 支持文章封面图片 URL |
| SEO 摘要 | 支持自定义文章摘要，未填写时自动生成 |
| 评论系统 | 登录用户可评论，支持评论审核状态 |
| 点赞系统 | 支持点赞与取消点赞 |
| 图片上传 | 支持常见图片格式上传，并限制 SVG 和文件大小 |
| 个人中心 | 查看自己的文章、草稿、统计数据，设置头像 |
| 用户主页 | 展示作者公开文章 |
| RSS | 提供 `/rss.xml` 订阅源 |

### 管理后台

| 功能 | 说明 |
| --- | --- |
| 数据概览 | 用户数、文章数、评论数、分类数 |
| 用户管理 | 查看用户、切换管理员、删除用户 |
| 文章管理 | 查看文章、区分草稿/已发布、删除文章 |
| 评论管理 | 查看评论、按状态筛选、通过/隐藏/删除评论 |
| 分类管理 | 创建、删除分类 |
| 后台分页 | 用户、文章、评论列表支持分页 |

### 安全与工程质量

- 密码使用 Werkzeug 哈希存储
- API 使用 JWT，网页端使用 Session
- 登录后清理旧 Session，降低 Session Fixation 风险
- 网页表单带 CSRF 校验
- Markdown 渲染后使用 `bleach` 清洗，降低 XSS 风险
- 上传文件限制扩展名、MIME 类型和大小
- 登录失败限流
- 数据库结构使用 Flask-Migrate / Alembic 管理
- 自动测试覆盖主要流程，目前 `35 passed`

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 后端 | Flask 3.0, Flask-SQLAlchemy, Flask-JWT-Extended |
| 数据库 | MySQL 8.0, SQLAlchemy ORM |
| 迁移 | Flask-Migrate, Alembic |
| 前端 | HTML, CSS, JavaScript, Jinja2 |
| Markdown | Python-Markdown, Marked.js, Highlight.js |
| 安全 | bleach, CSRF token, 登录限流 |
| 测试 | pytest, Flask test client, SQLite 内存库 |

## 快速开始

### 1. 安装依赖

推荐使用普通 `pip`：

```bash
pip install -r requirements.txt
pip install pytest pytest-flask
```

如果你使用 `uv`，项目也保留了 `uv.lock`：

```bash
uv sync
```

### 2. 配置环境变量

Windows PowerShell 示例：

```powershell
$env:DATABASE_URL="mysql+pymysql://root:your_password@localhost:3306/blog_db?charset=utf8mb4"
$env:SECRET_KEY="change-this-secret-key"
$env:JWT_SECRET_KEY="change-this-jwt-secret-key"
```

Linux / macOS 示例：

```bash
export DATABASE_URL="mysql+pymysql://root:your_password@localhost:3306/blog_db?charset=utf8mb4"
export SECRET_KEY="change-this-secret-key"
export JWT_SECRET_KEY="change-this-jwt-secret-key"
```

可选配置：

```bash
# 默认 5MB
MAX_CONTENT_LENGTH=5242880

# 是否开启评论审核，true 时新评论进入 pending 状态
COMMENT_REQUIRE_APPROVAL=false
```

### 3. 创建数据库

```sql
CREATE DATABASE blog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 执行迁移并初始化数据

```bash
flask --app app:create_app db upgrade
python init_db.py
```

默认管理员账号：

| 用户名 | 密码 |
| --- | --- |
| `admin` | `123456` |

首次进入后建议立即修改默认密码。

### 5. 启动项目

```bash
python app.py
```

访问：

- 首页：http://localhost:5000
- 个人中心：http://localhost:5000/dashboard
- 管理后台：http://localhost:5000/admin
- API 文档：http://localhost:5000/apidocs
- RSS：http://localhost:5000/rss.xml

## API 概览

### 认证

| 方法 | 路径 | 说明 | 认证 |
| --- | --- | --- | --- |
| POST | `/api/register` | 用户注册 | 无 |
| POST | `/api/login` | 用户登录，返回 JWT | 无 |

### 文章

| 方法 | 路径 | 说明 | 认证 |
| --- | --- | --- | --- |
| GET | `/api/posts` | 文章列表，支持分页、搜索、分类、标签 | 无 |
| GET | `/api/posts/<id>` | 文章详情 | 无 |
| POST | `/api/posts` | 创建文章，可设置草稿/发布状态 | JWT |
| PUT | `/api/posts/<id>` | 更新文章 | JWT |
| DELETE | `/api/posts/<id>` | 删除文章 | JWT |
| POST | `/api/posts/<id>/like` | 点赞/取消点赞 | JWT |
| POST | `/api/upload` | 上传图片 | JWT |

### 评论与分类

| 方法 | 路径 | 说明 | 认证 |
| --- | --- | --- | --- |
| GET | `/api/posts/<id>/comments` | 获取已通过评论 | 无 |
| POST | `/api/posts/<id>/comments` | 发表评论 | JWT |
| GET | `/api/categories` | 获取分类列表 | 无 |
| POST | `/api/categories` | 创建分类 | JWT |

## 项目结构

```text
flask-blog/
├── app.py                     # 应用工厂、扩展初始化、错误处理、CSRF
├── config.py                  # 环境变量配置
├── init_db.py                 # 默认管理员和分类初始化
├── requirements.txt           # Python 依赖
├── migrations/                # Alembic 数据库迁移
│   └── versions/
│       └── 0001_initial_blog_schema.py
├── models/                    # 数据模型
│   ├── user.py
│   ├── post.py
│   ├── tag.py
│   ├── comment.py
│   ├── category.py
│   └── like.py
├── routes/                    # Flask 蓝图
│   ├── auth.py
│   ├── posts.py
│   ├── comments.py
│   └── admin.py
├── templates/                 # Jinja2 页面模板
│   ├── index.html
│   ├── post_detail.html
│   ├── write_post.html
│   ├── dashboard.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   └── admin/
├── static/                    # CSS 和静态资源
└── tests/                     # 自动测试
```

## 测试

运行全部测试：

```bash
python -m pytest -q
```

当前测试覆盖：

- 注册、登录、找回密码
- 文章 CRUD、搜索、分页
- 草稿不公开
- 标签筛选
- Markdown 安全清洗
- 图片上传限制
- 评论创建与审核可见性
- 点赞/取消点赞
- RSS feed
- CSRF 拦截

当前结果：

```text
35 passed
```

## 说明

找回密码功能目前是本地开发版：系统会生成一次性重置链接并显示在页面上。若用于真实线上环境，应接入邮件服务发送重置链接。

本项目聚焦个人项目完整度和核心功能，不包含 Docker、CI/CD、线上监控、备份等部署工程化内容。
