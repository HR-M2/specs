# 需求文档

## 简介

本项目旨在创建一个全新的 FastAPI 后端项目，完全替代现有的 Django 后端（HRM2-Django-Backend）功能。新后端必须保持与现有 Vue 前端（HRM2-Vue-Frontend_new）的完全兼容，确保前端零改动即可切换后端。

## 术语表

- **HRM_System**: 智能招聘管理系统（Human Resource Management System）
- **FastAPI_Backend**: 基于 FastAPI 框架的新后端服务
- **API_Endpoint**: 后端提供的 HTTP 接口端点
- **Resume**: 简历，候选人的求职文档
- **Position**: 岗位，招聘职位及其要求标准
- **Screening**: 筛选，对简历进行 AI 初步评估的过程
- **Interview_Session**: 面试会话，面试辅助系统中的一次面试记录
- **Resume_Data**: 筛选后的简历数据，包含 AI 分析结果
- **Resume_Group**: 简历组，用于批量管理筛选后的简历
- **Video_Analysis**: 视频分析，对面试视频进行 AI 分析（预留功能）
- **Comprehensive_Analysis**: 综合分析，对候选人进行最终评估推荐

## 需求

### 需求 1

**用户故事:** 作为前端开发者，我希望新后端保持与现有 API 完全兼容，以便无需修改前端代码即可切换后端。

#### 验收标准

1. WHEN 前端调用任意 API 端点 THEN FastAPI_Backend SHALL 返回与 Django 后端相同结构的 JSON 响应
2. WHEN 前端发送请求 THEN FastAPI_Backend SHALL 接受相同的请求参数格式和数据结构
3. THE FastAPI_Backend SHALL 保持所有 49 个 API 端点的 URL 路径与 Django 后端完全一致
4. THE FastAPI_Backend SHALL 使用统一的响应格式 `{code: number, message: string, data: any}`
5. WHEN 业务操作成功 THEN FastAPI_Backend SHALL 返回 code 为 200、201 或 202
6. WHEN 业务操作失败 THEN FastAPI_Backend SHALL 返回对应的错误 code 和 message

### 需求 2

**用户故事:** 作为系统管理员，我希望能够管理岗位设置，以便定义招聘标准和要求。

#### 验收标准

1. WHEN 用户请求 GET /api/positions/ THEN FastAPI_Backend SHALL 返回岗位列表，包含 positions 数组和 total 计数
2. WHEN 用户请求 POST /api/positions/ 并提供岗位数据 THEN FastAPI_Backend SHALL 创建新岗位并返回岗位详情
3. WHEN 用户请求 GET /api/positions/{position_id}/ THEN FastAPI_Backend SHALL 返回指定岗位的详细信息
4. WHEN 用户请求 PUT /api/positions/{position_id}/ THEN FastAPI_Backend SHALL 更新岗位信息
5. WHEN 用户请求 DELETE /api/positions/{position_id}/ THEN FastAPI_Backend SHALL 软删除岗位
6. WHEN 用户请求 POST /api/positions/{position_id}/resumes/ THEN FastAPI_Backend SHALL 将简历分配到指定岗位
7. WHEN 用户请求 DELETE /api/positions/{position_id}/resumes/{resume_id}/ THEN FastAPI_Backend SHALL 从岗位移除指定简历
8. WHEN 用户请求 POST /api/positions/ai/generate/ THEN FastAPI_Backend SHALL 调用 AI 生成岗位要求

### 需求 3

**用户故事:** 作为 HR 人员，我希望能够管理简历库，以便集中存储和检索候选人简历。

#### 验收标准

1. WHEN 用户请求 GET /api/library/ THEN FastAPI_Backend SHALL 返回分页的简历列表，支持 keyword、is_screened、is_assigned 筛选参数
2. WHEN 用户请求 POST /api/library/ 并上传简历 THEN FastAPI_Backend SHALL 存储简历并返回上传结果，包含 uploaded 和 skipped 列表
3. WHEN 用户请求 GET /api/library/{id}/ THEN FastAPI_Backend SHALL 返回简历详情
4. WHEN 用户请求 PUT /api/library/{id}/ THEN FastAPI_Backend SHALL 更新简历信息
5. WHEN 用户请求 DELETE /api/library/{id}/ THEN FastAPI_Backend SHALL 删除简历
6. WHEN 用户请求 POST /api/library/batch-delete/ THEN FastAPI_Backend SHALL 批量删除指定简历
7. WHEN 用户请求 POST /api/library/check-hash/ THEN FastAPI_Backend SHALL 检查文件哈希值是否已存在，防止重复上传

### 需求 4

**用户故事:** 作为 HR 人员，我希望能够提交简历筛选任务，以便 AI 自动评估候选人与岗位的匹配度。

#### 验收标准

1. WHEN 用户请求 POST /api/screening/ 并提供岗位和简历数据 THEN FastAPI_Backend SHALL 创建筛选任务并返回任务信息
2. WHEN 用户请求 GET /api/screening/tasks/ THEN FastAPI_Backend SHALL 返回任务历史列表，支持 status、page、page_size 参数
3. WHEN 用户请求 GET /api/screening/tasks/{task_id}/status/ THEN FastAPI_Backend SHALL 返回任务状态和结果
4. WHEN 用户请求 DELETE /api/screening/tasks/{task_id}/ THEN FastAPI_Backend SHALL 删除指定任务
5. WHEN 用户请求 GET /api/screening/reports/{report_id}/ THEN FastAPI_Backend SHALL 返回筛选报告详情
6. WHEN 用户请求 GET /api/screening/reports/{report_id}/download/ THEN FastAPI_Backend SHALL 返回可下载的 Markdown 报告文件
7. WHEN 用户请求 GET /api/screening/data/ THEN FastAPI_Backend SHALL 返回筛选后的简历数据列表

### 需求 5

**用户故事:** 作为 HR 人员，我希望能够管理简历组，以便对筛选后的简历进行分类管理。

#### 验收标准

1. WHEN 用户请求 GET /api/screening/groups/ THEN FastAPI_Backend SHALL 返回简历组列表
2. WHEN 用户请求 POST /api/screening/groups/create/ THEN FastAPI_Backend SHALL 创建新的简历组
3. WHEN 用户请求 GET /api/screening/groups/{group_id}/ THEN FastAPI_Backend SHALL 返回简历组详情
4. WHEN 用户请求 POST /api/screening/groups/add-resume/ THEN FastAPI_Backend SHALL 向简历组添加简历
5. WHEN 用户请求 POST /api/screening/groups/remove-resume/ THEN FastAPI_Backend SHALL 从简历组移除简历
6. WHEN 用户请求 POST /api/screening/groups/set-status/ THEN FastAPI_Backend SHALL 更新简历组状态

### 需求 6

**用户故事:** 作为 HR 人员，我希望能够关联简历与视频分析，以便综合评估候选人。

#### 验收标准

1. WHEN 用户请求 POST /api/screening/videos/link/ THEN FastAPI_Backend SHALL 建立简历与视频分析的关联
2. WHEN 用户请求 POST /api/screening/videos/unlink/ THEN FastAPI_Backend SHALL 解除简历与视频分析的关联

### 需求 7

**用户故事:** 作为开发人员，我希望有开发测试工具，以便快速生成测试数据和调试系统。

#### 验收标准

1. WHEN 用户请求 POST /api/screening/dev/generate-resumes/ THEN FastAPI_Backend SHALL 根据岗位要求生成随机简历
2. WHEN 用户请求 GET/POST /api/screening/dev/force-error/ THEN FastAPI_Backend SHALL 控制是否强制筛选任务失败
3. WHEN 用户请求 POST /api/screening/dev/reset-state/ THEN FastAPI_Backend SHALL 清除所有测试相关的缓存和状态

### 需求 8

**用户故事:** 作为 HR 人员，我希望能够上传和分析面试视频，以便获取候选人的非语言表现评估。

#### 验收标准

1. WHEN 用户请求 GET /api/videos/ THEN FastAPI_Backend SHALL 返回视频分析列表
2. WHEN 用户请求 POST /api/videos/upload/ THEN FastAPI_Backend SHALL 上传视频并开始分析任务
3. WHEN 用户请求 GET /api/videos/{video_id}/status/ THEN FastAPI_Backend SHALL 返回视频分析状态和结果
4. WHEN 用户请求 POST /api/videos/{video_id}/ THEN FastAPI_Backend SHALL 更新视频分析结果

### 需求 9

**用户故事:** 作为 HR 主管，我希望能够获取候选人的综合分析和推荐，以便做出最终录用决策。

#### 验收标准

1. WHEN 用户请求 GET /api/recommend/stats/ THEN FastAPI_Backend SHALL 返回已完成综合分析的统计数据
2. WHEN 用户请求 POST /api/recommend/analysis/{resume_id}/ THEN FastAPI_Backend SHALL 对候选人进行综合分析并返回结果
3. WHEN 用户请求 GET /api/recommend/analysis/{resume_id}/ THEN FastAPI_Backend SHALL 返回候选人的分析历史

### 需求 10

**用户故事:** 作为面试官，我希望有 AI 面试辅助系统，以便在面试过程中获得问题建议和答案评估。

#### 验收标准

1. WHEN 用户请求 GET /api/interviews/sessions/ THEN FastAPI_Backend SHALL 返回面试会话列表，支持 resume_id 参数筛选
2. WHEN 用户请求 POST /api/interviews/sessions/ THEN FastAPI_Backend SHALL 创建新的面试会话
3. WHEN 用户请求 GET /api/interviews/sessions/{session_id}/ THEN FastAPI_Backend SHALL 返回会话详情
4. WHEN 用户请求 DELETE /api/interviews/sessions/{session_id}/ THEN FastAPI_Backend SHALL 删除会话
5. WHEN 用户请求 POST /api/interviews/sessions/{session_id}/questions/ THEN FastAPI_Backend SHALL 生成候选面试问题
6. WHEN 用户请求 POST /api/interviews/sessions/{session_id}/qa/ THEN FastAPI_Backend SHALL 记录问答并返回评估和候选问题
7. WHEN 用户请求 POST /api/interviews/sessions/{session_id}/report/ THEN FastAPI_Backend SHALL 生成面试最终报告

### 需求 11

**用户故事:** 作为系统架构师，我希望新后端采用现代化的技术栈和最佳实践，以便提高系统的可维护性和性能。

#### 验收标准

1. THE FastAPI_Backend SHALL 使用 FastAPI 框架作为 Web 框架
2. THE FastAPI_Backend SHALL 使用 SQLAlchemy 作为 ORM 框架
3. THE FastAPI_Backend SHALL 使用 Pydantic 进行数据验证和序列化
4. THE FastAPI_Backend SHALL 使用 SQLite 作为默认数据库（支持切换到其他数据库）
5. THE FastAPI_Backend SHALL 提供 OpenAPI/Swagger 文档，路径为 /api/docs/
6. THE FastAPI_Backend SHALL 支持异步任务处理（用于 AI 分析等耗时操作）
7. THE FastAPI_Backend SHALL 实现统一的错误处理和日志记录

### 需求 12

**用户故事:** 作为系统架构师，我希望数据库设计合理优化，以便支持系统的高效运行。

#### 验收标准

1. THE FastAPI_Backend SHALL 设计合理的数据库表结构，支持所有业务功能
2. THE FastAPI_Backend SHALL 使用 UUID 作为主键类型，与前端期望一致
3. THE FastAPI_Backend SHALL 实现软删除机制，保留数据历史
4. THE FastAPI_Backend SHALL 建立合理的表关联关系，支持岗位-简历、简历-筛选数据等关联
5. THE FastAPI_Backend SHALL 支持数据库迁移管理

### 需求 13

**用户故事:** 作为运维人员，我希望新后端易于部署和配置，以便快速上线和维护。

#### 验收标准

1. THE FastAPI_Backend SHALL 支持通过环境变量配置数据库连接、AI 服务等参数
2. THE FastAPI_Backend SHALL 提供 requirements.txt 或 pyproject.toml 管理依赖
3. THE FastAPI_Backend SHALL 支持 CORS 配置，允许前端跨域访问
4. THE FastAPI_Backend SHALL 提供静态文件和媒体文件服务
5. THE FastAPI_Backend SHALL 在独立目录中创建，不影响现有 Django 项目
