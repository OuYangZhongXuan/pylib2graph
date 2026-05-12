from neo4j import GraphDatabase
from typing import Dict, Any, List


class Neo4jClient:
    """Neo4j客户端类，负责连接和操作Neo4j数据库"""

    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

    def connect(self):
        """连接到Neo4j"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # 验证连接
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            print(f"Neo4j连接失败: {e}")
            return False

    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()

    def clear_database(self):
        """清空数据库（可选）"""
        if not self.driver:
            return

        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def create_module_node(self, module_data: Dict[str, Any]):
        """创建模块节点"""
        if not self.driver:
            return

        with self.driver.session() as session:
            session.run("""
                CREATE (m:Module {
                    name: $name,
                    doc: $doc
                })
            """, name=module_data['name'], doc=module_data['doc'])

    def create_class_node(self, class_data: Dict[str, Any], module_name: str):
        """创建类节点并建立与模块的关系"""
        if not self.driver:
            return

        with self.driver.session() as session:
            # 创建类节点
            session.run("""
                CREATE (c:Class {
                    name: $name,
                    doc: $doc,
                    bases: $bases
                })
            """, name=class_data['name'], doc=class_data['doc'],
                        bases=str(class_data['bases']))

            # 建立类与模块的关系
            session.run("""
                MATCH (m:Module {name: $module_name})
                MATCH (c:Class {name: $class_name})
                CREATE (m)-[:CONTAINS]->(c)
            """, module_name=module_name, class_name=class_data['name'])

            # 创建类的方法节点并建立关系
            for method in class_data['methods']:
                session.run("""
                    CREATE (mtd:Method {
                        name: $name,
                        doc: $doc,
                        parameters: $parameters
                    })
                """, name=method['name'], doc=method['doc'],
                            parameters=str(method['parameters']))

                session.run("""
                    MATCH (c:Class {name: $class_name})
                    MATCH (mtd:Method {name: $method_name})
                    CREATE (c)-[:HAS_METHOD]->(mtd)
                """, class_name=class_data['name'], method_name=method['name'])

    def create_function_node(self, func_data: Dict[str, Any], module_name: str):
        """创建函数节点并建立与模块的关系"""
        if not self.driver:
            return

        with self.driver.session() as session:
            # 创建函数节点
            session.run("""
                CREATE (f:Function {
                    name: $name,
                    doc: $doc,
                    parameters: $parameters
                })
            """, name=func_data['name'], doc=func_data['doc'],
                        parameters=str(func_data['parameters']))

            # 建立函数与模块的关系
            session.run("""
                MATCH (m:Module {name: $module_name})
                MATCH (f:Function {name: $func_name})
                CREATE (m)-[:CONTAINS]->(f)
            """, module_name=module_name, func_name=func_data['name'])

    def create_submodule_relationship(self, module_name: str, submodule_name: str):
        """建立模块与子模块的关系"""
        if not self.driver:
            return

        with self.driver.session() as session:
            session.run("""
                MATCH (m:Module {name: $module_name})
                MATCH (sm:Module {name: $submodule_name})
                CREATE (m)-[:HAS_SUBMODULE]->(sm)
            """, module_name=module_name, submodule_name=submodule_name)

    def upload_to_graph(self, parsed_data: List[Dict[str, Any]]):
        """将解析数据上传到Neo4j"""
        if not self.driver:
            return

        for module_data in parsed_data:
            print(f"正在上传模块: {module_data['name']}")

            # 创建模块节点
            self.create_module_node(module_data)

            # 创建类节点
            for class_data in module_data['classes']:
                self.create_class_node(class_data, module_data['name'])

            # 创建函数节点
            for func_data in module_data['functions']:
                self.create_function_node(func_data, module_data['name'])

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()