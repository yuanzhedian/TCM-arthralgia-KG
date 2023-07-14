#实现论治部分代码，首先实现由症状到症候再由症候到方名；
from py2neo import Graph, Node, Relationship
graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456"))


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
                probability *= co_occurrence
            else:
                probability = 0.0  # 如果关系属性不存在，则概率为0

        recommendation = {"zhenghou": zhenghou, "probability": probability}
        recommendations.append(recommendation)

    # 根据概率排序，返回可能性最大的10个证候
    recommendations = sorted(recommendations, key=lambda x: x["probability"], reverse=True)[:10]

    return recommendations

def recommend_fangmin(patterns):
    # 查询所有的证候节点
    query = """
    MATCH (z:方名)
    RETURN z.name AS fangming
    """

    result = graph.run(query)
#     print(result)
    # 处理结果
    recommendations = []
    for record in result:
        fangming = record["fangming"]
        # 计算每个证候与输入症状之间的关系属性的乘积
        probability = 1.0
        for pattern in patterns:
#             print(pattern)
            # 查询症状节点与证候节点的关系属性
            query = """
            MATCH (s:中医证候)-[r]->(z:方名 {name: $fangming})
            WHERE s.name = $pattern
            RETURN r.co_occurrence AS co_occurrence
            """
            result = graph.run(query, fangming=fangming, pattern=pattern).data()
                # 如果关系属性存在，则将概率乘以该属性值
#             print(result)
            if result:
                co_occurrence = result[0]['co_occurrence']
                probability *= co_occurrence
            else:
                probability = 0.0  # 如果关系属性不存在，则概率为0

        recommendation = {"fangming": fangming, "probability": probability}
        recommendations.append(recommendation)

    # 根据概率排序，返回可能性最大的10个证候
    recommendations = sorted(recommendations, key=lambda x: x["probability"], reverse=True)[:10]

    return recommendations

def resplit_array(results):
    #拆分函数
    filtered_fangming = []
    for res in results:
        probability = res["probability"]
        if probability > 0:
            fangming = res["zhenghou"]
            filtered_fangming.append(fangming)
#     print(filtered_fangming)
    result = []
    for i in range(1, len(filtered_fangming) + 1):
        sub_array = filtered_fangming[:i]
        result.append(sub_array)
    return result

#将拆分的输入数组输入到指定数据中
def lunzhi(recommendations):
    result1 = resplit_array(recommendations)
    re_list = []
    for res1 in result1:
        result = recommend_fangmin(res1)
#         print("每次次输出结果为：",result)
        re_list.append(result)
    return re_list

#该函数实现将上次输出整合成只有5个数据的数组
def calculate_probabilities(array):
    result = []
    probabilities = {}

    for sublist in array:
        for item in sublist:
            fangming = item['fangming']
            probability = item['probability']

            if fangming in probabilities:
                probabilities[fangming] += probability
            else:
                probabilities[fangming] = probability

    for fangming, probability in probabilities.items():
        result.append({'fangming': fangming, 'probability': probability})
    recommendations = sorted(result, key=lambda x: x["probability"], reverse=True)[:5]
    return recommendations

if __name__ == '__main__':
    #s输入对应的症状即可
    symptoms = ['关节痛']
    res = recommend_patterns(symptoms)
    # print(res)
    lun_res = lunzhi(res)
    final_res = calculate_probabilities(lun_res)
    # print(final_res)
    print('辨证论治系统所给出的最可能的5个方名为：')
    for item in final_res:
        fangming = item['fangming']
        print(fangming)