#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单表任务管理系统 - 完整版本
包含导入导出功能
"""

import sqlite3
import sys
import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

class TodoManager:
    def __init__(self, db_path: str = "/Users/cloudv/Desktop/todo-sqlite/simple.db"):
        """初始化任务管理器"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todo_unified (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_uuid TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    task TEXT NOT NULL,
                    status TEXT CHECK(status IN ('todo', 'in_progress', 'completed')) DEFAULT 'todo',
                    priority TEXT CHECK(priority IN ('urgent_important', 'important', 'urgent', 'normal')) DEFAULT 'normal',
                    due_date DATE,
                    operation_type TEXT CHECK(operation_type IN ('create', 'update', 'status_change', 'delete', 'restore', 'current_snapshot', 'migration')) DEFAULT 'update',
                    change_summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_uuid ON todo_unified(task_uuid)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON todo_unified(status)')
            conn.commit()
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
🎯 单表任务管理系统 - 帮助指南

📋 可用命令:
───────────────────────────────────────────────────────────────────────────────

🔧 基础操作:
  help                    - 显示此帮助信息
  version                 - 显示系统版本信息
  clear                   - 清屏

📝 任务管理:
  list [status]           - 列出所有任务 (可选按状态过滤: todo/in_progress/completed)
  show <task_uuid>        - 显示任务详情和完整历史
  create <task_name> [priority] - 创建新任务 (优先级: urgent_important/important/urgent/normal)
  update <task_uuid> <field> <value> - 更新任务信息 (field: task/priority/due_date)
  status <task_uuid> <status> - 更新任务状态 (todo/in_progress/completed)
  
🗑️ 删除和恢复:
  delete <task_uuid>      - 软删除任务
  restore <task_uuid>     - 恢复已删除的任务
  clear_completed         - 清除所有已完成的任务
  
📊 历史与统计:
  history <task_uuid>     - 显示任务变更历史
  stats                   - 显示任务统计信息
  search <keyword>        - 搜索任务
  
🔍 筛选操作:
  overdue                 - 显示逾期任务
  
💾 数据操作:
  export <file>           - 导出任务数据到JSON文件
  import <file>           - 从JSON文件导入任务数据
  
───────────────────────────────────────────────────────────────────────────────
💡 示例用法:
  python3 todo_manager.py create "完成项目文档" high
  python3 todo_manager.py list completed
  python3 todo_manager.py status abc123 in_progress
  python3 todo_manager.py delete abc123
  python3 todo_manager.py restore abc123
  python3 todo_manager.py export backup.json
  python3 todo_manager.py import backup.json
        """
        print(help_text)
    
    def show_version(self):
        """显示版本信息"""
        print("📌 单表任务管理系统 v2.4.1")
        print("🔧 基于SQLite的统一版本控制设计 - 完整版")
        print("👤 作者: cloudv2077")
        print(f"📅 版本日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def list_tasks(self, status_filter: Optional[str] = None):
        """列出任务"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if status_filter:
                cursor.execute('''
                    SELECT 
                        u.task_uuid,
                        u.task,
                        u.status,
                        u.priority,
                        u.due_date,
                        u.version as current_version,
                        u.created_at as last_updated
                    FROM todo_unified u
                    JOIN (
                        SELECT task_uuid, MAX(version) as max_version
                        FROM todo_unified 
                        GROUP BY task_uuid
                    ) latest ON u.task_uuid = latest.task_uuid AND u.version = latest.max_version
                    WHERE u.operation_type != 'delete' AND u.status = ?
                    ORDER BY 
                        CASE u.status 
                            WHEN 'in_progress' THEN 1
                            WHEN 'todo' THEN 2
                            WHEN 'completed' THEN 3
                        END,
                        u.created_at DESC
                ''', (status_filter,))
            else:
                cursor.execute('''
                    SELECT 
                        u.task_uuid,
                        u.task,
                        u.status,
                        u.priority,
                        u.due_date,
                        u.version as current_version,
                        u.created_at as last_updated
                    FROM todo_unified u
                    JOIN (
                        SELECT task_uuid, MAX(version) as max_version
                        FROM todo_unified 
                        GROUP BY task_uuid
                    ) latest ON u.task_uuid = latest.task_uuid AND u.version = latest.max_version
                    WHERE u.operation_type != 'delete'
                    ORDER BY 
                        CASE u.status 
                            WHEN 'in_progress' THEN 1
                            WHEN 'todo' THEN 2
                            WHEN 'completed' THEN 3
                        END,
                        u.created_at DESC
                ''')
            
            tasks = cursor.fetchall() or []
            
            if not tasks:
                print("📋 暂无任务")
                return
            
            # 显示表头
            print(f"{'任务UUID':<36} {'任务名称':<30} {'状态':<12} {'优先级':<8} {'版本':<6}")
            print("─" * 100)
            
            for task in tasks:
                status_icon = {"todo": "🔴", "in_progress": "🟡", "completed": "✅"}
                priority_icons = {"urgent_important": "🔴", "important": "🟡", "urgent": "🟠", "normal": "🟢"}
                
                print(f"{task[0]:<36} {task[1]:<30} {status_icon.get(task[2], '❓')}{task[2]:<11} {priority_icons.get(task[3], '❓')}{task[3]:<7} {task[5]}")
            
            print(f"\n📊 总计: {len(tasks)} 个任务")
    
    def show_task(self, task_uuid: str):
        """显示任务详情"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取任务基本信息
            cursor.execute('''
                SELECT 
                    u.task_uuid,
                    u.task,
                    u.status,
                    u.priority,
                    u.due_date,
                    u.version as current_version,
                    u.created_at as last_updated
                FROM todo_unified u
                JOIN (
                    SELECT task_uuid, MAX(version) as max_version
                    FROM todo_unified 
                    GROUP BY task_uuid
                ) latest ON u.task_uuid = latest.task_uuid AND u.version = latest.max_version
                WHERE u.task_uuid = ? AND u.operation_type != 'delete'
            ''', (task_uuid,))
            
            task_info = cursor.fetchone()
            
            if not task_info:
                print(f"❌ 未找到UUID为 {task_uuid} 的任务或任务已删除")
                return
            
            # 获取完整历史
            cursor.execute('''
                SELECT 
                    version,
                    status,
                    operation_type,
                    change_summary,
                    created_at
                FROM todo_unified 
                WHERE task_uuid = ?
                ORDER BY version
            ''', (task_uuid,))
            
            history = cursor.fetchall() or []
            
            # 显示任务信息
            print(f"\n📋 任务详情:")
            print(f"UUID: {task_info[0]}")
            print(f"任务: {task_info[1]}")
            print(f"状态: {task_info[2]} (版本: {task_info[5]})")
            print(f"优先级: {task_info[3]}")
            print(f"截止日期: {task_info[4] or '未设置'}")
            print(f"最后更新: {task_info[6]}")
            
            print(f"\n📜 变更历史:")
            if not history:
                print("📝 暂无变更历史")
            else:
                print(f"{'版本':<6} {'状态':<12} {'操作类型':<15} {'变更说明':<30} {'时间':<20}")
                print("─" * 90)
                
                for record in history:
                    print(f"{record[0]:<6} {record[1]:<12} {record[2]:<15} {record[3]:<30} {record[4]}")
    
    def create_task(self, task_name: str, priority: str = "normal"):
        """创建新任务"""
        task_uuid = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO todo_unified (
                    task_uuid, version, task, status, priority, operation_type, change_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (task_uuid, 1, task_name, "todo", priority, "create", "Task created"))
            
            conn.commit()
            print(f"✅ 任务创建成功: {task_name}")
            print(f"🔗 UUID: {task_uuid}")
            print(f"🎯 状态: todo")
            print(f"📊 优先级: {priority}")
    
    def update_task(self, task_uuid: str, field: str, value: str):
        """更新任务信息"""
        valid_fields = ['task', 'priority', 'due_date']
        if field not in valid_fields:
            print(f"❌ 无效字段: {field}. 有效字段: {', '.join(valid_fields)}")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查任务是否存在且未删除
            cursor.execute('''
                SELECT MAX(version), status FROM todo_unified 
                WHERE task_uuid = ? AND operation_type != 'delete'
                GROUP BY task_uuid
            ''', (task_uuid,))
            
            result = cursor.fetchone()
            if not result:
                print(f"❌ 未找到UUID为 {task_uuid} 的任务或任务已删除")
                return
            
            current_version, current_status = result
            new_version = current_version + 1
            
            # 插入新版本记录
            cursor.execute('''
                INSERT INTO todo_unified (
                    task_uuid, version, task, status, priority, due_date, operation_type, change_summary
                ) SELECT 
                    ?, ?, task, ?, priority, due_date, 'update', ?
                FROM todo_unified 
                WHERE task_uuid = ? AND version = ?
            ''', (task_uuid, new_version, current_status, f"Updated {field}: {value}", task_uuid, current_version))
            
            # 更新具体字段
            if field == 'task':
                cursor.execute('UPDATE todo_unified SET task = ?, updated_at = CURRENT_TIMESTAMP WHERE task_uuid = ? AND version = ?', (value, task_uuid, new_version))
            elif field == 'priority':
                cursor.execute('UPDATE todo_unified SET priority = ?, updated_at = CURRENT_TIMESTAMP WHERE task_uuid = ? AND version = ?', (value, task_uuid, new_version))
            elif field == 'due_date':
                cursor.execute('UPDATE todo_unified SET due_date = ?, updated_at = CURRENT_TIMESTAMP WHERE task_uuid = ? AND version = ?', (value, task_uuid, new_version))
            
            conn.commit()
            print(f"✅ 任务更新成功: {field} = {value}")
    
    def update_status(self, task_uuid: str, new_status: str):
        """更新任务状态"""
        valid_statuses = ['todo', 'in_progress', 'completed']
        if new_status not in valid_statuses:
            print(f"❌ 无效状态: {new_status}. 有效状态: {', '.join(valid_statuses)}")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查任务是否存在且未删除
            cursor.execute('''
                SELECT MAX(version), status, task, priority FROM todo_unified 
                WHERE task_uuid = ? AND operation_type != 'delete'
                GROUP BY task_uuid
            ''', (task_uuid,))
            
            result = cursor.fetchone()
            if not result:
                print(f"❌ 未找到UUID为 {task_uuid} 的任务或任务已删除")
                return
            
            current_version, current_status, task_name, priority = result
            new_version = current_version + 1
            
            # 插入新状态记录
            cursor.execute('''
                INSERT INTO todo_unified (
                    task_uuid, version, task, status, priority, operation_type, change_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_uuid, new_version, task_name, new_status, priority, 
                'status_change', 
                f"Status changed from {current_status} to {new_status}"
            ))
            
            conn.commit()
            print(f"✅ 状态更新成功: {current_status} → {new_status}")
            print(f"📋 任务: {task_name}")
            print(f"🎯 版本: {current_version} → {new_version}")
    
    def delete_task(self, task_uuid: str):
        """软删除任务"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查任务是否存在且未删除
            cursor.execute('''
                SELECT MAX(version), task, status, priority FROM todo_unified 
                WHERE task_uuid = ? AND operation_type != 'delete'
                GROUP BY task_uuid
            ''', (task_uuid,))
            
            result = cursor.fetchone()
            if not result:
                print(f"❌ 未找到UUID为 {task_uuid} 的任务或任务已删除")
                return
            
            current_version, task_name, current_status, priority = result
            new_version = current_version + 1
            
            # 插入删除记录
            cursor.execute('''
                INSERT INTO todo_unified (
                    task_uuid, version, task, status, priority, operation_type, change_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_uuid, new_version, task_name, current_status, priority, 
                'delete', 
                f"Task deleted: {task_name}"
            ))
            
            conn.commit()
            print(f"🗑️ 任务删除成功: {task_name}")
            print(f"🔗 UUID: {task_uuid}")
            print(f"💡 可以使用 'restore {task_uuid}' 命令恢复")
    
    def restore_task(self, task_uuid: str):
        """恢复已删除的任务"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查是否存在删除记录
            cursor.execute('''
                SELECT MAX(version), task, status, priority FROM todo_unified 
                WHERE task_uuid = ?
                GROUP BY task_uuid
            ''', (task_uuid,))
            
            result = cursor.fetchone()
            if not result:
                print(f"❌ 未找到UUID为 {task_uuid} 的任务")
                return
            
            current_version, task_name, current_status, priority = result
            
            # 检查最后一条记录是否是删除操作
            cursor.execute('''
                SELECT operation_type FROM todo_unified 
                WHERE task_uuid = ? AND version = ?
            ''', (task_uuid, current_version))
            
            last_operation = cursor.fetchone()
            if not last_operation or last_operation[0] != 'delete':
                print(f"❌ 任务 {task_uuid} 尚未删除，无法恢复")
                return
            
            new_version = current_version + 1
            
            # 插入恢复记录
            cursor.execute('''
                INSERT INTO todo_unified (
                    task_uuid, version, task, status, priority, operation_type, change_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_uuid, new_version, task_name, current_status, priority, 
                'restore', 
                f"Task restored: {task_name}"
            ))
            
            conn.commit()
            print(f"♻️ 任务恢复成功: {task_name}")
            print(f"🔗 UUID: {task_uuid}")
            print(f"🎯 状态: {current_status}")
    
    def clear_completed_tasks(self):
        """清除所有已完成的任务"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取所有已完成的任务
            cursor.execute('''
                SELECT 
                    u.task_uuid,
                    u.task,
                    u.version as current_version,
                    u.priority
                FROM todo_unified u
                JOIN (
                    SELECT task_uuid, MAX(version) as max_version
                    FROM todo_unified 
                    GROUP BY task_uuid
                ) latest ON u.task_uuid = latest.task_uuid AND u.version = latest.max_version
                WHERE u.status = 'completed' AND u.operation_type != 'delete'
            ''')
            
            completed_tasks = cursor.fetchall() or []
            
            if not completed_tasks:
                print("📋 没有已完成的任务需要清除")
                return
            
            print(f"🧹 找到 {len(completed_tasks)} 个已完成的任务")
            
            # 批量删除
            deleted_count = 0
            for task_uuid, task_name, current_version, priority in completed_tasks:
                new_version = current_version + 1
                cursor.execute('''
                    INSERT INTO todo_unified (
                        task_uuid, version, task, status, priority, operation_type, change_summary
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task_uuid, new_version, task_name, 'completed', priority, 
                    'delete', 
                    f"Completed task cleared: {task_name}"
                ))
                deleted_count += 1
            
            conn.commit()
            print(f"✅ 已清除 {deleted_count} 个已完成的任务")
    
    
    
    def show_overdue_tasks(self):
        """显示逾期任务"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    u.task_uuid,
                    u.task,
                    u.status,
                    u.due_date,
                    u.version as current_version
                FROM todo_unified u
                JOIN (
                    SELECT task_uuid, MAX(version) as max_version
                    FROM todo_unified 
                    GROUP BY task_uuid
                ) latest ON u.task_uuid = latest.task_uuid AND u.version = latest.max_version
                WHERE u.operation_type != 'delete' AND u.due_date < ? AND u.status != 'completed'
                ORDER BY u.due_date ASC
            ''', (today,))
            
            overdue_tasks = cursor.fetchall() or []
            
            if not overdue_tasks:
                print("🎉 没有逾期任务！")
                return
            
            print(f"⏰ 逾期任务 (截止日期早于 {today}):")
            print(f"{'任务UUID':<36} {'任务名称':<30} {'状态':<12} {'截止日期':<12}")
            print("─" * 95)
            
            for task in overdue_tasks:
                status_icon = {"todo": "🔴", "in_progress": "🟡", "completed": "✅"}
                
                print(f"{task[0]:<36} {task[1]:<30} {status_icon.get(task[2], '❓')}{task[2]:<11} {task[3]}")
            
            print(f"\n📊 总计: {len(overdue_tasks)} 个逾期任务")
    
    def search_tasks(self, keyword: str):
        """搜索任务"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    u.task_uuid,
                    u.task,
                    u.status,
                    u.priority,
                    u.version as current_version
                FROM todo_unified u
                JOIN (
                    SELECT task_uuid, MAX(version) as max_version
                    FROM todo_unified 
                    GROUP BY task_uuid
                ) latest ON u.task_uuid = latest.task_uuid AND u.version = latest.max_version
                WHERE u.operation_type != 'delete' AND u.task LIKE ?
                ORDER BY u.version DESC
            ''', (f'%{keyword}%',))
            
            results = cursor.fetchall() or []
            
            if not results:
                print(f"🔍 未找到包含关键词 '{keyword}' 的任务")
                return
            
            print(f"🔍 搜索结果 (关键词: {keyword})")
            print(f"{'任务UUID':<36} {'任务名称':<30} {'状态':<12} {'优先级':<8}")
            print("─" * 90)
            
            for result in results:
                status_icon = {"todo": "🔴", "in_progress": "🟡", "completed": "✅"}
                priority_icons = {"urgent_important": "🔴", "important": "🟡", "urgent": "🟠", "normal": "🟢"}
                
                print(f"{result[0]:<36} {result[1]:<30} {status_icon.get(result[2], '❓')}{result[2]:<11} {priority_icons.get(result[3], '❓')}{result[3]:<7}")
            
            print(f"\n📊 找到 {len(results)} 个匹配的任务")
    
    def show_stats(self):
        """显示统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 状态统计
            cursor.execute('''
                SELECT 
                    u.status,
                    COUNT(DISTINCT u.task_uuid) as count
                FROM todo_unified u
                JOIN (
                    SELECT task_uuid, MAX(version) as max_version
                    FROM todo_unified 
                    GROUP BY task_uuid
                ) latest ON u.task_uuid = latest.task_uuid AND u.version = latest.max_version
                WHERE u.operation_type != 'delete'
                GROUP BY u.status
            ''')
            
            status_stats = cursor.fetchall() or []
            
            # 优先级统计
            cursor.execute('''
                SELECT 
                    u.priority,
                    COUNT(DISTINCT u.task_uuid) as count
                FROM todo_unified u
                JOIN (
                    SELECT task_uuid, MAX(version) as max_version
                    FROM todo_unified 
                    GROUP BY task_uuid
                ) latest ON u.task_uuid = latest.task_uuid AND u.version = latest.max_version
                WHERE u.operation_type != 'delete'
                GROUP BY u.priority
            ''')
            
            priority_stats = cursor.fetchall() or []
            
            # 总版本数
            cursor.execute('SELECT COUNT(*) FROM todo_unified')
            total_versions = cursor.fetchone()[0]
            
            print("📊 任务统计信息")
            print("=" * 50)
            
            print("\n🎯 按状态分布:")
            for status, count in status_stats:
                status_icon = {"todo": "🔴", "in_progress": "🟡", "completed": "✅"}
                print(f"  {status_icon.get(status, '❓')} {status}: {count} 个")
            
            print("\n📈 按优先级分布:")
            for priority, count in priority_stats:
                priority_icons = {"urgent_important": "🔴", "important": "🟡", "urgent": "🟠", "normal": "🟢"}
                print(f"  {priority_icons.get(priority, '❓')} {priority}: {count} 个")
            
            print(f"\n💾 数据统计:")
            print(f"  📋 任务版本总数: {total_versions}")
    
    def export_data(self, filename: str):
        """导出数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM todo_unified ORDER BY task_uuid, version')
            all_records = cursor.fetchall() or []
            
            # 获取列名
            column_names = [description[0] for description in cursor.description]
            
            # 转换为字典格式
            export_data = []
            for record in all_records:
                record_dict = dict(zip(column_names, record))
                export_data.append(record_dict)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 数据已导出到: {filename}")
            print(f"📊 导出记录数: {len(export_data)}")
    
    def import_data(self, filename: str):
        """导入数据"""
        if not os.path.exists(filename):
            print(f"❌ 文件不存在: {filename}")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ JSON格式错误: {e}")
            return
        except Exception as e:
            print(f"❌ 读取文件错误: {e}")
            return
        
        if not import_data:
            print("❌ 导入文件为空")
            return
        
        # 获取数据库列名
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('PRAGMA table_info(todo_unified)')
            db_columns = [column[1] for column in cursor.fetchall()]
            
            imported_count = 0
            skipped_count = 0
            
            for record in import_data:
                try:
                    # 检查必要字段
                    if 'task_uuid' not in record or 'version' not in record or 'task' not in record:
                        print(f"⚠️ 跳过不完整记录: {record}")
                        skipped_count += 1
                        continue
                    
                    # 构建插入数据
                    insert_data = []
                    for col in db_columns:
                        if col in record:
                            insert_data.append(record[col])
                        else:
                            insert_data.append(None)
                    
                    # 插入记录
                    placeholders = ','.join(['?' for _ in db_columns])
                    cursor.execute(f'''
                        INSERT INTO todo_unified ({','.join(db_columns)})
                        VALUES ({placeholders})
                    ''', insert_data)
                    
                    imported_count += 1
                    
                except Exception as e:
                    print(f"⚠️ 跳过记录 (错误: {e}): {record}")
                    skipped_count += 1
            
            conn.commit()
            
            print(f"✅ 数据导入完成!")
            print(f"📊 成功导入: {imported_count} 条记录")
            if skipped_count > 0:
                print(f"⚠️ 跳过: {skipped_count} 条记录")
            print(f"📁 导入文件: {filename}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("❌ 请提供命令参数")
        print("💡 使用 'help' 命令查看可用选项")
        return
    
    manager = TodoManager()
    command = sys.argv[1].lower()
    
    try:
        if command == "help":
            manager.show_help()
        
        elif command == "version":
            manager.show_version()
        
        elif command == "clear":
            manager.clear_screen()
        
        elif command == "list":
            status_filter = sys.argv[2] if len(sys.argv) > 2 else None
            manager.list_tasks(status_filter)
        
        elif command == "show":
            if len(sys.argv) < 3:
                print("❌ 请提供任务UUID")
                return
            manager.show_task(sys.argv[2])
        
        elif command == "create":
            if len(sys.argv) < 3:
                print("❌ 请提供任务名称")
                return
            task_name = sys.argv[2]
            priority = sys.argv[3] if len(sys.argv) > 3 else "normal"
            manager.create_task(task_name, priority)
        
        elif command == "update":
            if len(sys.argv) < 4:
                print("❌ 请提供UUID、字段名和值")
                return
            manager.update_task(sys.argv[2], sys.argv[3], sys.argv[4])
        
        elif command == "status":
            if len(sys.argv) < 4:
                print("❌ 请提供UUID和新状态")
                return
            manager.update_status(sys.argv[2], sys.argv[3])
        
        elif command == "delete":
            if len(sys.argv) < 3:
                print("❌ 请提供任务UUID")
                return
            manager.delete_task(sys.argv[2])
        
        elif command == "restore":
            if len(sys.argv) < 3:
                print("❌ 请提供任务UUID")
                return
            manager.restore_task(sys.argv[2])
        
        elif command == "clear_completed":
            manager.clear_completed_tasks()
        
        elif command == "overdue":
            manager.show_overdue_tasks()
        
        elif command == "search":
            if len(sys.argv) < 3:
                print("❌ 请提供搜索关键词")
                return
            manager.search_tasks(sys.argv[2])
        
        elif command == "stats":
            manager.show_stats()
        
        elif command == "export":
            if len(sys.argv) < 3:
                print("❌ 请提供文件名")
                return
            manager.export_data(sys.argv[2])
        
        elif command == "import":
            if len(sys.argv) < 3:
                print("❌ 请提供文件名")
                return
            manager.import_data(sys.argv[2])
        
        else:
            print(f"❌ 未知命令: {command}")
            print("💡 使用 'help' 命令查看可用选项")
    
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        print("💡 检查参数是否正确，使用 'help' 查看用法")

if __name__ == "__main__":
    main()
