# 智能优先级任务管理系统 (Smart Priority Todo Manager)

## 📌 项目简介

这是一个基于SQLite的企业级智能任务管理系统，融合了**艾森豪威尔矩阵理论**和**动态权重算法**，实现科学化的任务优先级管理。系统采用统一版本控制设计，提供完整的任务生命周期管理和智能化的决策支持。

### 🎯 核心特性

#### 🧮 智能权重计算系统
- **三大权重系数**: 时间压力 + 任务类型 + 工作量评估
- **动态权重算法**: `基础权重 × (1 + 时间压力 + 类型加成 + 工作量)`
- **权重范围**: 50-240+，精确区分任务优先级
- **透明计算**: 完全可视化的权重计算过程

#### 🎯 艾森豪威尔矩阵
- **Q1 立即执行**: 紧急且重要 (urgent_important)
- **Q2 计划安排**: 重要但不紧急 (important)  
- **Q3 委托处理**: 紧急但不重要 (urgent)
- **Q4 消除删除**: 既不紧急也不重要 (normal)

#### ⏰ 动态时间压力感知
- **已逾期**: +50% 权重加成
- **今明截止**: +40% 权重加成  
- **3天内**: +30% 权重加成
- **1周内**: +20% 权重加成
- **自动计算**: 基于当前日期和截止日期

#### 🏷️ 12种任务类型分类
```
[紧急响应] emergency(+40%), security(+40%), bug_fix(+35%)
[业务核心] client(+30%), deadline(+30%), development(+20%)  
[协调沟通] meeting(+25%), communication(+15%)
[支撑运营] maintenance(+8%), routine(+5%)
[发展提升] research(+12%)
[通用任务] general(+0%)
```

#### 🔧 完整任务管理
- **📝 统一版本控制**: 每个操作创建新版本，完整追踪历史
- **💾 数据安全**: 软删除机制，支持导出导入备份
- **⚡ 高性能**: 优化的SQL查询，高效的数据操作
- **🌟 用户友好**: 直观的命令行界面，丰富的可视化信息

## 🏗️ 系统架构

### 数据库设计
```sql
todo_unified 表结构:
- id: 主键 (AUTOINCREMENT)
- task_uuid: 任务唯一标识符
- version: 版本号 (自动递增)
- task: 任务名称
- status: 状态 (todo/in_progress/completed)
- priority: 优先级 (urgent_important/important/urgent/normal)
- due_date: 截止日期
- task_type: 任务类型 (12种分类)
- estimated_hours: 预估工时
- operation_type: 操作类型
- change_summary: 变更说明
- created_at: 创建时间
- updated_at: 更新时间
```

### 智能权重算法
```python
动态权重 = 基础权重 × (1 + 时间压力系数 + 任务类型系数 + 工作量系数)

基础权重:
- urgent_important: 100 (Q1象限)
- important: 80 (Q2象限)
- urgent: 70 (Q3象限)  
- normal: 50 (Q4象限)
```

## 📥 安装和使用

### 系统要求
- Python 3.6+
- SQLite3 (内置)

### 快速开始
```bash
# 创建任务 (完整参数)
python3 todo_manager.py create "修复生产Bug" urgent_important 2025-11-20 bug_fix 3

# 创建任务 (简化)
python3 todo_manager.py create "开会讨论需求"

# 查看智能矩阵
python3 todo_manager.py matrix

# 查看智能列表
python3 todo_manager.py list
```

## 🎯 主要功能

### 📋 任务管理
```bash
# 创建任务
python3 todo_manager.py create "任务内容" [priority] [due_date] [task_type] [hours]

# 更新任务  
python3 todo_manager.py update <UUID> <field> <value>

# 查看任务详情
python3 todo_manager.py show <UUID>

# 删除任务
python3 todo_manager.py delete <UUID>
```

### 🎯 智能优先级功能
```bash
# 艾森豪威尔矩阵 (推荐)
python3 todo_manager.py matrix

# 智能优先级列表
python3 todo_manager.py list [status]

# 详细任务分析
python3 todo_manager.py analyze <UUID>
```

### 📊 数据管理
```bash
# 导出数据
python3 todo_manager.py export [filepath]

# 导入数据
python3 todo_manager.py import <filepath>

# 搜索任务
python3 todo_manager.py search "关键词"
```

## 🏆 智能权重示例

### 高优先级任务组合
```bash
# 权重: ~190 (紧急生产问题)
create "修复支付系统崩溃" urgent_important 2025-11-18 emergency 4

# 权重: ~152 (重要安全问题)  
create "修复用户数据泄露" important 2025-11-19 security 8

# 权重: ~132 (重要开发任务)
create "完成核心功能开发" important 2025-11-21 development 16
```

### 中低优先级任务
```bash
# 权重: ~75 (常规会议)
create "周例会" normal 2025-11-25 meeting 1

# 权重: ~56 (维护任务)
create "清理日志文件" normal "" maintenance 2
```

## 📈 企业应用价值

### 🎯 科学决策支持
- **量化优先级**: 基于时间管理理论的权重算法
- **透明过程**: 完全可视化的权重计算逻辑  
- **动态调整**: 自动感知时间压力变化

### 📊 提升工作效率
- **智能排序**: 自动按权重排列任务
- **四象限管理**: 基于艾森豪威尔矩阵分类
- **类型感知**: 12种任务类型精确加权

### 🔧 企业级特性
- **数据完整性**: 完整的版本控制和历史追踪
- **高可靠性**: SQLite数据库确保数据安全
- **易于集成**: 命令行接口便于自动化集成

## 🎊 系统优势

✨ **科学算法** - 基于时间管理理论的权重计算  
🎯 **精确排序** - 240+权重级别精确区分优先级  
⏰ **时间感知** - 动态感知时间压力自动调权  
🏷️ **类型丰富** - 12种任务类型覆盖企业场景  
📊 **可视化强** - 艾森豪威尔矩阵直观展示  
🚀 **性能优秀** - SQLite高性能数据存储  
🔧 **功能完整** - 企业级任务管理全功能  

---

**这是一个真正面向企业实战的智能任务优先级管理系统！** 🏆
