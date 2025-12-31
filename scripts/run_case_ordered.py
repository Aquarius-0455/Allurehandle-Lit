# -*- coding:UTF-8 -*-
"""
按自定义顺序执行测试用例的示例
"""
import unittest
from framework import HTMLTestRunner_PY3
from utils.test_order import OrderedTestSuite, OrderedTestLoader
import os
import datetime

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(BASE_DIR, "case")
REPORT_DIR = os.path.join(BASE_DIR, "report")


def run(test_suite):
    report_name = f"report_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.html"
    report_path = os.path.join(REPORT_DIR, report_name)
    
    with open(report_path, 'wb') as fp:
        runner = HTMLTestRunner_PY3.HTMLTestRunner(
            stream=fp,
            title='《接口自动化测试报告》',
            description='Data Intelligence',
            verbosity=2
        )
        runner.run(test_suite)


if __name__ == "__main__":
    
    # ============= 方式1：按优先级装饰器执行（支持类和方法级别） =============
    # 在测试用例中使用 @priority(1) 装饰器
    # 类级别：控制类的执行顺序
    # 方法级别：控制类内方法的执行顺序
    loader = OrderedTestLoader()
    suite = loader.discover(TEST_DIR, pattern="test_example*.py")  # 测试示例
    
    
    # ============= 方式2：按指定方法顺序执行 =============
    # suite = OrderedTestSuite.by_names([
    #     # (模块名, 类名, 方法名)
    #     ('case.test_a_workspace', 'Merchants_Case', 'test_a_save'),
    #     ('case.test_a_workspace', 'Merchants_Case', 'test_b_pglist'),
    #     ('case.test_b_connector', 'Connector_Case', 'test_a_list'),
    #     ('case.test_a_workspace', 'Merchants_Case', 'test_c_detail'),
    #     ('case.test_a_workspace', 'Merchants_Case', 'test_d_update'),
    #     ('case.test_a_workspace', 'Merchants_Case', 'test_e_delete'),
    # ])
    
    
    # ============= 方式3：按文件顺序执行 =============
    # suite = OrderedTestSuite.by_files([
    #     'case/test_b_connector.py',  # 先执行连接器测试
    #     'case/test_a_workspace.py',  # 再执行商户测试
    # ])
    
    
    run(suite)

