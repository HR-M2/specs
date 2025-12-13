# Implementation Plan

## 概述

本任务书指导将HRM2系统数据库从11个表简化为6个表的重构工作。

**预计工作量**: 4-6个工作日  
**风险等级**: 中（不迁移旧数据，降低风险）

---

## Phase 1: 基础设施准备 ✅

- [x] 1.1 创建新的 resume Django 应用
  - 在 `apps/` 目录下运行 `python manage.py startapp resume`
  - 配置 `apps.py` 设置 `name = 'apps.resume'`
  - 注册到 `config/settings/base.py` 的 `INSTALLED_APPS`
  - _Requirements: 1.1_

- [x] 1.2 备份现有数据库（可选）
  - 导出 SQLite 数据库备份
  - 记录当前表结构
  - _Requirements: 7.1_

---

## Phase 2: 新模型定义 ✅

- [x] 2.1 重构 Position 模型
  - 文件: `apps/position_settings/models.py`
  - 重命名 `PositionCriteria` 为 `Position`
  - 合并技能、学历等字段到 `requirements` JSON
  - 删除 `resume_count` 缓存字段
  - 删除 `ResumePositionAssignment` 中间表
  - _Requirements: 4.1, 2.1_

- [x] 2.2 创建统一的 Resume 模型
  - 文件: `apps/resume/models.py`
  - 定义 Resume 模型（合并 ResumeLibrary + ResumeData）
  - 包含: 文件信息、候选人信息、岗位外键、状态、筛选结果
  - 添加 Status 枚举: pending/screened/interviewing/analyzed
  - _Requirements: 1.1, 1.2, 5.1-5.5_

- [x] 2.3 简化 ScreeningTask 模型
  - 文件: `apps/resume_screening/models.py`
  - 创建新的 `ScreeningTask` 模型（简化版）
  - 关联到 Position 而非存储 position_data
  - 删除 current_step, total_steps, current_speaker 字段
  - _Requirements: 4.1_

- [x] 2.4 简化 VideoAnalysis 模型
  - 文件: `apps/video_analysis/models.py`
  - 关联到 Resume（原 ResumeData）
  - 合并评分字段到 `analysis_result` JSON
  - 删除 candidate_name, position_applied（从关联获取）
  - _Requirements: 4.2_

- [x] 2.5 简化 InterviewSession 模型
  - 文件: `apps/interview_assist/models.py`
  - 重命名 `InterviewAssistSession` 为 `InterviewSession`
  - 关联到新的 Resume 模型
  - 删除 job_config（从 resume.position 获取）
  - 删除 report_file（报告存JSON）
  - _Requirements: 4.1_

- [x] 2.6 简化 ComprehensiveAnalysis 模型
  - 文件: `apps/final_recommend/models.py`
  - 重命名 `CandidateComprehensiveAnalysis` 为 `ComprehensiveAnalysis`
  - 合并 recommendation_level/label/action 到 `recommendation` JSON
  - 删除 input_data_snapshot
  - 删除废弃的 `InterviewEvaluationTask` 模型
  - _Requirements: 3.1, 4.3_

---

## Phase 3: 数据库迁移

- [ ] 3.1 创建数据库迁移文件
  - 运行 `python manage.py makemigrations`
  - 检查生成的迁移文件
  - 确保迁移顺序正确（先创建新表，后删除旧表）
  - _Requirements: 3.1-3.4_

- [ ] 3.2 执行数据库迁移
  - 运行 `python manage.py migrate`
  - 验证新表结构
  - 删除旧的 db.sqlite3（重新开始）
  - _Requirements: 3.1-3.4_

- [ ] 3.3 验证数据库结构
  - 检查表数量是否为6个
  - 检查外键关联是否正确
  - 检查索引是否创建
  - _Requirements: 7.1-7.4_

---

## Phase 4: Serializers 更新

- [ ] 4.1 创建 Resume Serializers
  - 文件: `apps/resume/serializers.py`
  - 定义 ResumeListSerializer, ResumeDetailSerializer
  - 兼容原 ResumeLibrary 和 ResumeData 的响应格式
  - _Requirements: 6.2_

- [ ] 4.2 更新 Position Serializers
  - 文件: `apps/position_settings/serializers.py`
  - 适配新的 Position 模型结构
  - 处理 requirements JSON 的序列化
  - _Requirements: 6.2_

- [ ] 4.3 更新 ScreeningTask Serializers
  - 文件: `apps/resume_screening/serializers.py`
  - 适配新的简化模型
  - _Requirements: 6.2_

- [ ] 4.4 更新 VideoAnalysis Serializers
  - 文件: `apps/video_analysis/serializers.py`
  - 处理 analysis_result JSON 的序列化
  - 从 resume 关联获取 candidate_name
  - _Requirements: 6.2_

- [ ] 4.5 更新 InterviewSession Serializers
  - 文件: `apps/interview_assist/serializers.py`
  - 适配新模型名称和字段
  - _Requirements: 6.2_

- [ ] 4.6 更新 ComprehensiveAnalysis Serializers
  - 文件: `apps/final_recommend/serializers.py`
  - 处理 recommendation JSON 的序列化
  - 删除废弃模型的 serializer
  - _Requirements: 6.2_

---

## Phase 5: Views 更新

- [ ] 5.1 创建 Resume Views
  - 文件: `apps/resume/views.py`
  - 合并原 LibraryView 和部分 ScreeningView 功能
  - 实现: 列表、详情、上传、更新、删除
  - _Requirements: 6.1_

- [ ] 5.2 更新 Position Views
  - 文件: `apps/position_settings/views.py`
  - 简历分配改为更新 resume.position_id
  - 删除 ResumePositionAssignment 相关逻辑
  - _Requirements: 2.1-2.4_

- [ ] 5.3 更新 ScreeningTask Views
  - 文件: `apps/resume_screening/views/`
  - 适配新的简化模型
  - 任务创建时关联 Position
  - _Requirements: 6.1_

- [ ] 5.4 更新 VideoAnalysis Views
  - 文件: `apps/video_analysis/views.py`
  - 创建时关联 Resume
  - 返回数据从 Resume 获取候选人信息
  - _Requirements: 6.1_

- [ ] 5.5 更新 InterviewSession Views
  - 文件: `apps/interview_assist/views.py`
  - 适配新模型
  - 从 resume.position 获取岗位配置
  - _Requirements: 6.1_

- [ ] 5.6 更新 ComprehensiveAnalysis Views
  - 文件: `apps/final_recommend/views.py`
  - 删除废弃任务相关视图
  - 适配新模型
  - _Requirements: 3.1, 6.1_

---

## Phase 6: URL 路由更新

- [ ] 6.1 创建 Resume URL 路由
  - 文件: `apps/resume/urls.py`
  - 定义 `/api/resumes/` 路由
  - 合并原 `/api/library/` 功能
  - _Requirements: 6.1_

- [ ] 6.2 更新主路由配置
  - 文件: `config/urls.py`
  - 添加 resume 模块路由
  - 保留 library 路由作为兼容（可选）
  - _Requirements: 6.1_

- [ ] 6.3 更新各模块 URL 路由
  - 适配新的视图函数
  - 确保路径与 API 文档一致
  - _Requirements: 6.1_

---

## Phase 7: 服务层更新

- [ ] 7.1 创建 Resume 服务层
  - 文件: `apps/resume/services.py`
  - 实现简历状态转换逻辑
  - 实现筛选结果更新逻辑
  - _Requirements: 5.1-5.4_

- [ ] 7.2 更新 Screening 服务层
  - 文件: `apps/resume_screening/services/`
  - 任务完成时更新 Resume 状态和结果
  - _Requirements: 5.2_

- [ ] 7.3 更新 Interview 服务层
  - 文件: `apps/interview_assist/services.py`
  - 创建会话时更新 Resume 状态
  - _Requirements: 5.3_

- [ ] 7.4 更新 Recommend 服务层
  - 文件: `apps/final_recommend/services.py`
  - 分析完成时更新 Resume 状态
  - _Requirements: 5.4_

---

## Phase 8: 废弃代码清理

- [ ] 8.1 删除废弃模型文件
  - 删除 `ResumeLibrary` 模型（已迁移到 Resume）
  - 删除 `ResumeData` 模型（已迁移到 Resume）
  - 删除 `ResumeGroup` 模型
  - 删除 `ScreeningReport` 模型
  - 删除 `ResumePositionAssignment` 模型
  - 删除 `InterviewEvaluationTask` 模型
  - _Requirements: 3.1-3.4_

- [ ] 8.2 删除废弃视图和 URL
  - 清理 `apps/resume_library/` 目录（合并到 resume）
  - 清理 `apps/resume_screening/` 中废弃代码
  - _Requirements: 3.1-3.4_

- [ ] 8.3 清理废弃导入和引用
  - 检查所有文件中对废弃模型的引用
  - 更新为新模型引用
  - _Requirements: 3.1-3.4_

---

## Phase 9: 前端适配

- [ ] 9.1 更新前端 API 端点
  - 文件: `HRM2-Vue-Frontend_new/src/api/endpoints.ts`
  - 更新简历相关端点指向 `/api/resumes/`
  - 保持其他端点不变
  - _Requirements: 6.1_

- [ ] 9.2 更新前端类型定义
  - 文件: `HRM2-Vue-Frontend_new/src/types/`
  - 定义新的 Resume 类型
  - 适配字段变更
  - _Requirements: 6.2_

- [ ] 9.3 更新前端 API 调用
  - 合并 libraryApi 和部分 screeningApi 到 resumeApi
  - 更新组件中的 API 调用
  - _Requirements: 6.1_

- [ ] 9.4 验证前端编译
  - 运行 `npm run build`
  - 确保无 TypeScript 错误
  - _Requirements: 6.1_

---

## Phase 10: 测试与验证

- [ ] 10.1 更新后端单元测试
  - 更新各模块测试文件
  - 删除废弃模型相关测试
  - 添加新模型测试
  - _Requirements: 7.1-7.4_

- [ ] 10.2 运行后端测试
  - 运行 `python manage.py test`
  - 确保所有测试通过
  - _Requirements: 7.1-7.4_

- [ ] 10.3 手动集成测试
  - 启动前后端服务
  - 测试完整业务流程
  - 验证数据关联正确
  - _Requirements: 7.1-7.4_

---

## Phase 11: 文档更新

- [ ] 11.1 更新 API 文档
  - 运行 `python Docs/生成API文档.py`
  - 更新 `Docs/API参考文档.md`
  - 更新 `Docs/openapi.json`
  - _Requirements: 6.3_

- [ ] 11.2 更新项目文档
  - 更新 README.md
  - 记录数据库结构变更
  - _Requirements: 6.3_

- [ ] 11.3 归档本任务书
  - 记录完成状态
  - 添加 changelog
  - _Requirements: 6.3_

---

## Checkpoints

### Checkpoint 1: Phase 2 完成后 ✅
- [x] 所有新模型定义完成
- [x] 模型关系正确
- [x] makemigrations 无错误

### Checkpoint 2: Phase 3 完成后
- [ ] 数据库迁移成功
- [ ] 表数量为 6
- [ ] Django admin 可访问

### Checkpoint 3: Phase 6 完成后
- [ ] 所有 API 端点可访问
- [ ] 返回格式正确
- [ ] 无 500 错误

### Checkpoint 4: Phase 9 完成后
- [ ] 前端编译通过
- [ ] 前后端联调成功
- [ ] 业务流程正常

### Final Checkpoint
- [ ] 后端测试全部通过
- [ ] 前端编译成功
- [ ] API 文档已更新
- [ ] 表数量: 11 -> 6 ✓
- [ ] 废弃模型: 1 -> 0 ✓

---

## 快速参考

### 表映射关系

| 旧表 | 新表 | 操作 |
|:-----|:-----|:-----|
| PositionCriteria | Position | 重命名+简化 |
| ResumePositionAssignment | - | 删除 |
| ResumeLibrary | Resume | 合并 |
| ResumeData | Resume | 合并 |
| ResumeGroup | - | 删除 |
| ScreeningReport | - | 删除 |
| ResumeScreeningTask | ScreeningTask | 简化 |
| VideoAnalysis | VideoAnalysis | 简化 |
| InterviewAssistSession | InterviewSession | 重命名 |
| CandidateComprehensiveAnalysis | ComprehensiveAnalysis | 简化 |
| InterviewEvaluationTask | - | 删除 |

### 命令速查

```bash
# 创建新应用
cd HRM2-Django-Backend
python manage.py startapp resume apps/resume

# 生成迁移
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 重置数据库（如需）
rm db.sqlite3
python manage.py migrate

# 运行测试
python manage.py test

# 生成API文档
python Docs/生成API文档.py

# 前端构建
cd ../HRM2-Vue-Frontend_new
npm run build
```
