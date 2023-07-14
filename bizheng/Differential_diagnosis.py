#该部分代码主要实现可解释性辩证功能（输出症候的同时输出最可能的病机病因）
from py2neo import Graph, Node, Relationship
graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456"))
#实现辩证部分代码，输入症状输出对应的证候，并同时输出每种证候对应的病机和病因
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

    # 根据概率排序，返回可能性最大的10个证候
    recommendations = sorted(recommendations, key=lambda x: x["probability"], reverse=True)[:10]

    return recommendations


#由症候推病机
def recommend_etiology(patterns):
    query = """
    MATCH (z:病机)
    RETURN z.name AS etiology
    """
    result = graph.run(query)
#     print(result)
    # 处理结果
    recommendations = []
    for record in result:
        etiology = record["etiology"]
        probability = 1.0
        for pattern in patterns:
            query = """
            MATCH (s:中医证候)-[r]->(z:病机 {name:$etiology})
            WHERE s.name = $pattern
            RETURN r.co_occurrence AS co_occurrence
            """
            result = graph.run(query, etiology=etiology, pattern=pattern).data()
            if result:
                co_occurrence = result[0]['co_occurrence']
                probability *= co_occurrence
            else:
                probability = 0.0  # 如果关系属性不存在，则概率为0

        recommendation = {"etiology": etiology, "probability": probability}
        recommendations.append(recommendation)

    recommendations = sorted(recommendations, key=lambda x: x["probability"], reverse=True)[:3]
    return recommendations

#由症候推病因
def recommend_pathogenesis(patterns):
    query = """
    MATCH (z:病因)
    RETURN z.name AS pathogenesis
    """
    result = graph.run(query)
#     print(result)
    # 处理结果
    recommendations = []
    for record in result:
        pathogenesis = record["pathogenesis"]
        probability = 1.0
        for pattern in patterns:
            query = """
            MATCH (s:中医证候)-[r]->(z:病机 {name:$pathogenesis})
            WHERE s.name = $pattern
            RETURN r.co_occurrence AS co_occurrence
            """
            result = graph.run(query, pathogenesis=pathogenesis, pattern=pattern).data()
            # 如果关系属性存在，则将概率乘以该属性值
            if result:
                co_occurrence = result[0]['co_occurrence']
                if(co_occurrence!=None):
                    probability *= co_occurrence
            else:
                probability = 0.0  # 如果关系属性不存在，则概率为0

        recommendation = {"pathogenesis": pathogenesis, "probability": probability}
        recommendations.append(recommendation)
    recommendations = sorted(recommendations, key=lambda x: x["probability"], reverse=True)[:3]

    return recommendations

#测试代码
symptoms = ['关节痛','动则汗出','下肢水肿','面色晦暗']
# pattern = ['湿邪阻络']
# res = recommend_etiology(symptoms)
# res = recommend_pathogenesis(pattern)
# print(res)
def compent(symptoms):
    pa_results = recommend_patterns(symptoms)
    for res in pa_results:
        pattern = res["zhenghou"]
        print('症候为',pattern)
        res_e = recommend_etiology(pattern)
        res_p = recommend_pathogenesis(pattern)
        print('对应的病因为',res_e)
        print('对应的病机为', res_p)

compent(symptoms)


