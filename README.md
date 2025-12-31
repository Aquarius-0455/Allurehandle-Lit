# 接口自动化测试框架使用说明

> **Data Intelligence API 自动化测试框架**
>
> 基于 Python + Pytest + Allure + YAML 配置驱动的接口自动化测试框架

---

## 📁 目录结构

```
Api-Tc-Fw/
├── apis/                           # API 封装层
│   └── merchants_api.py           # 商户模块 API 封装
├── case/                           # 测试用例层
│   └── test_a_workspace.py        # 商户测试用例
├── framework/                      # 测试报告生成器
│   └── HTMLTestRunner_PY3.py      # HTML 报告生成器
├── locust/                         # 性能测试目录
│   ├── run_locust.py              # Locust 无界面运行脚本
│   └── run_locust_web.py          # Locust Web UI 运行脚本
├── log/                            # 日志目录
│   └── requests.log               # 请求日志
├── reports/                        # 测试报告目录
│   └── api_report.html            # HTML 测试报告
├── resources/                      # 资源配置目录
│   ├── config.yaml                # 环境配置（Base URL、Token、公共Headers）
│   ├── api/                       # API 接口定义
│   │   └── merchants.yaml         # 商户模块接口定义
│   └── testdata/                  # 测试数据
│       └── merchants_testdata.yaml # 商户模块测试数据
├── utils/                          # 工具类
│   ├── email_sender.py            # 邮件发送工具
│   ├── locust_config.py           # Locust 性能测试配置
│   ├── logger.py                  # 日志工具
│   ├── request_utils.py           # HTTP 请求工具
│   ├── test_order.py              # 测试顺序控制
│   ├── token_manager.py           # Token 管理器
│   └── yaml_loader.py             # YAML 配置加载器
├── scripts/                        # 脚本目录
│   └── run_case_ordered.py        # 按顺序执行脚本
└── run_case.py                     # 主运行入口
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖（推荐使用 requirements.txt）
pip install -r requirements.txt

# 安装 Allure 命令行工具（用于生成 Allure 报告）
# Windows: 下载 https://github.com/allure-framework/allure2/releases
# Mac: brew install allure
# Linux: 参考 https://docs.qameta.io/allure/
```

### 2. 配置环境

编辑 `resources/config.yaml`，配置测试环境：

```yaml
# 当前使用环境
current_env: staging

environments:
  staging:
    base_url: "https://your-staging-api.com"
    token_url: "/api/iam/token"
    login_user:
      username: "your_username"
      password: "your_password"
      grantType: "password"
```

### 3. 运行测试

```bash
# 方式1: 使用主运行脚本（推荐）
python run_case.py

# 方式2: 直接使用 pytest
pytest case/ -v --alluredir=reports/allure-results

# 方式3: 运行指定测试文件
pytest case/test_a_workspace.py -v

# 方式4: 运行指定测试用例
pytest case/test_a_workspace.py::TestMerchants::test_a_save -v
```

### 4. 查看报告

测试完成后，可以查看两种报告：

**HTML 报告：**
- 打开 `reports/api_report.html` 查看 HTML 测试报告

**Allure 报告（推荐）：**
```bash
# 生成 Allure 报告
allure generate reports/allure-results -o reports/allure-report --clean

# 打开 Allure 报告
allure open reports/allure-report
```

---

## 📖 框架核心概念

### 三层架构设计

```
┌─────────────────────────────────────────────────────────┐
│                     测试用例层 (case/)                    │
│         编写测试逻辑，调用 API 封装方法，使用测试数据           │
└─────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────┐
│                    API 封装层 (apis/)                     │
│      封装接口调用逻辑，参数处理，响应解析，断言验证              │
└─────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────┐
│                  配置数据层 (resources/)                   │
│         API定义(YAML) + 测试数据(YAML) + 环境配置           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 框架维护指南

### 1. 环境配置维护

**文件路径：** `resources/config.yaml`

#### 添加新环境

```yaml
environments:
  # 新增 UAT 环境
  uat:
    base_url: "https://uat-api.example.com"
    token_url: "/api/iam/token"
    timeout: 15
    retry: 3
    login_user:
      username: "uat_user@example.com"
      password: "uat_password"
      grantType: "password"

# 切换到新环境
current_env: uat
```

#### 修改公共 Headers

```yaml
default_headers:
  user-agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  accept: "application/json"
  locale: "zh-CN"
  # 添加新的公共 Header
  x-custom-header: "custom_value"
```

### 2. Token 管理

Token 由 `utils/token_manager.py` 自动管理，特性：
- ✅ 单例模式，全局共享
- ✅ 自动缓存，避免重复获取
- ✅ 登录失败时自动刷新

如需手动刷新 Token：

```python
from utils.token_manager import TokenManager

token_manager = TokenManager()
token_manager.refresh_token()  # 强制刷新
```

### 3. 测试执行顺序控制

使用 `@pytest.mark.order()` 装饰器控制执行顺序（数字越小越先执行）：

```python
import pytest
import allure

@pytest.mark.order(1)  # 类级别优先级
@allure.epic("登录模块")
class TestLogin:
    
    @pytest.mark.order(1)  # 方法级别优先级
    @allure.story("用户登录")
    @allure.title("测试登录功能")
    def test_login(self):
        pass
    
    @pytest.mark.order(2)
    @allure.story("用户登出")
    @allure.title("测试登出功能")
    def test_logout(self):
        pass
```

---

## ✨ 新增接口用例指南

新增一个接口用例需要维护以下 **4 个文件**：

| 序号 | 文件位置 | 作用 | 必须 |
|------|----------|------|------|
| 1 | `resources/api/{module}.yaml` | 定义接口信息（URL、Method、Headers、Body） | ✅ |
| 2 | `resources/testdata/{module}_testdata.yaml` | 定义测试数据 | ⚪ 可选 |
| 3 | `apis/{module}_api.py` | 封装 API 调用方法 | ✅ |
| 4 | `case/test_{module}.py` | 编写测试用例 | ✅ |

---

### 📝 Step 1: 定义接口配置 (YAML)

**文件路径：** `resources/api/{module}.yaml`

以新增 **订单模块** 为例：

```yaml
# resources/api/orders.yaml

# ==========================================
# 订单模块接口定义
# ==========================================

module: "orders"
description: "订单管理相关接口"

apis:
  # ============ 创建订单 ============
  create:
    name: "创建订单"
    path: "/api/orders"           # 接口路径
    method: "POST"                 # 请求方法
    headers:                       # 额外的 Headers（可选，会合并公共 Headers）
      referer: "https://example.com/orders"
    body_type: "json"              # 请求体类型：json | form | params
    default_body:                  # 默认请求体（会被 override_body 覆盖）
      productId: ""
      quantity: 1
      customerId: ""
    assertions:                    # 断言配置
      - type: "status_code"
        expected: 200
      - type: "json_path"
        path: "code"
        expected: 200

  # ============ 查询订单列表 ============
  list:
    name: "订单列表"
    path: "/api/orders"
    method: "GET"
    body_type: "params"            # GET 请求使用 params
    default_body:
      pageNo: 1
      pageSize: 20
      status: ""
    assertions:
      - type: "status_code"
        expected: 200
      - type: "json_path"
        path: "code"
        expected: 200

  # ============ 查询订单详情 ============
  detail:
    name: "订单详情"
    path: "/api/orders/{order_id}"  # 路径参数使用 {param_name}
    method: "GET"
    path_params:                    # 声明路径参数
      - order_id
    assertions:
      - type: "status_code"
        expected: 200
      - type: "json_path"
        path: "code"
        expected: 200

  # ============ 更新订单 ============
  update:
    name: "更新订单"
    path: "/api/orders/{order_id}"
    method: "PUT"
    path_params:
      - order_id
    body_type: "json"
    default_body:
      status: ""
      remark: ""
    assertions:
      - type: "status_code"
        expected: 200
      - type: "json_path"
        path: "code"
        expected: 200

  # ============ 删除订单 ============
  delete:
    name: "删除订单"
    path: "/api/orders/{order_id}"
    method: "DELETE"
    path_params:
      - order_id
    assertions:
      - type: "status_code"
        expected: 200
      - type: "json_path"
        path: "code"
        expected: 200
```

#### YAML 配置说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `path` | 接口路径，支持 `{param}` 路径参数 | `/api/orders/{order_id}` |
| `method` | HTTP 方法 | `GET`、`POST`、`PUT`、`DELETE` |
| `body_type` | 请求体类型 | `json` / `form` / `params` |
| `default_body` | 默认请求体，可被覆盖 | - |
| `path_params` | 路径参数列表 | `[order_id]` |
| `headers` | 接口专属 Headers（会合并公共 Headers） | - |
| `assertions` | 断言规则列表 | - |

---

### 📝 Step 2: 定义测试数据 (可选)

**文件路径：** `resources/testdata/{module}_testdata.yaml`

```yaml
# resources/testdata/orders_testdata.yaml

# ==========================================
# 订单模块测试数据
# ==========================================

# 正常场景测试数据
normal:
  create_order_1:
    productId: "PROD-001"
    quantity: 2
    customerId: "CUST-001"
  
  create_order_2:
    productId: "PROD-002"
    quantity: 5
    customerId: "CUST-002"
    # 支持 {timestamp} {date} {time} 占位符
    remark: "订单创建于 {date}"

# 边界测试数据
boundary:
  max_quantity:
    productId: "PROD-001"
    quantity: 9999
  
  min_quantity:
    productId: "PROD-001"
    quantity: 1

# 异常测试数据
error:
  empty_product:
    productId: ""
    quantity: 1
    expected_code: 400
  
  invalid_quantity:
    productId: "PROD-001"
    quantity: -1
    expected_code: 400
```

#### 支持的占位符

| 占位符 | 说明 | 示例输出 |
|--------|------|----------|
| `{timestamp}` | 当前时间戳 | `1702617600` |
| `{date}` | 当前日期 | `2024-12-15` |
| `{time}` | 当前时间 | `14:30:00` |

---

### 📝 Step 3: 封装 API 调用类

**文件路径：** `apis/{module}_api.py`

```python
# apis/orders_api.py
# -*- coding:UTF-8 -*-
"""
订单模块 API 封装
"""

from faker import Faker
from utils.yaml_loader import get_yaml_loader
from utils.logger import logger
from utils.request_utils import RequestUtils

# 全局变量存储数据
ORDER_DATA = {}
order_id = None

faker_data = Faker(locale='zh_CN')
yaml_loader = get_yaml_loader()


class OrdersAPI:
    """订单 API 封装类"""
    
    def __init__(self):
        self.loader = yaml_loader
        self.request = RequestUtils()
        self.module = "orders"  # 对应 YAML 文件名
    
    def _send_request(self, api_config: dict) -> dict:
        """
        发送请求的通用方法
        
        Args:
            api_config: API 配置字典
        
        Returns:
            响应的 JSON 数据
        """
        params = {
            'url': api_config['url'],
            'method': api_config['method'],
            'headers': api_config['headers']
        }
        
        # 根据 body_type 添加数据
        if 'json' in api_config:
            params['json'] = api_config['json']
        elif 'data' in api_config:
            params['data'] = api_config['data']
        elif 'params' in api_config:
            params['params'] = api_config['params']
        
        response = self.request.send_request(**params)
        return response.json()
    
    def _assert_response(self, response_json: dict, assertions: list):
        """
        通用断言方法
        
        Args:
            response_json: 响应 JSON
            assertions: 断言列表
        """
        for assertion in assertions:
            assert_type = assertion.get('type')
            
            if assert_type == 'json_path':
                path = assertion.get('path')
                expected = assertion.get('expected')
                actual = response_json.get(path)
                assert actual == expected, f"断言失败: {path} 期望={expected}, 实际={actual}"
    
    def create(self, custom_data: dict = None):
        """
        创建订单
        
        Args:
            custom_data: 自定义数据，覆盖默认值
        """
        global order_id
        
        # 准备请求数据
        override_body = custom_data or {}
        
        # 获取 API 配置
        api_config = self.loader.get_api_config(
            module=self.module,
            api='create',
            override_body=override_body
        )
        
        try:
            response_json = self._send_request(api_config)
            self._assert_response(response_json, api_config['assertions'])
            
            # 提取 order_id 供后续接口使用
            order_id = response_json.get('data', {}).get('orderId')
            
            print(f"✅ 订单创建成功: {order_id}")
            logger.info(f"✅ 订单创建成功: {order_id}")
            return response_json
            
        except Exception as e:
            print(f"❌ 订单创建失败: {str(e)}")
            logger.error(f"❌ 订单创建失败: {str(e)}")
            raise
    
    def list(self, status: str = None):
        """
        查询订单列表
        
        Args:
            status: 订单状态（可选）
        """
        override_body = {}
        if status:
            override_body['status'] = status
        
        api_config = self.loader.get_api_config(
            module=self.module,
            api='list',
            override_body=override_body
        )
        
        try:
            response_json = self._send_request(api_config)
            self._assert_response(response_json, api_config['assertions'])
            
            print(f"✅ 订单列表查询成功")
            logger.info(f"✅ 订单列表查询成功")
            return response_json
            
        except Exception as e:
            print(f"❌ 订单列表查询失败: {str(e)}")
            logger.error(f"❌ 订单列表查询失败: {str(e)}")
            raise
    
    def detail(self, target_order_id: str = None):
        """
        查询订单详情
        
        Args:
            target_order_id: 订单 ID（可选，不传则使用全局 order_id）
        """
        global ORDER_DATA
        
        target_id = target_order_id or order_id
        if not target_id:
            raise ValueError("order_id 不能为空")
        
        api_config = self.loader.get_api_config(
            module=self.module,
            api='detail',
            path_params={'order_id': target_id}
        )
        
        try:
            response_json = self._send_request(api_config)
            self._assert_response(response_json, api_config['assertions'])
            
            # 存储订单数据
            ORDER_DATA = response_json.get('data', {})
            
            print(f"✅ 订单详情查询成功: {target_id}")
            logger.info(f"✅ 订单详情查询成功: {target_id}")
            return response_json
            
        except Exception as e:
            print(f"❌ 订单详情查询失败: {str(e)}")
            logger.error(f"❌ 订单详情查询失败: {str(e)}")
            raise
    
    def update(self, target_order_id: str = None, custom_data: dict = None):
        """
        更新订单
        
        Args:
            target_order_id: 订单 ID（可选）
            custom_data: 自定义数据（可选）
        """
        target_id = target_order_id or order_id
        if not target_id:
            raise ValueError("order_id 不能为空")
        
        override_body = custom_data or {}
        
        api_config = self.loader.get_api_config(
            module=self.module,
            api='update',
            path_params={'order_id': target_id},
            override_body=override_body
        )
        
        try:
            response_json = self._send_request(api_config)
            self._assert_response(response_json, api_config['assertions'])
            
            print(f"✅ 订单更新成功")
            logger.info(f"✅ 订单更新成功")
            return response_json
            
        except Exception as e:
            print(f"❌ 订单更新失败: {str(e)}")
            logger.error(f"❌ 订单更新失败: {str(e)}")
            raise
    
    def delete(self, target_order_id: str = None):
        """
        删除订单
        
        Args:
            target_order_id: 订单 ID（可选）
        """
        target_id = target_order_id or order_id
        if not target_id:
            raise ValueError("order_id 不能为空")
        
        api_config = self.loader.get_api_config(
            module=self.module,
            api='delete',
            path_params={'order_id': target_id}
        )
        
        try:
            response_json = self._send_request(api_config)
            self._assert_response(response_json, api_config['assertions'])
            
            print(f"✅ 订单删除成功")
            logger.info(f"✅ 订单删除成功")
            return response_json
            
        except Exception as e:
            print(f"❌ 订单删除失败: {str(e)}")
            logger.error(f"❌ 订单删除失败: {str(e)}")
            raise
```

---

### 📝 Step 4: 编写测试用例

**文件路径：** `case/test_{module}.py`

```python
# case/test_orders.py
# -*- coding:UTF-8 -*-
import pytest
import allure


@pytest.mark.order(2)  # 设置类优先级（数字越小越先执行）
@allure.epic("订单管理")
@allure.feature("订单CRUD操作")
class TestOrders:
    """订单模块测试用例"""
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, orders_api, yaml_loader):
        """测试类初始化"""
        self.api = orders_api
        self.loader = yaml_loader

    @pytest.mark.order(1)
    @allure.story("创建订单")
    @allure.title("创建订单")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_a_create(self):
        """创建订单"""
        # 方式1: 使用测试数据文件
        testdata = self.loader.get_testdata('orders_testdata', 'normal.create_order_1')
        with allure.step("调用创建订单接口"):
            self.api.create(custom_data=testdata)
        
        # 方式2: 直接传参
        # with allure.step("调用创建订单接口"):
        #     self.api.create(custom_data={
        #         "productId": "PROD-001",
        #         "quantity": 3
        #     })

    @pytest.mark.order(2)
    @allure.story("订单列表")
    @allure.title("查询订单列表")
    @allure.severity(allure.severity_level.NORMAL)
    def test_b_list(self):
        """订单列表"""
        with allure.step("调用订单列表接口"):
            self.api.list()

    @pytest.mark.order(3)
    @allure.story("订单详情")
    @allure.title("查询订单详情")
    @allure.severity(allure.severity_level.NORMAL)
    def test_c_detail(self):
        """订单详情"""
        with allure.step("调用订单详情接口"):
            self.api.detail()

    @pytest.mark.order(4)
    @allure.story("更新订单")
    @allure.title("更新订单信息")
    @allure.severity(allure.severity_level.NORMAL)
    def test_d_update(self):
        """更新订单"""
        with allure.step("调用更新订单接口"):
            self.api.update(custom_data={"status": "completed"})

    @pytest.mark.order(5)
    @allure.story("删除订单")
    @allure.title("删除订单")
    @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.skip("暂时跳过删除")  # 可选：跳过某个用例
    def test_e_delete(self):
        """删除订单"""
        with allure.step("调用删除订单接口"):
            self.api.delete()
```

---

## 📋 新增接口用例检查清单

当您需要新增一个接口用例时，请按以下步骤检查：

```
□ Step 1: 在 resources/api/ 下创建或编辑模块 YAML 文件
    - 定义接口路径 (path)
    - 定义请求方法 (method)
    - 定义请求体类型 (body_type)
    - 定义默认请求体 (default_body)
    - 定义断言规则 (assertions)

□ Step 2: 在 resources/testdata/ 下创建测试数据 YAML 文件（可选）
    - 定义正常场景数据 (normal)
    - 定义边界场景数据 (boundary)
    - 定义异常场景数据 (error)

□ Step 3: 在 apis/ 下创建 API 封装类
    - 封装接口调用方法
    - 处理参数和响应
    - 添加日志和断言

□ Step 4: 在 case/ 下创建测试用例类
    - 使用 @pytest.mark.order() 控制执行顺序
    - 调用 API 封装方法
    - 测试文件名必须以 test_ 开头
```

---

## 🛠 工具类使用说明

### yaml_loader - YAML 加载器

```python
from utils.yaml_loader import get_yaml_loader

loader = get_yaml_loader()

# 获取 API 配置
api_config = loader.get_api_config(
    module='merchants',           # 模块名
    api='save',                   # 接口名
    path_params={'id': '123'},    # 路径参数
    override_body={'name': 'xx'}, # 覆盖请求体
    override_headers={'x': 'y'}   # 覆盖请求头
)

# 获取测试数据
testdata = loader.get_testdata('merchants_testdata', 'normal.save_merchant_1')
```

### request_utils - 请求工具

```python
from utils.request_utils import RequestUtils

request = RequestUtils()

response = request.send_request(
    url='https://api.example.com/users',
    method='POST',
    headers={'Content-Type': 'application/json'},
    json={'name': 'test'}
)
```

### logger - 日志记录

```python
from utils.logger import logger

logger.info("信息日志")
logger.warning("警告日志")
logger.error("错误日志")
```

---

## 📊 测试报告

测试完成后，在 `reports/` 目录下生成两种报告：

### HTML 报告
- **报告文件：** `reports/api_report.html`
- **特点：** 独立 HTML 文件，可直接在浏览器中打开

### Allure 报告（推荐）
- **结果目录：** `reports/allure-results/`
- **报告目录：** `reports/allure-report/`
- **特点：** 
  - 美观的交互式报告
  - 支持步骤展示、附件、历史趋势
  - 支持按 Epic、Feature、Story 分组
  - 支持按优先级、严重程度筛选

**生成和查看 Allure 报告：**
```bash
# 生成报告
allure generate reports/allure-results -o reports/allure-report --clean

# 打开报告（会自动启动本地服务器）
allure open reports/allure-report
```

### 日志文件
- **日志文件：** `log/requests.log`

---

## 🔥 性能测试 (Locust)

框架集成了 Locust 性能测试工具，可复用 YAML 配置进行压力测试。

### 快速使用

```python
# locustfile.py
from locust import HttpUser, task, between
from utils.locust_config import get_locust_config

class ApiLoadTest(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # 方式1: 使用预设配置
        self.config = get_locust_config(preset_name='merchants_list')
        
        # 方式2: 自定义模块和接口
        # self.config = get_locust_config(api_module='orders', api_name='list')
    
    @task
    def test_api(self):
        req = self.config.get_request_config()
        self.client.request(
            method=req['method'],
            url=req['url'],
            headers=req['headers'],
            json=req.get('json'),
            params=req.get('params')
        )
```

### 运行压测

```bash
# 启动 Locust Web UI
locust -f locustfile.py

# 无界面模式运行
locust -f locustfile.py --headless -u 100 -r 10 -t 60s
# -u: 用户数  -r: 每秒启动用户数  -t: 运行时长
```

### 预设配置

在 `utils/locust_config.py` 中定义了预设配置：

| 预设名称 | 模块 | 接口 | 说明 |
|----------|------|------|------|
| `merchants_list` | merchants | list | 商户列表查询 |
| `merchants_save` | merchants | save | 新增商户 |
| `connectors_list` | integrations | list | 连接器列表 |

添加新预设：

```python
PRESET_CONFIGS = {
    'orders_list': {
        'module': 'orders',
        'api': 'list',
        'description': '订单列表查询'
    },
    # ... 更多预设
}
```

---

## 🔗 常见问题

### 1. Token 获取失败

检查 `resources/config.yaml` 中的登录配置：

```yaml
environments:
  staging:
    login_user:
      username: "正确的用户名"
      password: "正确的密码"
```

### 2. 接口路径参数未替换

确保在 API 配置中声明了 `path_params`，并在调用时传入：

```python
api_config = loader.get_api_config(
    module='orders',
    api='detail',
    path_params={'order_id': '12345'}  # 替换 {order_id}
)
```

### 3. 测试用例执行顺序不对

使用 `@pytest.mark.order()` 装饰器控制顺序，数字越小越先执行：

```python
@pytest.mark.order(1)  # 先执行
def test_create(self): pass

@pytest.mark.order(2)  # 后执行
def test_delete(self): pass
```

---

## 📝 维护日志

| 日期 | 版本 | 说明 |
|------|------|------|
| 2024-12-15 | v1.0 | 初始版本 |

---

**作者：** Linker 自动化测试团队  
**最后更新：** 2024-12-15

