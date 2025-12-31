# -*- coding:UTF-8 -*-
"""
测试用例执行顺序控制工具（已废弃）
现在使用 pytest-ordering 插件的 @pytest.mark.order() 装饰器

此文件保留仅用于向后兼容，新代码请使用：
    @pytest.mark.order(1)  # 替代 @priority(1)
"""
import warnings

warnings.warn(
    "utils.test_order.priority 已废弃，请使用 @pytest.mark.order() 替代",
    DeprecationWarning,
    stacklevel=2
)


def priority(level):
    """
    已废弃：请使用 @pytest.mark.order() 替代
    
    Args:
        level: 优先级（数字越小越先执行）
    """
    import pytest
    return pytest.mark.order(level)


class OrderedTestLoader(unittest.TestLoader):
    """自定义测试加载器，按优先级排序"""
    
    def getTestCaseNames(self, testCaseClass):
        """重写获取测试用例名称的方法，按优先级排序"""
        test_names = super().getTestCaseNames(testCaseClass)
        
        # 获取每个测试方法的优先级
        test_priority = []
        for name in test_names:
            test_method = getattr(testCaseClass, name)
            priority_value = getattr(test_method, '_priority', 999)  # 默认优先级999
            test_priority.append((priority_value, name))
        
        # 按优先级排序
        test_priority.sort(key=lambda x: x[0])
        
        # 返回排序后的测试名称
        return [name for _, name in test_priority]
    
    def discover(self, start_dir, pattern='test*.py', top_level_dir=None):
        """重写discover方法，支持类级别优先级排序"""
        # 使用父类的discover获取所有测试
        suite = super().discover(start_dir, pattern, top_level_dir)
        
        # 提取所有测试用例并按类优先级排序
        all_tests = self._flatten_suite(suite)
        sorted_tests = self._sort_by_class_priority(all_tests)
        
        # 重新组装为TestSuite
        new_suite = unittest.TestSuite()
        new_suite.addTests(sorted_tests)
        return new_suite
    
    def _flatten_suite(self, suite):
        """展平TestSuite，提取所有测试用例"""
        tests = []
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                tests.extend(self._flatten_suite(test))
            else:
                tests.append(test)
        return tests
    
    def _sort_by_class_priority(self, tests):
        """按类的优先级排序测试用例"""
        # 按类分组
        class_groups = {}
        for test in tests:
            test_class = test.__class__
            class_priority = getattr(test_class, '_priority', 999)
            
            if test_class not in class_groups:
                class_groups[test_class] = {
                    'priority': class_priority,
                    'tests': []
                }
            class_groups[test_class]['tests'].append(test)
        
        # 按类优先级排序
        sorted_classes = sorted(class_groups.items(), key=lambda x: x[1]['priority'])
        
        # 展平为测试列表
        sorted_tests = []
        for test_class, group_data in sorted_classes:
            sorted_tests.extend(group_data['tests'])
        
        return sorted_tests


class OrderedTestSuite:
    """
    自定义测试套件，支持多种排序方式
    """
    
    @staticmethod
    def by_priority(test_dir, pattern="test_*.py"):
        """
        按优先级加载测试用例
        
        Args:
            test_dir: 测试用例目录
            pattern: 文件匹配模式
            
        Returns:
            TestSuite
        """
        loader = OrderedTestLoader()
        return loader.discover(test_dir, pattern=pattern)
    
    @staticmethod
    def by_names(test_cases):
        """
        按指定顺序执行测试用例
        
        Args:
            test_cases: 测试用例列表，格式：
                [
                    ('case.test_a_workspace', 'Merchants_Case', 'test_a_save'),
                    ('case.test_b_connector', 'Connector_Case', 'test_a_list'),
                ]
        
        Returns:
            TestSuite
        """
        suite = unittest.TestSuite()
        
        for module_name, class_name, method_name in test_cases:
            # 动态导入模块
            module = __import__(module_name, fromlist=[class_name])
            test_class = getattr(module, class_name)
            suite.addTest(test_class(method_name))
        
        return suite
    
    @staticmethod
    def by_files(test_files):
        """
        按文件顺序执行
        
        Args:
            test_files: 测试文件列表，格式：
                ['case/test_a_workspace.py', 'case/test_b_connector.py']
        
        Returns:
            TestSuite
        """
        suite = unittest.TestSuite()
        loader = OrderedTestLoader()
        
        for test_file in test_files:
            # 将路径转换为模块名
            module_name = test_file.replace('/', '.').replace('\\', '.').replace('.py', '')
            module = __import__(module_name, fromlist=[''])
            
            # 加载模块中的所有测试
            module_suite = loader.loadTestsFromModule(module)
            suite.addTests(module_suite)
        
        return suite


# 别名，方便使用
order = priority

