# -*- coding:UTF-8 -*-
import pytest
import allure
from utils.allure_handle import AllureHandle  # 导入 Allure 工具类
from utils.yaml_loader import get_yaml_loader
from apis.merchants_api import MerchantsAPI


@pytest.mark.order(1)  # 使用 pytest-ordering 插件控制执行顺序
@allure.epic("商户管理")
@allure.feature("商户CRUD操作")
class TestMerchants:
    """商户测试用例"""
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        """类级别的初始化"""
        # 直接创建实例，不使用 fixtures
        self.api = MerchantsAPI()
        self.loader = get_yaml_loader()

    @pytest.mark.order(1)
    @allure.story("新增商户")
    @allure.title("新增商户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_a_save(self):
        """新增商户"""
        # 获取测试数据
        testdata = self.loader.get_testdata('merchants_testdata', 'normal.save_merchant_1')
        
        # 方式1: 添加测试数据到 Allure 报告（推荐）
        AllureHandle.add_testdata_to_report(testdata, "新增商户测试数据")
        
        # 方式2: 也可以添加用例描述HTML（可选）
        # case_data = {
        #     'case_id': 'TC_MERCHANT_001',
        #     'case_module': '商户管理',
        #     'case_name': '新增商户',
        #     'case_priority': 3,  # 1-低, 2-中, 3-高
        #     'case_setup': '系统已登录',
        #     'case_step': '1. 准备商户数据\n2. 调用新增商户接口\n3. 验证返回结果',
        #     'case_expect_result': '商户创建成功，返回商户信息',
        #     'case_result': 'passed'
        # }
        # AllureHandle.add_case_description_html(case_data)

        # 使用测试数据新增商户
        # 注意：请求和响应信息会自动记录到 Allure（已在 request_utils 中集成）
        with allure.step("调用新增商户接口"):
            response = self.api.save(custom_data=testdata)
            
            # 如果需要添加额外的验证步骤信息
            with allure.step("验证商户创建成功"):
                AllureHandle.add_step_with_attachment(
                    title="创建结果",
                    content=f"商户名称: {response.get('data', {}).get('merchantName', 'N/A')}",
                    attachment_type="TEXT"
                )

    @pytest.mark.order(2)
    @allure.story("商户列表")
    @allure.title("查询商户列表")
    @allure.severity(allure.severity_level.NORMAL)
    def test_b_pglist(self):
        """商户列表"""
        # 请求和响应会自动记录到 Allure
        with allure.step("调用商户列表接口"):
            response = self.api.list()
            
            # 可选：添加查询结果摘要到报告
            if response and 'data' in response:
                result_summary = {
                    "查询结果": "成功",
                    "商户数量": len(response.get('data', {}).get('list', []))
                }
                AllureHandle.add_testdata_to_report(result_summary, "查询结果摘要")

    @pytest.mark.order(3)
    @allure.story("商户详情")
    @allure.title("查询商户详情")
    @allure.severity(allure.severity_level.NORMAL)
    def test_c_detail(self):
        """商户详情"""
        with allure.step("调用商户详情接口"):
            response = self.api.detail()
            
            # 可选：添加商户详情信息到报告
            if response and 'data' in response:
                merchant_info = {
                    "商户名称": response['data'].get('merchantName'),
                    "商户状态": response['data'].get('merchantStatus'),
                    "商户国家": response['data'].get('merchantCountry')
                }
                AllureHandle.add_testdata_to_report(merchant_info, "商户详情信息")

    @pytest.mark.order(4)
    @allure.story("更新商户")
    @allure.title("更新商户信息")
    @allure.severity(allure.severity_level.NORMAL)
    def test_d_update(self):
        """更新商户"""
        # 准备更新数据
        update_data = {
            "merchantName": "更新后的商户名称"
        }
        AllureHandle.add_testdata_to_report(update_data, "更新数据")
        
        with allure.step("调用更新商户接口"):
            self.api.update()

    # @pytest.mark.order(5)
    # @allure.story("连接器管理")
    # @allure.title("添加连接器和渠道")
    # @allure.severity(allure.severity_level.NORMAL)
    # def test_e_connecter(self):
    #     """添加连接器"""
    #     with allure.step("测试Shopify V3连接器"):
    #         self.api.shopify_v3_test()
    #     with allure.step("创建渠道"):
    #         self.api.create_channel()

    @pytest.mark.order(5)
    @allure.story("删除商户")
    @allure.title("删除商户")
    @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.skip("测试时，不删除商户")
    def test_f_delete(self):
        """删除商户"""
        with allure.step("调用删除商户接口"):
            response = self.api.delete()
            
            # 可选：添加删除结果到报告
            if response:
                AllureHandle.add_step_with_attachment(
                    title="删除结果",
                    content=f"删除状态: {response.get('code', 'N/A')}",
                    attachment_type="TEXT"
                )
        
        # 可选：添加日志文件到报告（如果有）
        # AllureHandle.add_file_to_report("log/requests.log", "请求日志")




