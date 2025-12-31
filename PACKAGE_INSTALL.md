# Allure Handle 打包和安装指南

## 包信息

- **包名**: `allure-handle`
- **版本**: 1.0.0
- **最小依赖**: 只需要 `allure-pytest>=2.13.0`

## 方式1: 本地开发安装（推荐）

### 安装到本地环境

```bash
# 在项目根目录执行
pip install -e .
```

安装后可以直接使用：

```python
from allure_handle import AllureHandle, allure_handle

# 使用类方法
AllureHandle.add_testdata_to_report({"key": "value"}, "测试数据")

# 或使用全局实例
allure_handle.add_testdata_to_report({"key": "value"}, "测试数据")
```

## 方式2: 打包成 wheel 文件

### 1. 安装打包工具

```bash
pip install build wheel
```

### 2. 打包

```bash
# 使用 build 工具（推荐）
python -m build

# 或者使用 setuptools
python setup.py sdist bdist_wheel
```

打包后会生成：
- `dist/allure_handle-1.0.0-py3-none-any.whl` - wheel 文件
- `dist/allure-handle-1.0.0.tar.gz` - 源码包

### 3. 安装打包好的文件

```bash
# 安装 wheel 文件
pip install dist/allure_handle-1.0.0-py3-none-any.whl

# 或安装源码包
pip install dist/allure-handle-1.0.0.tar.gz
```

## 方式3: 发布到 PyPI（可选）

### 1. 注册 PyPI 账号

访问 https://pypi.org/account/register/

### 2. 安装发布工具

```bash
pip install twine
```

### 3. 上传到 PyPI

```bash
# 先上传到测试 PyPI
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ allure-handle

# 确认无误后上传到正式 PyPI
twine upload dist/*
```

### 4. 安装发布的包

```bash
pip install allure-handle
```

## 使用方式

### 在测试项目中安装

```bash
# 安装 allure-handle
pip install allure-handle

# 安装 pytest 和 allure-pytest（如果还没有）
pip install pytest allure-pytest
```

### 在测试用例中使用

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
        
        # 执行请求...
        # response = requests.post(...)
        
        # 添加响应信息
        AllureHandle.add_response_to_report(
            status_code=200,
            response_json={"id": 1},
            response_time=0.123
        )
        
        # 添加用例描述（可选）
        AllureHandle.add_case_description_html({
            'case_id': 'TC001',
            'case_module': '用户管理',
            'case_name': '创建用户',
            'case_priority': 3,
            'case_setup': '系统已登录',
            'case_step': '1. 准备数据\n2. 调用接口',
            'case_expect_result': '用户创建成功',
            'case_result': 'passed'
        })
```

### 配置 pytest.ini

```ini
[pytest]
addopts = 
    -v
    --alluredir=reports/allure_results

testpaths = case
```

### 运行测试

```bash
# 运行测试
pytest case/ -v --alluredir=reports/allure_results

# 生成 Allure 报告
allure generate reports/allure_results -o reports/allure_reports --clean

# 打开报告
allure open reports/allure_reports
```

## 包结构

打包后会包含：
- ✅ `allure_handle/` - 核心模块
  - `__init__.py` - 包初始化
  - `allure_handle.py` - 主要功能实现

不会包含：
- ❌ `case/` - 测试用例（用户自己编写）
- ❌ `reports/` - 测试报告（运行时生成）
- ❌ `log/` - 日志文件（运行时生成）
- ❌ 其他项目文件

## 依赖说明

**最小依赖**：
- `allure-pytest>=2.13.0` - 唯一的必需依赖

**可选依赖**（由开发者自己安装）：
- `pytest` - 测试框架
- `requests` - HTTP 请求（如果需要）
- 其他工具库

## 版本管理

更新版本号：
1. 修改 `setup.py` 中的 `version`
2. 修改 `pyproject.toml` 中的 `version`
3. 修改 `allure_handle/__init__.py` 中的 `__version__`
4. 重新打包和发布

## 注意事项

1. **最小依赖**：包只依赖 `allure-pytest`，其他依赖由开发者自己管理
2. **灵活使用**：开发者可以在测试用例中自由使用 AllureHandle 的功能
3. **配置独立**：pytest 配置和 Allure 配置由开发者自己管理
4. **轻量级**：包体积小，安装快速
