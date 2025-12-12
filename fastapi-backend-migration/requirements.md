# Requirements Document

## Introduction

本项目旨在创建一个全新的 FastAPI 后端项目，完全替代现有的 Django 后端（HRM2-Django-Backend）功能。新后端必须与现有 Vue 前端（HRM2-Vue-Frontend_new）完全兼容，确保前端零改动即可正常工作。

核心目标：
- 保持 API 完全兼容（URL、方法、请求/响应格式）
- 自由设计优化的数据库结构
- 独立项目目录，不修改原 Django 项目

## Glossary

- **HRM_FastAPI_System**: 新建的 FastAPI 后端系统
- **API_Response**: 统一响应格式 `{code: number, message: string, data: T}`
- **Position**: 岗位招聘标准，包含职位名称、技能要求、经验要求等
- **ResumeLibrary**: 简历库，存储上传的原始简历
- **ResumeData**: 筛选后的简历数据，包含评分和分析结果
- **ScreeningTask**: 简历筛选任务，异步处理简历评估
- **InterviewSession**: 面试辅助会话，记录问答和评估
- **VideoAnalysis**: 视频分析记录，存储面试视频分析结果
- **ComprehensiveAnalysis**: 综合分析结果，多维度候选人评估

## Requirements

### Requirement 1: API 响应格式兼容

**User Story:** As a 前端开发者, I want 后端返回统一的响应格式, so that 前端无需修改即可正常解析数据。

#### Acceptance Criteria

1. WHEN 任何 API 请求成功 THEN THE HRM_FastAPI_System SHALL 返回格式为 `{code: 200|201|202, message: string, data: T}` 的 JSON 响应
2. WHEN 任何 API 请求失败 THEN THE HRM_FastAPI_System SHALL 返回格式为 `{code: number, message: string, data: null}` 的 JSON 响应，其中 code 为非 200/201/202 的错误码
3. WHEN 返回分页数据 THEN THE HRM_FastAPI_System SHALL 在 data 字段中包含 `{items: T[], total: number, page: number, page_size: number}` 结构

### Requirement 2: 岗位管理 API

**User Story:** As a HR 用户, I want 管理岗位招聘标准, so that 可以定义和维护不同岗位的要求。

#### Acceptance Criteria

1. WHEN 客户端发送 GET 请求到 `/api/positions/` THEN THE HRM_FastAPI_System SHALL 返回岗位列表，包含 `{positions: Position[], total: number}`
2. WHEN 客户端发送 POST 请求到 `/api/positions/` 并提供岗位数据 THEN THE HRM_FastAPI_System SHALL 创建新岗位并返回创建的岗位对象
3. WHEN 客户端发送 GET 请求到 `/api/positions/{position_id}/` THEN THE HRM_FastAPI_System SHALL 返回指定岗位的详细信息
4. WHEN 客户端发送 PUT 请求到 `/api/positions/{position_id}/` THEN THE HRM_FastAPI_System SHALL 更新岗位信息并返回更新后的对象
5. WHEN 客户端发送 DELETE 请求到 `/api/positions/{position_id}/` THEN THE HRM_FastAPI_System SHALL 软删除岗位（设置 is_active=false）
6. WHEN 客户端发送 POST 请求到 `/api/positions/{position_id}/resumes/` 并提供 resume_data_ids THEN THE HRM_FastAPI_System SHALL 将简历分配到岗位并返回分配结果
7. WHEN 客户端发送 DELETE 请求到 `/api/positions/{position_id}/resumes/{resume_id}/` THEN THE HRM_FastAPI_System SHALL 从岗位移除指定简历
8. WHEN 客户端发送 POST 请求到 `/api/positions/ai/generate/` 并提供描述 THEN THE HRM_FastAPI_System SHALL 调用 AI 生成岗位要求并返回生成的岗位数据

### Requirement 3: 简历库 API

**User Story:** As a HR 用户, I want 管理简历库, so that 可以上传、查看和管理候选人简历。

#### Acceptance Criteria

1. WHEN 客户端发送 GET 请求到 `/api/library/` THEN THE HRM_FastAPI_System SHALL 返回简历库列表，支持分页和筛选参数（page, page_size, keyword, is_screened, is_assigned）
2. WHEN 客户端发送 POST 请求到 `/api/library/` 并提供简历数组 THEN THE HRM_FastAPI_System SHALL 上传简历并返回 `{uploaded: [], skipped: [], uploaded_count, skipped_count}`
3. WHEN 客户端发送 GET 请求到 `/api/library/{id}/` THEN THE HRM_FastAPI_System SHALL 返回简历详情
4. WHEN 客户端发送 PUT 请求到 `/api/library/{id}/` THEN THE HRM_FastAPI_System SHALL 更新简历信息（candidate_name, notes）
5. WHEN 客户端发送 DELETE 请求到 `/api/library/{id}/` THEN THE HRM_FastAPI_System SHALL 删除指定简历
6. WHEN 客户端发送 POST 请求到 `/api/library/batch-delete/` 并提供 resume_ids THEN THE HRM_FastAPI_System SHALL 批量删除简历
7. WHEN 客户端发送 POST 请求到 `/api/library/check-hash/` 并提供 hashes 数组 THEN THE HRM_FastAPI_System SHALL 返回 `{exists: Record<string, boolean>, existing_count: number}`

### Requirement 4: 简历筛选 API

**User Story:** As a HR 用户, I want 提交简历筛选任务, so that AI 可以自动评估候选人与岗位的匹配度。

#### Acceptance Criteria

1. WHEN 客户端发送 POST 请求到 `/api/screening/` 并提供 position 和 resumes THEN THE HRM_FastAPI_System SHALL 创建筛选任务并返回任务对象
2. WHEN 客户端发送 GET 请求到 `/api/screening/tasks/` THEN THE HRM_FastAPI_System SHALL 返回任务历史列表，支持 status、page、page_size 参数
3. WHEN 客户端发送 GET 请求到 `/api/screening/tasks/{task_id}/status/` THEN THE HRM_FastAPI_System SHALL 返回任务状态和进度信息
4. WHEN 客户端发送 DELETE 请求到 `/api/screening/tasks/{task_id}/` THEN THE HRM_FastAPI_System SHALL 删除指定任务
5. WHEN 客户端发送 GET 请求到 `/api/screening/reports/{report_id}/` THEN THE HRM_FastAPI_System SHALL 返回简历筛选报告详情
6. WHEN 客户端发送 GET 请求到 `/api/screening/reports/{report_id}/download/` THEN THE HRM_FastAPI_System SHALL 返回 Markdown 格式的报告文件
7. WHEN 客户端发送 GET 请求到 `/api/screening/data/` THEN THE HRM_FastAPI_System SHALL 返回筛选后的简历数据列表
8. WHEN 客户端发送 POST 请求到 `/api/screening/data/` THEN THE HRM_FastAPI_System SHALL 创建新的简历数据记录

### Requirement 5: 简历组管理 API

**User Story:** As a HR 用户, I want 管理简历组, so that 可以组织和分类筛选后的简历。

#### Acceptance Criteria

1. WHEN 客户端发送 GET 请求到 `/api/screening/groups/` THEN THE HRM_FastAPI_System SHALL 返回简历组列表
2. WHEN 客户端发送 POST 请求到 `/api/screening/groups/create/` THEN THE HRM_FastAPI_System SHALL 创建新的简历组
3. WHEN 客户端发送 GET 请求到 `/api/screening/groups/{group_id}/` THEN THE HRM_FastAPI_System SHALL 返回简历组详情
4. WHEN 客户端发送 POST 请求到 `/api/screening/groups/add-resume/` THEN THE HRM_FastAPI_System SHALL 向简历组添加简历
5. WHEN 客户端发送 POST 请求到 `/api/screening/groups/remove-resume/` THEN THE HRM_FastAPI_System SHALL 从简历组移除简历
6. WHEN 客户端发送 POST 请求到 `/api/screening/groups/set-status/` THEN THE HRM_FastAPI_System SHALL 更新简历组状态

### Requirement 6: 视频分析 API

**User Story:** As a HR 用户, I want 上传和分析面试视频, so that 可以获取候选人的行为分析结果。

#### Acceptance Criteria

1. WHEN 客户端发送 GET 请求到 `/api/videos/` THEN THE HRM_FastAPI_System SHALL 返回视频分析列表
2. WHEN 客户端发送 POST 请求到 `/api/videos/upload/` 并提供视频文件 THEN THE HRM_FastAPI_System SHALL 上传视频并创建分析任务
3. WHEN 客户端发送 GET 请求到 `/api/videos/{video_id}/status/` THEN THE HRM_FastAPI_System SHALL 返回视频分析状态和结果
4. WHEN 客户端发送 POST 请求到 `/api/videos/{video_id}/` THEN THE HRM_FastAPI_System SHALL 更新视频分析结果
5. WHEN 客户端发送 POST 请求到 `/api/screening/videos/link/` THEN THE HRM_FastAPI_System SHALL 建立简历与视频分析的关联
6. WHEN 客户端发送 POST 请求到 `/api/screening/videos/unlink/` THEN THE HRM_FastAPI_System SHALL 解除简历与视频分析的关联

### Requirement 7: 面试辅助 API

**User Story:** As a 面试官, I want 使用 AI 辅助面试, so that 可以获取智能问题建议和回答评估。

#### Acceptance Criteria

1. WHEN 客户端发送 POST 请求到 `/api/interviews/sessions/` 并提供 resume_data_id THEN THE HRM_FastAPI_System SHALL 创建面试会话并返回会话对象
2. WHEN 客户端发送 GET 请求到 `/api/interviews/sessions/` THEN THE HRM_FastAPI_System SHALL 返回会话列表，支持 resume_id 筛选
3. WHEN 客户端发送 GET 请求到 `/api/interviews/sessions/{session_id}/` THEN THE HRM_FastAPI_System SHALL 返回会话详情
4. WHEN 客户端发送 DELETE 请求到 `/api/interviews/sessions/{session_id}/` THEN THE HRM_FastAPI_System SHALL 结束并删除会话
5. WHEN 客户端发送 POST 请求到 `/api/interviews/sessions/{session_id}/questions/` THEN THE HRM_FastAPI_System SHALL 生成面试问题并返回问题池
6. WHEN 客户端发送 POST 请求到 `/api/interviews/sessions/{session_id}/qa/` THEN THE HRM_FastAPI_System SHALL 记录问答并返回评估结果和候选问题
7. WHEN 客户端发送 POST 请求到 `/api/interviews/sessions/{session_id}/report/` THEN THE HRM_FastAPI_System SHALL 生成最终面试报告

### Requirement 8: 最终推荐 API

**User Story:** As a HR 用户, I want 获取候选人综合分析, so that 可以做出最终录用决策。

#### Acceptance Criteria

1. WHEN 客户端发送 GET 请求到 `/api/recommend/stats/` THEN THE HRM_FastAPI_System SHALL 返回已分析候选人统计数据
2. WHEN 客户端发送 POST 请求到 `/api/recommend/analysis/{resume_id}/` THEN THE HRM_FastAPI_System SHALL 执行综合分析并返回分析结果
3. WHEN 客户端发送 GET 请求到 `/api/recommend/analysis/{resume_id}/` THEN THE HRM_FastAPI_System SHALL 返回候选人的历史分析结果

### Requirement 9: 开发测试工具 API

**User Story:** As a 开发者, I want 使用测试工具 API, so that 可以生成测试数据和调试系统。

#### Acceptance Criteria

1. WHEN 客户端发送 POST 请求到 `/api/screening/dev/generate-resumes/` 并提供 position 和 count THEN THE HRM_FastAPI_System SHALL 生成随机简历并添加到简历库
2. WHEN 客户端发送 GET/POST 请求到 `/api/screening/dev/force-error/` THEN THE HRM_FastAPI_System SHALL 控制是否强制筛选任务失败
3. WHEN 客户端发送 POST 请求到 `/api/screening/dev/reset-state/` THEN THE HRM_FastAPI_System SHALL 清除所有测试相关的缓存和状态

### Requirement 10: 数据库设计

**User Story:** As a 系统架构师, I want 设计优化的数据库结构, so that 系统具有良好的性能和可维护性。

#### Acceptance Criteria

1. THE HRM_FastAPI_System SHALL 使用 SQLAlchemy 作为 ORM 框架
2. THE HRM_FastAPI_System SHALL 使用 UUID 作为所有表的主键
3. THE HRM_FastAPI_System SHALL 为所有表添加 created_at 和 updated_at 时间戳字段
4. THE HRM_FastAPI_System SHALL 使用 JSON 字段存储复杂的嵌套数据结构
5. THE HRM_FastAPI_System SHALL 为常用查询字段创建数据库索引
6. THE HRM_FastAPI_System SHALL 支持 SQLite（开发）和 PostgreSQL（生产）数据库

### Requirement 11: 项目结构和配置

**User Story:** As a 开发者, I want 清晰的项目结构, so that 代码易于理解和维护。

#### Acceptance Criteria

1. THE HRM_FastAPI_System SHALL 创建独立的项目目录 `HRM2-FastAPI-Backend`
2. THE HRM_FastAPI_System SHALL 使用 Python 3.10+ 和 FastAPI 框架
3. THE HRM_FastAPI_System SHALL 使用 Pydantic 进行数据验证
4. THE HRM_FastAPI_System SHALL 使用环境变量管理配置（.env 文件）
5. THE HRM_FastAPI_System SHALL 提供 requirements.txt 依赖文件
6. THE HRM_FastAPI_System SHALL 保持与 Django 后端相同的端口配置（默认 8000）

### Requirement 12: 异步任务处理

**User Story:** As a 系统用户, I want 长时间任务异步执行, so that 系统响应保持流畅。

#### Acceptance Criteria

1. WHEN 提交简历筛选任务 THEN THE HRM_FastAPI_System SHALL 异步执行 AI 分析，立即返回任务 ID
2. WHEN 提交视频分析任务 THEN THE HRM_FastAPI_System SHALL 异步执行分析，立即返回任务 ID
3. WHEN 生成面试问题或报告 THEN THE HRM_FastAPI_System SHALL 支持同步执行（带超时配置）
4. THE HRM_FastAPI_System SHALL 使用后台任务或任务队列处理异步操作

### Requirement 13: 文件处理

**User Story:** As a 用户, I want 上传和下载文件, so that 可以管理简历和报告文件。

#### Acceptance Criteria

1. WHEN 上传简历文件 THEN THE HRM_FastAPI_System SHALL 解析文件内容并存储
2. WHEN 上传视频文件 THEN THE HRM_FastAPI_System SHALL 保存文件到 media 目录
3. WHEN 下载报告 THEN THE HRM_FastAPI_System SHALL 返回正确的 Content-Disposition 头，包含 UTF-8 编码的文件名
4. THE HRM_FastAPI_System SHALL 使用 media 目录存储上传的文件

### Requirement 14: AI 服务集成

**User Story:** As a 系统, I want 集成 AI 服务, so that 可以提供智能分析功能。

#### Acceptance Criteria

1. THE HRM_FastAPI_System SHALL 提供 AI 服务接口抽象层
2. THE HRM_FastAPI_System SHALL 支持配置 AI 服务端点和 API 密钥
3. WHEN AI 服务不可用 THEN THE HRM_FastAPI_System SHALL 返回适当的错误信息
4. THE HRM_FastAPI_System SHALL 为 AI 调用设置合理的超时时间（60-120秒）
