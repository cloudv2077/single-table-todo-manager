#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版智能优先级系统 - 修复SQL错误和显示问题
"""

import sqlite3
import sys
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

class EnhancedTodoManagerV2:
    def __init__(self, db_path: str = "/Users/cloudv/Desktop/todo-sqlite/simple.db"):
        """初始化增强版任务管理器"""
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
            
            # 检查是否需要添加新字段
            cursor.execute("PRAGMA table_info(todo_unified)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # 如果没有task_type字段，添加它
            if 'task_type' not in columns:
                cursor.execute('ALTER TABLE todo_unified ADD COLUMN task_type TEXT DEFAULT "general"')
                print("✅ 已添加任务类型字段")
            
            # 如果没有estimated_hours字段，添加它
            if 'estimated_hours' not in columns:
                cursor.execute('ALTER TABLE todo_unified ADD COLUMN estimated_hours REAL DEFAULT 0')
                print("✅ 已添加预估工时字段")
            
            conn.commit()
    
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
    
    def show_enhanced_task_list(self, status_filter: Optional[str] = None):
        """显示增强版任务列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取所有活跃任务 - 修复SQL
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
            print("\n🎯 智能优先级任务列表 (优化版)")
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
            
            # 显示时间压力说明
            self._show_time_pressure_legend()
            
            # 显示优先级分布
            self._show_priority_distribution(task_priorities)
    
    def _show_time_pressure_legend(self):
        """显示时间压力等级说明"""
        print("\n⏰ 时间压力等级说明:")
        print("─" * 50)
        for pressure, info in sorted(self.time_pressure_levels.items(), reverse=True):
            if pressure > 0:
                print(f"   {info['color']} {info['level']}: {info['desc']} (+{pressure*100:.0f}%) - {info['advice']}")
        print(f"   🟢 无压力: 无截止日期 (+0%) - 灵活处理")
    
    def _show_priority_distribution(self, task_priorities: List[Dict]):
        """显示优先级分布统计"""
        distribution = {'urgent_important': 0, 'important': 0, 'urgent': 0, 'normal': 0}
        
        for task in task_priorities:
            final_priority = task['final_priority']
            distribution[final_priority] += 1
        
        print("\n📊 智能优先级分布:")
        print("─" * 60)
        
        for priority, count in distribution.items():
            if count > 0:
                display = self.eisenhower_matrix[priority]
                percentage = (count / len(task_priorities)) * 100
                print(f"{display['icon']} {display['name']}: {count} 个任务 ({percentage:.1f}%)")
                print(f"   建议: {display['action']}")
    
    def show_eisenhower_matrix(self):
        """显示艾森豪威尔矩阵视图"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取所有活跃任务UUID
            cursor.execute('''
                SELECT u.task_uuid
                FROM todo_unified u
                JOIN (
                    SELECT task_uuid, MAX(version) as max_version
                    FROM todo_unified GROUP BY task_uuid
                ) latest ON u.task_uuid = latest.task_uuid AND u.version = latest.max_version
                WHERE u.operation_type != 'delete'
            ''')
            
            task_uuids = [row[0] for row in cursor.fetchall()]
            
            # 按象限分类
            matrix = {
                'Q1_urgent_important': [],
                'Q2_important': [],
                'Q3_urgent': [],
                'Q4_normal': []
            }
            
            quadrant_map = {
                'urgent_important': 'Q1_urgent_important',
                'important': 'Q2_important',
                'urgent': 'Q3_urgent',
                'normal': 'Q4_normal'
            }
            
            for uuid in task_uuids:
                priority_info = self.calculate_smart_priority(uuid)
                if priority_info:
                    final_priority = priority_info['final_priority']
                    quadrant = quadrant_map.get(final_priority, 'Q4_normal')
                    matrix[quadrant].append(priority_info)
            
            # 显示矩阵
            print("\n" + "="*80)
            print("🎯 艾森豪威尔矩阵 - 智能任务优先级管理 (优化版)")
            print("="*80)
            
            print("\n📊 矩阵分布:")
            print("┌─────────────────────────────────────┬─────────────────────────────────────┐")
            print("│             重要 + 紧急              │             重要 + 不紧急            │")
            print("│           🔥 Q1 - 立即执行           │           ⭐ Q2 - 计划安排           │")
            print("├─────────────────────────────────────┼─────────────────────────────────────┤")
            print("│            不重要 + 紧急             │           不重要 + 不紧急            │")
            print("│           ⚡ Q3 - 委托处理           │           📝 Q4 - 消除删除           │")
            print("└─────────────────────────────────────┴─────────────────────────────────────┘")
            
            # 显示各象限详情
            quadrants = [
                ('Q1_urgent_important', '🔥 Q1 象限 - 紧急且重要 (立即执行)'),
                ('Q2_important', '⭐ Q2 象限 - 重要但不紧急 (计划安排)'),
                ('Q3_urgent', '⚡ Q3 象限 - 紧急但不重要 (委托处理)'),
                ('Q4_normal', '📝 Q4 象限 - 既不紧急也不重要 (考虑删除)')
            ]
            
            for quadrant_key, title in quadrants:
                tasks = matrix.get(quadrant_key, [])
                print(f"\n{title}")
                print("─" * 70)
                
                if not tasks:
                    print("  📝 暂无任务")
                    continue
                
                # 按权重排序
                tasks.sort(key=lambda x: x['dynamic_weight'], reverse=True)
                
                for task_info in tasks[:5]:  # 只显示前5个
                    # 智能截断任务名称
                    task_display = self._truncate_text(task_info['task'], 55)
                    
                    print(f"  • {task_display}")
                    print(f"    UUID: {task_info['task_uuid'][:8]}... | 权重: {task_info['dynamic_weight']:.1f}")
                    
                    # 显示时间压力详情
                    if task_info['time_pressure'] > 0:
                        time_info = task_info['time_pressure_info']
                        print(f"    {time_info['color']} 时间压力: {time_info['level']} ({time_info['desc']}) +{task_info['time_pressure']:.0f}%")
                    
                    if task_info['type_bonus'] > 0:
                        print(f"    📂 类型加成: +{task_info['type_bonus']:.1f}%")
                    print()
                
                if len(tasks) > 5:
                    print(f"  ... 还有 {len(tasks) - 5} 个任务")
    
    def analyze_task_detailed(self, task_uuid: str):
        """详细任务分析"""
        priority_info = self.calculate_smart_priority(task_uuid)
        
        if not priority_info:
            print(f"❌ 未找到UUID为 {task_uuid} 的任务")
            return
        
        print(f"\n🔬 任务智能分析 (优化版)")
        print("="*70)
        
        # 任务基本信息
        task_display = self._truncate_text(priority_info['task'], 60)
        print(f"📋 任务: {task_display}")
        print(f"🔗 UUID: {priority_info['task_uuid']}")
        
        # 优先级分析
        print(f"\n🎯 优先级分析:")
        print(f"   原始优先级: {priority_info['base_priority']}")
        print(f"   智能优先级: {priority_info['final_priority']}")
        
        # 权重分析
        print(f"\n⚖️ 权重构成分析:")
        print(f"   基础权重: {priority_info['base_weight']}")
        print(f"   动态权重: {priority_info['dynamic_weight']:.1f}/150")
        
        # 详细的时间压力分析
        time_info = priority_info['time_pressure_info']
        print(f"\n⏰ 时间压力详析:")
        print(f"   {time_info['color']} 压力等级: {time_info['level']} ({time_info['desc']})")
        print(f"   📈 权重贡献: +{priority_info['time_pressure']:.1f}% (基础权重 × 0.{int(priority_info['time_pressure']/10)})")
        
        # 解释时间压力算法
        if 'remaining_days' in time_info:
            remaining = time_info['remaining_days']
            if remaining < 0:
                print(f"   🚨 状态: 已逾期 {abs(remaining)} 天 → 应用50%权重加成")
            elif remaining == 0:
                print(f"   🔥 状态: 今天截止 → 应用40%权重加成")
            elif remaining == 1:
                print(f"   ⚡状态: 明天截止 → 应用40%权重加成")
            elif remaining <= 3:
                print(f"   ⏰ 状态: 还有 {remaining} 天截止 → 应用30%权重加成")
            elif remaining <= 7:
                print(f"   📅 状态: 还有 {remaining} 天截止 → 应用20%权重加成")
            else:
                print(f"   📅 状态: 还有 {remaining} 天截止 → 应用10%权重加成")
        else:
            print(f"   🟢 状态: 无截止日期 → 无时间压力加成")
        
        # 其他权重因素
        if priority_info['type_bonus'] > 0:
            print(f"\n📂 任务类型加成: +{priority_info['type_bonus']:.1f}%")
        
        if priority_info['effort_bonus'] > 0:
            print(f"\n💪 工作量加成: +{priority_info['effort_bonus']:.1f}%")
        
        # 算法解释
        print(f"\n🧮 智能权重计算公式:")
        print(f"   动态权重 = 基础权重 × (1 + 时间压力系数 + 类型系数 + 工作量系数)")
        print(f"   {priority_info['dynamic_weight']:.1f} = {priority_info['base_weight']} × (1 + {priority_info['time_pressure']/100:.2f} + {priority_info['type_bonus']/100:.2f} + {priority_info['effort_bonus']/100:.2f})")
        
        # 行动建议
        display = priority_info['display_info']
        print(f"\n💡 推荐行动:")
        print(f"   {display['action']}")
        print(f"   建议提示: {', '.join(display['tips'][:2])}")
        
        # 时间管理建议
        print(f"   时间安排: {time_info['advice']}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("❌ 请提供命令参数")
        print("💡 可用命令: list, matrix, analyze <UUID>")
        return
    
    manager = EnhancedTodoManagerV2()
    command = sys.argv[1].lower()
    
    try:
        if command == "list":
            status_filter = sys.argv[2] if len(sys.argv) > 2 else None
            manager.show_enhanced_task_list(status_filter)
        
        elif command == "matrix":
            manager.show_eisenhower_matrix()
        
        elif command == "analyze":
            if len(sys.argv) < 3:
                print("❌ 请提供任务UUID")
                return
            
            task_uuid = sys.argv[2]
            manager.analyze_task_detailed(task_uuid)
        
        else:
            print(f"❌ 未知命令: {command}")
            print("💡 可用命令: list, matrix, analyze <UUID>")
    
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")

if __name__ == "__main__":
    main()
