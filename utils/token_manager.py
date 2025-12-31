# -*- coding:UTF-8 -*-
import os
import yaml
import requests
import urllib3
from typing import Dict, Optional
from utils.logger import logger


# YAML 配置根目录（固定使用 resources/，包含 config.yaml / api/ / testdata/）
YAML_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')


class TokenManager:
    """Token管理类（单例）"""
    _instance = None
    _token = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.config = self._load_config()
            self._initialized = True
    
    def _load_config(self) -> Dict:
        """从yaml加载配置"""
        config_path = os.path.join(YAML_CONFIG_PATH, 'config.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        logger.warning(f"公共配置文件不存在: {config_path}")
        return {}
    
    def get_token(self) -> Optional[str]:
        """获取Token（带缓存）"""
        if self._token:
            return self._token
        
        # 从yaml读取环境配置
        env = self.config.get('current_env', 'staging')
        env_config = self.config.get('environments', {}).get(env, {})
        
        base_url = env_config.get('base_url', '')
        token_url = env_config.get('token_url', '/api/linker-di/iam/token')
        login_user = env_config.get('login_user', {})
        
        if not base_url or not login_user:
            logger.error(
                f"❌ 环境配置不完整: {env}。"
                f"请检查 {os.path.join(YAML_CONFIG_PATH, 'config.yaml')} 中的 environments.{env}.base_url / login_user"
            )
            return None
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*"
        }
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        try:
            response = requests.post(
                url=f"{base_url}{token_url}",
                headers=headers,
                json=login_user,
                verify=False,
                timeout=env_config.get('timeout', 10)
            )
            response.raise_for_status()
            
            result = response.json()
            data = (result or {}).get('data') if isinstance(result, dict) else None
            if not isinstance(data, dict):
                logger.error(f"❌ Token响应结构不符合预期，缺少data字段: {result}")
                return None

            token_type = data.get('token_type')
            access_token = data.get('access_token')
            if not token_type or not access_token:
                logger.error(f"❌ Token响应缺少 token_type/access_token: {result}")
                return None
            self._token = f"{token_type} {access_token}"
            
            logger.info(f"✅ Token获取成功 [环境: {env}]")
            return self._token
            
        except Exception as e:
            logger.error(f"❌ Token获取失败: {e}")
            return None
    
    def refresh_token(self):
        """刷新Token"""
        self._token = None
        return self.get_token()

