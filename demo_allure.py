# -*- coding:UTF-8 -*-
"""
Allurehandle-Lit 使用示例 Demo
演示如何使用 Allurehandle-Lit 增强测试报告
"""
import os
import sys
import subprocess
import pytest
import allure
from pathlib import Path
from allure_handle import AllureHandle

# 设置报告目录
BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "reports" / "allure_results"
REPORT_DIR = BASE_DIR / "reports" / "allure_reports"


@allure.epic("用户管理模块")
@allure.feature("用户CRUD操作")
class TestUserDemo:
    """用户管理测试用例示例"""
    
    @allure.story("创建用户")
    @allure.title("测试创建新用户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_user(self):
        """创建用户示例"""
        
        # 1. 添加测试数据到报告
        testdata = {
            "username": "test_user_001",
            "email": "test@example.com",
            "phone": "13800138000",
            "age": 25
        }
        AllureHandle.add_testdata_to_report(testdata, "创建用户测试数据")
        
        # 2. 添加用例描述（HTML格式）
        case_data = {
            'case_id': 'TC_USER_001',
            'case_module': '用户管理',
            'case_name': '创建新用户',
            'case_priority': 3,  # 1-低, 2-中, 3-高
            'case_setup': '系统已登录，具备用户管理权限',
            'case_step': '''1. 准备用户测试数据
2. 调用创建用户接口
3. 验证返回结果
4. 检查用户是否创建成功''',
            'case_expect_result': '用户创建成功，返回用户ID和基本信息',
            'case_result': 'passed'
        }
        AllureHandle.add_case_description_html(case_data)
        
        # 3. 添加测试步骤和附件
        with allure.step("准备测试数据"):
            print("准备用户数据...")
            AllureHandle.add_step_with_attachment(
                title="用户数据",
                content=str(testdata),
                attachment_type="JSON"
            )
        
        with allure.step("调用创建用户接口"):
            # 模拟接口调用
            response = {
                "code": 200,
                "message": "success",
                "data": {
                    "user_id": "12345",
                    "username": "test_user_001",
                    "created_at": "2024-01-01 10:00:00"
                }
            }
            
            # 添加响应结果附件
            AllureHandle.add_step_with_attachment(
                title="接口响应",
                content=str(response),
                attachment_type="JSON"
            )
        
        with allure.step("验证返回结果"):
            assert response["code"] == 200
            assert response["data"]["user_id"] is not None
            print("[OK] 用户创建成功")
    
    @allure.story("查询用户")
    @allure.title("测试查询用户列表")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_user_list(self):
        """查询用户列表示例"""
        
        # 添加用例描述
        case_data = {
            'case_id': 'TC_USER_002',
            'case_module': '用户管理',
            'case_name': '查询用户列表',
            'case_priority': 2,
            'case_setup': '系统已登录',
            'case_step': '1. 调用用户列表接口\n2. 验证返回列表数据',
            'case_expect_result': '返回用户列表，包含分页信息',
            'case_result': 'passed'
        }
        AllureHandle.add_case_description_html(case_data)
        
        with allure.step("调用用户列表接口"):
            # 模拟接口调用
            response = {
                "code": 200,
                "data": {
                    "total": 100,
                    "page": 1,
                    "page_size": 20,
                    "users": [
                        {"id": 1, "username": "user1"},
                        {"id": 2, "username": "user2"}
                    ]
                }
            }
            
            AllureHandle.add_step_with_attachment(
                title="列表响应",
                content=str(response),
                attachment_type="JSON"
            )
        
        assert response["code"] == 200
        assert len(response["data"]["users"]) > 0
    
    @allure.story("更新用户")
    @allure.title("测试更新用户信息")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_user(self):
        """更新用户示例"""
        
        # 添加测试数据
        update_data = {
            "user_id": "12345",
            "email": "newemail@example.com",
            "phone": "13900139000"
        }
        AllureHandle.add_testdata_to_report(update_data, "更新用户数据")
        
        # 添加用例描述
        case_data = {
            'case_id': 'TC_USER_003',
            'case_module': '用户管理',
            'case_name': '更新用户信息',
            'case_priority': 3,
            'case_setup': '系统已登录，存在测试用户',
            'case_step': '1. 准备更新数据\n2. 调用更新接口\n3. 验证更新结果',
            'case_expect_result': '用户信息更新成功',
            'case_result': 'passed'
        }
        AllureHandle.add_case_description_html(case_data)
        
        with allure.step("调用更新接口"):
            response = {
                "code": 200,
                "message": "更新成功"
            }
            
            AllureHandle.add_step_with_attachment(
                title="更新响应",
                content=str(response),
                attachment_type="TEXT"
            )
        
        assert response["code"] == 200


def check_allure_installed():
    """检查 Allure CLI 是否已安装"""
    try:
        result = subprocess.run(
            ["allure", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=True
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return False


def generate_allure_report():
    """生成 Allure 报告"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    if not list(RESULTS_DIR.glob("*")):
        print("\n[WARN] 没有找到测试结果文件，请先运行测试")
        return False
    
    if not check_allure_installed():
        print("\n[WARN] Allure CLI 未安装，无法生成报告")
        print("测试结果已保存到:", RESULTS_DIR)
        print("安装 Allure CLI 后，运行以下命令生成报告:")
        print(f"  allure generate {RESULTS_DIR} -o {REPORT_DIR} --clean")
        return False
    
    print("\n" + "=" * 60)
    print("正在生成 Allure 报告...")
    print("=" * 60)
    
    try:
        cmd = [
            "allure", "generate",
            str(RESULTS_DIR),
            "-o", str(REPORT_DIR),
            "--clean"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print(f"\n[OK] 报告生成成功: {REPORT_DIR}")
            print(f"\n打开报告命令: allure open {REPORT_DIR}")
            
            try:
                choice = input("\n是否打开报告? (y/n): ").strip().lower()
                if choice == 'y':
                    subprocess.Popen(["allure", "open", str(REPORT_DIR)], shell=True)
                    print("[OK] 报告已在浏览器中打开")
            except KeyboardInterrupt:
                print("\n已取消")
            
            return True
        else:
            print(f"\n[ERROR] 报告生成失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] 生成报告时出错: {e}")
        return False


if __name__ == "__main__":
    """
    运行方式:
    直接运行: python demo_allure.py
    会自动执行测试并生成 Allure 报告
    """
    print("=" * 60)
    print("Allurehandle-Lit Demo - 自动运行测试并生成报告")
    print("=" * 60)
    print()
    
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    print("开始运行测试...")
    exit_code = pytest.main([
        __file__,
        "--alluredir", str(RESULTS_DIR),
        "-v",
        "-s"
    ])
    
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("[OK] 所有测试通过")
    else:
        print("[WARN] 部分测试失败")
    print("=" * 60)
    
    generate_allure_report()
    
    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)

