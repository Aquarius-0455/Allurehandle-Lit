# -*- coding:UTF-8 -*-
"""
Locust压测配置工具
"""
import os
import yaml
from utils.token_manager import TokenManager, YAML_CONFIG_PATH


class LocustConfig:
    """Locust压测配置管理"""
    
    def __init__(self, api_module: str, api_name: str):
        """
        初始化配置
        
        Args:
            api_module: API模块名（如：merchants）
            api_name: API名称（如：merchant_save, merchant_list）
        """
        self.api_module = api_module
        self.api_name = api_name
        self.yaml_path = YAML_CONFIG_PATH
        
        # 加载配置
        self.global_config = self._load_global_config()
        self.api_config = self._load_api_config()
        self.token = TokenManager().get_token()
    
    def _load_global_config(self):
        """加载全局配置"""
        config_path = os.path.join(self.yaml_path, 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_api_config(self):
        """加载API配置"""
        api_file = os.path.join(self.yaml_path, 'api', f'{self.api_module}.yaml')
        with open(api_file, 'r', encoding='utf-8') as f:
            module_config = yaml.safe_load(f)
            apis = module_config.get('apis', {})
            if self.api_name not in apis:
                raise ValueError(f"API [{self.api_name}] 不存在于模块 [{self.api_module}]")
            return apis[self.api_name]
    
    def get_base_url(self):
        """获取基础URL"""
        env = self.global_config.get('current_env', 'staging')
        return self.global_config['environments'][env]['base_url']
    
    def get_full_url(self, path_params=None):
        """获取完整URL"""
        base_url = self.get_base_url()
        path = self.api_config.get('path', '')
        
        # 替换路径参数
        if path_params:
            for key, value in path_params.items():
                path = path.replace(f'{{{key}}}', str(value))
        
        return f"{base_url}{path}"
    
    def get_headers(self):
        """获取请求头"""
        # 合并默认headers和API特定headers
        headers = self.global_config.get('default_headers', {}).copy()
        headers.update(self.api_config.get('headers', {}))
        
        # 填充token
        if 'authorization' in headers:
            headers['authorization'] = self.token
        
        return headers
    
    def get_method(self):
        """获取请求方法"""
        return self.api_config.get('method', 'GET')
    
    def get_params(self):
        """获取查询参数"""
        return self.api_config.get('params', {})
    
    def get_body(self):
        """获取请求体"""
        return self.api_config.get('body', {})
    
    def get_request_config(self, path_params=None):
        """
        获取完整的请求配置
        
        Returns:
            dict: {
                'url': 完整URL,
                'method': 请求方法,
                'headers': 请求头,
                'params': 查询参数,
                'json': JSON请求体,
                'host': 基础URL
            }
        """
        return {
            'url': self.get_full_url(path_params),
            'method': self.get_method(),
            'headers': self.get_headers(),
            'params': self.get_params(),
            'json': self.get_body(),
            'host': self.get_base_url()
        }


# 预定义的压测配置
PRESET_CONFIGS = {
    'merchants_list': {
        'module': 'merchants',
        'api': 'list',
        'description': '商户列表查询'
    },
    'merchants_save': {
        'module': 'merchants',
        'api': 'save',
        'description': '新增商户'
    },
    'connectors_list': {
        'module': 'integrations',
        'api': 'list',
        'description': '连接器列表'
    }
}


def get_locust_config(preset_name: str = None, api_module: str = None, api_name: str = None):
    """
    获取Locust配置
    
    Args:
        preset_name: 预设配置名称（如：merchants_list）
        api_module: API模块名（如果不使用预设）
        api_name: API名称（如果不使用预设）
    
    Returns:
        LocustConfig实例
    """
    if preset_name:
        if preset_name not in PRESET_CONFIGS:
            raise ValueError(f"未找到预设配置: {preset_name}，可用: {list(PRESET_CONFIGS.keys())}")
        preset = PRESET_CONFIGS[preset_name]
        return LocustConfig(preset['module'], preset['api'])
    elif api_module and api_name:
        return LocustConfig(api_module, api_name)
    else:
        raise ValueError("必须提供 preset_name 或 (api_module + api_name)")

