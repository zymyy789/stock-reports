"""
自我保护与进度监控系统
- Token 监控
- 超时检测
- 定期汇报
"""
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path


class SelfProtection:
    """自我保护系统"""
    
    def __init__(self):
        self.state_file = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'protection_state.json'
        )
        self.state = self.load_state()
        
        # 配置
        self.token_warning_threshold = 0.90  # 90% 警告
        self.token_pause_threshold = 0.95    # 95% 暂停
        self.max_task_duration = 600        # 10分钟超时
        self.report_interval = 7200         # 2小时汇报
    
    def load_state(self) -> dict:
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'last_report_time': None,
            'last_task_start': None,
            'task_count': 0,
            'total_tasks': 0,
            'paused': False,
            'pause_reason': None
        }
    
    def save_state(self):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def start_task(self, task_name: str):
        """开始任务"""
        self.state['last_task_start'] = datetime.now().isoformat()
        self.state['current_task'] = task_name
        self.state['task_count'] += 1
        self.state['total_tasks'] += 1
        self.state['paused'] = False
        self.state['pause_reason'] = None
        self.save_state()
    
    def end_task(self):
        """结束任务"""
        self.state['last_task_start'] = None
        self.state['current_task'] = None
        self.save_state()
    
    def check_token_usage(self, current_usage: float) -> dict:
        """
        检查 Token 使用情况
        返回: {should_pause, warning, message}
        """
        usage = current_usage / 100.0  # 转换为 0-1
        
        if usage >= self.token_pause_threshold:
            self.state['paused'] = True
            self.state['pause_reason'] = f"Token使用率{usage*100:.0f}%超过95%"
            self.save_state()
            
            return {
                'should_pause': True,
                'warning': 'danger',
                'message': f"⚠️ Token使用率已达{usage*100:.0f}%，暂停开发以保留资源"
            }
        elif usage >= self.token_warning_threshold:
            return {
                'should_pause': False,
                'warning': 'warning',
                'message': f"⚠️ Token使用率{usage*100:.0f}%达到90%，请注意资源消耗"
            }
        
        return {
            'should_pause': False,
            'warning': None,
            'message': None
        }
    
    def check_task_timeout(self) -> bool:
        """检查任务是否超时"""
        if not self.state.get('last_task_start'):
            return False
        
        start = datetime.fromisoformat(self.state['last_task_start'])
        elapsed = (datetime.now() - start).total_seconds()
        
        if elapsed > self.max_task_duration:
            self.state['paused'] = True
            self.state['pause_reason'] = f"任务超时{elapsed/60:.0f}分钟"
            self.save_state()
            return True
        
        return False
    
    def should_report(self) -> bool:
        """是否应该发送汇报"""
        last_report = self.state.get('last_report_time')
        
        if not last_report:
            return True
        
        last_time = datetime.fromisoformat(last_report)
        elapsed = (datetime.now() - last_time).total_seconds()
        
        return elapsed >= self.report_interval
    
    def report_completed(self):
        """汇报完成"""
        self.state['last_report_time'] = datetime.now().isoformat()
        self.save_state()
    
    def is_paused(self) -> tuple:
        """检查是否暂停"""
        if self.state.get('paused'):
            return True, self.state.get('pause_reason', '未知原因')
        return False, None
    
    def resume(self):
        """恢复"""
        self.state['paused'] = False
        self.state['pause_reason'] = None
        self.save_state()
    
    def get_status(self) -> str:
        """获取状态"""
        paused, reason = self.is_paused()
        
        if paused:
            return f"⏸️ 已暂停: {reason}"
        
        task = self.state.get('current_task', '无任务')
        task_count = self.state.get('task_count', 0)
        
        return f"✅ 运行中 - 当前任务: {task} (已完成{task_count}个)"
    
    def reset_daily(self):
        """每日重置（用于6点报告后）"""
        self.state['task_count'] = 0
        self.state['last_report_time'] = datetime.now().isoformat()
        self.state['paused'] = False
        self.state['pause_reason'] = None
        self.save_state()


# 全局实例
_protection = None

def get_protection() -> SelfProtection:
    """获取保护系统实例"""
    global _protection
    if _protection is None:
        _protection = SelfProtection()
    return _protection


def check_and_report() -> bool:
    """
    检查是否需要汇报
    返回: 是否需要发送汇报
    """
    protection = get_protection()
    
    # 检查暂停状态
    paused, reason = protection.is_paused()
    if paused:
        print(f"系统暂停: {reason}")
        return False
    
    # 检查是否应该汇报
    if protection.should_report():
        return True
    
    return False


def main():
    """测试"""
    protection = SelfProtection()
    
    # 模拟任务
    protection.start_task("开发测试")
    print(protection.get_status())
    
    # 检查超时
    print(f"超时: {protection.check_task_timeout()}")
    
    # 汇报检查
    print(f"需要汇报: {protection.should_report()}")
    
    # Token检查
    result = protection.check_token_usage(85)
    print(f"Token检查: {result}")
    
    protection.end_task()
    print(protection.get_status())


if __name__ == "__main__":
    main()