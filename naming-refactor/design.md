# Design Document

## Overview

本文档描述HRM2招聘系统命名一致性重构的详细设计方案，按优先级分为三个阶段执行。

---

## 🔴 Phase 1: 高优先级重构

### 1.1 视图类名与模型名统一

#### 变更清单

| 文件 | 原名称 | 新名称 |
|:-----|:------|:------|
| `apps/position_settings/views.py` | `PositionCriteriaListView` | `PositionListView` |
| `apps/position_settings/views.py` | `PositionCriteriaDetailView` | `PositionDetailView` |
| `apps/position_settings/urls.py` | 导入和引用 | 同步更新 |

#### 实现细节

**修改前** (`views.py`):
```python
class PositionCriteriaListView(SafeAPIView):
    """岗位标准列表API"""
    ...

class PositionCriteriaDetailView(SafeAPIView):
    """单个岗位API"""
    ...
```

**修改后** (`views.py`):
```python
class PositionListView(SafeAPIView):
    """岗位列表API"""
    ...

class PositionDetailView(SafeAPIView):
    """岗位详情API"""
    ...
```

**修改前** (`urls.py`):
```python
from .views import (
    PositionCriteriaListView,
    PositionCriteriaDetailView,
    ...
)

urlpatterns = [
    path('', PositionCriteriaListView.as_view(), name='list'),
    path('<uuid:position_id>/', PositionCriteriaDetailView.as_view(), name='detail'),
    ...
]
```

**修改后** (`urls.py`):
```python
from .views import (
    PositionListView,
    PositionDetailView,
    ...
)

urlpatterns = [
    path('', PositionListView.as_view(), name='list'),
    path('<uuid:position_id>/', PositionDetailView.as_view(), name='detail'),
    ...
]
```

#### 影响分析

- **无API变更**：仅重命名Python类，不影响URL路径
- **无前端变更**：前端调用的是URL，不依赖视图类名
- **需更新测试**：如有直接引用视图类的测试用例

---

### 1.2 前端 PositionData 字段统一

#### 变更清单

| 文件 | 变更内容 |
|:-----|:--------|
| `src/types/index.ts` | `position` → `title` |
| `src/components/positions/*.vue` | 字段访问更新 |
| `src/api/index.ts` | 请求/响应字段更新 |
| `src/composables/usePositionManagement.ts` | 字段访问更新 |
| `src/composables/usePositionEditor.ts` | 字段访问更新 |

#### 实现细节

**修改前** (`types/index.ts`):
```typescript
export interface PositionData {
  id?: string
  position: string  // 岗位名称
  department?: string
  ...
}
```

**修改后** (`types/index.ts`):
```typescript
export interface PositionData {
  id?: string
  title: string  // 岗位名称（与后端一致）
  /** @deprecated 使用 title 代替，将在下个版本移除 */
  position?: string
  department?: string
  ...
}
```

**后端配合修改** (`Position.to_dict()`):
```python
def to_dict(self):
    return {
        "id": str(self.id),
        "title": self.title,
        # "position": self.title,  # 移除此兼容字段
        ...
    }
```

#### 影响分析

- **前端组件需全局搜索替换**：`.position` → `.title`
- **后端需移除兼容字段**：`Position.to_dict()` 中的 `position` 字段
- **过渡策略**：前端先改，后端再移除

---

### 1.3 前端路由统一

#### 变更清单

| 文件 | 变更内容 |
|:-----|:--------|
| `src/router/index.ts` | `/library` → `/resumes` |
| `src/views/ResumeLibraryView.vue` | 重命名为 `ResumesView.vue` |
| `src/components/layout/AppSidebar.vue` | 导航链接更新 |

#### 实现细节

**修改前** (`router/index.ts`):
```typescript
{
  path: 'library',
  name: 'library',
  component: () => import('@/views/ResumeLibraryView.vue'),
  meta: { title: '简历库 - HRM2招聘管理系统' }
}
```

**修改后** (`router/index.ts`):
```typescript
// 新路由
{
  path: 'resumes',
  name: 'resumes',
  component: () => import('@/views/ResumesView.vue'),
  meta: { title: '简历管理 - HRM2招聘管理系统' }
},
// 旧路由重定向（兼容）
{
  path: 'library',
  redirect: '/resumes'
}
```

#### 影响分析

- **用户书签兼容**：通过重定向保持旧链接可用
- **侧边栏需更新**：导航路径和名称
- **SEO友好**：URL语义更清晰

---

### 1.4 API字段 resume_data_id 统一

#### 变更清单

**前端文件**:
| 文件 | 变更内容 |
|:-----|:--------|
| `src/api/index.ts` | `resume_data_id` → `resume_id` |
| `src/types/index.ts` | 类型字段更新 |
| `src/composables/*.ts` | 相关调用更新 |

**后端文件**:
| 文件 | 变更内容 |
|:-----|:--------|
| `apps/position_settings/views.py` | 移除 `resume_data_ids` 支持 |
| `apps/interview_assist/views.py` | `resume_data_id` → `resume_id` |
| `apps/video_analysis/views.py` | `resume_data_id` → `resume_id` |
| `apps/resume_screening/views.py` | `resume_data_id` → `resume_id` |

#### 实现细节

**阶段一：后端兼容期**
```python
# 同时接受两种参数名
resume_id = data.get('resume_id') or data.get('resume_data_id')
```

**阶段二：前端迁移**
```typescript
// 修改前
{ resume_data_id: resumeId }
// 修改后
{ resume_id: resumeId }
```

**阶段三：后端清理**
```python
# 仅接受新参数名
resume_id = data.get('resume_id')
if not resume_id:
    raise ValidationException("缺少 resume_id 参数")
```

#### 影响分析

- **需分阶段执行**：避免前后端同时改动导致故障
- **全量搜索**：`resume_data_id` 关键词
- **测试覆盖**：所有涉及简历ID的接口

---

## 🟡 Phase 2: 中优先级重构

### 2.1 Screening 模块视图类统一

#### 变更清单

| 原名称 | 新名称 | 说明 |
|:------|:------|:-----|
| `ResumeScreeningView` | `ScreeningSubmitView` | 提交筛选任务 |
| `ResumeDataDetailView` | `ScreeningReportView` | 获取筛选报告 |

#### 实现细节

统一使用 `Screening` 前缀，明确模块归属。

---

### 2.2 面试模块视图类统一

#### 变更清单

| 原名称 | 新名称 | 说明 |
|:------|:------|:-----|
| `SessionListView` | `InterviewSessionListView` | 会话列表 |
| `SessionDetailView` | `InterviewSessionDetailView` | 会话详情 |
| `GenerateQuestionsView` | `InterviewQuestionsView` | 生成问题 |
| `RecordQAView` | `InterviewQAView` | 记录问答 |
| `GenerateReportView` | `InterviewReportView` | 生成报告 |

#### 实现细节

添加 `Interview` 前缀，避免与其他模块的 Session 概念混淆。

---

### 2.3 推荐模块视图类统一

#### 变更清单

| 原名称 | 新名称 |
|:------|:------|
| `CandidateComprehensiveAnalysisView` | `ComprehensiveAnalysisView` |

#### 实现细节

移除 `Candidate` 前缀，与模型名 `ComprehensiveAnalysis` 保持一致。

---

## 🟢 Phase 3: 低优先级重构

### 3.1 后端兼容字段清理

#### 变更清单

| 文件 | 变更内容 |
|:-----|:--------|
| `apps/position_settings/models.py` | `to_dict()` 移除 `position` 字段 |

#### 前置条件

- Phase 1.2 前端迁移完成
- 确认无外部系统依赖旧字段

---

### 3.2 前端类型合并

#### 变更清单

| 操作 | 内容 |
|:-----|:-----|
| 删除 | `ResumeData` 类型 |
| 保留 | `Resume` 类型 |
| 更新 | 所有引用 `ResumeData` 的地方改用 `Resume` |

#### 前置条件

- Phase 1 全部完成
- 确认两个类型的字段已完全对齐

---

## 执行顺序建议

```
Phase 1 (高优先级)
  ├── 1.1 视图类重命名（后端独立，可先行）
  ├── 1.2 PositionData.position → title
  │     ├── 前端类型修改
  │     ├── 前端组件修改
  │     └── 后端移除兼容字段
  ├── 1.3 前端路由 /library → /resumes
  └── 1.4 resume_data_id → resume_id
        ├── 后端添加兼容
        ├── 前端迁移
        └── 后端移除旧字段

Phase 2 (中优先级)
  ├── 2.1 Screening 视图类重命名
  ├── 2.2 Interview 视图类重命名
  └── 2.3 Recommend 视图类重命名

Phase 3 (低优先级)
  ├── 3.1 后端兼容字段清理
  └── 3.2 前端类型合并
```

---

## 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|:----|:----:|:----:|:--------|
| 前端编译失败 | 中 | 高 | 逐文件修改，每步验证 |
| API兼容性问题 | 低 | 高 | 后端先兼容，前端后迁移 |
| 测试用例失败 | 中 | 中 | 同步更新测试 |
| 用户书签失效 | 低 | 低 | 路由重定向兼容 |

---

## 验证清单

### Phase 1 完成标准

- [ ] 后端服务正常启动
- [ ] 前端编译无错误
- [ ] 所有API端点正常响应
- [ ] 前端页面功能正常
- [ ] 无 TypeScript 类型错误

### Phase 2 完成标准

- [ ] 后端视图类命名规范
- [ ] OpenAPI 文档自动更新

### Phase 3 完成标准

- [ ] 无冗余兼容代码
- [ ] 前端类型定义精简
