# Allure Handle

轻量级 Allure 报告处理工具，用于 pytest 测试框架。

## 特点

- ✅ **最小依赖**：只需要 `allure-pytest`
- ✅ **简单易用**：提供简洁的 API
- ✅ **功能完整**：支持请求/响应、测试数据、用例描述等
- ✅ **灵活配置**：开发者可以在测试用例中自由使用

## 安装

```bash
pip install allurehandle-lit
```

## 快速开始

### 1. 安装依赖

```bash
pip install allurehandle-lit pytest allure-pytest
```

### 2. 配置 pytest

创建 `pytest.ini`：

```ini
[pytest]
addopts = 
    -v
    --alluredir=reports/allure_results
```

### 3. 在测试用例中使用

```python
import pytest
import allure
from allure_handle import AllureHandle

@pytest.mark.order(1)
@allure.epic("用户管理")
class TestUser:
    
    def test_create_user(self):
        """创建用户"""
        # 添加测试数据到报告
        testdata = {"username": "test", "email": "test@example.com"}
        AllureHandle.add_testdata_to_report(testdata, "用户数据")
        
        # 添加请求信息
        AllureHandle.add_request_to_report(
            method='POST',
            url='https://api.example.com/users',
            json_data=testdata
        )
        
        # 执行请求（使用你的 HTTP 客户端）
        # response = requests.post(...)
        
        # 添加响应信息
        AllureHandle.add_response_to_report(
            status_code=200,
            response_json={"id": 1, "username": "test"},
            response_time=0.123
        )
        
        # 添加用例描述（可选）
        case_data = {
            'case_id': 'TC001',
            'case_module': '用户管理',
            'case_name': '创建用户',
            'case_priority': 3,  # 1-低, 2-中, 3-高
            'case_setup': '系统已登录',
            'case_step': '1. 准备数据\n2. 调用接口\n3. 验证结果',
            'case_expect_result': '用户创建成功',
            'case_result': 'passed'
        }
        AllureHandle.add_case_description_html(case_data)
```

### 4. 运行测试并生成报告

```bash
# 运行测试
pytest case/ -v --alluredir=reports/allure_results

# 生成报告
allure generate reports/allure_results -o reports/allure_reports --clean

# 打开报告
allure open reports/allure_reports
```

## API 文档

### AllureHandle.add_request_to_report()

添加请求信息到 Allure 报告。

```python
AllureHandle.add_request_to_report(
    method='POST',
    url='https://api.example.com/users',
    headers={'Authorization': 'Bearer token'},
    json_data={'name': 'test'}
)
```

### AllureHandle.add_response_to_report()

添加响应信息到 Allure 报告。

```python
AllureHandle.add_response_to_report(
    status_code=200,
    response_json={'id': 1, 'name': 'test'},
    response_time=0.123
)
```

### AllureHandle.add_testdata_to_report()

添加测试数据到 Allure 报告。

```python
AllureHandle.add_testdata_to_report(
    {"key": "value"},
    name="测试数据"
)
```

### AllureHandle.add_case_description_html()

添加用例描述HTML到 Allure 报告。

```python
AllureHandle.add_case_description_html({
    'case_id': 'TC001',
    'case_module': '模块名',
    'case_name': '用例名',
    'case_priority': 2,
    'case_setup': '前置条件',
    'case_step': '测试步骤',
    'case_expect_result': '预期结果',
    'case_result': 'passed'
})
```

### AllureHandle.add_step_with_attachment()

添加步骤并附加内容。

```python
AllureHandle.add_step_with_attachment(
    title="验证结果",
    content='{"status": "success"}',
    attachment_type="JSON"  # TEXT, JSON, HTML
)
```

### AllureHandle.add_file_to_report()

添加文件附件。

```python
AllureHandle.add_file_to_report(
    "log/requests.log",
    name="请求日志"
)
```

## 使用全局实例

也可以使用全局实例 `allure_handle`：

```python
from allure_handle import allure_handle

allure_handle.add_testdata_to_report({"key": "value"}, "数据")
```

## 依赖

- `allure-pytest>=2.13.0` - 唯一的依赖

## 许可证

MIT License

