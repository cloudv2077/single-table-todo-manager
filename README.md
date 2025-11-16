# 单表任务管理系统 (Single-Table Todo Manager)

## 📌 项目简介

这是一个基于SQLite的单表任务管理系统，采用创新的统一版本控制设计，实现了完整的任务生命周期管理。该系统使用单个数据库表存储所有任务和版本历史，确保数据的完整性和一致性。

### 🎯 核心特性

- **🔧 统一版本控制**: 每个操作都创建新版本，完整追踪任务历史
- **📝 完整任务管理**: 创建、更新、状态管理、删除和恢复
- **🔍 智能查询**: 支持多种筛选、搜索和统计功能
- **💾 数据安全**: 软删除机制，支持导出导入备份
- **⚡ 高性能**: 优化的SQL查询，高效的数据操作
- **🌟 用户友好**: 直观的命令行界面，丰富的可视化信息

## 🏗️ 系统架构

### 数据库设计
```
todo_unified 表结构:
- id: 主键 (AUTOINCREMENT)
- task_uuid: 任务唯一标识符
- version: 版本号 (自动递增)
- task: 任务名称
- status: 状态 (todo/in_progress/completed)
- priority: 优先级 (low/medium/high)
- due_date: 截止日期
- operation_type: 操作类型 (create/update/delete/restore等)
- change_summary: 变更说明
- created_at: 创建时间
- updated_at: 更新时间
```

### 版本控制机制
- 每次任务操作创建新版本记录
- 当前状态通过MAX(version)查询获取
- 完整的操作历史保存永不丢失
- 支持软删除和恢复机制

## 📥 安装和配置

### 系统要求
- Python 3.6+
- SQLite3 (Python内置)
- macOS/Linux/Windows

### 安装步骤
1. 克隆或下载项目文件
2. 确保Python环境正常
3. 运行系统命令测试

```bash
# 测试系统安装
python3 todo_manager.py version
```

## 🚀 使用指南

### 基础命令

#### 查看帮助和版本信息
```bash
# 显示详细帮助信息
python3 todo_manager.py help

# 显示系统版本
python3 todo_manager.py version

# 清屏
python3 todo_manager.py clear
```

#### 任务管理
```bash
# 创建新任务
python3 todo_manager.py create "完成项目文档" high
python3 todo_manager.py create "设计用户界面" medium
python3 todo_manager.py create "优化性能" low

# 列出所有任务
python3 todo_manager.py list

# 按状态筛选任务
python3 todo_manager.py list todo
python3 todo_manager.py list in_progress
python3 todo_manager.py list completed

# 显示任务详情
python3 todo_manager.py show <task_uuid>

# 更新任务信息
python3 todo_manager.py update <task_uuid> task "新的任务名称"
python3 todo_manager.py update <task_uuid> priority high
python3 todo_manager.py update <task_uuid> due_date "2025-12-31"

# 更新任务状态
python3 todo_manager.py status <task_uuid> in_progress
python3 todo_manager.py status <task_uuid> completed
python3 todo_manager.py status <task_uuid> todo
```

#### 删除和恢复
```bash
# 软删除任务
python3 todo_manager.py delete <task_uuid>

# 恢复已删除的任务
python3 todo_manager.py restore <task_uuid>

# 清除所有已完成的任务
python3 todo_manager.py clear_completed
```

### 高级功能

#### 搜索和筛选
```bash
# 关键词搜索任务
python3 todo_manager.py search "文档"
python3 todo_manager.py search "界面"
python3 todo_manager.py search "性能"

# 按状态筛选
python3 todo_manager.py filter_by_status todo
python3 todo_manager.py filter_by_status in_progress
python3 todo_manager.py filter_by_status completed

# 按优先级筛选
python3 todo_manager.py filter_by_priority high
python3 todo_manager.py filter_by_priority medium
python3 todo_manager.py filter_by_priority low

# 显示逾期任务
python3 todo_manager.py overdue

# 显示任务统计
python3 todo_manager.py stats

# 显示任务历史
python3 todo_manager.py history <task_uuid>
```

#### 数据管理
```bash
# 导出数据到JSON文件
python3 todo_manager.py export backup.json

# 从JSON文件导入数据
python3 todo_manager.py import backup.json
```

## 💡 使用示例

### 完整的工作流程示例

```bash
# 1. 创建多个任务
python3 todo_manager.py create "需求分析" high
python3 todo_manager.py create "原型设计" medium
python3 todo_manager.py create "代码实现" high
python3 todo_manager.py create "测试验证" medium
python3 todo_manager.py create "文档编写" low

# 2. 查看任务列表
python3 todo_manager.py list

# 3. 更新任务状态
python3 todo_manager.py status <需求分析的UUID> in_progress
python3 todo_manager.py status <原型设计的UUID> completed

# 4. 按优先级查看高优先级任务
python3 todo_manager.py filter_by_priority high

# 5. 搜索特定任务
python3 todo_manager.py search "设计"

# 6. 完成一些任务
python3 todo_manager.py status <代码实现的UUID> completed
python3 todo_manager.py status <测试验证的UUID> completed

# 7. 查看统计信息
python3 todo_manager.py stats

# 8. 清除已完成的任务
python3 todo_manager.py clear_completed

# 9. 备份数据
python3 todo_manager.py export final_backup.json

# 10. 查看最终状态
python3 todo_manager.py list
```

## 📊 输出格式说明

### 任务列表格式
```
任务UUID                               任务名称                           状态           优先级      版本    
────────────────────────────────────────────────────────────────────────────────────────────────────
a0243b38-3d69-40c5-88e6-37249a79aa4b 完成项目文档                         🟡in_progress 🔴high    2
new-uuid-1763281013                  设计用户界面                         🔴todo        🟡medium  1
cba39d46-2908-4323-a2c0-b8b4c830dacc 更新网站首页                         ✅completed   🔴high    3

📊 总计: 3 个任务
```

### 图标说明
- **状态图标**: 🔴 todo, 🟡 in_progress, ✅ completed
- **优先级图标**: 🟢 low, 🟡 medium, 🔴 high

### 任务详情格式
```
📋 任务详情:
UUID: 3578a9c2-f8c2-4f65-8f4f-0948f5605cec
任务: 完成项目文档
状态: in_progress (版本: 2)
优先级: high
截止日期: 2025-11-20
最后更新: 2025-11-16 07:36:13

📜 变更历史:
版本  状态           操作类型        变更说明                           时间                 
────────────────────────────────────────────────────────────────────────────────────────--
1     todo           create          Task created                       2025-11-16 07:36:05  
2     in_progress    status_change   Status changed from todo to in_progress 2025-11-16 07:36:13
```

## 🔧 技术特性

### 数据库优化
- 索引优化: task_uuid 和 status 字段建立索引
- 查询优化: 使用JOIN子查询获取最新版本
- 事务保证: 所有操作都在事务中执行

### 版本控制机制
- 每次操作自动递增版本号
- 完整保存变更历史
- 当前状态通过MAX(version)获取
- 支持软删除和恢复

### 数据安全
- 软删除机制: 任务不直接删除，而是标记为删除状态
- 数据备份: 完整的导出导入功能
- 历史保护: 所有变更历史永不丢失

## ⚠️ 注意事项

### 数据库文件
- 默认数据库文件: `simple.db`
- 建议定期备份数据库文件
- 导入导出功能可以用于数据迁移

### UUID使用
- 每个任务都有唯一的UUID
- UUID用于标识任务，不因操作而改变
- 恢复操作使用原来的UUID

### 状态管理
- 任务状态: todo → in_progress → completed
- 可以逆向操作 (completed → in_progress → todo)
- 软删除任务不显示在常规列表中

### 优先级说明
- high: 高优先级，重要紧急任务
- medium: 中优先级，一般任务
- low: 低优先级，可延后任务

## 🐛 故障排除

### 常见问题

#### 1. 命令未找到
```bash
# 检查Python环境
python3 --version

# 检查文件是否存在
ls -la todo_manager.py

# 使用完整路径
/Users/your/path/to/todo_manager.py version
```

#### 2. 数据库错误
```bash
# 检查数据库文件权限
ls -la simple.db

# 重新创建数据库
rm simple.db
python3 todo_manager.py create "测试任务"
```

#### 3. 参数错误
```bash
# 查看帮助信息
python3 todo_manager.py help

# 检查UUID格式
python3 todo_manager.py show invalid-uuid
```

#### 4. 导入导出问题
```bash
# 检查JSON文件格式
cat backup.json | python3 -m json.tool

# 确认文件路径正确
ls -la backup.json
```

### 日志调试
如果遇到问题，可以：
1. 检查Python版本兼容性
2. 确认SQLite3模块正常
3. 验证文件路径和权限
4. 查看完整的错误信息

## 🔮 扩展开发

### 添加新功能
系统设计支持轻松添加新功能:
1. 在TodoManager类中添加新方法
2. 在main()函数中添加新的命令处理
3. 更新help()方法的帮助信息

### 自定义字段
可以轻松添加新的任务字段:
1. 修改数据库表结构
2. 更新相关方法
3. 处理数据迁移

### 界面改进
当前是命令行界面，可以扩展为:
- Web界面
- GUI界面
- API服务

## 📄 许可证

本项目采用MIT许可证，允许自由使用和修改。

## 👤 作者

Claude Code Assistant - 基于AI的任务管理系统开发助手

## 📅 更新日志

### v2.4.0 (2025-11-16)
- ✅ 完整功能实现
- ✅ 导入导出功能
- ✅ 版本控制系统
- ✅ 完整错误处理
- ✅ 用户友好界面

### v2.3.0 (2025-11-16)
- 🔧 修复查询逻辑问题
- ✅ 正确处理删除任务显示
- ✅ 优化数据库查询性能

### v2.2.0 (2025-11-16)
- 🔧 修复clear_completed功能
- ✅ 解决NoneType错误
- ✅ 完善版本控制逻辑

### v2.1.0 (2025-11-16)
- 🎯 核心功能开发
- 📝 任务CRUD操作
- 🔍 搜索和筛选功能
- 📊 统计和历史功能

---

**🎉 感谢使用单表任务管理系统！**

如有问题或建议，请查看帮助信息或联系开发者。
