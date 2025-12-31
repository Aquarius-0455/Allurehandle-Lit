# -*- coding:UTF-8 -*-
"""
基于YAML配置的Locust压测工具（Web UI模式）
使用方法：
1. 运行: python run_locust_web.py
2. 浏览器打开: http://localhost:8089
3. Web界面可实时看到每个接口的独立曲线对比
"""
from locust import task, FastHttpUser
import sys
import os
from locust.main import main
from utils.logger import logger
from utils.locust_config import get_locust_config


# ============= 压测配置（修改这里） =============

# 压测接口列表（支持多个接口同时压测）
API_CONFIGS = [
    {'module': 'merchants', 'api': 'list', 'weight': 3},
    # {'module': 'integrations', 'api': 'list', 'weight': 2},
]

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
        else:
            response.failure(f"状态码错误: {response.status_code}")


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Locust压测启动（Web UI模式）")
    print("=" * 80)
    print(f"📋 压测接口列表:")
    for config in REQUEST_CONFIGS:
        print(f"   - {config['name']} ({config['method']}) [权重: {config['weight']}]")
    print(f"🌐 Web UI地址: http://localhost:8089")
    print(f"📊 在Web界面中可以实时看到每个接口的独立曲线对比")
    print("=" * 80 + "\n")
    
    logger.info(f"压测接口: {[c['name'] for c in REQUEST_CONFIGS]}")
    
    # 启动Locust Web UI
    sys.argv = [
        "locust",
        "-f", __file__,
        "--web-host", "0.0.0.0",
        "--web-port", "8089"
    ]
    
    main()

