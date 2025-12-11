# Requirements Document

## Introduction

本文档定义了HRM2招聘系统前后端API优化的需求规范。当前系统存在API命名不一致、路径冗余、响应格式不统一等问题，需要进行系统性优化以提高代码可维护性和开发效率。

## Glossary

- **API**: Application Programming Interface，应用程序编程接口
- **HRM2系统**: 智能招聘管理系统，包含岗位设置、简历筛选、面试辅助、视频分析、最终推荐五大模块
- **前端**: HRM2-Vue-Frontend_new，基于Vue 3 + TypeScript的前端应用
- **后端**: HRM2-Django-Backend，基于Django REST Framework的后端服务
- **RESTful**: 一种API设计风格，强调资源导向和HTTP方法语义
- **响应包装器**: 统一的API响应格式，包含code、message、data字段

## Requirements

### Requirement 1: API路径规范化

**User Story:** As a 开发者, I want API路径遵循统一的RESTful命名规范, so that 代码更易理解和维护。

#### Acceptance Criteria

1. WHEN 定义任何API端点 THEN THE 后端 SHALL 使用统一的 `/api/` 前缀（如 `/api/positions/` 而非 `/position-settings/`）
2. WHEN 定义资源列表端点 THEN THE 后端 SHALL 使用复数名词形式（如 `/api/positions/` 而非 `/api/position-settings/list/`）
3. WHEN 定义资源操作端点 THEN THE 后端 SHALL 使用HTTP方法语义（GET获取、POST创建、PUT更新、DELETE删除）
4. WHEN 存在冗余路径（如 `/positions/` 和 `/list/` 指向同一视图）THEN THE 后端 SHALL 移除冗余路径并保留规范路径
5. WHEN 定义嵌套资源端点 THEN THE 后端 SHALL 使用层级路径（如 `/api/positions/{id}/resumes/` 而非 `/assign-resumes/`）

### Requirement 2: 响应格式统一化

**User Story:** As a 前端开发者, I want 所有API返回统一的响应格式, so that 可以使用统一的响应处理逻辑。

#### Acceptance Criteria

1. WHEN 后端返回成功响应 THEN THE 后端 SHALL 返回格式 `{ "code": 200, "message": "success", "data": {...} }`
2. WHEN 后端返回错误响应 THEN THE 后端 SHALL 返回格式 `{ "code": <错误码>, "message": "<错误描述>", "data": null }`
3. WHEN 后端返回分页数据 THEN THE 后端 SHALL 在data中包含 `{ "items": [...], "total": n, "page": n, "page_size": n }`
4. WHEN 前端解析响应 THEN THE 前端 SHALL 统一检查code字段判断请求是否成功

### Requirement 3: 前端API模块重构

**User Story:** As a 前端开发者, I want API调用代码结构清晰且类型安全, so that 减少运行时错误并提高开发效率。

#### Acceptance Criteria

1. WHEN 前端调用API THEN THE 前端 SHALL 使用统一的axios实例而非混用fetch和axios
2. WHEN 定义API函数 THEN THE 前端 SHALL 为请求参数和响应数据提供完整的TypeScript类型定义
3. WHEN API路径变更 THEN THE 前端 SHALL 在单一配置文件中维护所有API端点路径
4. WHEN 处理API错误 THEN THE 前端 SHALL 使用统一的错误处理拦截器

### Requirement 4: 废弃API清理

**User Story:** As a 系统维护者, I want 移除不再使用的API端点和代码, so that 减少代码复杂度和潜在的安全风险。

#### Acceptance Criteria

1. WHEN 后端存在标记为废弃的API THEN THE 后端 SHALL 移除相关路由和视图代码
2. WHEN 前端存在调用废弃API的代码 THEN THE 前端 SHALL 移除或更新相关调用
3. WHEN 移除废弃API THEN THE 系统 SHALL 更新API文档以反映当前状态

### Requirement 5: API文档同步

**User Story:** As a 开发者, I want API文档与实际实现保持同步, so that 可以准确了解API的使用方式。

#### Acceptance Criteria

1. WHEN API实现变更 THEN THE 后端 SHALL 更新OpenAPI schema和API参考文档
2. WHEN 定义API端点 THEN THE 后端 SHALL 在视图类中提供完整的docstring描述
3. WHEN 生成API文档 THEN THE 系统 SHALL 包含请求参数、响应格式和示例

### Requirement 6: 模块解耦

**User Story:** As a 系统架构师, I want 简历库管理与简历筛选功能分离到独立模块, so that 职责清晰且便于独立维护和扩展。

#### Acceptance Criteria

1. WHEN 管理简历库（上传、查看、删除原始简历）THEN THE 后端 SHALL 通过独立的 `/resume-library/` 路径提供服务
2. WHEN 执行简历筛选任务 THEN THE 后端 SHALL 通过 `/resume-screening/` 路径提供服务，与简历库管理分离
3. WHEN 前端调用简历库API THEN THE 前端 SHALL 使用独立的 `libraryApi` 模块，路径指向 `/resume-library/`
4. WHEN 简历库和筛选模块需要交互 THEN THE 后端 SHALL 通过明确的服务接口而非直接模型引用进行通信

### Requirement 7: 命名规范化

**User Story:** As a 开发者, I want 前后端字段命名遵循统一规范, so that 减少混淆和数据映射错误。

#### Acceptance Criteria

1. WHEN 后端返回JSON字段 THEN THE 后端 SHALL 使用snake_case命名（如 `candidate_name`、`screening_score`）
2. WHEN 前端定义TypeScript接口 THEN THE 前端 SHALL 字段名与后端保持一致，避免创建别名字段
3. WHEN 存在同义字段（如 `scores` 和 `screening_score`）THEN THE 系统 SHALL 统一为单一命名并移除冗余别名
4. WHEN 定义API端点路径 THEN THE 后端 SHALL 使用kebab-case命名（如 `/resume-screening/`、`/task-history/`）
5. WHEN 定义模型类和视图类 THEN THE 后端 SHALL 使用PascalCase命名（如 `ResumeData`、`ScreeningTaskView`）

### Requirement 8: 验证机制

**User Story:** As a 开发者, I want 有自动化检查机制确保API修改的完整性, so that 避免遗漏导致的运行时错误。

#### Acceptance Criteria

1. WHEN 修改后端API路径 THEN THE 系统 SHALL 检查前端是否存在对应的路径更新
2. WHEN 修改API响应格式 THEN THE 系统 SHALL 检查前端解析逻辑是否兼容
3. WHEN 完成一轮修改 THEN THE 系统 SHALL 运行前后端联调测试验证API可用性
