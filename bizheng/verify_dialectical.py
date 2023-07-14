from py2neo import Graph, Node, Relationship
import pandas as pd
graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456"))

from sklearn.metrics import accuracy_score, recall_score, f1_score

def calculate_metrics(true_labels, predicted_labels):
    # 计算准确率
    accuracy = accuracy_score(true_labels, predicted_labels)

    # 计算召回率
    recall = recall_score(true_labels, predicted_labels)

    # 计算F1值
    f1 = f1_score(true_labels, predicted_labels)

    return accuracy, recall, f1

def recommend_patterns(symptoms):
    # 查询所有的证候节点
    query = """
    MATCH (z:中医证候)
    RETURN z.name AS zhenghou
    """
    result = graph.run(query)
#     print(result)
    # 处理结果
    recommendations = []
    for record in result:
        zhenghou = record["zhenghou"]
        # 计算每个证候与输入症状之间的关系属性的乘积
        probability = 1.0
        for symptom in symptoms:
            # 查询症状节点与证候节点的关系属性
            query = """
            MATCH (s:阳性症状)-[r]->(z:中医证候 {name: $zhenghou})
            WHERE s.name = $symptom
            RETURN r.co_occurrence AS co_occurrence
            """
            result = graph.run(query, zhenghou=zhenghou, symptom=symptom).data()
            # 如果关系属性存在，则将概率乘以该属性值
            if result:
                co_occurrence = result[0]['co_occurrence']
                # print(co_occurrence)
                if co_occurrence!=None:
                    probability *= co_occurrence
            else:
                probability = 0.0  # 如果关系属性不存在，则概率为0

        recommendation = {"zhenghou": zhenghou, "probability": probability}
        recommendations.append(recommendation)

    # 根据概率排序，返回可能性最大的5个证候
    recommendations = sorted(recommendations, key=lambda x: x["probability"], reverse=True)[:5]

    return recommendations


def read_excel_file(file_path):
    # 读取 Excel 文件
    df = pd.read_excel(file_path)
    # 提取前 15 列作为输入数据（数组）
    input_data = df.iloc[:, :15].values.tolist()

    # 提取第 16 列作为标签
    labels = df.iloc[:, 15].tolist()

    return input_data, labels


def clean_nan_values(data):
    # 创建DataFrame对象
    df = pd.DataFrame(data)

    # 使用dropna()函数清理NaN元素
    cleaned_data = df.dropna().values.tolist()
    flatten_list = [item for sublist in cleaned_data for item in sublist]

    return flatten_list


def check_labels(input_data, labels):
    result = []
    for data, label in zip(input_data, labels):
        ow_res = recommend_patterns(data)  # 使用 final_code 函数获取输出结果
        ow_labels = [item['zhenghou'] for item in ow_res]  # 获取输出结果中的标签
        if label in ow_labels:
            result.append(True)
        else:
            result.append(False)

    length = len(result)
    true_array = [True] * length
    accuracy, recall, f1 = calculate_metrics(true_array, result)

    print("准确率:", accuracy)
    print("召回率:", recall)
    print("F1值:", f1)

if __name__ == '__main__':
    # 指定 Excel 文件路径
    file_path = "Data/验证数据.xlsx"

    # 调用函数读取 Excel 文件
    input_data, labels = read_excel_file(file_path)

    res = []
    for da in input_data:
        # print(da)
        flatten_list = clean_nan_values(da)
        res.append(flatten_list)
    # print(res)

    # 打印读取的数据
    print("Input data:")
    for data in res:
        print(data)

    print("Labels:")
    print(labels)

    results = check_labels(res, labels)
    print(results)

#如果想要获得top k的相应评价数据只需要在recommend_patterns函数中修改推荐的数量即可