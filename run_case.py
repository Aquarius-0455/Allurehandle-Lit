# -*- coding:UTF-8 -*-
"""
使用 pytest + allure 运行测试用例
"""
import pytest
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(BASE_DIR, "case")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
ALLURE_RESULTS_DIR = os.path.join(REPORT_DIR, "allure_results")
ALLURE_REPORT_DIR = os.path.join(REPORT_DIR, "allure_reports")


def run_tests():
    """
    运行测试用例并生成 Allure 报告
    """
    # 确保报告目录存在
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(ALLURE_RESULTS_DIR, exist_ok=True)
    
    # pytest 命令行参数
    pytest_args = [
        TEST_DIR,
        f"--alluredir={ALLURE_RESULTS_DIR}",  # Allure 结果目录（使用绝对路径）
    ]
    
    # 运行测试
    print("="*80)
    print("开始运行测试用例...")
    print("="*80)
    exit_code = pytest.main(pytest_args)
    
    # 生成 Allure 报告
    print("\n" + "="*80)
    print("正在生成 Allure 报告...")
    print("="*80)
    
    # 检测 Allure 命令行工具
    allure_found = False
    allure_cmd = None
    
    # Windows 上优先尝试 allure.bat
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["allure.bat", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            if result.returncode == 0:
                allure_found = True
                allure_cmd = "allure.bat"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    
    # 方法1: 尝试直接调用 allure 命令
    if not allure_found:
        try:
            result = subprocess.run(
                ["allure", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=(sys.platform == "win32")
            )
            if result.returncode == 0:
                allure_found = True
                allure_cmd = "allure"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    
    # 方法2: 尝试使用 where 命令查找 (Windows)
    if not allure_found and sys.platform == "win32":
        try:
            result = subprocess.run(
                ["where", "allure"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            if result.returncode == 0 and result.stdout.strip():
                allure_path = result.stdout.strip().split('\n')[0].strip()
                # 检查是否是 .bat 文件
                if allure_path.endswith('.bat'):
                    allure_cmd = allure_path
                else:
                    allure_cmd = "allure"
                allure_found = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    
    # 方法3: 尝试使用 which 命令查找 (Linux/Mac)
    if not allure_found and sys.platform != "win32":
        try:
            result = subprocess.run(
                ["which", "allure"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                allure_found = True
                allure_cmd = result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    
    if allure_found:
        try:
            # 检查结果目录是否存在且有文件
            if not os.path.exists(ALLURE_RESULTS_DIR):
                print(f"⚠️ 测试结果目录不存在: {ALLURE_RESULTS_DIR}")
            elif not os.listdir(ALLURE_RESULTS_DIR):
                print(f"⚠️ 测试结果目录为空: {ALLURE_RESULTS_DIR}")
            else:
                # 生成 Allure 报告
                print(f"正在使用 Allure 生成报告...")
                print(f"   命令: {allure_cmd} generate {ALLURE_RESULTS_DIR} -o {ALLURE_REPORT_DIR} --clean")
                
                # 确保使用绝对路径
                results_path = os.path.abspath(ALLURE_RESULTS_DIR)
                report_path = os.path.abspath(ALLURE_REPORT_DIR)
                
                result = subprocess.run(
                    [
                        allure_cmd, "generate",
                        results_path,
                        "-o", report_path,
                        "--clean"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    shell=(sys.platform == "win32" and allure_cmd.endswith('.bat'))
                )
                
                if result.returncode == 0:
                    print(f"\n✅ Allure 报告已生成: {ALLURE_REPORT_DIR}")
                    print(f"\n📊 打开报告方式:")
                    print(f"   方式1: allure open {ALLURE_REPORT_DIR}")
                    report_url = f"file:///{report_path.replace(os.sep, '/')}/index.html"
                    print(f"   方式2: 在浏览器中打开: {report_url}")
                else:
                    print(f"⚠️ Allure 报告生成失败 (退出码: {result.returncode}):")
                    if result.stdout:
                        print(f"   输出: {result.stdout}")
                    if result.stderr:
                        print(f"   错误: {result.stderr}")
        except FileNotFoundError as e:
            print(f"⚠️ 找不到 Allure 命令: {allure_cmd}")
            print(f"   错误详情: {e}")
            print(f"   请检查 Allure 是否正确安装并配置在 PATH 中")
        except subprocess.TimeoutExpired:
            print(f"⚠️ Allure 报告生成超时")
        except Exception as e:
            print(f"⚠️ 生成 Allure 报告时出错: {e}")
            import traceback
            print(f"   详细错误: {traceback.format_exc()}")
    else:
        print("⚠️ 未检测到 Allure 命令行工具")
        print("\n📦 Allure 安装指南:")
        print("   1. 确保已安装 Java (运行: java -version)")
        print("   2. 下载 Allure:")
        print("      Windows: https://github.com/allure-framework/allure2/releases")
        print("      下载 allure-2.x.x.zip 并解压")
        print("   3. 配置环境变量:")
        print("      将 Allure 的 bin 目录添加到系统 PATH")
        print("      例如: C:\\allure\\bin")
        print("   4. 验证安装: allure --version")
        print(f"\n💾 测试结果已保存到: {ALLURE_RESULTS_DIR}")
        print(f"   安装 Allure 后运行以下命令生成报告:")
        print(f"   allure generate {ALLURE_RESULTS_DIR} -o {ALLURE_REPORT_DIR} --clean")
    
    print("="*80)
    
    return exit_code


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)



