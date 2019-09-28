import matplotlib.pyplot as plt
import networkx as nx
from abstract_data import Article, CitedReference, AVertex

# Проверяет для авторов A1 и A2, можно ли считать их одинаковыми.
# Если одно из множеств является подмножеством другого, то
# считаем, что авторы равны
def is_equal(A1, A2):
    new_A1 = []
    # Переводим авторов A1 в лист из авторов new_A1
    for a in A1:
        surn = ""
        n1 = ""
        n2 = ""
        name = a.split(" ")
        surn = name[0]
        if len(name) > 1:
            n1 = name[1]
        if len(name) > 2:
            n2 = name[2]
        new_A1.append([surn, n1, n2])

    new_A2 = []
    # Переводим авторов A2 в лист из авторов new_A2
    for a in A2:
        surn = ""
        n1 = ""
        n2 = ""
        name = a.split(" ")
        surn = name[0]
        if len(name) > 1:
            n1 = name[1]
        if len(name) > 2:
            n2 = name[2]
        new_A2.append([surn, n1, n2])

    # Является ли new_A1 подмножеством new_A2
    is_subset1 = 1
    for a in new_A1:
        is_find = 0
        for b in new_A2:
            if (a[0] == b[0] and
                (a[1] == b[1] or a[1] == "" or b[1] == "") and
                (a[2] == b[2] or a[2] == "" or b[2] == "")):
                is_find = 1
                break
        if is_find == 0:
            is_subset1 = 0
            break

    # Является ли new_A2 подмножеством new_A1
    is_subset2 = 1
    for a in new_A2:
        is_find = 0
        for b in new_A1:
            if (a[0] == b[0] and
                (a[1] == b[1] or a[1] == "" or b[1] == "") and
                (a[2] == b[2] or a[2] == "" or b[2] == "")):
                is_find = 1
                break
        if is_find == 0:
            is_subset2 = 0
            break
    # Если одно из множеств является подмножеством другого,
    # возвращаем 1, иначе 0
    return is_subset1 or is_subset2


# Удаляет одинаковые статьи
def del_equal_articles(articles):
    new_articles = []
    for A in articles:
        equal_art = 0
        for B in new_articles:
            # Если названия статей совпадают и авторы равны,
            # то статьи одинаковы
            if (A.name == B.name and
                 is_equal(A.author, B.author)):
                equal_art = 1
                break
        if not equal_art:
            new_articles.append(A)
    return new_articles


# Строит граф цитирования на основе статей articles
# В данной функции граф == вершина, ссылка == ориентированное ребро
def build_graph(articles, topic_name):
    articles = del_equal_articles(articles)
    vertexes = []
    edges = []
    # v_number - хеш-таблица для того, чтобы понимать, добавлена
    # ли статья в граф
    v_number = {}
    # Добавляем в граф статьи, которые выданы по запросу пользователя
    for i in range(len(articles)):
        AV = AVertex()
        AV.name = articles[i].name
        AV.author = articles[i].author
        v_number[AV.name] = i
        AV.indeg = 0
        vertexes.append(AV)
    # ind_v-1 - номер статьи, которая добавлена последней
    ind_v = len(articles)
    for art_i in range(len(articles)):
        # Для каждой статьи в articles проходим циклом по статьям,
        # на которые она ссылается
        for ref_i in range(len(articles[art_i].CitedReferences)):
            # Если статья с таким названием уже добавлена в массив
            if v_number.get(articles[art_i].CitedReferences[ref_i].name):
                # И если авторы добавляемой статьи совпадают с авторами
                # уже добавленной с таким же названием
                if is_equal(vertexes[v_number[articles[art_i].
                                              CitedReferences[ref_i]
                                              .name]].author,
                            articles[art_i].CitedReferences[ref_i].author):
                    # В этом случае новую вершину создавать не нужно,
                    # но следует увеличить степень найденной вершины
                    # и добавить новое ребро
                    vertexes[v_number[articles[art_i].
                                      CitedReferences[ref_i].
                                      name]].indeg += 1
                    edges.append((v_number[articles[art_i].name],
                                  v_number[articles[art_i].
                                           CitedReferences[ref_i].
                                           name]))
                    continue
            # Если добавляемой вершины еще нет в графе, то следует ее
            # туда добавить
            AV = AVertex()
            AV.name = articles[art_i].CitedReferences[ref_i].name
            AV.author = articles[art_i].CitedReferences[ref_i].author
            AV.indeg = 1
            vertexes.append(AV)
            v_number[AV.name] = ind_v
            # Также добавляем ребро
            edges.append((v_number[articles[art_i].name], ind_v))
            ind_v += 1

    # Создаем граф
    G = nx.DiGraph()
    for i in range(len(vertexes)):
        # Добавляем вершины. id вершины - ее номер в массиве
        # vertexes, название вершины: <title> | <authors>
        G.add_node(i)
        vertex_name = vertexes[i].name+" | "
        for a in vertexes[i].author:
            vertex_name += a+"; "
        G.nodes[i]['label'] = vertex_name
        # Увеличиваем размер вершины в зависимости от ее степени,
        # т.е. в зависимости от того, сколько статей ссылаются
        # на статью, соответствующую данной вершине
        G.nodes[i]['viz'] = {'size': 4 + 3*vertexes[i].indeg}
        if i < len(articles):
            # Если данная статья входит во множество тех,
            # которые нашлись по запросу пользователя,
            # красим ее в белый цвет
            G.nodes[i]['viz']['color'] = {'a' : 0,
                                          'r' : 255,
                                          'g' : 255,
                                          'b' : 255}
        else:
            # Если данная статья не входит в это множество,
            # но хотя бы одна из статей на нее ссылается,
            # красим ее в зеленый цвет
            G.nodes[i]['viz']['color'] = {'a' : 0,
                                          'r' : 67,
                                          'g' : 255,
                                          'b' : 20}
    # Добавляем в граф ребра
    G.add_edges_from(edges)

    # Сохраняем граф в формате .gexf. Для того, чтобы визуализировать
    # данный граф, следует открыть его программой gephi
    nx.write_gexf(G, "../data/"+topic_name+".gexf")
    print("Graph saved in ", "../data/"+topic_name+".gexf")
    return articles
