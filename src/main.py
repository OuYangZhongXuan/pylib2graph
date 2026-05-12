from utils import ConfigLoader
from src.pkgs_processer.pkgs_manager import PackageManager
from src.pkgs_processer.pkgs_parser import PackageParser
from src.neo4j.neo4j_client import Neo4jClient


def main():
    # 加载配置
    print("正在加载配置...")
    config_loader = ConfigLoader()
    neo4j_config = config_loader.get_neo4j_config()
    target_libs = config_loader.get_target_libs()

    print(f"待解析的库: {target_libs}")

    # 初始化包管理器
    package_manager = PackageManager()

    # 初始化库解析器
    parser = PackageParser(package_manager)

    # 解析库
    print("正在解析库...")
    parsed_results = parser.parse_multiple_libs(target_libs)

    if not parsed_results:
        print("没有成功解析任何库")
        return

    # 连接Neo4j并上传数据
    print("正在连接Neo4j...")
    with Neo4jClient(
            uri=neo4j_config.get('uri', 'neo4j://localhost:7687'),
            user=neo4j_config.get('user', 'neo4j'),
            password=neo4j_config.get('pwd', 'neo4j')
    ) as client:
        if not client.driver:
            print("无法连接Neo4j，跳过数据上传")
        else:
            print("正在上传数据到Neo4j...")
            client.upload_to_graph(parsed_results)
            print("数据上传完成")

    # 检查安装失败的包
    failed_packages = package_manager.get_failed_packages()
    if failed_packages:
        print("\n以下包安装失败:")
        for pkg in failed_packages:
            print(f"  - {pkg}")


if __name__ == '__main__':
    main()