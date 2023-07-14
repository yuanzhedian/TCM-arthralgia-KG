#尝试实现由症状到疾病名，再由疾病名到方名的路径
from py2neo import Graph, Node, Relationship
graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456"))
#由症状推疾病名
def recommend_disease(symptoms):
    # 查询所有的证候节点
    query = """
    MATCH (z:西医疾病名)
    RETURN z.name AS disease
    """
    result = graph.run(query)
#     print(result)
    # 处理结果
    recommendations = []
    for record in result:
        disease = record["disease"]
        # 计算每个证候与输入症状之间的关系属性的乘积
        probability = 1.0
        for symptom in symptoms:
            # 查询症状节点与证候节点的关系属性
            query = """
            MATCH (s:阳性症状)-[r]->(z:西医疾病名 {name: $disease})
            WHERE s.name = $symptom
            RETURN r.co_occurrence AS co_occurrence
            """
            result = graph.run(query, disease=disease, symptom=symptom).data()
            # 如果关系属性存在，则将概率乘以该属性值
            if result:
                co_occurrence = result[0]['co_occurrence']
                # print(co_occurrence)
                probability *= co_occurrence
            else:
                probability = 0.0  # 如果关系属性不存在，则概率为0

        recommendation = {"disease": disease, "probability": probability}
        recommendations.append(recommendation)

    # 根据概率排序，返回可能性最大的10个证候
    recommendations = sorted(recommendations, key=lambda x: x["probability"], reverse=True)[:10]

    return recommendations
#由疾病名推方名
def recommend_fangji(diseases):
    # 查询所有的证候节点
    query = """
    MATCH (z:方名)
    RETURN z.name AS durg
    """
    result = graph.run(query)
#     print(result)
    # 处理结果
    recommendations = []
    for record in result:
        durg = record["durg"]
        # 计算每个证候与输入症状之间的关系属性的乘积
        probability = 1.0
        for disease in diseases:
            # 查询症状节点与证候节点的关系属性
            query = """
            MATCH (s:西医疾病名)-[r]->(z:方名 {name: $durg})
            WHERE s.name = $disease
            RETURN r.co_occurrence AS co_occurrence
            """
            result = graph.run(query, disease=disease, durg=durg).data()
            # 如果关系属性存在，则将概率乘以该属性值
            if result:
                co_occurrence = result[0]['co_occurrence']
                # print(co_occurrence)
                probability *= co_occurrence
            else:
                probability = 0.0  # 如果关系属性不存在，则概率为0


        recommendation = {"方名": durg, "probability": probability}
        recommendations.append(recommendation)

    # 根据概率排序，返回可能性最大的10个证候
    recommendations = sorted(recommendations, key=lambda x: x["probability"], reverse=True)[:3]

    return recommendations

def resplit_array(results):
    #拆分函数
    filtered_fangming = []
    for res in results:
        probability = res["probability"]
        if probability > 0:
            fangming = res["disease"]
            filtered_fangming.append(fangming)
#     print(filtered_fangming)
    result = []
    # print(filtered_fangming)
    return result

def compontent(symptoms):
    res = recommend_disease(symptoms)
    result = [[item['disease']] for item in res]
    fin_res = []
    for res in result:
        res_f = recommend_fangji(res)
        # print('对应疾病为',res)
        fin_res.append(res_f)
        # 创建一个空字典用于存储方名对应的累加后的probability
        result = {}

        # 遍历每个子列表
        for sublist in fin_res:
            # 遍历子列表中的字典元素
            for item in sublist:
                fangming = item['方名']
                probability = item['probability']
                # 检查方名是否已经存在于结果字典中
                if fangming in result:
                    # 若存在，则将当前的probability累加到已有的值上
                    result[fangming] += probability
                else:
                    # 若不存在，则将当前的probability作为初始值
                    result[fangming] = probability

        # 根据累加后的probability值进行排序，并输出前5个方名及其累加后的probability值
        sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)[:5]
        # print(sorted_result)
    print('辨病论治系统所给出的最可能的5个方名为：')
    for fangming, probability in sorted_result:
        print(fangming)

if __name__ == '__main__':
    symptoms = ['关节痛']
    compontent(symptoms)


