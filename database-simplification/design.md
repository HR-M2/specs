# Design Document

## Overview

本文档描述HRM2招聘系统数据库简化重构的技术设计方案。目标是将现有11个数据表简化为6个，消除数据冗余，明确模型职责边界。

## Architecture

### 简化后架构（6个表）

```
Position (岗位)
    |
    | 1:N (position_id FK)
    v
Resume (简历) <-- 核心表，合并 ResumeLibrary + ResumeData
    |
    +-- 1:N --> ScreeningTask (筛选任务)
    |
    +-- 1:N --> VideoAnalysis (视频分析)
    |
    +-- 1:N --> InterviewSession (面试会话)
    |
    +-- 1:N --> ComprehensiveAnalysis (综合分析)
```

### 表关系说明

| 关系 | 类型 | 说明 |
|:-----|:-----|:-----|
| Position -> Resume | 1:N | 一个岗位可有多份简历 |
| Resume -> ScreeningTask | 1:N | 一份简历可参与多次筛选任务 |
| Resume -> VideoAnalysis | 1:N | 一份简历可有多个视频分析 |
| Resume -> InterviewSession | 1:N | 一份简历可有多次面试会话 |
| Resume -> ComprehensiveAnalysis | 1:N | 一份简历可有多次综合分析 |

## Data Models

### 1. Position (岗位表)

**文件位置**: `apps/position_settings/models.py`

```python
class Position(models.Model):
    """
    岗位模型 - 简化版
    
    合并原 PositionCriteria 的多个字段为 requirements JSON
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 基本信息
    title = models.CharField(max_length=255, verbose_name="岗位名称")
    department = models.CharField(max_length=255, blank=True, verbose_name="部门")
    description = models.TextField(blank=True, verbose_name="岗位描述")
    
    # 岗位要求（JSON合并）
    requirements = models.JSONField(default=dict, verbose_name="岗位要求")
    # 格式示例:
    # {
    #     "required_skills": ["Python", "Django"],
    #     "optional_skills": ["React", "Docker"],
    #     "min_experience": 3,
    #     "education": ["本科", "硕士"],
    #     "certifications": [],
    #     "salary_range": [15000, 25000]
    # }
    
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    
    class Meta:
        db_table = 'positions'
        ordering = ['-created_at']
```

**字段映射（旧 -> 新）**:
| 原字段 | 新字段 | 说明 |
|:-------|:-------|:-----|
| `position` | `title` | 重命名更清晰 |
| `required_skills` | `requirements["required_skills"]` | 合并到JSON |
| `optional_skills` | `requirements["optional_skills"]` | 合并到JSON |
| `min_experience` | `requirements["min_experience"]` | 合并到JSON |
| `education` | `requirements["education"]` | 合并到JSON |
| `certifications` | `requirements["certifications"]` | 合并到JSON |
| `salary_min/max` | `requirements["salary_range"]` | 合并为数组 |
| `project_requirements` | `requirements["project_requirements"]` | 合并到JSON |
| `resume_count` | **删除** | 动态计算 |

---

### 2. Resume (简历表 - 核心表)

**文件位置**: `apps/resume/models.py` (新建模块)

```python
class Resume(models.Model):
    """
    简历模型 - 核心表
    
    合并原 ResumeLibrary 和 ResumeData
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', '待筛选'
        SCREENED = 'screened', '已筛选'
        INTERVIEWING = 'interviewing', '面试中'
        ANALYZED = 'analyzed', '已分析'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # === 文件信息（原 ResumeLibrary）===
    filename = models.CharField(max_length=255, verbose_name="文件名")
    file_hash = models.CharField(max_length=64, unique=True, verbose_name="文件哈希")
    file_size = models.IntegerField(default=0, verbose_name="文件大小")
    file_type = models.CharField(max_length=50, blank=True, verbose_name="文件类型")
    
    # === 候选人信息 ===
    candidate_name = models.CharField(max_length=100, verbose_name="候选人姓名")
    content = models.TextField(verbose_name="简历内容")
    
    # === 岗位关联（简化，直接外键）===
    position = models.ForeignKey(
        'position_settings.Position',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resumes',
        verbose_name="应聘岗位"
    )
    
    # === 状态管理 ===
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="状态"
    )
    
    # === 筛选结果（内嵌，原 ResumeData 部分字段）===
    screening_result = models.JSONField(null=True, blank=True, verbose_name="筛选结果")
    # 格式示例:
    # {
    #     "score": 85,
    #     "dimensions": {...},
    #     "summary": "..."
    # }
    
    screening_report = models.TextField(null=True, blank=True, verbose_name="筛选报告MD")
    
    # === 备注 ===
    notes = models.TextField(blank=True, verbose_name="备注")
    
    class Meta:
        db_table = 'resumes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['file_hash']),
            models.Index(fields=['candidate_name']),
            models.Index(fields=['status']),
            models.Index(fields=['position']),
        ]
```

**数据合并说明**:

| 原表 | 原字段 | 新字段 | 说明 |
|:-----|:-------|:-------|:-----|
| ResumeLibrary | filename | filename | 保留 |
| ResumeLibrary | file_hash | file_hash | 保留 |
| ResumeLibrary | content | content | 保留 |
| ResumeLibrary | candidate_name | candidate_name | 保留 |
| ResumeLibrary | is_screened | status | 用状态枚举替代 |
| ResumeLibrary | is_assigned | position (FK) | 用外键是否为null判断 |
| ResumeData | screening_score | screening_result | 合并到JSON |
| ResumeData | screening_summary | screening_result | 合并到JSON |
| ResumeData | json_report_content | screening_result | 合并到JSON |
| ResumeData | report_md_file | screening_report | 直接存内容 |
| ResumeData | position_title | **删除** | 从position关联获取 |
| ResumeData | position_details | **删除** | 从position关联获取 |

**删除的模型**:
- `ResumeLibrary` - 合并到 Resume
- `ResumeData` - 合并到 Resume  
- `ResumeGroup` - 用 Position 替代
- `ScreeningReport` - 报告内容存入 Resume
- `ResumePositionAssignment` - 改为直接外键

---

### 3. ScreeningTask (筛选任务表)

**文件位置**: `apps/resume_screening/models.py`

```python
class ScreeningTask(models.Model):
    """
    筛选任务模型 - 简化版
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', '等待中'
        RUNNING = 'running', '进行中'
        COMPLETED = 'completed', '已完成'
        FAILED = 'failed', '失败'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    # 关联岗位
    position = models.ForeignKey(
        'position_settings.Position',
        on_delete=models.CASCADE,
        related_name='screening_tasks',
        verbose_name="岗位"
    )
    
    # 任务状态
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    progress = models.IntegerField(default=0, verbose_name="进度%")
    total_count = models.IntegerField(default=0, verbose_name="总数量")
    processed_count = models.IntegerField(default=0, verbose_name="已处理数量")
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'screening_tasks'
        ordering = ['-created_at']
```

**删除的字段**:
- `current_step` / `total_steps` - 用 progress 百分比替代
- `current_speaker` - Agent相关，移到运行时状态
- `position_data` - 通过 position FK 获取

---

### 4. VideoAnalysis (视频分析表)

**文件位置**: `apps/video_analysis/models.py`

```python
class VideoAnalysis(models.Model):
    """
    视频分析模型 - 简化版
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', '等待分析'
        PROCESSING = 'processing', '分析中'
        COMPLETED = 'completed', '已完成'
        FAILED = 'failed', '失败'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    # 关联简历
    resume = models.ForeignKey(
        'resume.Resume',
        on_delete=models.CASCADE,
        related_name='video_analyses',
        verbose_name="简历"
    )
    
    # 视频信息
    video_file = models.FileField(
        upload_to='videos/%Y/%m/%d/',
        verbose_name="视频文件"
    )
    video_name = models.CharField(max_length=255, verbose_name="视频名称")
    
    # 状态
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    error_message = models.TextField(null=True, blank=True)
    
    # 分析结果（JSON合并）
    analysis_result = models.JSONField(null=True, blank=True)
    # 格式示例:
    # {
    #     "personality": {
    #         "neuroticism": 0.3,
    #         "extraversion": 0.7,
    #         "openness": 0.6,
    #         "agreeableness": 0.8,
    #         "conscientiousness": 0.75
    #     },
    #     "fraud_score": 0.1,
    #     "confidence_score": 0.85,
    #     "summary": "..."
    # }
    
    class Meta:
        db_table = 'video_analyses'
        ordering = ['-created_at']
```

**删除的字段**:
- `candidate_name` - 从 resume 关联获取
- `position_applied` - 从 resume.position 获取
- 多个独立评分字段 - 合并到 `analysis_result` JSON

---

### 5. InterviewSession (面试会话表)

**文件位置**: `apps/interview_assist/models.py`

```python
class InterviewSession(models.Model):
    """
    面试辅助会话模型 - 简化版
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 关联简历
    resume = models.ForeignKey(
        'resume.Resume',
        on_delete=models.CASCADE,
        related_name='interview_sessions',
        verbose_name="简历"
    )
    
    # 问答记录（JSON数组）
    qa_records = models.JSONField(default=list, verbose_name="问答记录")
    # 格式示例:
    # [
    #     {
    #         "round": 1,
    #         "question": "...",
    #         "answer": "...",
    #         "evaluation": {...}
    #     }
    # ]
    
    # 最终报告
    final_report = models.JSONField(null=True, blank=True, verbose_name="面试报告")
    
    class Meta:
        db_table = 'interview_sessions'
        ordering = ['-created_at']
```

**删除的字段**:
- `job_config` - 从 resume.position 获取岗位配置
- `report_file` - 报告直接存JSON

---

### 6. ComprehensiveAnalysis (综合分析表)

**文件位置**: `apps/final_recommend/models.py`

```python
class ComprehensiveAnalysis(models.Model):
    """
    综合分析结果模型 - 简化版
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    # 关联简历
    resume = models.ForeignKey(
        'resume.Resume',
        on_delete=models.CASCADE,
        related_name='comprehensive_analyses',
        verbose_name="简历"
    )
    
    # 评估结果
    final_score = models.FloatField(verbose_name="综合得分")
    
    # 推荐结果（JSON合并）
    recommendation = models.JSONField(verbose_name="推荐结果")
    # 格式示例:
    # {
    #     "level": "A",
    #     "label": "强烈推荐",
    #     "action": "建议尽快发放offer"
    # }
    
    # 维度评分
    dimension_scores = models.JSONField(default=dict, verbose_name="维度评分")
    
    # 综合报告
    report = models.TextField(verbose_name="综合报告")
    
    class Meta:
        db_table = 'comprehensive_analyses'
        ordering = ['-created_at']
```

**删除的字段**:
- `recommendation_level` / `recommendation_label` / `recommendation_action` - 合并到 `recommendation` JSON
- `input_data_snapshot` - 可从关联表获取，不再冗余存储

**删除的模型**:
- `InterviewEvaluationTask` - 废弃功能，直接删除

---

## API Changes

### 需要合并的API

| 原API路径 | 新API路径 | 说明 |
|:----------|:----------|:-----|
| `/api/library/` | `/api/resumes/` | 简历库合并到简历管理 |
| `/api/screening/reports/{id}/` | `/api/resumes/{id}/` | 报告作为简历属性 |

### 需要调整的API

| API路径 | 变更说明 |
|:--------|:---------|
| `/api/positions/{id}/resumes/` | 分配简历改为更新 resume.position_id |
| `/api/screening/` | 任务关联 position_id 而非 position_data |
| `/api/videos/` | 创建时关联 resume_id |

### 保持不变的API

- `/api/positions/` - 岗位CRUD
- `/api/interviews/sessions/` - 面试会话
- `/api/recommend/` - 综合分析

---

## Migration Strategy

### Phase 1: 准备工作
1. 创建新的 `resume` Django app
2. 定义新的简化模型
3. 编写数据迁移脚本

### Phase 2: 数据迁移
1. 迁移 ResumeLibrary 数据到 Resume
2. 合并 ResumeData 数据到对应 Resume
3. 更新外键关联

### Phase 3: 代码迁移
1. 更新 Views 使用新模型
2. 更新 Serializers
3. 更新前端 API 调用

### Phase 4: 清理
1. 删除废弃模型
2. 删除废弃迁移文件
3. 更新文档

---

## Risks and Mitigations

| 风险 | 影响 | 缓解措施 |
|:-----|:-----|:---------|
| 数据丢失 | 高 | 不要求迁移旧数据，重新开始 |
| API不兼容 | 中 | 序列化层做兼容转换 |
| 外键约束问题 | 中 | 分步骤迁移，先创建后关联 |
| 性能下降 | 低 | 添加合适的索引 |
