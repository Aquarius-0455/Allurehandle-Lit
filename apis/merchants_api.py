# -*- coding:UTF-8 -*-
"""
商户模块API - 增强版
使用新的YAML配置结构
"""

from faker import Faker
from utils.yaml_loader import get_yaml_loader
from utils.logger import logger
from utils.request_utils import RequestUtils

# 全局变量存储数据
MERCHANT_DATA = {}
merchant_no = None
Fk_merchantName = None

faker_data = Faker(locale='zh_CN')
yaml_loader = get_yaml_loader()


class MerchantsAPI:
    """商户API封装类"""
    
    def __init__(self):
        self.loader = yaml_loader
        self.request = RequestUtils()
        self.module = "merchants"
    
    def _send_request(self, api_config: dict) -> dict:
        """
        发送请求的通用方法
        
        Args:
            api_config: API配置字典
        
        Returns:
            响应的JSON数据
        """
        # 构建请求参数
        params = {
            'url': api_config['url'],
            'method': api_config['method'],
            'headers': api_config['headers']
        }
        
        # 根据body_type添加数据
        if 'json' in api_config:
            params['json'] = api_config['json']
        elif 'data' in api_config:
            params['data'] = api_config['data']
        elif 'params' in api_config:
            params['params'] = api_config['params']
        
        # 发送请求
        response = self.request.send_request(**params)
        return response.json()
    
    def _assert_response(self, response_json: dict, assertions: list):
        """
        通用断言方法
        
        Args:
            response_json: 响应JSON
            assertions: 断言列表
        """
        for assertion in assertions:
            assert_type = assertion.get('type')
            
            if assert_type == 'json_path':
                path = assertion.get('path')
                expected = assertion.get('expected')
                actual = response_json.get(path)
                assert actual == expected, f"断言失败: {path} 期望={expected}, 实际={actual}"
            
            elif assert_type == 'status_code':
                # 状态码在请求工具中已经检查
                pass
    
    def save(self, custom_data: dict = None):
        """
        新增商户
        
        Args:
            custom_data: 自定义数据，覆盖默认值
        """
        global Fk_merchantName
        
        # 生成商户名
        Fk_merchantName = f"API-AUTO-{faker_data.phone_number()}"
        
        # 准备请求数据
        override_body = custom_data or {}
        override_body['merchantName'] = Fk_merchantName
        
        # 获取API配置
        api_config = self.loader.get_api_config(
            module=self.module,
            api='save',
            override_body=override_body
        )
        
        try:
            # 发送请求
            response_json = self._send_request(api_config)
            
            # 断言
            self._assert_response(response_json, api_config['assertions'])
            
            # 输出到报告
            print(f"✅ 商户新增成功: {Fk_merchantName}")
            print(f"响应结果: {response_json}")
            
            logger.info(f"✅ 商户新增成功: {Fk_merchantName}")
            return response_json
            
        except Exception as e:
            print(f"❌ 商户新增失败: {str(e)}")
            logger.error(f"❌ 商户新增失败: {str(e)}")
            raise
    
    def list(self, merchant_name: str = None):
        """
        查询商户列表
        
        Args:
            merchant_name: 商户名称（可选）
        """
        global merchant_no
        
        # 准备请求数据
        override_body = {}
        if merchant_name:
            override_body['merchantName'] = merchant_name
        else:
            override_body['merchantName'] = Fk_merchantName or ''
        
        # 获取API配置
        api_config = self.loader.get_api_config(
            module=self.module,
            api='list',
            override_body=override_body
        )
        
        try:
            # 发送请求
            response_json = self._send_request(api_config)
            
            # 断言
            self._assert_response(response_json, api_config['assertions'])
            
            # 提取merchant_no
            try:
                merchant_no = response_json['data']['list'][0]['merchantNo']
                print(f"✅ 商户列表查询成功, merchantNo={merchant_no}")
                logger.info(f"✅ 商户列表查询成功, merchantNo={merchant_no}")
            except (KeyError, IndexError):
                print("⚠️ 未找到merchantNo")
                logger.warning("⚠️ 未找到merchantNo")
            
            print(f"响应结果: {response_json}")
            return response_json
            
        except Exception as e:
            print(f"❌ 商户列表查询失败: {str(e)}")
            logger.error(f"❌ 商户列表查询失败: {str(e)}")
            raise
    
    def detail(self, merchant_id: str = None):
        """
        查询商户详情
        
        Args:
            merchant_id: 商户ID（可选，不传则使用全局merchant_no）
        """
        global MERCHANT_DATA
        
        # 获取商户ID
        target_id = merchant_id or merchant_no
        if not target_id:
            raise ValueError("merchant_id不能为空")
        
        # 获取API配置
        api_config = self.loader.get_api_config(
            module=self.module,
            api='detail',
            path_params={'merchant_no': target_id}
        )
        
        try:
            # 发送请求
            response_json = self._send_request(api_config)
            
            # 断言
            self._assert_response(response_json, api_config['assertions'])
            
            # 存储商户数据
            data = response_json['data']
            MERCHANT_DATA = {
                "name": data["merchantName"],
                "status": data["merchantStatus"],
                "country": data["merchantCountry"],
                "currency": data["merchantCurrency"],
                "state": data["merchantState"],
                "city": data["merchantCity"],
                "address": data["merchantAddress"],
                "zipcode": data["merchantZipCode"],
                "type": data["type"],
                "logo_id": data["merchantLogoId"]
            }
            
            print(f"✅ 商户详情查询成功: {MERCHANT_DATA['name']}")
            print(f"响应结果: {response_json}")
            logger.info(f"✅ 商户详情查询成功: {MERCHANT_DATA['name']}")
            return response_json
            
        except Exception as e:
            print(f"❌ 商户详情查询失败: {str(e)}")
            logger.error(f"❌ 商户详情查询失败: {str(e)}")
            raise
    
    def update(self, merchant_id: str = None, custom_data: dict = None):
        """
        更新商户
        
        Args:
            merchant_id: 商户ID（可选）
            custom_data: 自定义数据（可选）
        """
        # 获取商户ID
        target_id = merchant_id or merchant_no
        if not target_id:
            raise ValueError("merchant_id不能为空")
        
        # 准备更新数据
        if custom_data:
            override_body = custom_data
        else:
            # 使用详情数据更新
            override_body = {
                "merchantName": f"修改后的-{MERCHANT_DATA['name']}",
                "merchantStatus": MERCHANT_DATA['status'],
                "merchantCountry": MERCHANT_DATA['country'],
                "merchantCurrency": MERCHANT_DATA['currency'],
                "merchantState": MERCHANT_DATA['state'],
                "merchantCity": MERCHANT_DATA['city'],
                "merchantAddress": MERCHANT_DATA['address'],
                "merchantZipCode": MERCHANT_DATA['zipcode'],
                "type": MERCHANT_DATA['type'],
                "merchantLogoId": MERCHANT_DATA['logo_id']
            }
        
        # 获取API配置
        api_config = self.loader.get_api_config(
            module=self.module,
            api='update',
            path_params={'merchant_no': target_id},
            override_body=override_body
        )
        
        try:
            # 发送请求
            response_json = self._send_request(api_config)
            
            # 断言
            self._assert_response(response_json, api_config['assertions'])
            
            print(f"✅ 商户更新成功")
            print(f"响应结果: {response_json}")
            logger.info(f"✅ 商户更新成功")
            return response_json
            
        except Exception as e:
            print(f"❌ 商户更新失败: {str(e)}")
            logger.error(f"❌ 商户更新失败: {str(e)}")
            raise
    
    def delete(self, merchant_id: str = None):
        """
        删除商户
        
        Args:
            merchant_id: 商户ID（可选）
        """
        # 获取商户ID
        target_id = merchant_id or merchant_no
        if not target_id:
            raise ValueError("merchant_id不能为空")
        
        # 获取API配置
        api_config = self.loader.get_api_config(
            module=self.module,
            api='delete',
            path_params={'merchant_no': target_id}
        )
        
        try:
            # 发送请求
            response_json = self._send_request(api_config)
            
            # 断言
            self._assert_response(response_json, api_config['assertions'])
            
            print(f"✅ 商户删除成功")
            print(f"响应结果: {response_json}")
            logger.info(f"✅ 商户删除成功")
            return response_json
            
        except Exception as e:
            print(f"❌ 商户删除失败: {str(e)}")
            logger.error(f"❌ 商户删除失败: {str(e)}")
            raise
    
    def shopify_v3_test(self, merchant_id: str = None, custom_data: dict = None):
        """
        ShopifyV3连接器测试
        
        Args:
            merchant_id: 商户ID（可选，用于referer中的merchant_no）
            custom_data: 自定义数据（可选），可覆盖默认的连接器配置
        """
        # 获取商户ID
        target_id = merchant_id or merchant_no
        if not target_id:
            raise ValueError("merchant_id不能为空")
        
        # 准备请求数据
        override_body = custom_data or {}
        
        # 获取API配置，传入path_params用于替换referer中的{merchant_no}
        api_config = self.loader.get_api_config(
            module=self.module,
            api='shopify_v3_test',
            path_params={'merchant_no': target_id},
            override_body=override_body
        )
        
        try:
            # 发送请求
            response_json = self._send_request(api_config)
            
            # 断言
            self._assert_response(response_json, api_config['assertions'])
            
            print(f"✅ ShopifyV3连接器测试成功")
            print(f"响应结果: {response_json}")
            logger.info(f"✅ ShopifyV3连接器测试成功")
            return response_json
            
        except Exception as e:
            print(f"❌ ShopifyV3连接器测试失败: {str(e)}")
            logger.error(f"❌ ShopifyV3连接器测试失败: {str(e)}")
            raise
    
    def create_channel(self, merchant_id: str = None, channel_name: str = None, custom_data: dict = None):
        """
        新增渠道
        
        Args:
            merchant_id: 商户ID（可选，不传则使用全局merchant_no）
            channel_name: 渠道名称（可选，不传则使用默认值）
            custom_data: 自定义数据（可选），可覆盖默认的渠道配置
        """

        Fk_connectorName = f"API-AUTO-{faker_data.phone_number()}"

        # 获取商户ID
        target_id = merchant_id or merchant_no
        if not target_id:
            raise ValueError("merchant_id不能为空")
        
        # 准备请求数据
        override_body = custom_data or {}
        override_body['channelName'] = Fk_connectorName
        
        # 设置customerCode为商户ID
        if 'customerCode' not in override_body:
            override_body['customerCode'] = target_id

        # 获取API配置
        api_config = self.loader.get_api_config(
            module=self.module,
            api='create_channel',
            path_params={'merchant_no': target_id},
            override_body=override_body
        )
        
        try:
            # 发送请求
            response_json = self._send_request(api_config)
            
            # 断言
            self._assert_response(response_json, api_config['assertions'])
            
            print(f"✅ 渠道创建成功")
            print(f"响应结果: {response_json}")
            logger.info(f"✅ 渠道创建成功")
            return response_json
            
        except Exception as e:
            print(f"❌ 渠道创建失败: {str(e)}")
            logger.error(f"❌ 渠道创建失败: {str(e)}")
            raise


