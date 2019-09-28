def build_csv(articles, topic_name):
    new_articles = del_empty_abstracts(articles)
    for A in new_articles:
        A.abstract = A.abstract +" "+A.name
    csvf = open("../data/"+topic_name+".csv", "w")
    csvf.write("name\0author\0abstract\n")
    for A in new_articles:
        csvf.write(A.name+"\0")
        for i in range(len(A.author)):
            if i != len(A.author)-1:
                csvf.write(A.author[i]+", ")
            else:
                csvf.write(A.author[i]+"\0")
        csvf.write(A.abstract+"\n")
    csvf.close()
    print("Database from articles saved in ../data/"+topic_name+".csv")

def article_clasterization(topic_name, showtfidf, showmds,
                           showts, showhdc, showlda):
    df = pd.read_csv("../data/"+topic_name+".csv", sep="\0")
    with redirect_stdout(open(os.devnull, "w")):
        nltk.download('punkt')
        nltk.download('stopwords')
    stopwords = nltk.corpus.stopwords.words('english')
    stemmer = SnowballStemmer("english")

    def local_stop_words(word):
        not_stopword = 1
        if stemmer.stem(word) == "use":
            not_stopword = 0
        return not_stopword

    def tokenize_and_stem(text):
        tokens = [word for sent in nltk.sent_tokenize(text) for word in
                  nltk.word_tokenize(sent)]
        tokens = [word for word in tokens if local_stop_words(word)]
        filtered_tokens = []
        for token in tokens:
            if (re.search('[a-zA-Z]', token) and
                    not re.search("'", token)):
                filtered_tokens.append(token)
        stems = [stemmer.stem(t) for t in filtered_tokens]
        return stems

    def tokenize(text):
        tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in
                  nltk.word_tokenize(sent)]
        tokens = [word for word in tokens if local_stop_words(word)]
        filtered_tokens = []
        for token in tokens:
            if (re.search('[a-zA-Z]', token) and
                   not re.search("'", token)):
                filtered_tokens.append(token)
        return filtered_tokens


    totalvocab_stemmed = []
    totalvocab_tokenized = []

    df = df.dropna(axis=0, how='any')
    for abstract in df['abstract'].tolist():
        allwords_stemmed = tokenize_and_stem(abstract)
        totalvocab_stemmed.extend(allwords_stemmed)

        allwords_tokenized = tokenize(abstract)
        totalvocab_tokenized.extend(allwords_tokenized)

    vocab_frame = pd.DataFrame({'words': totalvocab_tokenized},
                               index = totalvocab_stemmed)

    tfidf_vectorizer = TfidfVectorizer(max_df=0.8,
                                      max_features=200000,
                                      min_df=0.001,
                                      stop_words='english',
                                      use_idf=True,
                                      tokenizer=tokenize_and_stem,
                                      ngram_range=(1,8))

    tfidf_matrix = tfidf_vectorizer.fit_transform(df['abstract'].tolist())
    terms = tfidf_vectorizer.get_feature_names()

    dist = 1 - cosine_similarity(tfidf_matrix)
    distortions = {}
    for num_clusters in range(1, min(11, len(df['abstract'].tolist())+1)):
        print("K Means with "+str(num_clusters)+" clusters")
        km = KMeans(n_clusters = num_clusters)
        km.fit(tfidf_matrix)
        distortions[num_clusters] = km.inertia_

    plt.figure()
    plt.plot(list(distortions.keys()), list(distortions.values()))
    plt.xlabel("Number of cluster")
    plt.ylabel("Distortions")
    plt.show()

    print("Input count of clusters:")
    num_clusters = int(input())
    km = KMeans(n_clusters = num_clusters)
    km.fit(tfidf_matrix)

    print("Kmeans saved in ../data/"+topic_name+".pkl")
    joblib.dump(km, "../data/"+topic_name+".pkl")
    km = joblib.load("../data/"+topic_name+".pkl")

    clusters = km.labels_.tolist()

    articles_describe = {'title' : df['name'].tolist(),
             'author' : df['author'].tolist(),
             'abstract' : df['abstract'].tolist(),
             'cluster' : clusters}

    cluster_df = pd.DataFrame(articles_describe,
                         index = [clusters],
                         columns = ['title',
                                    'author',
                                    'abstract',
                                    'cluster',])

    print("\nTop terms per cluster:\n")

    for i in range(num_clusters):
        print("Cluster %d words:" % (i+1), end='')
        # <...>
        if showts:
            print("Cluster %d titles:" % i)
            ind_t = 1
            for title in cluster_df.ix[i]['title'].values.tolist():
                print("Title", str(ind_t)+":", title)
                ind_t += 1
            print("\n")

    if showlda:
        tokenized_text = [tokenize_and_stem(text) for text
                          in df['abstract'].tolist()]
        texts = ([[word for word in text if word not in stopwords]
                  for text in tokenized_text])
        dictionary = corpora.Dictionary(texts)
        dictionary.filter_extremes(no_below=1, no_above=0.5)
        corpus = [dictionary.doc2bow(text) for text in texts]

        lda = models.LdaModel(corpus, num_topics=num_clusters,
                              id2word=dictionary,
                              update_every=5,
                              chunksize=10000,
                              passes=100)
        topics_matrix = lda.show_topics(formatted=False, num_words=10)
        topics_matrix = np.array(topics_matrix, dtype=object)
        # <...>

    if showmds:
        mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)
        pos = mds.fit_transform(dist)
        xs, ys = pos[:, 0], pos[:, 1]

        cluster_colors = {0: '#000000', 1: '#ff0000', 2: '#9a37b4',
                          3: '#308b1b', 4: '#2dc7e7', 5: '#00097e',
                          6: '#9a9a9a', 7: '#b7d41b', 8: '#90aeff',
                          9: '#92002c'}
        cluster_names = {}
        for i in range(len(res_labels)):
            cluster_names[i] = res_labels[i][:min(3, len(res_labels[i]))]

        df_mds = pd.DataFrame(dict(x=xs, y=ys,
                                   label=clusters))
        groups_mds = df_mds.groupby("label")
        for name, group in groups_mds:
            ax.plot(group.x, group.y, marker='o', linestyle='',
                    label=cluster_names[name], ms=12,
                    color=cluster_colors[name], mec='none')

        ax.legend(numpoints=1)
        plt.draw()
        plt.savefig("../data/mds_"+topic_name+".png", dpi=200)
        print("Mds plot saved in ../data/mds_"+topic_name+".png")
        plt.close()

    if showhdc:
        linkage_matrix = ward(dist)
        ax = dendrogram(linkage_matrix, orientation="right",
                    labels=df['name'].tolist())

        plt.draw()
        plt.savefig("../data/hdc_"+topic_name+".png", dpi=200)
        print("Hdc plot saved in ../data/hdc_"+topic_name+".png")
        plt.close()
