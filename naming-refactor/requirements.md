# Requirements Document

## Introduction

本文档定义了HRM2招聘系统命名一致性重构的需求规范。当前系统存在前后端命名不一致、视图类名与模型名不匹配、API字段命名混乱等问题，需要进行系统性统一以提高代码可读性和可维护性。

**核心目标**：统一前后端命名约定，消除歧义，建立清晰的命名规范。

## Glossary

- **HRM2系统**: 智能招聘管理系统，包含岗位设置、简历管理、简历筛选、视频分析、面试辅助、最终推荐六大模块
- **View Class**: Django REST Framework 视图类，处理 HTTP 请求
- **Model**: Django ORM 模型，对应数据库表
- **Endpoint**: API 端点，即 URL 路径
- **Type/Interface**: TypeScript 类型定义

## Current State Analysis

### 命名不一致清单

| 序号 | 类型 | 现状 | 问题描述 |
|:-----|:-----|:-----|:-----|
| 1 | 视图类 | `PositionCriteriaListView` | 模型已重命名为 Position，视图类名未同步 |
| 2 | 前端类型 | `PositionData.position` | 字段名与后端 `Position.title` 不一致 |
| 3 | 前端路由 | `/library` | 与 API 路径 `/resumes/` 概念不一致 |
| 4 | API字段 | `resume_data_id` | 历史遗留，应统一为 `resume_id` |
| 5 | 视图类 | `ResumeDataDetailView` | 命名风格不统一 |
| 6 | 视图类 | `SessionListView` | 过于简单，缺少模块前缀 |
| 7 | 视图类 | `CandidateComprehensiveAnalysisView` | 与模型名不完全一致 |
| 8 | 后端兼容 | `Position.to_dict()` 返回双字段 | 同时返回 position 和 title |
| 9 | 前端类型 | `ResumeData` vs `Resume` | 两个相似类型造成混淆 |

### 核心问题

1. **历史遗留**：数据库简化重构后，部分命名未同步更新
2. **前后端割裂**：前端使用旧字段名，后端使用新字段名
3. **风格不统一**：视图类命名缺乏统一规范
4. **概念混淆**：`library` vs `resumes`、`position` vs `title`

## Requirements

### Requirement 1: 视图类命名与模型一致

**User Story:** As a 后端开发者, I want 视图类名与模型名保持一致, so that 代码可读性更高。

#### Acceptance Criteria

1. WHEN 模型名为 `Position` THEN THE 视图类 SHALL 命名为 `PositionXxxView`
2. WHEN 模型名为 `InterviewSession` THEN THE 视图类 SHALL 命名为 `InterviewSessionXxxView`
3. WHEN 模型名为 `ComprehensiveAnalysis` THEN THE 视图类 SHALL 命名为 `ComprehensiveAnalysisXxxView`
4. WHEN 重命名视图类 THEN THE urls.py SHALL 同步更新导入和引用

### Requirement 2: 前端类型字段与后端一致

**User Story:** As a 前端开发者, I want 类型字段名与后端响应一致, so that 减少字段映射逻辑。

#### Acceptance Criteria

1. WHEN 后端返回 `title` 字段 THEN THE 前端类型 SHALL 使用 `title` 而非 `position`
2. WHEN 后端返回 `resume_id` THEN THE 前端 SHALL 使用 `resume_id` 而非 `resume_data_id`
3. WHEN 存在过渡期 THEN THE 前端类型 SHALL 标注 `@deprecated` 注释
4. WHEN 重命名字段 THEN THE 相关组件 SHALL 同步更新字段访问

### Requirement 3: 前端路由与API路径一致

**User Story:** As a 用户, I want URL路径语义清晰, so that 理解当前所在功能模块。

#### Acceptance Criteria

1. WHEN API路径为 `/resumes/` THEN THE 前端路由 SHALL 为 `/resumes`
2. WHEN 路由变更 THEN THE 系统 SHALL 提供旧路由重定向
3. WHEN 路由变更 THEN THE 侧边栏导航 SHALL 同步更新
4. WHEN 路由变更 THEN THE 视图组件 SHALL 考虑重命名

### Requirement 4: API字段命名统一

**User Story:** As a 全栈开发者, I want API字段命名统一, so that 减少认知负担。

#### Acceptance Criteria

1. WHEN 引用简历ID THEN THE 字段名 SHALL 统一为 `resume_id`
2. WHEN 引用简历ID列表 THEN THE 字段名 SHALL 统一为 `resume_ids`
3. WHEN 过渡期 THEN THE 后端 SHALL 同时接受新旧字段名
4. WHEN 过渡期结束 THEN THE 后端 SHALL 移除旧字段名支持

### Requirement 5: 后端兼容字段清理

**User Story:** As a 系统维护者, I want 移除冗余兼容字段, so that 减少代码复杂度。

#### Acceptance Criteria

1. WHEN 前端已迁移完成 THEN THE 后端 SHALL 移除 `to_dict()` 中的兼容字段
2. WHEN 移除兼容字段 THEN THE API文档 SHALL 同步更新
3. WHEN 移除兼容字段 THEN THE 测试用例 SHALL 同步更新
4. WHEN 移除兼容字段 THEN THE changelog SHALL 记录变更

## Success Metrics

| 指标 | 当前值 | 目标值 |
|:-----|:------:|:------:|
| 命名不一致项 | 9 | 0 |
| 视图类命名规范符合率 | 60% | 100% |
| 前端类型与后端字段一致率 | 70% | 100% |
| API字段命名统一率 | 80% | 100% |

## Priority Classification

### 🔴 高优先级（直接影响开发体验）

1. 视图类名与模型名不一致
2. 前端 PositionData 字段命名
3. 前端路由与API路径不一致
4. API 字段 `resume_data_id` vs `resume_id`

### 🟡 中优先级（影响代码可读性）

5. Screening 模块视图类命名混乱
6. 面试模块视图类名过于简单
7. ComprehensiveAnalysis 视图类命名

### 🟢 低优先级（兼容遗留清理）

8. Position.to_dict() 返回双字段
9. 前端类型 ResumeData vs Resume 合并
