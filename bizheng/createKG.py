import pandas as pd
from py2neo import Graph, Node, Relationship
import math

#读取数据
def find_rows_by_value(s1, excel_file):
    # 读取Excel文件
    df = pd.read_excel(excel_file)

    # 根据条件筛选匹配的行
    matched_rows = df[df.iloc[:, 1] == s1]

    return matched_rows

# find_rows_by_value("肝肾亏虚",excel_file)


#求共现概率
def count_rows(s1, s2, excel_file):
    # 读取Excel文件
    df1 = pd.read_excel(excel_file)

    # 根据条件筛选匹配的行
    df = df1[df1.iloc[:, 1] == s1]

    # 返回表中的行数
    total_rows = df.shape[0]

    if total_rows!=0:
        # 返回第二列中值为 "s2" 的行数
        matched_rows = df[df.iloc[:, 2] == s2]
        s2_rows = matched_rows.shape[0]
        return s2_rows / total_rows


#通过函数判断两个节点之间是否存在关系
def check_relationship_exists(s1, s2):
    # Neo4j数据库连接配置
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456"))
    # 建立与数据库的连接

    # 执行Cypher查询
    query = '''
    MATCH (s1)-[r]->(s2)
    WHERE s1.name = $s1 AND s2.name = $s2
    RETURN COUNT(r) AS count
    '''
    result = graph.run(query, s1=s1, s2=s2)
    count = result.evaluate()

    # 根据查询结果判断是否存在关系
    if count > 0:
        return "yes"
    else:
        return "no"

#求特异度
def count_rows_spe(s1, s2, excel_file):
    # 读取Excel文件
    df1 = pd.read_excel(excel_file)

    # 根据条件筛选匹配的行
    df = df1[df1.iloc[:, 1] == s1]

    # 返回表中的行数
    total_rows = df.shape[0]

    # 返回第二列中值为 "s2" 的行数
    matched_rows = df[df.iloc[:, 2] == s2]
    s2_rows = matched_rows.shape[0]

    # 先计算每个宾语节点在每个主语节点的比例
    updata = s2_rows / total_rows

    # 然后计算每个宾语节点在所有节点中的比例
    downdata = s2_rows / len(df1)

    return math.log(updata / downdata)

#连接之后通过excel向数据库中导入数据
def import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type):
    # 连接Neo4j数据库
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456"))

    # 读取Excel数据
    data = pd.read_excel(excel_file)

    # 获取数据列名
    columns = data.columns.tolist()

    # 创建节点和关系
    for _, row in data.iterrows():
        entity1 = row[columns[1]]
        entity2 = row[columns[2]]

        # 查询节点1是否存在
        existing_node1 = graph.nodes.match(node1_label, name=entity1).first()

        if existing_node1:
            # 更新节点1属性
            existing_node1["name"] = entity1
            graph.push(existing_node1)
        else:
            # 创建节点1
            node1 = Node(node1_label, name=entity1)
            graph.create(node1)

        # 查询节点2是否存在
        existing_node2 = graph.nodes.match(node2_label, name=entity2).first()

        if existing_node2:
            # 更新节点2属性
            existing_node2["name"] = entity2
            graph.push(existing_node2)
        else:
            # 创建节点2
            node2 = Node(node2_label, name=entity2)
            graph.create(node2)

        # 创建关系
        if check_relationship_exists(entity1,entity2) == "yes":
            relationship = Relationship(existing_node1 or node1, relationship_type, existing_node2 or node2)
        else:
            relationship = Relationship(existing_node1 or node1, relationship_type, existing_node2 or node2)
            relationship["co_occurrence"] = count_rows(entity1, entity2,excel_file)
            # relationship["specificity"] = count_rows_spe(entity1, entity2,excel_file)
        graph.create(relationship)
    print("数据导入完成！")

if __name__ == '__main__':
    excel_file = "Data/CreateDate/阳性症状VS西医疾病名.xlsx"
    node1_label = "阳性症状"
    node2_label = "西医疾病名"
    relationship_type = "对应为"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/中医疾病名VS西医疾病名.xlsx"
    node1_label = "中医疾病名"
    node2_label = "西医疾病名"
    relationship_type = "对应为"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/西医疾病名VS方名.xlsx"
    node1_label = "西医疾病名"
    node2_label = "方名"
    relationship_type = "对应为"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/中医证候VS方名.xlsx"
    node1_label = "中医证候"
    node2_label = "方名"
    relationship_type = "辩证论治"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/new中医证候VS病因.xlsx"
    node1_label = "中医证候"
    node2_label = "病因"
    relationship_type = "对应为"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/new中医证候VS病机.xlsx"
    node1_label = "中医证候"
    node2_label = "病机"
    relationship_type = "对应为"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/中医证候VS方名.xlsx"
    node1_label = "中医证候"
    node2_label = "方名"
    relationship_type = "辩证论治"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/方名VS中医证候.xlsx"
    node1_label = "方名"
    node2_label = "中医证候"
    relationship_type = "被....辩证论治"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/病机VS西医疾病名.xlsx"
    node1_label = "病机"
    node2_label = "西医疾病名"
    relationship_type = "导致"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/西医疾病名VS病机.xlsx"
    node1_label = "西医疾病名"
    node2_label = "病机"
    relationship_type = "由...导致"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/西医疾病名VS病因.xlsx"
    node1_label = "西医疾病名"
    node2_label = "病因"
    relationship_type = "由...导致"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/病因VS西医疾病名.xlsx"
    node1_label = "病因"
    node2_label = "西医疾病名"
    relationship_type = "导致"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/治则治法VS西医疾病名.xlsx"
    node1_label = "治则治法"
    node2_label = "西医疾病名"
    relationship_type = "被...治则治法"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/西医疾病名VS治则治法.xlsx"
    node1_label = "西医疾病名"
    node2_label = "治则治法"
    relationship_type = "治则治法"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/西医疾病名VS中医证候.xlsx"
    node1_label = "西医疾病名"
    node2_label = "中医证候"
    relationship_type = "反映为"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/中医证候VS西医疾病名.xlsx"
    node1_label = "中医证候"
    node2_label = "西医疾病名"
    relationship_type = "是....反映"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/阳性症状VS中医证候.xlsx"
    node1_label = "阳性症状"
    node2_label = "中医证候"
    relationship_type = "是....表现"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/中医证候VS阳性症状.xlsx"
    node1_label = "中医证候"
    node2_label = "阳性症状"
    relationship_type = "表现"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/中医证候VS脉象.xlsx"
    node1_label = "中医证候"
    node2_label = "脉象"
    relationship_type = "表现"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/脉象VS中医证候.xlsx"
    node1_label = "脉象"
    node2_label = "中医证候"
    relationship_type = "是....表现"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/舌象VS中医证候.xlsx"
    node1_label = "舌象"
    node2_label = "中医证候"
    relationship_type = "是....表现"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/中医证候VS舌象.xlsx"
    node1_label = "中医证候"
    node2_label = "舌象"
    relationship_type = "表现"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/中药vs方名.xlsx"
    node1_label = "中药"
    node2_label = "方名"
    relationship_type = "由..组成"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)

    excel_file = "Data/CreateDate/方名vs中药.xlsx"
    node1_label = "方名"
    node2_label = "中药"
    relationship_type = "组成"
    # 导入Excel数据到Neo4j
    import_excel_data_to_neo4j(excel_file, node1_label, node2_label, relationship_type)