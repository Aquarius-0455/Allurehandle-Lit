# -*- coding:UTF-8 -*-
"""
增强版YAML配置加载器
支持：
1. 模块化API定义
2. 公共配置复用
3. 测试数据管理
4. 环境切换
5. 数据模板
"""

import os
import yaml
import time
from typing import Dict, Optional, Any
from utils.logger import logger
from utils.token_manager import TokenManager, YAML_CONFIG_PATH


class EnhancedYAMLLoader:
    """增强版YAML加载器"""
    
    def __init__(self):
        self.config = None
        self.apis = {}
        self.testdata = {}
        self.token = None
        self._load_all()
    
    def _load_all(self):
        """加载所有配置文件"""
        # 1. 加载公共配置
        config_path = os.path.join(YAML_CONFIG_PATH, 'config.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            logger.warning(f"公共配置文件不存在: {config_path}")
            self.config = {}
        
        # 2. 加载所有API定义
        api_dir = os.path.join(YAML_CONFIG_PATH, 'api')
        if os.path.exists(api_dir):
            for file in os.listdir(api_dir):
                if file.endswith(('.yaml', '.yml')):
                    module_name = file.split('.')[0]
                    file_path = os.path.join(api_dir, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.apis[module_name] = yaml.safe_load(f)
                    logger.info(f"✅ 加载API模块: {module_name}")
        
        # 3. 加载所有测试数据
        testdata_dir = os.path.join(YAML_CONFIG_PATH, 'testdata')
        if os.path.exists(testdata_dir):
            for file in os.listdir(testdata_dir):
                if file.endswith(('.yaml', '.yml')):
                    data_name = file.split('.')[0]
                    file_path = os.path.join(testdata_dir, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.testdata[data_name] = yaml.safe_load(f)
                    logger.info(f"✅ 加载测试数据: {data_name}")
        
        # 4. 获取token
        self.token = TokenManager().get_token()
        if not self.token:
            raise Exception("Token获取失败")
    
    def get_base_url(self) -> str:
        """获取当前环境的base_url"""
        current_env = self.config.get('current_env', 'staging')
        env_config = self.config.get('environments', {}).get(current_env, {})
        return env_config.get('base_url', '')
    
    def get_common_headers(self) -> Dict:
        """获取公共headers"""
        headers = self.config.get('default_headers', {}).copy()
        # 自动填充token
        if 'authorization' in headers:
            headers['authorization'] = self.token
        return headers
    
    def get_token(self) -> str:
        """获取token"""
        if not self.token:
            self.token = TokenManager().get_token()
        return self.token
    
    def get_api_config(
        self, 
        module: str, 
        api: str, 
        path_params: Optional[Dict] = None,
        override_body: Optional[Dict] = None,
        override_headers: Optional[Dict] = None
    ) -> Dict:
        """
        获取接口配置
        
        Args:
            module: 模块名 (如: merchants)
            api: 接口名 (如: save, list)
            path_params: 路径参数 {merchant_no: "123"}
            override_body: 覆盖请求体数据
            override_headers: 覆盖请求头
        
        Returns:
            完整的接口配置字典
        """
        # 获取API定义
        if module not in self.apis:
            raise ValueError(f"模块 [{module}] 不存在")
        
        module_config = self.apis[module]
        if 'apis' not in module_config or api not in module_config['apis']:
            available_apis = list(module_config.get('apis', {}).keys())
            raise ValueError(f"接口 [{api}] 不存在，可用接口: {available_apis}")
        
        api_config = module_config['apis'][api]
        
        # 构建URL
        path = api_config.get('path', '')
        if path_params:
            for key, value in path_params.items():
                path = path.replace(f'{{{key}}}', str(value))
        
        base_url = self.get_base_url()
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        
        # 合并headers
        headers = self.get_common_headers()
        if 'headers' in api_config:
            headers.update(api_config['headers'])
        if override_headers:
            headers.update(override_headers)
        
        # 处理请求体
        method = api_config.get('method', 'GET')
        body_type = api_config.get('body_type', 'params')
        default_body = api_config.get('default_body', {})
        
        # 合并请求体数据
        final_body = {**default_body, **(override_body or {})}
        
        # 替换时间戳等占位符
        final_body = self._replace_placeholders(final_body)
        
        result = {
            'url': url,
            'method': method,
            'headers': headers,
            'body_type': body_type,
            'assertions': api_config.get('assertions', [])
        }
        
        # 根据body_type设置数据
        if body_type == 'json':
            result['json'] = final_body
        elif body_type == 'form':
            result['data'] = final_body
        else:  # params
            result['params'] = final_body
        
        return result
    
    def get_testdata(self, data_name: str, case_name: str) -> Dict:
        """
        获取测试数据
        
        Args:
            data_name: 数据文件名 (如: merchants_testdata)
            case_name: 测试用例名 (如: normal.save_merchant_1)
        
        Returns:
            测试数据字典
        """
        if data_name not in self.testdata:
            raise ValueError(f"测试数据文件 [{data_name}] 不存在")
        
        # 支持点号分隔的多级访问
        data = self.testdata[data_name]
        for key in case_name.split('.'):
            if key not in data:
                raise ValueError(f"测试用例 [{case_name}] 不存在于 [{data_name}]")
            data = data[key]
        
        # 替换占位符
        return self._replace_placeholders(data)
    
    def _replace_placeholders(self, data: Any) -> Any:
        """递归替换数据中的占位符"""
        if isinstance(data, dict):
            return {k: self._replace_placeholders(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_placeholders(item) for item in data]
        elif isinstance(data, str):
            # 替换时间戳
            if '{timestamp}' in data:
                data = data.replace('{timestamp}', str(int(time.time())))
            # 替换日期
            if '{date}' in data:
                data = data.replace('{date}', time.strftime('%Y-%m-%d'))
            # 替换时间
            if '{time}' in data:
                data = data.replace('{time}', time.strftime('%H:%M:%S'))
            return data
        return data


# 单例模式
_loader_instance = None

def get_yaml_loader() -> EnhancedYAMLLoader:
    """获取YAML加载器单例"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = EnhancedYAMLLoader()
    return _loader_instance

