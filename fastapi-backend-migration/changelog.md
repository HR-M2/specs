# 变更日志

## [0.1.0] - 2024-12-12

### 任务 1: 项目初始化和基础架构

#### 1.1 创建项目目录结构
- 创建 `HRM2-FastAPI-Backend/` 主目录
- 创建子目录: `app/`, `tests/`, `media/`, `alembic/`
- 创建 `app/` 子模块: `models/`, `schemas/`, `api/`, `services/`, `utils/`
- 创建媒体子目录: `media/screening_reports/`, `media/interview_reports/`, `media/videos/`
- 创建 `requirements.txt` (使用 >= 版本约束)
- 创建 `.env.example` 环境变量模板
- 创建 `README.md` 项目文档

#### 1.2 配置 FastAPI 应用入口
- 创建 `app/main.py`: FastAPI 实例、生命周期管理
- 配置 CORS 中间件 (支持前端跨域)
- 配置静态文件服务 (`/media` 路由)
- 配置 Swagger UI 文档路径 `/api/docs/`
- 实现健康检查端点 `/` 和 `/health`

#### 1.3 配置数据库连接
- 创建 `app/config.py`: 基于 pydantic-settings 的配置管理
- 创建 `app/database.py`: SQLAlchemy 2.0 异步引擎和会话工厂
- 创建 `app/api/deps.py`: 数据库会话依赖注入
- 配置 Alembic 数据库迁移:
  - `alembic.ini` 配置文件
  - `alembic/env.py` 异步迁移环境
  - `alembic/script.py.mako` 迁移脚本模板
  - `alembic/versions/` 迁移版本目录

#### 1.4 创建统一响应格式
- 创建 `app/schemas/common.py`:
  - `ApiResponse[T]` 泛型响应模型
  - `PaginatedResponse[T]` 分页响应模型
  - `ErrorResponse` 错误响应模型
  - `ResponseCode` 响应码常量
- 创建 `app/utils/response.py`:
  - `success_response()` 成功响应 (200)
  - `created_response()` 创建成功响应 (201)
  - `accepted_response()` 异步处理响应 (202)
  - `error_response()` 错误响应
  - `ApiException` 自定义异常类

#### 1.5 编写属性测试
- 创建 `pytest.ini` 测试配置
- 创建 `tests/conftest.py` 测试 fixtures (异步数据库、测试客户端)
- 创建 `tests/test_api/test_response_format.py`:
  - **Property 1: 统一响应格式** - 验证响应包含 code, message, data 字段
  - **Property 2: 成功响应码范围** - 验证成功码在 [200, 201, 202] 范围内
  - 共 14 个测试用例，全部通过

#### 依赖安装
安装的主要依赖:
- fastapi >= 0.104.1
- uvicorn[standard] >= 0.24.0
- sqlalchemy[asyncio] >= 2.0.23
- pydantic >= 2.5.2
- alembic >= 1.13.0
- pytest >= 7.4.3
- hypothesis >= 6.92.1

#### 验证结果
- 测试: 14/14 通过
- 服务器: 成功启动在 http://127.0.0.1:8000
- API 文档: http://127.0.0.1:8000/api/docs/

#### 1.6 Git 仓库初始化与配置完善 (2024-12-12)
- 创建 `.gitignore` 文件:
  - Python 编译文件 (`__pycache__/`, `*.pyc`)
  - 虚拟环境 (`.env`, `venv/`)
  - 测试缓存 (`.pytest_cache/`, `.hypothesis/`)
  - IDE 文件 (`.idea/`, `.vscode/`)
  - 数据库文件 (`*.db`, `*.sqlite3`)
  - Media 目录内容（保留 `.gitkeep`）
  - Alembic 迁移脚本（保留 `.gitkeep`）
- 完善 `.env.example` 配置:
  - 新增基础配置: `APP_ENV`, `SECRET_KEY`
  - 新增 LLM 配置: `LLM_MODEL`, `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_TEMPERATURE`, `LLM_TIMEOUT`
  - 新增 Embedding 配置: `EMBEDDING_MODEL`, `EMBEDDING_API_KEY`, `EMBEDDING_BASE_URL`
  - 移除 Celery 配置（经验证 Django 后端实际使用 threading 而非 Celery）
- 更新 `app/config.py` Settings 类与 `.env.example` 保持同步
- 初始化 Git 仓库并推送到 https://github.com/HR-M2/HRM2-FastAPI-Backend
