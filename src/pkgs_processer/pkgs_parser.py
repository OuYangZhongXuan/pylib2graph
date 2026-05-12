import inspect
import importlib

from typing import List, Dict, Any


class PackageParser:
    """库解析器类，基于inspect库解析Python库"""

    def __init__(self, package_manager):
        self.package_manager = package_manager

    def parse_module(self, module_name: str) -> Dict[str, Any]:
        """解析指定模块"""
        # 确保模块已安装
        if not self.package_manager.ensure_package_installed(module_name):
            return None

        try:
            module = importlib.import_module(module_name)
            return self._analyze_module(module)
        except ImportError as e:
            print(f"导入模块失败: {module_name}, 错误: {e}")
            return None

    def _analyze_module(self, module) -> Dict[str, Any]:
        """分析模块结构"""
        result = {
            'name': module.__name__,
            'doc': inspect.getdoc(module) or '',
            'functions': [],
            'classes': [],
            'submodules': []
        }

        # 获取模块的所有成员
        members = inspect.getmembers(module)

        for name, obj in members:
            # 跳过私有成员
            if name.startswith('_'):
                continue

            # 跳过内置对象
            if inspect.isbuiltin(obj):
                continue

            # 处理函数
            if inspect.isfunction(obj) or inspect.ismethod(obj):
                result['functions'].append(self._analyze_function(name, obj))

            # 处理类
            elif inspect.isclass(obj):
                result['classes'].append(self._analyze_class(name, obj))

            # 处理子模块
            elif inspect.ismodule(obj):
                # 只处理当前模块的直接子模块
                if obj.__name__.startswith(module.__name__ + '.'):
                    result['submodules'].append(obj.__name__)

        return result

    def _analyze_function(self, name: str, func) -> Dict[str, Any]:
        """分析函数信息"""
        try:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
        except ValueError:
            params = []

        return {
            'name': name,
            'doc': inspect.getdoc(func) or '',
            'parameters': params,
            'source': inspect.getsource(func) if inspect.isfunction(func) else ''
        }

    def _analyze_class(self, name: str, cls) -> Dict[str, Any]:
        """分析类信息"""
        class_info = {
            'name': name,
            'doc': inspect.getdoc(cls) or '',
            'bases': [base.__name__ for base in cls.__bases__],
            'methods': [],
            'attributes': []
        }

        # 获取类的成员
        try:
            for method_name, method_obj in inspect.getmembers(cls):
                if method_name.startswith('_'):
                    continue

                if inspect.isfunction(method_obj) or inspect.ismethod(method_obj):
                    try:
                        sig = inspect.signature(method_obj)
                        params = list(sig.parameters.keys())
                    except ValueError:
                        params = []

                    class_info['methods'].append({
                        'name': method_name,
                        'doc': inspect.getdoc(method_obj) or '',
                        'parameters': params
                    })
                elif not inspect.isroutine(method_obj):
                    class_info['attributes'].append(method_name)
        except Exception:
            pass

        return class_info

    def parse_multiple_libs(self, lib_names: List[str]) -> List[Dict[str, Any]]:
        """解析多个库"""
        results = []
        for lib_name in lib_names:
            parsed = self.parse_module(lib_name)
            if parsed:
                results.append(parsed)
        return results