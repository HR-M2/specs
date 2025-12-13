# Requirements Document

## Introduction

本文档定义了HRM2招聘系统数据库结构简化重构的需求规范。当前系统存在数据冗余、模型职责不清、废弃代码残留等问题，需要进行系统性简化以提高数据一致性和系统可维护性。

**核心目标**：从 11 个数据表简化为 6 个数据表，消除数据冗余，明确模型职责。

## Glossary

- **HRM2系统**: 智能招聘管理系统，包含岗位设置、简历管理、简历筛选、视频分析、面试辅助、最终推荐六大模块
- **Django ORM**: Django对象关系映射，用于数据库操作
- **Migration**: Django数据库迁移机制
- **FK (Foreign Key)**: 外键，表示表之间的关联关系
- **JSON Field**: Django中用于存储JSON格式数据的字段类型

## Current State Analysis

### 现有数据表（11个）

| 序号 | 表名 | 模块 | 主要问题 |
|:-----|:-----|:-----|:-----|
| 1 | `PositionCriteria` | position_settings | 字段过多，可合并 |
| 2 | `ResumePositionAssignment` | position_settings | 中间表可简化 |
| 3 | `ResumeLibrary` | resume_library | 与ResumeData冗余 |
| 4 | `ResumeScreeningTask` | resume_screening | 字段冗余 |
| 5 | `ScreeningReport` | resume_screening | 与ResumeData重复存储报告 |
| 6 | `ResumeGroup` | resume_screening | 与PositionCriteria功能重叠 |
| 7 | `ResumeData` | resume_screening | 外键过多，职责混乱 |
| 8 | `VideoAnalysis` | video_analysis | 字段冗余 |
| 9 | `InterviewAssistSession` | interview_assist | 基本合理 |
| 10 | `CandidateComprehensiveAnalysis` | final_recommend | 字段可合并 |
| 11 | `InterviewEvaluationTask` | final_recommend | **已废弃，应删除** |

### 核心问题

1. **数据冗余**：`ResumeLibrary` 和 `ResumeData` 存储相同的简历内容和候选人信息
2. **职责重叠**：`ResumeGroup` 与 `PositionCriteria` 都在管理简历分组
3. **报告分散**：`ScreeningReport` 和 `ResumeData` 都存储筛选报告
4. **废弃模型**：`InterviewEvaluationTask` 已废弃但仍占用空间
5. **关联复杂**：`ResumeData` 有4个外键加1个反向关联，关系混乱

## Requirements

### Requirement 1: 简历数据模型统一

**User Story:** As a 系统架构师, I want 简历数据存储在单一模型中, so that 消除数据冗余并简化数据流。

#### Acceptance Criteria

1. WHEN 上传新简历 THEN THE 系统 SHALL 存储到统一的 `Resume` 表中
2. WHEN 执行简历筛选 THEN THE 系统 SHALL 在同一 `Resume` 记录上更新筛选结果
3. WHEN 查询简历信息 THEN THE 系统 SHALL 从单一数据源获取，无需跨表关联
4. WHEN 删除简历 THEN THE 系统 SHALL 级联删除所有关联数据（面试、分析等）

### Requirement 2: 岗位-简历关系简化

**User Story:** As a 开发者, I want 岗位与简历的关系简单明了, so that 减少关联查询复杂度。

#### Acceptance Criteria

1. WHEN 分配简历到岗位 THEN THE 系统 SHALL 直接在简历记录上设置 `position_id` 外键
2. WHEN 查询岗位下的简历 THEN THE 系统 SHALL 使用简单的外键反向查询
3. WHEN 移除岗位分配 THEN THE 系统 SHALL 将简历的 `position_id` 设为 null
4. WHEN 删除岗位 THEN THE 系统 SHALL 保留简历但清空其 `position_id`

### Requirement 3: 废弃模型清理

**User Story:** As a 系统维护者, I want 移除不再使用的数据模型, so that 减少数据库复杂度和维护负担。

#### Acceptance Criteria

1. WHEN 清理废弃模型 THEN THE 系统 SHALL 删除 `InterviewEvaluationTask` 表及相关代码
2. WHEN 清理废弃模型 THEN THE 系统 SHALL 删除 `ResumeGroup` 表及相关代码
3. WHEN 清理废弃模型 THEN THE 系统 SHALL 删除 `ScreeningReport` 表（报告内容迁移到Resume）
4. WHEN 清理废弃模型 THEN THE 系统 SHALL 删除 `ResumePositionAssignment` 中间表

### Requirement 4: 字段结构优化

**User Story:** As a 开发者, I want 相关配置数据合并到JSON字段, so that 减少表字段数量并提高灵活性。

#### Acceptance Criteria

1. WHEN 存储岗位要求 THEN THE 系统 SHALL 将技能、学历、经验等合并到 `requirements` JSON字段
2. WHEN 存储视频分析结果 THEN THE 系统 SHALL 将多个评分字段合并到 `analysis_result` JSON字段
3. WHEN 存储推荐结果 THEN THE 系统 SHALL 将level/label/action合并到 `recommendation` JSON字段
4. WHEN 访问JSON字段内容 THEN THE 系统 SHALL 提供便捷的属性访问方法

### Requirement 5: 简历状态管理

**User Story:** As a HR用户, I want 简历状态一目了然, so that 快速了解候选人处于哪个阶段。

#### Acceptance Criteria

1. WHEN 上传简历 THEN THE 简历 SHALL 初始状态为 `pending`
2. WHEN 完成初筛 THEN THE 简历 SHALL 状态更新为 `screened`
3. WHEN 开始面试 THEN THE 简历 SHALL 状态更新为 `interviewing`
4. WHEN 完成综合分析 THEN THE 简历 SHALL 状态更新为 `analyzed`
5. WHEN 查询简历列表 THEN THE 系统 SHALL 支持按状态筛选

### Requirement 6: API兼容性

**User Story:** As a 前端开发者, I want API接口保持兼容, so that 前端改动最小化。

#### Acceptance Criteria

1. WHEN 重构数据模型 THEN THE 后端 SHALL 保持现有API路径不变
2. WHEN 重构数据模型 THEN THE 后端 SHALL 保持响应数据格式兼容
3. WHEN 合并简历库和简历数据API THEN THE 后端 SHALL 提供清晰的迁移指引
4. WHEN 存在字段变更 THEN THE 后端 SHALL 在序列化层做兼容转换

### Requirement 7: 数据完整性

**User Story:** As a 系统管理员, I want 数据关联完整可追溯, so that 确保数据一致性。

#### Acceptance Criteria

1. WHEN 简历关联视频分析 THEN THE 系统 SHALL 通过外键保持引用完整性
2. WHEN 简历关联面试会话 THEN THE 系统 SHALL 通过外键保持引用完整性
3. WHEN 简历关联综合分析 THEN THE 系统 SHALL 通过外键保持引用完整性
4. WHEN 删除简历 THEN THE 系统 SHALL 级联删除所有关联记录

## Success Metrics

| 指标 | 当前值 | 目标值 |
|:-----|:------:|:------:|
| 数据表数量 | 11 | 6 |
| ResumeData 外键数量 | 4 | 1 |
| 数据冗余表数量 | 3 | 0 |
| 废弃模型数量 | 1 | 0 |
