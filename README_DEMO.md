# Allurehandle-Lit 使用 Demo

## 📝 快速开始

### 1. 安装依赖

```bash
pip install allurehandle-lit pytest allure-pytest
```

### 2. 运行 Demo

```bash
# 直接运行（会自动生成报告）
python demo_allure.py

# 或使用 pytest
pytest demo_allure.py --alluredir=reports/allure_results -v
```

### 3. 查看报告

```bash
# 生成报告
allure generate reports/allure_results -o reports/allure_reports --clean

# 打开报告
allure open reports/allure_reports
```

## 🎯 Demo 功能演示

`demo_allure.py` 演示了以下功能：

1. **测试数据展示** - 在报告中以表格形式展示测试数据
2. **用例描述** - 格式化的 HTML 用例描述，包含用例ID、优先级等信息
3. **步骤附件** - 支持 JSON、TEXT、HTML 等格式的附件
4. **测试分类** - 使用 Epic、Feature、Story、Severity 进行分类

## 📋 代码示例

### 基本用法

```python
import pytest
import allure
from allure_handle import AllureHandle

@allure.epic("模块名称")
class TestDemo:
    
    def test_example(self):
        # 1. 添加测试数据
        testdata = {"username": "test", "password": "123456"}
        AllureHandle.add_testdata_to_report(testdata, "测试数据")
        
        # 2. 添加用例描述
        case_data = {
            'case_id': 'TC_001',
            'case_module': '模块名',
            'case_name': '用例名',
            'case_priority': 3,
            'case_setup': '前置条件',
            'case_step': '测试步骤',
            'case_expect_result': '预期结果',
            'case_result': 'passed'
        }
        AllureHandle.add_case_description_html(case_data)
        
        # 3. 添加步骤附件
        with allure.step("执行操作"):
            AllureHandle.add_step_with_attachment(
                title="响应结果",
                content='{"code": 200}',
                attachment_type="JSON"
            )
```

## 🔧 主要 API

### `add_testdata_to_report(testdata, title)`
添加测试数据到报告

### `add_case_description_html(case_data)`
添加格式化的用例描述

### `add_step_with_attachment(title, content, attachment_type)`
添加步骤附件（支持 TEXT、JSON、HTML、XML）

## 📚 更多信息

- 详细安装指南: `INSTALL_ALLURE.md`
- 完整集成指南: `ALLURE_INTEGRATION.md`
- 包文档: [README.md](README.md)

