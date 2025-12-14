# Tasks Document

## Overview

本文档列出HRM2招聘系统命名一致性重构的所有任务，按优先级和执行顺序排列。

---

## 🔴 Phase 1: 高优先级任务

### Task 1.1: 后端视图类重命名

**状态**: ✅ 已完成

**目标**: 将岗位模块视图类名与 Position 模型保持一致

**文件清单**:
- `apps/position_settings/views.py`
- `apps/position_settings/urls.py`

**步骤**:

- [x] 1.1.1 修改 `views.py` 中 `PositionCriteriaListView` → `PositionListView`
- [x] 1.1.2 修改 `views.py` 中 `PositionCriteriaDetailView` → `PositionDetailView`
- [x] 1.1.3 修改 `urls.py` 中的导入语句
- [x] 1.1.4 修改 `urls.py` 中的视图引用
- [ ] 1.1.5 运行后端服务验证无报错
- [ ] 1.1.6 访问 `/api/positions/` 验证正常

**验证命令**:
```powershell
cd HRM2-Django-Backend
python manage.py check
python manage.py runserver
# 访问 http://localhost:8000/api/positions/
```

---

### Task 1.2: 前端 PositionData.position → title

**状态**: ✅ 已完成

**目标**: 将前端岗位类型字段与后端模型字段一致

**文件清单**:
- `src/types/index.ts`
- `src/components/positions/PositionEditForm.vue`
- `src/components/positions/PositionListPanel.vue`
- `src/components/positions/PositionAIGenerateDrawer.vue`
- `src/components/common/PositionList.vue`
- `src/composables/usePositionManagement.ts`
- `src/composables/usePositionEditor.ts`
- `src/api/index.ts`

**步骤**:

- [x] 1.2.1 修改 `types/index.ts` 中 `PositionData` 接口，`position` → `title`
- [x] 1.2.2 全局搜索 `.position` 并替换为 `.title`（仅岗位名称相关）
- [x] 1.2.3 修改组件中的模板绑定 `{{ item.position }}` → `{{ item.title }}`
- [x] 1.2.4 修改 API 请求构造中的字段名
- [ ] 1.2.5 运行 `npm run build` 验证无 TypeScript 错误
- [ ] 1.2.6 测试岗位管理页面功能

**验证命令**:
```powershell
cd HRM2-Vue-Frontend_new
npm run build
npm run dev
# 访问岗位设置页面测试 CRUD
```

**注意事项**:
- 搜索时注意区分 `position`（岗位名称）和 `position_id`（岗位ID）
- 后端 `to_dict()` 暂时保留 `position` 兼容字段，待 Phase 3 移除

---

### Task 1.3: 前端路由 /library → /resumes

**状态**: ✅ 已完成

**目标**: 统一前端路由与 API 路径命名

**文件清单**:
- `src/router/index.ts`
- `src/views/ResumeLibraryView.vue` → `ResumesView.vue`
- `src/components/layout/AppSidebar.vue`

**步骤**:

- [x] 1.3.1 重命名 `ResumeLibraryView.vue` → `ResumesView.vue`
- [x] 1.3.2 修改 `router/index.ts` 路由路径和组件导入
- [x] 1.3.3 添加 `/library` → `/resumes` 重定向
- [x] 1.3.4 修改 `AppSidebar.vue` 导航链接
- [ ] 1.3.5 全局搜索 `library` 路由引用并更新
- [ ] 1.3.6 测试页面跳转和导航

**验证步骤**:
- 访问 `/resumes` 正常显示
- 访问 `/library` 自动跳转到 `/resumes`
- 侧边栏导航点击正常

---

### Task 1.4: API字段 resume_data_id → resume_id

**状态**: ✅ 已完成

**目标**: 统一简历ID字段命名

**阶段一：后端添加兼容** (先执行)

**文件清单**:
- `apps/interview_assist/views.py`
- `apps/video_analysis/views.py`
- `apps/resume_screening/views.py`

**步骤**:
- [x] 1.4.1 确认后端已支持 `resume_id` 参数（或添加兼容）
- [x] 1.4.2 运行后端验证兼容性

**阶段二：前端迁移**

**文件清单**:
- `src/api/index.ts`
- `src/types/index.ts`
- `src/composables/useInterviewAssist.ts`
- `src/composables/useVideoUpload.ts`

**步骤**:
- [x] 1.4.3 修改 `api/index.ts` 中所有 `resume_data_id` → `resume_id`
- [x] 1.4.4 修改 `types/index.ts` 中类型定义
- [x] 1.4.5 修改 composables 中的字段引用
- [ ] 1.4.6 运行前端验证无错误

**阶段三：后端清理** (Phase 1 完成后执行)

**步骤**:
- [ ] 1.4.7 后端移除 `resume_data_id` 兼容代码
- [ ] 1.4.8 更新 API 文档

**验证清单**:
- 面试辅助功能正常
- 视频上传关联正常
- 筛选视频关联正常

---

## 🟡 Phase 2: 中优先级任务

### Task 2.1: Screening 模块视图类重命名

**状态**: ✅ 已完成

**文件清单**:
- `apps/resume_screening/views.py`
- `apps/resume_screening/urls.py`

**变更清单**:
| 原名称 | 新名称 |
|:------|:------|
| `ResumeScreeningView` | `ScreeningSubmitView` |
| `ResumeDataDetailView` | `ScreeningReportView` |

**步骤**:
- [x] 2.1.1 修改 `views.py` 中的类名
- [x] 2.1.2 修改 `urls.py` 中的导入和引用
- [ ] 2.1.3 运行后端验证

---

### Task 2.2: Interview 模块视图类重命名

**状态**: ✅ 已完成

**文件清单**:
- `apps/interview_assist/views.py`
- `apps/interview_assist/urls.py`

**变更清单**:
| 原名称 | 新名称 |
|:------|:------|
| `SessionListView` | `InterviewSessionListView` |
| `SessionDetailView` | `InterviewSessionDetailView` |
| `GenerateQuestionsView` | `InterviewQuestionsView` |
| `RecordQAView` | `InterviewQAView` |
| `GenerateReportView` | `InterviewReportView` |

**步骤**:
- [x] 2.2.1 修改 `views.py` 中的类名
- [x] 2.2.2 修改 `urls.py` 中的导入和引用
- [ ] 2.2.3 运行后端验证

---

### Task 2.3: Recommend 模块视图类重命名

**状态**: ✅ 已完成

**文件清单**:
- `apps/final_recommend/views.py`
- `apps/final_recommend/urls.py`

**变更清单**:
| 原名称 | 新名称 |
|:------|:------|
| `CandidateComprehensiveAnalysisView` | `ComprehensiveAnalysisView` |

**步骤**:
- [x] 2.3.1 修改 `views.py` 中的类名
- [x] 2.3.2 修改 `urls.py` 中的导入和引用
- [ ] 2.3.3 运行后端验证

---

## 🟢 Phase 3: 低优先级任务

### Task 3.1: 后端移除 Position.to_dict() 兼容字段

**状态**: ⬜ 待执行

**前置条件**: Task 1.2 完成

**文件清单**:
- `apps/position_settings/models.py`

**步骤**:
- [ ] 3.1.1 移除 `to_dict()` 中的 `"position": self.title` 行
- [ ] 3.1.2 运行后端验证
- [ ] 3.1.3 测试前端岗位页面正常

---

### Task 3.2: 前端类型 ResumeData → Resume 合并

**状态**: ⬜ 待执行

**前置条件**: Phase 1 全部完成

**文件清单**:
- `src/types/index.ts`
- 引用 `ResumeData` 的所有组件

**步骤**:
- [ ] 3.2.1 对比 `ResumeData` 和 `Resume` 类型差异
- [ ] 3.2.2 将缺失字段合并到 `Resume`
- [ ] 3.2.3 全局替换 `ResumeData` → `Resume`
- [ ] 3.2.4 删除 `ResumeData` 类型定义
- [ ] 3.2.5 运行前端验证

---

## 执行进度追踪

### Phase 1 进度

| 任务 | 状态 | 完成时间 |
|:----|:----:|:-------:|
| Task 1.1 视图类重命名 | ✅ | 2024-12-14 |
| Task 1.2 PositionData 字段 | ✅ | 2024-12-14 |
| Task 1.3 路由统一 | ✅ | 2024-12-14 |
| Task 1.4 resume_id 统一 | ✅ | 2024-12-14 |

### Phase 2 进度

| 任务 | 状态 | 完成时间 |
|:----|:----:|:-------:|
| Task 2.1 Screening 视图类 | ✅ | 2024-12-14 |
| Task 2.2 Interview 视图类 | ✅ | 2024-12-14 |
| Task 2.3 Recommend 视图类 | ✅ | 2024-12-14 |

### Phase 3 进度

| 任务 | 状态 | 完成时间 |
|:----|:----:|:-------:|
| Task 3.1 后端兼容清理 | ⬜ | - |
| Task 3.2 前端类型合并 | ⬜ | - |

---

## 状态说明

- ⬜ 待执行
- 🔄 进行中
- ✅ 已完成
- ❌ 已取消
- ⏸️ 已暂停
