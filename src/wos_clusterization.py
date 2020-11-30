import numpy as np
import pandas as pd
import nltk
import sklearn
import re
import os
import sys
import matplotlib.pyplot as plt
import matplotlib as mlp

from contextlib import redirect_stdout

from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.externals import joblib
from sklearn.manifold import MDS
from scipy.cluster.hierarchy import ward, dendrogram
from gensim import corpora, models, similarities
from scipy.spatial.distance import cdist

from abstract_data import Article, CitedReference


def del_empty_abstracts(articles):
    """Remove articles without abstract.

    Args:
        articles(list): list of articles.
    
    Returns:
        list: list of articles with abstract.

    """
    new_articles = []
    for A in articles:
        if hasattr(A, "abstract"):
            new_articles.append(A)
    return new_articles


def build_csv(articles, topic_name):
    """Build a csv file by article and save it.

    Args:
        articles (list): list of articles.
        topic_name (str): name of the new csv file.

    """
    new_articles = del_empty_abstracts(articles)
    for A in new_articles:
        A.abstract = A.abstract +" "+A.name
    csvf = open("../data/"+topic_name+".csv", "w")
    # Так как в абстрактах могут быть использованы практически
    # любые символы ascii, в качестве разделяющего символа
    # используем '\0'
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


# Кластеризирует статьи
def article_clusterization(topic_name, showtfidf, showmds,
                           showts, showhdc, showlda):
    """Clusterization of the articles. 

    Args:
        topic_name(str): name of the csv file with articles.
        showtfidf(bool): if True, show tf-idf matrix of the articles, 500 columns.
        showmds(bool): if True, show result of the Multidimensional scaling (MDS).
        showts(bool): if True, show titles for every cluster.
        showhdc(bool): if True, show result of the hierarchical document clustering.
        showlda(bool): if True, show the result of Latent Dirichlet allocation (LDA).


    """
    # Создаем dataframe из csv-файла
    df = pd.read_csv("../data/"+topic_name+".csv", sep="\0")
    # Подгружаем в библиотеу nltk нужные словари
    # Вывод, который генерирует nltk, игнорируем
    with redirect_stdout(open(os.devnull, "w")):
        nltk.download('punkt')
        nltk.download('stopwords')
    # stopwords - слова, которые повторяются в любом тексте
    # и не имеют специфики
    stopwords = nltk.corpus.stopwords.words('english')
    # stemmer - модуль для нахождения основы слова для
    # заданного исходного слова
    stemmer = SnowballStemmer("english")

    # Проверяет, является ли слово локальным (т.е. именно для
    # данной выборки) стоп-словом
    def local_stop_words(word):
        not_stopword = 1
        # Пока что только 'use', для каждого запроса подбираем свои
        # стоп-слова
        if stemmer.stem(word) == "use":
            not_stopword = 0
        return not_stopword

    # Токенизирует text: разбивает его на слова согласно
    # nltk.word_tokenize(). Удаляет локальные стоп-слова. Удаляет
    # слова, в которых либо нет латинских символов, либо есть "'".
    # Находит основы слов (stem) всех слов, отобранных таким образом
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


    # То же самое, что и tokenize_and_stem(), но без stem-a
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


    # totalvocab_stemmed - вывод функции tokenize_and_stem() для
    # каждого абстракта
    totalvocab_stemmed = []
    # totalvocab_tokenized - вывод функции tokenize() для
    # каждого абстракта
    totalvocab_tokenized = []
    # Удаляем строки, в которых не хватает данных
    df = df.dropna(axis=0, how='any')
    # Заполнение totalvocab_stemmed и totalvocab_tokenized
    for abstract in df['abstract'].tolist():
        allwords_stemmed = tokenize_and_stem(abstract)
        totalvocab_stemmed.extend(allwords_stemmed)

        allwords_tokenized = tokenize(abstract)
        totalvocab_tokenized.extend(allwords_tokenized)

    # Датафрейм с одной колонкой: токенизированными словам. Индексы -
    # номера эти же слова, но приведенные к их основам
    vocab_frame = pd.DataFrame({'words': totalvocab_tokenized},
                               index = totalvocab_stemmed)

    # Создаем tf-idf матрицу.
    # max_df - порог максимального индекса tf-idf
    # min_df - порог минимального индекса tf-idf
    # max_features - максимальное количество слов в матрице
    # stop_words - удаляемые из матрицы слова
    # use_idf - использовать понижающий коэффициент idf
    # tokenizer - функция, по которой строятся слова
    # ngram - рассматривать N-Gram-ы, т.е. совокупности слов
    tfidf_vectorizer = TfidfVectorizer(max_df=0.8,
                                      max_features=200000,
                                      min_df=0.001,
                                      stop_words='english',
                                      use_idf=True,
                                      tokenizer=tokenize_and_stem,
                                      ngram_range=(1,8))

    # Обучить построенный vectorizer на текстах абстрактов
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['abstract'].tolist())
    # terms - список построенных слов
    terms = tfidf_vectorizer.get_feature_names()
    # dist - список расстояний, расстояние - (1 - косинусное сходство в
    # N-мерном пространстве слов)
    dist = 1 - cosine_similarity(tfidf_matrix)

    # Показать tf-idf матрицу
    if showtfidf:
        tfidf_df = (pd.DataFrame(tfidf_matrix.todense()).
                    rename(columns=dict(zip(tfidf_vectorizer.
                                            vocabulary_.
                                            values(),
                                            tfidf_vectorizer.
                                            vocabulary_.
                                            keys()))))
        pd.set_option('display.max_columns', 500)
        print("\nTf-idf matrix:")
        print(tfidf_df)
        print()
        pd.set_option('display.max_columns', 20)

    # distortions - сумма квадратов расстояний от каждого из центров
    # кластеров до вершин, которые принадлежат этому кластеру.
    # Данную величину можно получить с помощью метода inertia_ для
    # sklearn.KMeans
    distortions = {}
    # Используем Elbow method (см. Википедию) для определения
    # оптимального количества кластеров
    for num_clusters in range(1, min(11, len(df['abstract'].tolist())+1)):
        print("K Means with "+str(num_clusters)+" clusters")
        km = KMeans(n_clusters = num_clusters)
        km.fit(tfidf_matrix)
        distortions[num_clusters] = km.inertia_
    # Строим график, согласно которому пользователь должен решить,
    # какое количество кластеров оптимально для данной выборки
    plt.figure()
    plt.plot(list(distortions.keys()), list(distortions.values()))
    plt.xlabel("Number of cluster")
    plt.ylabel("Distortions")
    plt.show()

    # Обучаемся еще раз на количестве кластеров, выбранном пользователем
    print("Input count of clusters:")
    num_clusters = int(input())
    km = KMeans(n_clusters = num_clusters)
    km.fit(tfidf_matrix)

    print("Kmeans saved in ../data/"+topic_name+".pkl")
    joblib.dump(km, "../data/"+topic_name+".pkl")
    km = joblib.load("../data/"+topic_name+".pkl")
    # clusters - список кластеров
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
    # order_centroids - список списков с номерами, соответствующими
    # позиции слов для каждого кластера в отсортированном массиве
    # с tf-idf коэффициентами
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    res_labels = []
    for i in range(num_clusters):
        print("Cluster %d words:" % (i+1), end='')

        result_words = []
        cnt_res_words = 0
        ind_res_words = 0
        # Выводим минимум между 5-ю и количеством топ-слов для
        # каждого кластера
        while (cnt_res_words <= 5 and
               ind_res_words < len(order_centroids[i])):
            if (vocab_frame.
               loc[terms[order_centroids[i][ind_res_words]].
                  split(' ')].
               values.tolist()[0][0] not in result_words):
                result_words.append(vocab_frame.
                       loc[terms[order_centroids[i][ind_res_words]].
                          split(' ')].
                       values.tolist()[0][0])
                cnt_res_words += 1
            ind_res_words += 1

        comma = ","
        print(comma.join(result_words), "\n")
        res_labels.append(result_words)

        # Если есть параметр showts, выводим также названия статей
        # для каждого из кластеров
        if showts:
            print("Cluster %d titles:" % i)
            ind_t = 1
            for title in cluster_df.ix[i]['title'].values.tolist():
                print("Title", str(ind_t)+":", title)
                ind_t += 1
            print("\n")

    # Если есть параметр showlds, обучаем lds модель
    if showlda:
        # Разделяем слова в тексте, приводим к виду без эффиксов
        tokenized_text = [tokenize_and_stem(text) for text
                          in df['abstract'].tolist()]
        # Удаляем стоп-слова
        texts = ([[word for word in text if word not in stopwords]
                  for text in tokenized_text])
        # Добавляем слова в gensim dictionary
        dictionary = corpora.Dictionary(texts)
        # Фильтруем по количеству употреблений:
        # нижнего ограничения нет, верхнее: употреблено
        # не более чем в половине абстрактов
        dictionary.filter_extremes(no_below=1, no_above=0.5)
        # doc2bow - возвращает кортеж (id слова, количество
        # употреблений каждого слова во всех абстрактах)
        corpus = [dictionary.doc2bow(text) for text in texts]

        print("LDA:")
        # corpus - словарь с id слов и количеством их использований
        # id2word - словарь, ставящий в соответствие каждому id
        # само слово
        # num_topics - количество кластеров
        # update_every - количество итераций между обновлениями кластеров
        # chunksize - размер буффера для каждого обновления
        # passes - количество прохождений алгоритма по corpus
        lda = models.LdaModel(corpus, num_topics=num_clusters,
                              id2word=dictionary,
                              update_every=5,
                              chunksize=10000,
                              passes=100)
        #Выводим топ-слова для каждого из кластеров
        topics_matrix = lda.show_topics(formatted=False, num_words=10)
        topics_matrix = np.array(topics_matrix, dtype=object)
        topic_words = topics_matrix[:,1]
        cluster_ind = 1

        for l in topic_words:
            print("Cluster "+str(cluster_ind)+": ", end='')
            for word in l:
                print(vocab_frame.ix[word[0].split(' ')].
                values.tolist()[0][0], end=', ')
            print()
            cluster_ind += 1

    # Если есть параметр showmds, показываем mds
    if showmds:
        # Строим модель для mds
        # n_components - размерность пространства, получаемого на выходе
        # dissimilarity - уже подсчитанно и будет подано на fit
        # random_state - генератор для инициализации центров кластеров
        mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)
        pos = mds.fit_transform(dist)
        #xs, ys - координаты по x и y
        xs, ys = pos[:, 0], pos[:, 1]
        # cluster_colors - список из 10 цветов для отображения mds
        # (10 - максимальное количество кластеров для выбора пользователем)
        cluster_colors = {0: '#000000', 1: '#ff0000', 2: '#9a37b4',
                          3: '#308b1b', 4: '#2dc7e7', 5: '#00097e',
                          6: '#9a9a9a', 7: '#b7d41b', 8: '#90aeff',
                          9: '#92002c'}

        cluster_names = {}
        for i in range(len(res_labels)):
            cluster_names[i] = res_labels[i][:min(3, len(res_labels[i]))]

        # Строим график mds и сохраняем его
        df_mds = pd.DataFrame(dict(x=xs, y=ys,
                                   label=clusters))
        groups_mds = df_mds.groupby("label")
        fig, ax = plt.subplots(figsize=(17,9))
        ax.margins(0.05)

        for name, group in groups_mds:
            ax.plot(group.x, group.y, marker='o', linestyle='',
                    label=cluster_names[name], ms=12,
                    color=cluster_colors[name], mec='none')
            ax.set_aspect('auto')
            ax.tick_params(\
                axis= 'x',
                which='both',
                bottom='off',
                top='off',
                labelbottom='off')
            ax.tick_params(\
                axis= 'y',
                which='both',
                left='off',
                top='off',
                labelleft='off')

        ax.legend(numpoints=1)
        plt.draw()
        plt.savefig("../data/mds_"+topic_name+".png", dpi=200)
        print("Mds plot saved in ../data/mds_"+topic_name+".png")
        plt.close()

    # Если есть параметр showhdc, отображаем
    # Hierarchical Document Clustering
    if showhdc:
        # Строим матрицу hdc методом ward из scipy
        linkage_matrix = ward(dist)
        fig, ax = plt.subplots(figsize=(80, 60))
        # По полученной матрице строим дендрограмму методом
        # dendrogram из scipy
        ax = dendrogram(linkage_matrix, orientation="right",
                    labels=df['name'].tolist())
        # Строим график и сохраняем его
        plt.tick_params(\
            axis='x',
            which='both',
            bottom='off',
            top='off',
            labelbottom='off')

        plt.tight_layout()
        plt.draw()
        plt.savefig("../data/hdc_"+topic_name+".png", dpi=200)
        print("Hdc plot saved in ../data/hdc_"+topic_name+".png")
        plt.close()
