import inspect
import networkx as nx
import shapely
from shapely.geometry import (
    Point, LineString, Polygon,
    MultiPoint, MultiLineString, MultiPolygon
)
import csv


# ==========================
# 1. 创建图
# ==========================
G = nx.DiGraph()


# ==========================
# 2. 定义领域几何类型
# ==========================
geometry_classes = [
    Point,
    LineString,
    Polygon,
    MultiPoint,
    MultiLineString,
    MultiPolygon,
]

# 添加 GeometryType 节点
for cls in geometry_classes:
    G.add_node(
        cls.__name__,
        entity_type="GeometryType",
        dimension=2,
        shapely_class=f"{cls.__module__}.{cls.__name__}"
    )


# ==========================
# 3. 抽取公共几何操作
# ==========================
common_methods = [
    "buffer",
    "intersection",
    "union",
    "difference",
    "simplify",
    "intersects",
    "contains",
    "within"
]


def infer_return_type(method_name):
    """简单的领域语义映射"""
    if method_name in ["intersects", "contains", "within"]:
        return "Boolean"
    elif method_name in ["buffer", "intersection", "union", "difference"]:
        return "GeometryType"
    elif method_name == "simplify":
        return "GeometryType"
    else:
        return "Unknown"


# 添加 Operation 节点
for method in common_methods:
    G.add_node(
        method,
        entity_type="Operation",
        category="PredicateOperation" if method in ["intersects", "contains", "within"]
                 else "TopologicalOperation",
    )


# ==========================
# 4. 建立关系
# ==========================
for cls in geometry_classes:
    for method in common_methods:
        if hasattr(cls, method):
            func = getattr(cls, method)

            # OPERATES_ON
            G.add_edge(
                method,
                cls.__name__,
                relation="OPERATES_ON"
            )

            # RETURNS
            return_type = infer_return_type(method)

            G.add_edge(
                method,
                return_type,
                relation="RETURNS"
            )


# ==========================
# 5. 继承关系（SUBTYPE_OF）
# ==========================
for cls in geometry_classes:
    mro = inspect.getmro(cls)
    if len(mro) > 1:
        parent = mro[1]
        if parent.__name__ != "object":
            G.add_edge(
                cls.__name__,
                parent.__name__,
                relation="SUBTYPE_OF"
            )


# ==========================
# 6. 导出节点 CSV
# ==========================
with open("nodes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "entity_type", "dimension", "category", "shapely_class"])

    for node, data in G.nodes(data=True):
        writer.writerow([
            node,
            data.get("entity_type"),
            data.get("dimension"),
            data.get("category"),
            data.get("shapely_class")
        ])


# ==========================
# 7. 导出边 CSV
# ==========================
with open("edges.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["source", "target", "relation"])

    for source, target, data in G.edges(data=True):
        writer.writerow([
            source,
            target,
            data.get("relation")
        ])


print("图构建完成，nodes.csv 和 edges.csv 已生成")
