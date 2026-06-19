# 📝 Flask + MySQL 博客系统

一个完整的博客系统，包含前端页面、RESTful API、管理员后台和 Docker 部署。

## 功能特性

### 用户功能
- ✅ 用户注册/登录（密码加密存储）
- ✅ JWT Token 认证
- ✅ 文章发布、编辑、删除
- ✅ 文章搜索和分页
- ✅ 评论功能
- ✅ 文章点赞
- ✅ 文章分类
- ✅ 个人主页
- ✅ RSS 订阅
- ✅ 图片上传（Markdown 编辑器）

### 管理员功能
- ✅ 数据概览（用户数、文章数、评论数）
- ✅ 文章管理（查看、删除）
- ✅ 评论管理（查看、删除）
- ✅ 用户管理（切换管理员权限、删除用户）
- ✅ 分类管理（创建、删除）

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.10+, Flask, Flask-JWT-Extended |
| 数据库 | MySQL 8.0+ |
| ORM | SQLAlchemy |
| 前端 | HTML, CSS, JavaScript (Fetch API) |
| 模板引擎 | Jinja2 |
| Markdown | Python-Markdown |
| RSS | feedgen |

## 快速开始

### 方式一：本地运行

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置数据库

修改 `config.py` 中的数据库连接信息：

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://用户名:密码@localhost:3306/blog_db?charset=utf8mb4'
```

#### 3. 创建数据库

```sql
CREATE DATABASE blog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 4. 设置环境变量（可选）

```bash
# Windows (PowerShell)
$env:SECRET_KEY="your-secret-key"
$env:JWT_SECRET_KEY="your-jwt-secret"

# Linux/Mac
export SECRET_KEY="your-secret-key"
export JWT_SECRET_KEY="your-jwt-secret"
```

#### 5. 初始化并运行

```bash
# 初始化数据库表
python init_db.py

# 启动服务
python app.py
```

访问 http://localhost:5000

### 方式二：Docker 部署（推荐）

#### 1. 准备环境

确保已安装 Docker 和 Docker Compose。

#### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，修改 SECRET_KEY 和 JWT_SECRET_KEY
```

#### 3. 启动服务

```bash
docker-compose up -d
```

#### 4. 初始化数据库

```bash
docker-compose exec web python init_db.py
```

#### 5. 访问系统

- 博客首页：http://localhost:5000
- 管理员后台：http://localhost:5000/admin
- 数据库端口：3306

#### 6. 常用命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 进入容器
docker-compose exec web bash
```

## 默认测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `123456` |

## API 接口

### 认证 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/register` | 用户注册 |
| POST | `/api/login` | 用户登录 |

### 文章 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/posts` | 获取文章列表（支持分页、搜索、分类筛选） |
| GET | `/api/posts/<id>` | 获取文章详情 |
| POST | `/api/posts` | 创建文章（需登录） |
| PUT | `/api/posts/<id>` | 更新文章（需登录） |
| DELETE | `/api/posts/<id>` | 删除文章（需登录） |
| POST | `/api/posts/<id>/like` | 点赞/取消点赞（需登录） |

### 评论 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/posts/<id>/comments` | 获取文章评论 |
| POST | `/api/posts/<id>/comments` | 发表评论（需登录） |

### 分类 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/categories` | 获取所有分类 |
| POST | `/api/categories` | 创建分类（需登录） |

### 文件上传 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload` | 上传图片（需登录） |

### 管理员 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/admin` | 数据概览（需管理员） |
| GET | `/admin/users` | 用户列表（需管理员） |
| POST | `/admin/users/<id>/toggle-admin` | 切换管理员权限（需管理员） |
| POST | `/admin/users/<id>/delete` | 删除用户（需管理员） |
| GET | `/admin/posts` | 文章列表（需管理员） |
| POST | `/admin/posts/<id>/delete` | 删除文章（需管理员） |
| GET | `/admin/comments` | 评论列表（需管理员） |
| POST | `/admin/comments/<id>/delete` | 删除评论（需管理员） |
| GET | `/admin/categories` | 分类列表（需管理员） |
| POST | `/admin/categories/create` | 创建分类（需管理员） |
| POST | `/admin/categories/<id>/delete` | 删除分类（需管理员） |

## 项目结构

```
blog_full/
├── Dockerfile              # Docker 镜像定义
├── docker-compose.yml      # Docker Compose 配置
├── .env                    # 环境变量配置
├── .dockerignore           # Docker 忽略文件
├── app.py                  # 主应用入口
├── config.py               # 配置文件
├── init_db.py              # 数据库初始化
├── requirements.txt        # Python 依赖
├── README.md               # 项目文档
├── models/
│   └── user.py             # 数据模型 (User, Post, Comment, Category, Like)
├── routes/
│   ├── __init__.py
│   ├── auth.py             # 认证路由
│   ├── posts.py            # 文章路由
│   ├── comments.py         # 评论路由
│   └── admin.py            # 管理员路由
├── utils/
│   └── __init__.py         # 工具函数（权限检查等）
├── templates/              # HTML 模板
│   ├── index.html          # 首页
│   ├── post_detail.html    # 文章详情
│   ├── write_post.html     # 写文章/编辑
│   ├── login.html          # 登录页
│   ├── register.html       # 注册页
│   ├── user_profile.html   # 用户主页
│   └── admin/              # 管理员后台
│       ├── layout.html     # 后台布局
│       ├── dashboard.html  # 数据概览
│       ├── posts.html      # 文章管理
│       ├── users.html      # 用户管理
│       ├── comments.html   # 评论管理
│       └── categories.html # 分类管理
├── static/
│   └── css/
│       └── style.css       # 全局样式
│       └── admin.css       # 后台样式
└── uploads/                # 图片上传目录
```

## 数据库模型

```
User (用户)
├── id
├── username
├── email
├── password_hash
├── role (user/admin)
├── created_at
└── 关联: posts, comments, likes

Post (文章)
├── id
├── title
├── content
├── user_id (外键)
├── category_id (外键)
├── views
├── likes
├── created_at
├── updated_at
└── 关联: comments, author, category

Comment (评论)
├── id
├── content
├── post_id (外键)
├── user_id (外键)
├── created_at
└── 关联: post, author

Category (分类)
├── id
├── name
└── 关联: posts

Like (点赞)
├── id
├── user_id (外键)
├── post_id (外键)
├── created_at
└── 关联: user, post
```

## 安全说明

⚠️ **生产环境注意事项**：

1. **修改密钥**：务必修改 `.env` 中的 `SECRET_KEY` 和 `JWT_SECRET_KEY`
2. **数据库密码**：修改 MySQL 的 root 密码
3. **HTTPS**：生产环境应使用 HTTPS
4. **防火墙**：限制数据库端口访问
5. **日志**：配置日志记录
6. **备份**：定期备份数据库

## 许可证

MIT License
