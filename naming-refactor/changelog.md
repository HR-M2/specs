# Changelog - 命名一致性重构

## [Phase 1] - 2024-12-14

### 🔴 高优先级重构完成

#### Task 1.1: 后端视图类重命名

**变更文件**:
- `apps/position_settings/views.py`
- `apps/position_settings/urls.py`

**变更内容**:
| 原名称 | 新名称 |
|:------|:------|
| `PositionCriteriaListView` | `PositionListView` |
| `PositionCriteriaDetailView` | `PositionDetailView` |

**影响**: 无API变更，仅Python类名更新

---

#### Task 1.2: 前端 PositionData.position → title

**变更文件**:
- `src/types/index.ts`
- `src/composables/usePositionEditor.ts`
- `src/composables/usePositionManagement.ts`
- `src/components/positions/PositionEditForm.vue`
- `src/components/positions/PositionListPanel.vue`

**变更内容**:
- `PositionData` 接口中 `position: string` → `title: string`
- 保留 `position?: string` 作为兼容字段（标记 @deprecated）
- 组件模板中 `pos.position` → `pos.title || pos.position`
- 表单验证规则 `position` → `title`

**兼容性**: 后端 `Position.to_dict()` 仍返回 `position` 字段，Phase 3 移除

---

#### Task 1.3: 前端路由 /library → /resumes

**变更文件**:
- `src/router/index.ts`
- `src/views/ResumeLibraryView.vue` → `ResumesView.vue`（重命名）
- `src/components/layout/AppSidebar.vue`

**变更内容**:
- 路由路径 `/library` → `/resumes`
- 路由名称 `library` → `resumes`
- 页面标题 `简历库` → `简历管理`
- 添加 `/library` → `/resumes` 重定向（兼容旧链接）
- 侧边栏导航更新

**兼容性**: 旧路由 `/library` 自动重定向到 `/resumes`

---

#### Task 1.4: API字段 resume_data_id → resume_id

**变更文件**:

前端:
- `src/api/index.ts`（12处修改）
- `src/composables/useInterviewAssist.ts`
- `src/composables/useVideoUpload.ts`
- `src/views/VideoView.vue`
- `src/views/RecommendView.vue`

**变更内容**:
- 所有 API 调用参数 `resume_data_id` → `resume_id`
- 所有 API 响应类型 `resume_data_id` → `resume_id`
- FormData 字段 `resume_data_id` → `resume_id`

**兼容性**: 后端已支持同时接受 `resume_id` 和 `resume_data_id`（兼容期）

---

## [Phase 2] - 2024-12-14

### 🟡 中优先级重构完成

#### Task 2.1: Screening 模块视图类重命名

**变更文件**:
- `apps/resume_screening/views/screening.py`
- `apps/resume_screening/views/resume_data.py`
- `apps/resume_screening/views/__init__.py`
- `apps/resume_screening/urls.py`

**变更内容**:
| 原名称 | 新名称 |
|:------|:------|
| `ResumeScreeningView` | `ScreeningSubmitView` |
| `ResumeDataDetailView` | `ScreeningReportView` |

---

#### Task 2.2: Interview 模块视图类重命名

**变更文件**:
- `apps/interview_assist/views.py`
- `apps/interview_assist/urls.py`

**变更内容**:
| 原名称 | 新名称 |
|:------|:------|
| `SessionListView` | `InterviewSessionListView` |
| `SessionDetailView` | `InterviewSessionDetailView` |
| `GenerateQuestionsView` | `InterviewQuestionsView` |
| `RecordQAView` | `InterviewQAView` |
| `GenerateReportView` | `InterviewReportView` |

---

#### Task 2.3: Recommend 模块视图类重命名

**变更文件**:
- `apps/final_recommend/views.py`
- `apps/final_recommend/urls.py`

**变更内容**:
| 原名称 | 新名称 |
|:------|:------|
| `CandidateComprehensiveAnalysisView` | `ComprehensiveAnalysisView` |

---

## [Task 1.4 阶段三] - 2024-12-14

### 后端 resume_data_id 兼容代码清理

**变更文件**:
- `apps/interview_assist/views.py` - 移除 resume_data_id 兼容
- `apps/video_analysis/views.py` - 移除 resume_data_id 兼容和 OpenAPI 更新
- `apps/resume_screening/views/link.py` - 参数名和响应字段更新
- `apps/position_settings/views.py` - 移除 resume_data_ids 兼容
- `apps/common/schemas.py` - 更新所有 resume_data_id 字段为 resume_id
- `Docs/API参考文档.md` - 更新文档
- `Docs/openapi.json` - 重新生成

**变更内容**:
- 所有 `resume_data_id` 参数统一为 `resume_id`
- 所有 `resume_data_ids` 参数统一为 `resume_ids`
- API 响应中的 `resume_data_id` 字段统一为 `resume_id`

---

## [Task 3.1] - 2024-12-14

### 修复 OpenAPI 文档生成警告和错误

**问题**: `python manage.py spectacular` 生成 OpenAPI 文档时存在 18 个 Warnings 和 2 个 Errors

**变更文件**:
- `apps/resume/serializers.py` - 为 `get_xxx` 方法添加 `@extend_schema_field` 装饰器和类型注释
- `apps/resume_screening/views/screening.py` - 为 `ScreeningSubmitView` 添加 `request=ResumeScreeningInputSerializer`
- `apps/final_recommend/views.py` - 为 `ComprehensiveAnalysisView` 添加 `request=None`
- `apps/position_settings/views.py` - 为列表/详情视图添加 `operation_id`
- `apps/resume/views.py` - 为列表/详情视图添加 `operation_id`
- `apps/interview_assist/views.py` - 为列表/详情视图添加 `operation_id`

**变更内容**:
| 问题类型 | 变更数量 | 变更方式 |
|:------|:------:|:--------|
| Serializer 类型注释缺失 | 15 | 添加 `@extend_schema_field` 装饰器 |
| 视图 request body 定义缺失 | 2 | 添加 `request` 参数到 `@extend_schema` |
| operationId 重复 | 3 | 添加唯一 `operation_id` |

**结果**: Warnings 18 → 0, Errors 2 → 0

---

## 待完成

### Phase 3 - 低优先级（待执行）
- [x] Task 3.1: 修复 OpenAPI 文档生成警告和错误
- [ ] Task 3.2: 后端移除 Position.to_dict() 兼容字段
- [ ] Task 3.3: 前端类型 ResumeData → Resume 合并

---

## 验证清单

### Phase 1 & 2 验证

- [ ] 后端服务正常启动 (`python manage.py runserver`)
- [ ] 前端编译无错误 (`npm run build`)
- [ ] 岗位管理页面 CRUD 正常
- [ ] 简历管理页面正常显示
- [ ] `/library` 重定向到 `/resumes`
- [ ] 面试辅助功能正常
- [ ] 视频上传关联正常
- [ ] 筛选提交功能正常
- [ ] 综合分析功能正常
