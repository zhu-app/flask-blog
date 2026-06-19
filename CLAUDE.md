# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A full-featured Flask + MySQL blog system with user-facing blog pages, RESTful API, admin dashboard, and Docker deployment.

## Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database and create default admin account (admin / 123456)
python init_db.py

# Run development server
python app.py

# Run tests (25 tests covering auth, posts, comments, likes)
python -m pytest tests/ -v

# Run tests with coverage report
python -m pytest tests/ -v --tb=short

# Database migration (after model changes)
flask db init           # first time only
flask db migrate -m "description"
flask db upgrade

# Run with Docker
docker-compose up -d

# Initialize DB in Docker
docker-compose exec web python init_db.py

# View logs
docker-compose logs -f

# Shutdown
docker-compose down
```

### API Documentation

```bash
# Swagger UI available at:
# http://localhost:5000/apidocs
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `your-secret-key-change-in-production` | Flask session key |
| `JWT_SECRET_KEY` | `jwt-secret-key-change-in-production` | JWT signing key |
| `DATABASE_URL` | `mysql+pymysql://root:123456@localhost:3306/blog_db?charset=utf8mb4` | MySQL connection string |

### Key URLs

- Blog home: http://localhost:5000
- Admin dashboard: http://localhost:5000/admin
- Swagger API docs: http://localhost:5000/apidocs
- RSS feed: http://localhost:5000/feed

## Architecture and Code Structure

### Authentication Model (Dual Auth)

Uses **both Flask Session (web pages) and JWT (API)** simultaneously:

- **Web routes**: use `@login_required_web` from `utils/__init__.py` — checks `session['user_id']`
- **API routes**: use `@login_required_api` — wraps `@jwt_required()` from flask-jwt-extended to verify JWT Bearer token
- **Admin routes**: use `@admin_required` wrapper (in `routes/admin.py`) — chains `@login_required_web` + checks `user.role == 'admin'`

### Application Factory

`app.py` uses `create_app(config_class=None)` factory pattern. Accepts optional config class for testing (uses SQLite in-memory). Registers 4 blueprints:

| Blueprint | Prefix | Handles |
|-----------|--------|---------|
| `auth` | none | `/api/register`, `/api/login`, `/register`, `/login`, `/logout`, `/user/<username>` |
| `posts` | none | `/`, `/post/<id>`, `/write`, `/edit/<id>`, `/feed`, all `/api/posts/*`, `/api/categories/*`, `/api/upload` |
| `comments` | none | `/post/<id>/comment`, `/api/posts/<id>/comments/*` |
| `admin` | `/admin` | Admin dashboard, user/post/comment/category management |

Factory also sets up:
- `setup_logging(app)` — console logging + file handler (production only)
- `register_error_handlers(app)` — unified 400/403/404/405/500 handlers (JSON vs HTML based on `request.is_json`)
- Swagger UI via flasgger
- Flask-Migrate for Alembic migrations

### Data Models

Models split into individual files under `models/`:

- `models/__init__.py` — exports `db`, re-exports all models (`User`, `Category`, `Post`, `Comment`, `Like`)
- **User** — `id`, `username`, `email`, `password_hash`, `role` (user/admin), `created_at`. Has `set_password()`/`check_password()` methods using Werkzeug. Type-annotated properties: `post_count`, `comment_count`.
- **Post** — `id`, `title`, `content`, `user_id`, `category_id`, `views`, `likes`, timestamps. Content is raw Markdown.
- **Comment** — `id`, `content`, `post_id`, `user_id`, `created_at`.
- **Category** — `id`, `name`.
- **Like** — `id`, `user_id`, `post_id`, `created_at`. Has `UniqueConstraint` on `(user_id, post_id)`.

Relationships: User has-many Posts, Comments, Likes. Post has-many Comments, Likes, belongs-to User and Category.

### Route Design Pattern

Every feature has both an **API endpoint** (JSON, JWT-protected) and a **web page route** (template-rendered, session-protected), e.g.:

- `POST /api/posts` ↔ `POST /publish` (web form)
- `GET /api/posts/<id>` ↔ `GET /post/<id>` (web detail page)

### Error Handling

`register_error_handlers(app)` in `app.py` provides unified error handling:
- Detects JSON requests vs HTML requests via `request.is_json`
- JSON requests get structured `{'success': False, 'message': ...}` responses
- HTML requests get flash messages + redirects, or error pages (404.html, 500.html)

### Markdown Rendering

Post content is stored as raw Markdown. Rendering happens in `posts.post_detail()` using `markdown.markdown()` with extensions: `fenced_code`, `codehilite`, `tables`, `nl2br`.

### Admin Permissions

`admin.py` defines an `@admin_required` decorator that chains with `@login_required_web` and checks `user.role == 'admin'`.

### Deployment

- `Dockerfile`: Python 3.10-slim, installs deps, runs `python app.py`
- `docker-compose.yml`: web service + MySQL 8.0 service with persisted volume
- `config.py`: reads `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET_KEY` from env vars with fallback defaults (warns on defaults)
- Default admin account is created by `init_db.py`: `admin / 123456`

### File Uploads

Uploaded images go to `uploads/` directory. Served via `@app.route('/uploads/<path:filename>')`. Filenames are sanitized with `secure_filename` and deduplicated with timestamps.

### Testing

Tests in `tests/` directory use SQLite in-memory database via `TestConfig`. Fixtures in `conftest.py`:
- `app` (session) — creates Flask app with test config
- `client` (function) — Flask test client
- `auth_headers` (function) — creates user + returns JWT auth headers
- `admin_headers` (function) — creates admin user + returns JWT auth headers
- `sample_post` (function) — creates a post via API for use in tests

Test files: `test_auth.py` (7 tests), `test_posts.py` (9 tests), `test_comments.py` (4 tests), `test_likes.py` (4 tests). Total: 25 tests.
