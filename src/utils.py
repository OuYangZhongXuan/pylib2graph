import os
import pathlib

from omegaconf import OmegaConf


class ConfigLoader:
    """配置加载类，负责读取config.yaml文件"""

    def __init__(self, config_path=None):
        if config_path is None:
            here = pathlib.Path(__file__).parents[1]
            print(here)
            self.config_path = here.joinpath('config/config.yaml')
        else:
            self.config_path = config_path
        print(f"加载配置文件: {self.config_path}")
        self.config = self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        return OmegaConf.load(self.config_path)

    def get_neo4j_config(self):
        """获取Neo4j连接配置"""
        return self.config.get('neo4j', {})

    def get_target_libs(self):
        """获取需要解析的库名列表"""
        libs = self.config.get('libs', '')
        if isinstance(libs, str):
            return [lib.strip() for lib in libs.split(',') if lib.strip()]
        return list(libs)
