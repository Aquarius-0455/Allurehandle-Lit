# Allure Handle - 轻量级 Allure 报告工具

## 📦 安装

```bash
pip install allure-handle
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install allure-handle pytest allure-pytest
```

### 2. 在测试用例中使用

```python
import pytest
import allure
from allure_handle import AllureHandle

@pytest.mark.order(1)
@allure.epic("用户管理")
class TestUser:
    
    def test_create_user(self):
        """创建用户"""
        # 添加测试数据
        testdata = {"username": "test", "email": "test@example.com"}
        AllureHandle.add_testdata_to_report(testdata, "用户数据")
        
        # 添加请求信息
        AllureHandle.add_request_to_report(
            method='POST',
            url='https://api.example.com/users',
            json_data=testdata
        )
        
        # 执行你的请求...
        # response = your_http_client.post(...)
        
        # 添加响应信息
        AllureHandle.add_response_to_report(
            status_code=200,
            response_json={"id": 1, "username": "test"},
            response_time=0.123
        )
```

### 3. 运行测试

```bash
pytest case/ -v --alluredir=reports/allure_results
allure generate reports/allure_results -o reports/allure_reports --clean
allure open reports/allure_reports
```

## ✨ 功能

- ✅ **添加请求信息** - `add_request_to_report()`
- ✅ **添加响应信息** - `add_response_to_report()`
- ✅ **添加测试数据** - `add_testdata_to_report()`
- ✅ **添加用例描述** - `add_case_description_html()`
- ✅ **添加步骤附件** - `add_step_with_attachment()`
- ✅ **添加文件附件** - `add_file_to_report()`

## 📋 API 文档

详细 API 文档请查看 `allure_handle/README.md`

## 💡 特点

- **最小依赖**：只需要 `allure-pytest`
- **简单易用**：提供简洁的 API
- **灵活配置**：开发者可以在测试用例中自由使用
- **轻量级**：包体积小，安装快速

## 📝 打包和发布

详细说明请查看 `PACKAGE_INSTALL.md`

