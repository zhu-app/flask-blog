<p align="center">
  <h1 align="center">✍️ Ink & Code</h1>
  <p align="center">全栈博客系统 — 当书写遇见代码</p>
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python"></a>
  <a href="https://flask.palletsprojects.com"><img src="https://img.shields.io/badge/Flask-3.0-black?logo=flask" alt="Flask"></a>
  <a href="https://mysql.com"><img src="https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql" alt="MySQL"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green" alt="License"></a>
</p>

---

## ✨ 功能特性

### 👤 用户端
| 功能 | 说明 |
|------|------|
| 📝 文章发布/编辑/删除 | 支持 Markdown 写作，实时预览，语法帮助 |
| 🔍 文章搜索 + 分类筛选 | 按关键词和分类快速定位 |
| 💬 评论系统 | 登录后可评论，作者可删除评论 |
| ❤️ 点赞功能 | 支持点赞/取消点赞 |
| 🖼️ 图片上传 | 支持在文章中插入图片 |
| 👤 个人主页 | 查看作者所有文章 |
| 🔐 双认证体系 | 网页用 Session，API 用 JWT Token |
| 🔑 密码修改 | 个人中心支持修改密码 |

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
- ✅ 评论所有权校验（评论作者、文章作者、管理员可删除）
- ✅ 防止 Session Fixation（登录时重置 session）
- ✅ 文件上传安全过滤（白名单扩展名 + 重命名）
- ✅ 统一的错误处理（JSON + HTML 双模式）

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.10+, Flask 3.0, Flask-JWT-Extended |
| **数据库** | MySQL 8.0+, SQLAlchemy ORM 2.0 |
| **前端** | HTML5, CSS3 (自定义设计系统), JavaScript (Fetch API), Jinja2 |
| **Markdown** | Python-Markdown (代码高亮 + 表格), Highlight.js, Marked.js |
| **字体** | Noto Serif SC (标题), JetBrains Mono (代码) |
| **API 文档** | Swagger UI (flasgger) |
| **数据库迁移** | Flask-Migrate (Alembic) |
| **测试** | pytest, pytest-flask (SQLite 内存数据库, 25个测试用例) |

---

## 🚀 快速开始

### 本地运行

#### 1. 安装依赖

推荐使用 `uv`（快速，项目自带 `uv.lock`）：

```bash
# 安装 uv（如果没有）
pip install uv

# 安装项目依赖
uv sync
```

或者使用 `pip`：

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

#### 4. 初始化并运行

```bash
# 初始化数据库（创建表 + 默认管理员账号 + 默认分类）
python init_db.py

# 启动服务
python app.py
```

访问 **http://localhost:5000** 🎉

---

## 🔑 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 👑 管理员 | `admin` | `123456` |

> ⚠️ 首次使用建议修改默认密码！

---

## 📖 使用指南

### 访问地址
- **博客首页**: http://localhost:5000
- **个人中心**: http://localhost:5000/dashboard
- **管理员后台**: http://localhost:5000/admin
- **API 文档**: http://localhost:5000/apidocs

### 写文章
1. 注册/登录账号
2. 点击导航栏「写文章」
3. 使用 Markdown 编写内容，❓ 按钮可查看语法帮助
4. 选择分类，点击发布

### 管理后台
1. 使用管理员账号登录（admin / 123456）
2. 访问 http://localhost:5000/admin
3. 管理用户、文章、评论、分类

---

## 🎨 设计系统

Ink & Code 使用 CSS 自定义属性构建的专属设计系统：

| Token | 值 | 用途 |
|-------|-----|------|
| `--primary` | `#4F46E5` | 靛蓝 — 按钮、链接、强调色 |
| `--accent` | `#F59E0B` | 琥珀 — 暖色点缀 |
| `--bg` | `#F8FAFC` | 浅灰 — 页面背景 |
| `--text` | `#1E293B` | 深灰 — 正文颜色 |
| `--font-ui` | `-apple-system, ...` | UI 字体 |
| `--font-display` | `'Noto Serif SC', serif` | 标题字体 |
| `--font-mono` | `'JetBrains Mono', monospace` | 等宽字体（代码） |

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
ink-and-code/
├── app.py                 # 应用工厂 + 错误处理
├── config.py              # 配置（环境变量 + 默认值）
├── init_db.py             # 数据库初始化脚本
├── pyproject.toml         # 项目元数据 + 依赖声明
├── requirements.txt       # Python 依赖
├── models/                # 数据模型层
│   ├── user.py            #   用户模型
│   ├── post.py            #   文章模型
│   ├── comment.py         #   评论模型
│   ├── category.py        #   分类模型
│   └── like.py            #   点赞模型
├── routes/                # 路由层（蓝图）
│   ├── auth.py            #   认证（注册/登录/登出）
│   ├── posts.py           #   文章（CRUD/搜索/点赞/个人中心）
│   ├── comments.py        #   评论
│   └── admin.py           #   管理员后台
├── utils/                 # 工具函数
│   └── __init__.py        #   权限装饰器
├── templates/             # Jinja2 模板
│   ├── index.html         #   首页
│   ├── post_detail.html   #   文章详情
│   ├── write_post.html    #   写文章/编辑（含Markdown帮助）
│   ├── login.html         #   登录
│   ├── register.html      #   注册
│   ├── dashboard.html     #   个人中心
│   ├── change_password.html # 修改密码
│   ├── user_profile.html  #   用户主页
│   ├── 404.html           #   404 页面
│   ├── 500.html           #   500 页面
│   └── admin/             #   管理后台模板
├── static/                # 静态资源
│   └── css/style.css      #   自定义设计系统
└── tests/                 # 测试
    ├── conftest.py        #   Fixtures
    ├── test_auth.py       #   认证测试
    ├── test_posts.py      #   文章测试
    ├── test_comments.py   #   评论测试
    └── test_likes.py      #   点赞测试
```

---

## 🧪 测试

```bash
# 运行全部测试
python -m pytest tests/ -v

# 运行测试 + 覆盖率
python -m pytest tests/ -v --cov=.

# 运行特定测试文件
python -m pytest tests/test_auth.py -v
```

---

<p align="center">
  <sub>Built with ❤️ using Flask & MySQL</sub>
</p>
