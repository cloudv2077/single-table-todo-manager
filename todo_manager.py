#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能优先级任务管理系统 - 统一版
集成基础任务管理和智能优先级功能
基于艾森豪威尔矩阵的科学任务管理
"""

import sqlite3
import sys
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

class TodoManager:
    def __init__(self, db_path: str = "/Users/cloudv/Desktop/todo-sqlite/simple.db"):
        """初始化任务管理器"""
        self.db_path = db_path
        self.init_database()
        self.setup_enhanced_priority_system()
    
    def setup_enhanced_priority_system(self):
        """设置增强的优先级系统"""
        # 艾森豪威尔矩阵定义
        self.eisenhower_matrix = {
            'urgent_important': {
                'name': '紧急且重要',
                'description': '立即处理 - 危机管理',
                'icon': '🔥',
                'bg_color': '\033[41m',  # 红色背景
                'text_color': '\033[97m', # 白色文字
                'weight': 100,
                'action': '🚨 立即执行',
                'quadrant': 'Q1',
                'tips': ['集中注意力', '消除干扰', '全力以赴完成']
            },
            'important': {  # 兼容旧系统
                'name': '重要但不紧急', 
                'description': '计划安排 - 战略发展',
                'icon': '⭐',
                'bg_color': '\033[43m',  # 黄色背景
                'text_color': '\033[30m', # 黑色文字
                'weight': 80,
                'action': '📅 计划安排',
                'quadrant': 'Q2',
                'tips': ['制定详细计划', '分配充足时间', '定期检查进度']
            },
            'urgent': {  # 兼容旧系统
                'name': '紧急但不重要',
                'description': '委托处理 - 干扰管理', 
                'icon': '⚡',
                'bg_color': '\033[45m',  # 紫色背景
                'text_color': '\033[97m', # 白色文字
                'weight': 60,
                'action': '🤝 委托授权',
                'quadrant': 'Q3',
                'tips': ['寻找合适的人选', '提供清晰指导', '设定检查节点']
            },
            'normal': {  # 兼容旧系统
                'name': '既不紧急也不重要',
                'description': '消除删除 - 时间浪费',
                'icon': '📝',
                'bg_color': '\033[42m',  # 绿色背景
                'text_color': '\033[30m', # 黑色文字
                'weight': 20,
                'action': '🗑️ 考虑删除',
                'quadrant': 'Q4',
                'tips': ['评估真实价值', '考虑完全删除', '或推迟到空闲时间']
            }
        }
        
        # 重置颜色
        self.reset_color = '\033[0m'
        
        # 时间压力说明
        self.time_pressure_levels = {
            0.5: {'level': '极高压力', 'desc': '已逾期', 'color': '🚨', 'advice': '立即处理'},
            0.4: {'level': '高压力', 'desc': '今明截止', 'color': '🔥', 'advice': '优先安排'},
            0.3: {'level': '中压力', 'desc': '3天内', 'color': '⚡', 'advice': '及时处理'},
            0.2: {'level': '低压力', 'desc': '1周内', 'color': '⏰', 'advice': '计划安排'},
            0.1: {'level': '微压力', 'desc': '1周以上', 'color': '📅', 'advice': '从容安排'},
            0.0: {'level': '无压力', 'desc': '无截止', 'color': '🟢', 'advice': '灵活处理'}
        }
    
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
                    task_type TEXT DEFAULT 'general',
                    estimated_hours REAL DEFAULT 0,
                    operation_type TEXT CHECK(operation_type IN ('create', 'update', 'status_change', 'delete', 'restore', 'current_snapshot', 'migration')) DEFAULT 'update',
                    change_summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_uuid ON todo_unified(task_uuid)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON todo_unified(status)')
            
            # 检查是否需要添加新字段
            cursor.execute("PRAGMA table_info(todo_unified)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # 如果没有task_type字段，添加它
            if 'task_type' not in columns:
                cursor.execute('ALTER TABLE todo_unified ADD COLUMN task_type TEXT DEFAULT "general"')
            
            # 如果没有estimated_hours字段，添加它
            if 'estimated_hours' not in columns:
                cursor.execute('ALTER TABLE todo_unified ADD COLUMN estimated_hours REAL DEFAULT 0')
            
            conn.commit()
    
    def create_task(self, task: str, priority: str = 'normal', due_date: str = None, task_type: str = 'general', estimated_hours: float = 0) -> str:
        """创建新任务"""
        task_uuid = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO todo_unified (
                    task_uuid, version, task, priority, due_date, task_type, estimated_hours,
                    operation_type, change_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_uuid, 1, task, priority, due_date, task_type, estimated_hours,
                'create', f'Created task: {task[:50]}'
            ))
            conn.commit()
        
        print(f"✅ 任务创建成功!")
        print(f"   UUID: {task_uuid}")
        print(f"   任务: {task}")
        print(f"   优先级: {priority}")
        if due_date:
            print(f"   截止日期: {due_date}")
        
        return task_uuid
    
    def list_tasks(self, status_filter: Optional[str] = None, smart_mode: bool = True):
        """列出任务"""
        if smart_mode:
            self.show_enhanced_task_list(status_filter)
        else:
            self.show_basic_task_list(status_filter)
    
    def show_enhanced_task_list(self, status_filter: Optional[str] = None):
        """显示增强版智能优先级任务列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取所有活跃任务
            if status_filter:
                cursor.execute('''
                    SELECT u.task_uuid
                    FROM todo_unified u
                    JOIN (
                        SELECT task_uuid, MAX(version) as max_version
                        FROM todo_unified GROUP BY task_uuid
                    ) latest ON u.task_uuid = latest.task_uuid AND u.version = latest.max_version
                    WHERE u.operation_type != 'delete' AND u.status = ?
                    ORDER BY u.created_at DESC
                ''', (status_filter,))
            else:
                cursor.execute('''
                    SELECT u.task_uuid
                    FROM todo_unified u
                    JOIN (
                        SELECT task_uuid, MAX(version) as max_version
                        FROM todo_unified GROUP BY task_uuid
                    ) latest ON u.task_uuid = latest.task_uuid AND u.version = latest.max_version
                    WHERE u.operation_type != 'delete'
                    ORDER BY u.created_at DESC
                ''')
            
            task_uuids = [row[0] for row in cursor.fetchall()]
            
            if not task_uuids:
                print("📝 暂无任务")
                return
            
            # 计算所有任务的智能优先级
            task_priorities = []
            for uuid in task_uuids:
                priority_info = self.calculate_smart_priority(uuid)
                if priority_info:
                    task_priorities.append(priority_info)
            
            # 按动态权重排序
            task_priorities.sort(key=lambda x: x['dynamic_weight'], reverse=True)
            
            # 显示表头
            print("\n🎯 智能优先级任务列表")
            print("=" * 125)
            print(f"{'UUID[:8]':<10} {'任务名称':<45} {'智能优先级':<20} {'权重':<8} {'时间压力':<20} {'截止日期':<12}")
            print("─" * 125)
            
            # 显示任务
            for task_info in task_priorities:
                display = task_info['display_info']
                uuid_short = task_info['task_uuid'][:8]
                
                # 智能截断任务名称
                task_name = self._truncate_text(task_info['task'], 42)
                
                # 彩色显示优先级
                priority_display = f"{display['bg_color']}{display['text_color']} {display['icon']} {display['name']} {self.reset_color}"
                
                # 时间压力显示
                time_info = task_info['time_pressure_info']
                if task_info['time_pressure'] > 0:
                    time_display = f"{time_info['color']} {time_info['level']} (+{task_info['time_pressure']:.0f}%)"
                else:
                    time_display = f"{time_info['color']} 无时间压力"
                
                due_date = task_info['due_date'] or "无截止"
                
                print(f"{uuid_short:<10} {task_name:<45} {priority_display:<20} {task_info['dynamic_weight']:<8.1f} {time_display:<20} {due_date:<12}")
            
            print(f"\n📊 总计: {len(task_priorities)} 个任务")
    
    def calculate_smart_priority(self, task_uuid: str) -> Dict:
        """计算智能优先级"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取最新任务信息
            cursor.execute('''
                SELECT 
                    u.task, u.priority, u.due_date, u.created_at, u.task_type, u.estimated_hours
                FROM todo_unified u
                JOIN (
                    SELECT task_uuid, MAX(version) as max_version
                    FROM todo_unified GROUP BY task_uuid
                ) latest ON u.task_uuid = latest.task_uuid AND u.version = latest.max_version
                WHERE u.task_uuid = ? AND u.operation_type != 'delete'
            ''', (task_uuid,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            task, base_priority, due_date, created_at, task_type, estimated_hours = result
            
            # 获取基础权重
            base_info = self.eisenhower_matrix.get(base_priority, self.eisenhower_matrix['normal'])
            base_weight = base_info['weight']
            
            # 计算时间压力权重
            time_pressure, time_pressure_info = self._calculate_time_pressure_with_info(due_date, created_at)
            
            # 计算任务类型权重
            type_weight = self._calculate_type_weight(task_type or 'general')
            
            # 工作量权重
            effort_weight = self._calculate_effort_weight(estimated_hours or 0)
            
            # 综合计算动态权重
            dynamic_weight = base_weight * (1 + time_pressure + type_weight + effort_weight)
            dynamic_weight = min(dynamic_weight, 150)  # 设置上限
            
            # 确定最终优先级
            final_priority = self._determine_final_priority(dynamic_weight, base_priority)
            
            return {
                'task_uuid': task_uuid,
                'task': task,
                'base_priority': base_priority,
                'final_priority': final_priority,
                'base_weight': base_weight,
                'dynamic_weight': round(dynamic_weight, 1),
                'time_pressure': round(time_pressure * 100, 1),
                'time_pressure_info': time_pressure_info,
                'type_bonus': round(type_weight * 100, 1),
                'effort_bonus': round(effort_weight * 100, 1),
                'display_info': self.eisenhower_matrix[final_priority],
                'due_date': due_date,
                'created_at': created_at
            }
    
    def _calculate_time_pressure_with_info(self, due_date: str, created_date: str) -> tuple:
        """计算时间压力权重并返回详细信息"""
        if not due_date:
            return 0.0, self.time_pressure_levels[0.0]
            
        try:
            due = datetime.strptime(due_date, '%Y-%m-%d')
            now = datetime.now()
            created = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S') if created_date else now
            
            remaining_time = (due - now).days
            
            # 时间压力递增曲线
            if remaining_time <= 0:
                pressure = 0.5  # 逾期，高压力
            elif remaining_time <= 1:
                pressure = 0.4  # 今明两天
            elif remaining_time <= 3:
                pressure = 0.3  # 3天内
            elif remaining_time <= 7:
                pressure = 0.2  # 一周内
            else:
                pressure = 0.1  # 一周以上
            
            # 获取对应的压力信息
            pressure_info = self.time_pressure_levels[pressure].copy()
            pressure_info['remaining_days'] = remaining_time
            
            return pressure, pressure_info
                
        except (ValueError, TypeError):
            return 0.0, self.time_pressure_levels[0.0]
    
    def _calculate_type_weight(self, task_type: str) -> float:
        """根据任务类型计算权重"""
        type_weights = {
            'emergency': 0.4,     # 紧急事务
            'meeting': 0.25,      # 会议
            'deadline': 0.3,      # 有明确截止日期
            'communication': 0.15, # 沟通协调
            'development': 0.2,   # 开发任务
            'bug_fix': 0.35,      # Bug修复
            'security': 0.4,      # 安全相关
            'client': 0.3,        # 客户相关
            'routine': 0.05,      # 日常事务
            'learning': 0.1,      # 学习任务
            'maintenance': 0.08,  # 维护任务
            'research': 0.12,     # 研究任务
            'general': 0.0        # 普通任务
        }
        return type_weights.get(task_type.lower(), 0.0)
    
    def _calculate_effort_weight(self, estimated_hours: float) -> float:
        """根据预估工时计算权重"""
        if estimated_hours <= 0:
            return 0.0
        elif estimated_hours <= 2:
            return 0.05  # 小任务，稍微提升
        elif estimated_hours <= 8:
            return 0.1   # 中等任务
        elif estimated_hours <= 24:
            return 0.15  # 大任务，需要规划
        else:
            return 0.2   # 超大任务，重点关注
    
    def _determine_final_priority(self, weight: float, base_priority: str) -> str:
        """根据动态权重确定最终优先级"""
        if weight >= 120:
            return 'urgent_important'
        elif weight >= 90:
            return 'important'
        elif weight >= 60:
            return 'urgent'
        else:
            return 'normal'
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """智能截断文本，保持可读性"""
        if len(text) <= max_length:
            return text
        
        # 尝试在单词边界截断
        truncated = text[:max_length-3]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.7:  # 如果空格位置合适
            return truncated[:last_space] + "..."
        else:
            return truncated + "..."
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
🎯 智能优先级任务管理系统 - 帮助指南

📋 基础任务管理:
   python3 todo_manager.py create "任务内容" [priority] [due_date] [task_type] [estimated_hours]
   python3 todo_manager.py list [status]          # 智能优先级任务列表 (推荐)
   python3 todo_manager.py matrix                 # 艾森豪威尔矩阵视图
   python3 todo_manager.py analyze <UUID>         # 详细任务分析

🏷️ 支持的优先级:
   • urgent_important  - 🔥 紧急且重要 (Q1)
   • important         - ⭐ 重要但不紧急 (Q2) 
   • urgent            - ⚡ 紧急但不重要 (Q3)
   • normal            - 📝 既不紧急也不重要 (Q4)

📂 支持的任务类型:
   emergency, meeting, deadline, communication, development, bug_fix, 
   security, client, routine, learning, maintenance, research, general

🎯 智能优先级特性:
   • 基于艾森豪威尔矩阵的科学分类
   • 动态权重计算: 基础权重 × (1 + 时间压力 + 类型加成 + 工作量)
   • 时间压力自动感知和可视化显示
   • 透明化的决策支持和行动建议

💡 使用建议:
   • 每天使用 list 命令查看智能排序的任务
   • 每周使用 matrix 命令分析任务分布
   • 重要任务使用 analyze 命令深度了解
        """
        print(help_text)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        manager = TodoManager()
        manager.show_help()
        return
    
    manager = TodoManager()
    command = sys.argv[1].lower()
    
    try:
        if command == "create":
            if len(sys.argv) < 3:
                print("❌ 请提供任务内容")
                return
            
            task = sys.argv[2]
            priority = sys.argv[3] if len(sys.argv) > 3 else 'normal'
            due_date = sys.argv[4] if len(sys.argv) > 4 else None
            task_type = sys.argv[5] if len(sys.argv) > 5 else 'general'
            estimated_hours = float(sys.argv[6]) if len(sys.argv) > 6 else 0
            
            manager.create_task(task, priority, due_date, task_type, estimated_hours)
        
        elif command == "list":
            status_filter = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in ['todo', 'in_progress', 'completed'] else None
            manager.list_tasks(status_filter, smart_mode=True)
        
        elif command == "matrix":
            print("🎯 矩阵功能开发中...")
        
        elif command == "analyze":
            print("🔬 分析功能开发中...")
        
        elif command == "help":
            manager.show_help()
        
        else:
            print(f"❌ 未知命令: {command}")
            manager.show_help()
    
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")

if __name__ == "__main__":
    main()
