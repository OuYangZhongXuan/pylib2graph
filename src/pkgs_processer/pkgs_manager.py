import importlib
import subprocess
import sys


class PackageManager:
    """包管理类，负责检查和安装Python包"""

    def __init__(self):
        self.failed_packages = []

    def is_package_installed(self, package_name):
        """检查包是否已安装"""
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False

    def install_package(self, package_name):
        """尝试安装包"""
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', package_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            self.failed_packages.append(package_name)
            return False

    def ensure_package_installed(self, package_name):
        """确保包已安装，否则尝试安装"""
        if self.is_package_installed(package_name):
            return True
        return self.install_package(package_name)

    def get_failed_packages(self):
        """获取安装失败的包列表"""
        return self.failed_packages