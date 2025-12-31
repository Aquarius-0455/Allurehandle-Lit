# -*- coding:UTF-8 -*-
"""
基于YAML配置的Locust压测工具
使用方法：修改下方配置，直接运行 python run_locust.py
"""
from locust import task, FastHttpUser
import sys
import os
import datetime
from locust.main import main
from utils.logger import logger
from utils.locust_config import get_locust_config


# ============= 压测配置（修改这里） =============

# 压测接口列表（支持多个接口同时压测）
# 格式：{'module': 'xxx', 'api': 'xxx', 'weight': 权重}
# weight: 调用权重，数字越大调用频率越高
API_CONFIGS = [
    {'module': 'merchants', 'api': 'list', 'weight': 3},  # 权重3
    # {'module': 'integrations', 'api': 'list', 'weight': 1},  # 权重1
    # {'module': 'integrations', 'api': 'list', 'weight': 2},  # 可添加更多
]

USER_COUNT = 10  # 并发用户数
SPAWN_RATE = 2  # 每秒启动用户数
RUN_TIME = "10s"  # 压测时长（s=秒，m=分，h=小时）
WORKERS = 1  # 压测进程数（根据CPU核心数调整）
PRINT_RESPONSE = False  # 是否打印响应内容
# ============= 配置结束 =============

# 加载所有API配置
REQUEST_CONFIGS = []
try:
    for api_cfg in API_CONFIGS:
        api_config = get_locust_config(api_module=api_cfg['module'], api_name=api_cfg['api'])
        req_config = api_config.get_request_config()
        req_config['weight'] = api_cfg.get('weight', 1)
        req_config['name'] = f"{api_cfg['module']}.{api_cfg['api']}"
        REQUEST_CONFIGS.append(req_config)
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    logger.error(f"配置加载失败: {e}")
    sys.exit(1)


class YAMLBasedLoadTestUser(FastHttpUser):
    """基于YAML配置的压测用户"""
    host = REQUEST_CONFIGS[0]['host']
    
    def on_start(self):
        """初始化：根据权重创建任务列表"""
        import random
        self.weighted_configs = []
        for config in REQUEST_CONFIGS:
            weight = config.get('weight', 1)
            self.weighted_configs.extend([config] * weight)
    
    @task
    def call_api(self):
        """执行API调用（随机选择配置的API）"""
        import random
        req_config = random.choice(self.weighted_configs)
        
        method = req_config['method'].upper()
        url = req_config['url']
        headers = req_config['headers']
        params = req_config.get('params', {})
        json_body = req_config.get('json', {})
        api_name = req_config['name']
        
        try:
            if method == "GET":
                with self.client.get(url, headers=headers, params=params, verify=False, catch_response=True, name=api_name) as resp:
                    self._handle_response(resp, api_name)
            elif method == "POST":
                with self.client.post(url, headers=headers, json=json_body, verify=False, catch_response=True, name=api_name) as resp:
                    self._handle_response(resp, api_name)
            elif method == "PUT":
                with self.client.put(url, headers=headers, json=json_body, verify=False, catch_response=True, name=api_name) as resp:
                    self._handle_response(resp, api_name)
            elif method == "DELETE":
                with self.client.delete(url, headers=headers, params=params, verify=False, catch_response=True, name=api_name) as resp:
                    self._handle_response(resp, api_name)
        except Exception as e:
            logger.error(f"请求异常 [{api_name}]: {e}")
    
    def _handle_response(self, response, api_name):
        if response.status_code in [200, 201, 204]:
            response.success()
            if PRINT_RESPONSE:
                try:
                    import json
                    print(f"✅ [{api_name}] 成功 [{response.status_code}]:")
                    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
                    print("-" * 80)
                except:
                    print(f"✅ [{api_name}] 成功 [{response.status_code}]: {response.text[:500]}")
                    print("-" * 80)
        else:
            response.failure(f"状态码错误: {response.status_code}")
            if PRINT_RESPONSE:
                print(f"❌ [{api_name}] 失败 [{response.status_code}]: {response.text[:500]}")
                print("-" * 80)


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Locust压测启动")
    print("=" * 80)
    print(f"📋 压测接口列表:")
    for config in REQUEST_CONFIGS:
        print(f"   - {config['name']} ({config['method']}) [权重: {config['weight']}]")
    print(f"👥 并发用户: {USER_COUNT} 个")
    print(f"⚡ 启动速率: {SPAWN_RATE} 个/秒")
    print(f"⏱️  压测时长: {RUN_TIME}")
    print(f"🔧 进程数: {WORKERS}")
    
    logger.info(f"压测接口: {[c['name'] for c in REQUEST_CONFIGS]}")
    
    report_dir = os.path.join(os.path.dirname(__file__), '..', 'report')
    report_name = f"locust_report.html"
    report_path = os.path.abspath(os.path.join(report_dir, report_name))
    
    print(f"📊 报告路径: {report_path}")
    logger.info(f"报告路径: {report_path}")
    print("=" * 80 + "\n")
    
    # 启动Locust
    args = [
        "locust",
        "-f", __file__,
        "--headless",
        "-u", str(USER_COUNT),
        "-r", str(SPAWN_RATE),
        "-t", RUN_TIME,
        "--html", report_path
    ]
    
    # 添加workers配置（需要多进程压测时使用）
    if WORKERS > 1:
        args.extend(["--processes", str(WORKERS)])
    
    sys.argv = args
    main()
