# -*- coding:UTF-8 -*-
import json
import requests
import time
from utils.logger import logger
from utils.allure_handle import AllureHandle


class RequestUtils:
    """HTTP请求工具类（单例模式）"""
    _instance = None
    _session = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._session = requests.Session()
        return cls._instance
    
    def send_request(self, **kwargs):
        """
        发送HTTP请求
        自动记录到日志和 Allure 报告
        """
        # 记录开始时间
        start_time = time.time()
        
        # 日志记录
        logger.info(f"{'='*80}")
        logger.info(f"📤 请求 {kwargs['method']} {kwargs['url']}")
        
        if kwargs.get("headers"):
            logger.info(f"📋 Headers: {json.dumps(kwargs['headers'], indent=2, ensure_ascii=False)}")
        
        if kwargs.get("params"):
            logger.info(f"🔗 Params: {json.dumps(kwargs['params'], indent=2, ensure_ascii=False)}")
        
        if kwargs.get("data"):
            logger.info(f"📦 Data: {json.dumps(kwargs['data'], indent=2, ensure_ascii=False)}")
        
        if kwargs.get("json"):
            logger.info(f"📦 JSON: {json.dumps(kwargs['json'], indent=2, ensure_ascii=False)}")
        
        # 添加到 Allure 报告 - 请求信息
        AllureHandle.add_request_to_report(
            method=kwargs.get('method', 'GET'),
            url=kwargs.get('url', ''),
            headers=kwargs.get('headers'),
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json_data=kwargs.get('json')
        )
        
        # 发送请求
        try:
            response = self._session.request(**kwargs, verify=False)
            response_time = time.time() - start_time
            
            # 记录响应
            response_json = None
            response_text = None
            try:
                response_json = response.json()
                logger.info(f"📥 响应[{response.status_code}]: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            except:
                response_text = response.text[:500]
                logger.info(f"📥 响应[{response.status_code}]: {response_text}")
            
            # 添加到 Allure 报告 - 响应信息
            AllureHandle.add_response_to_report(
                status_code=response.status_code,
                response_json=response_json,
                response_text=response_text if not response_json else None,
                response_time=response_time
            )
            
            logger.info(f"{'='*80}\n")
            return response
            
        except Exception as e:
            logger.error(f"❌ 请求失败: {e}")
            logger.info(f"{'='*80}\n")
            # 添加错误信息到 Allure
            AllureHandle.add_step_with_attachment(
                title="请求失败",
                content=str(e),
                attachment_type="TEXT"
            )
            raise

