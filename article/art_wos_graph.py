def build_graph(articles, topic_name):
    articles = del_equal_articles(articles)
    vertexes = []
    edges = []
    v_number = {}
    for i in range(len(articles)):
        AV = AVertex()
        AV.name = articles[i].name
        AV.author = articles[i].author
        v_number[AV.name] = i
        AV.indeg = 0
        vertexes.append(AV)
    ind_v = len(articles)
    for art_i in range(len(articles)):
        for ref_i in range(len(articles[art_i].CitedReferences)):
            if v_number.get(articles[art_i].CitedReferences[ref_i].name):
                if is_equal(vertexes[v_number[articles[art_i].
                                              CitedReferences[ref_i]
                                              .name]].author,
                            articles[art_i].CitedReferences[ref_i].author):
                    vertexes[v_number[articles[art_i].
                                      CitedReferences[ref_i].
                                      name]].indeg += 1
                    edges.append((v_number[articles[art_i].name],
                                  v_number[articles[art_i].
                                           CitedReferences[ref_i].
                                           name]))
                    continue
            AV = AVertex()
            AV.name = articles[art_i].CitedReferences[ref_i].name
            AV.author = articles[art_i].CitedReferences[ref_i].author
            AV.indeg = 1
            vertexes.append(AV)
            v_number[AV.name] = ind_v
            edges.append((v_number[articles[art_i].name], ind_v))
            ind_v += 1

    G = nx.DiGraph()
    for i in range(len(vertexes)):
        G.add_node(i)
        vertex_name = vertexes[i].name+" | "
        for a in vertexes[i].author:
            vertex_name += a+"; "
        G.nodes[i]['label'] = vertex_name
        G.nodes[i]['viz'] = {'size': 4 + 3*vertexes[i].indeg}
        if i < len(articles):
            G.nodes[i]['viz']['color'] = {'a' : 0,
                                          'r' : 255,
                                          'g' : 255,
                                          'b' : 255}
        else:
            G.nodes[i]['viz']['color'] = {'a' : 0,
                                          'r' : 67,
                                          'g' : 255,
                                          'b' : 20}
    G.add_edges_from(edges)

    nx.write_gexf(G, "../data/"+topic_name+".gexf")
    print("Graph saved in ", "../data/"+topic_name+".gexf")
    return articles
