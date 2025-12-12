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

### 任务 2: 数据模型实现 (2024-12-12)

#### 2.1 创建 Position 模型
- 创建 `app/models/position.py`
- 定义 `Position` 类：岗位招聘标准模型
  - 字段: `id` (UUID), `position`, `department`, `description`
  - 要求字段: `required_skills`, `optional_skills`, `min_experience`, `education`, `certifications`
  - 薪资字段: `salary_min`, `salary_max`
  - 其他: `project_requirements`, `is_active`, `resume_count`
  - 时间戳: `created_at`, `updated_at`
- 包含 `to_dict()` 方法用于序列化

#### 2.2 创建 Resume 模型
- 创建 `app/models/resume.py`
- 定义 `Resume` 类：统一简历模型（合并原 ResumeLibrary 和 ResumeData）
  - 原始简历信息: `filename`, `file_hash`, `file_size`, `file_type`, `content`
  - 候选人信息: `candidate_name`, `notes`
  - 状态标记: `is_screened`, `is_assigned`
  - 筛选结果: `position_title`, `position_details`, `screening_score`, `screening_summary`
  - 报告内容: `report_md_content`, `report_json_content`
  - 外键: `task_id`, `video_analysis_id`
- 包含 `to_library_dict()` 和 `to_screened_dict()` 方法

#### 2.3 创建 ScreeningTask 模型
- 创建 `app/models/screening.py`
- 定义 `TaskStatus` 枚举: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`
- 定义 `ScreeningTask` 类：简历初筛任务模型
  - 字段: `status`, `progress`, `current_step`, `total_steps`
  - 其他: `error_message`, `current_speaker`, `position_data`
- 包含 `to_dict()` 和 `to_status_dict()` 方法

#### 2.4 创建 VideoAnalysis 模型
- 创建 `app/models/video.py`
- 定义 `VideoStatus` 枚举: `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`
- 定义 `VideoAnalysis` 类：视频分析模型
  - 视频信息: `video_name`, `video_file_path`, `file_size`
  - 候选人信息: `candidate_name`, `position_applied`
  - 大五人格: `fraud_score`, `neuroticism_score`, `extraversion_score`, `openness_score`, `agreeableness_score`, `conscientiousness_score`
  - 其他: `status`, `error_message`, `confidence_score`, `summary`
- 包含 `analysis_result` 属性和 `to_dict()` 方法

#### 2.5 创建 InterviewSession 模型
- 创建 `app/models/interview.py`
- 定义 `InterviewSession` 类：面试辅助会话模型
  - 字段: `resume_id` (外键), `job_config` (JSON), `qa_records` (JSON数组)
  - 报告: `final_report` (JSON), `report_file_path`
- 包含 `current_round`, `is_completed` 属性
- 包含 `add_qa_record()` 方法

#### 2.6 创建 ComprehensiveAnalysis 模型
- 创建 `app/models/recommend.py`
- 定义 `ComprehensiveAnalysis` 类：候选人综合分析结果模型
  - 评估结果: `final_score`, `recommendation_level`, `recommendation_label`, `recommendation_action`
  - 详情: `dimension_scores` (JSON), `comprehensive_report`
  - 快照: `input_data_snapshot` (JSON)

#### 2.7 创建 ResumePositionAssignment 关联模型
- 在 `app/models/position.py` 中添加
- 定义 `ResumePositionAssignment` 类：简历-岗位分配中间表
  - 字段: `position_id`, `resume_id`, `assigned_at`, `notes`
- 支持多对多关系

#### 2.8 更新模型导出
- 更新 `app/models/__init__.py`：导出所有模型类
- 更新 `alembic/env.py`：导入所有模型以支持迁移
- 修复 Alembic 环境配置：使用同步引擎进行迁移

#### 2.9 生成数据库迁移
- 安装 alembic 依赖
- 运行 `alembic revision --autogenerate -m "create_all_models"`
- 生成迁移脚本 `5bfb82855472_create_all_models.py`
- 运行 `alembic upgrade head` 创建 7 张数据库表:
  - `positions`, `resumes`, `screening_tasks`, `video_analyses`
  - `interview_sessions`, `comprehensive_analyses`, `resume_position_assignments`

#### 2.10 编写属性测试
- 创建 `tests/test_models/__init__.py`
- 创建 `tests/test_models/test_uuid_consistency.py`:
  - **Property 10: UUID 格式一致性** - 验证所有模型 ID 为有效 UUID 格式
  - 7 个模型测试 + 2 个 Hypothesis 属性测试
- 更新 `tests/conftest.py`：导入所有模型
- 修复 `tests/test_api/test_response_format.py`：添加 `suppress_health_check`

#### 依赖安装
- 安装 `alembic >= 1.13.0`
- 安装 `pytest-asyncio >= 0.23.2`

#### 验证结果
- 测试: 23/23 通过
- 数据库: 7 张表成功创建
- 迁移: Alembic 迁移脚本正常工作

### 任务 3: 岗位管理 API (/api/positions/) (2024-12-12)

#### 3.1 创建岗位 Pydantic 模式
- 创建 `app/schemas/position.py`
- 定义请求模式:
  - `PositionBase`: 岗位基础字段
  - `PositionCreate`: 创建岗位请求
  - `PositionUpdate`: 更新岗位请求（所有字段可选）
  - `AssignResumesRequest`: 分配简历请求
  - `AIGenerateRequest`: AI 生成岗位要求请求
- 定义响应模式:
  - `PositionResponse`: 岗位详情响应
  - `PositionListData`: 岗位列表响应数据
  - `ResumeInPosition`: 岗位内的简历信息
  - `AssignResumesResponse`: 分配简历响应
  - `RemoveResumeResponse`: 移除简历响应
  - `AIGenerateResponse`: AI 生成结果响应

#### 3.2 实现岗位列表和创建 API
- 创建 `app/api/positions.py`
- 实现 `GET /api/positions/`:
  - 支持 `include_resumes` 参数控制是否返回分配的简历
  - 使用 `selectinload` 优化关联查询
  - 返回 `{positions: [], total: n}` 格式
- 实现 `POST /api/positions/`:
  - 验证岗位名称不能重复
  - 处理 `salary_range` 数组转换为 `salary_min/salary_max`
  - 成功返回 code 201

#### 3.3 实现岗位详情、更新、删除 API
- 实现 `GET /api/positions/{position_id}/`:
  - 支持 `include_resumes` 参数（默认 true）
  - 不存在返回 404
- 实现 `PUT /api/positions/{position_id}/`:
  - 使用 `model_dump(exclude_unset=True)` 仅更新提供的字段
  - 正确处理 `salary_range` 数组更新
- 实现 `DELETE /api/positions/{position_id}/`:
  - 软删除（设置 `is_active=False`）
  - 删除后无法再查询到该岗位

#### 3.4 实现简历分配和移除 API
- 实现 `POST /api/positions/{position_id}/resumes/`:
  - 接受 `resume_data_ids` 数组批量分配
  - 跳过已分配的简历，统计 `assigned_count` 和 `skipped_count`
  - 更新简历的 `is_assigned` 状态
  - 先 flush 新记录再查询总数确保计数准确
- 实现 `DELETE /api/positions/{position_id}/resumes/{resume_id}/`:
  - 删除分配记录
  - 检查简历是否还有其他岗位分配，更新 `is_assigned` 状态
  - 修复计数逻辑：先 flush 删除操作再查询真实计数

#### 3.5 实现 AI 生成岗位要求 API
- 实现 `POST /api/positions/ai/generate/`:
  - 接受 `description` 和 `documents` 参数
  - 当前为模拟实现，返回基于输入的示例数据
  - 预留 AI 服务集成接口（待任务 11 完善）

#### 3.6 编写属性测试
- 创建 `tests/test_api/test_positions.py`
- 测试类 `TestPositionListAndCreate` (4 个测试):
  - 获取空岗位列表
  - 成功创建岗位
  - 最小数据创建岗位
  - 创建重复岗位失败
- 测试类 `TestPositionDetail` (4 个测试):
  - 获取岗位详情
  - 获取不存在的岗位
  - 更新岗位
  - 删除岗位
- 测试类 `TestPositionResumeAssignment` (3 个测试):
  - 分配简历到岗位
  - 重复分配简历被跳过
  - 从岗位移除简历
- 测试类 `TestAIGeneratePosition` (2 个测试):
  - AI 生成岗位要求
  - 空描述调用失败
- 测试类 `TestProperty5PositionQueryable` (2 个测试):
  - **Property 5: 岗位创建后可查询** - 验证需求 2.2, 2.3
  - 创建多个岗位，所有岗位都可查询

#### 3.7 注册路由
- 更新 `app/main.py`:
  - 导入 `app.api.positions` 模块
  - 注册路由 `prefix="/api/positions"`, `tags=["岗位管理"]`

#### Bug 修复
- 修复 `app/api/positions.py` 中的依赖导入:
  - 将 `from app.api.deps import get_db` 改为 `from app.database import get_db`
  - 确保与测试配置中的依赖覆盖一致
- 修复简历分配计数逻辑:
  - 问题: 分配时计算已有数量再加新数量导致重复计数
  - 解决: 先 flush 新记录，再查询数据库获取真实总数
- 修复简历移除计数逻辑:
  - 问题: 使用内存中的旧值减 1 导致计数不准确
  - 解决: 先 flush 删除操作，再查询数据库获取真实总数

#### 验证结果
- 测试: 38/38 通过 (新增 15 个岗位 API 测试)
- API 端点: 8 个岗位管理端点全部实现
- 与 Django 后端兼容: 响应格式和字段与原有 API 保持一致
