import sys
import wos_parser
import wos_graph
import wos_clasterization
import test_articles

if __name__ == "__main__":
    if "help" in sys.argv:
        print("Parameters:")
        print("showbm - show articles before modification")
        print("showam - show articles after modification")
        print("addta - add test articles")
        print("showtfidf - show tf-idf matrix, 500 columns")
        print("showmds - show multidimensional scaling")
        print("nodownload - don't download new article, use old")
        print("showts - show titles for every claster")
        print("showhdc - show hierarchical document clustering")
        print("showlda - show latent Dirichlet allocation")
        sys.exit()
    print("Add 'help' for showing parameters")
    print("Input search string")
    topic_name = input()

    if "nodownload" in sys.argv:
        print("Input count of articles")
        cnt_articles = int(input())
    else:
        # site_parser - скачивает html-страницы каждой статьи,
        # выданной по запросу пользователя topic_name.
        # Возвращает количество статей
        cnt_articles = wos_parser.site_parser(topic_name)
    articles = []
    for i in range(1, cnt_articles+1):
        # article_parser - парсит из html страницы статьи имя,
        # автора, абстракт и статьи, на которые она ссылается
        # Эти данные добавляются в лист articles
        wos_parser.article_parser(topic_name + str(i), articles)

    if "showbm" in sys.argv:
        # show_articles - выводит на экран статьи, добавленные
        # в articles
        wos_parser.show_articles(articles)
    # correct_articles - удаляет статьи без названий, приводит
    # имена авторов в удобный для идентификации статей формат
    articles = wos_parser.correct_articles(articles)
    if "addta" in sys.argv:
        # add_test_articles - добавляет в конец articles тестовые
        # статьи. Они используются для проверки корректности графа
        test_articles.add_test_articles(articles)
    if "showam" in sys.argv:
        # show_correct_articles - выводит на экран статьи после
        # всех модификаций
        wos_parser.show_correct_articles(articles)

    # build_graph - строит граф, сохраняет его в формате gexf.
    # Возвращает articles без повторяющихся статей
    articles = wos_graph.build_graph(articles, topic_name)

    # Описания этих параметров приведены выше при обработке
    # параметра 'help'
    showtfidf = 0
    showmds = 0
    showts = 0
    showhdc = 0
    showlda = 0
    if "showtfidf" in sys.argv:
        showtfidf = 1
    if "showmds" in sys.argv:
        showmds = 1
    if "showts" in sys.argv:
        showts = 1
    if "showhdc" in sys.argv:
        showhdc = 1
    if "showlda" in sys.argv:
        showlda = 1

    # build_csv - строит базу данных по articles, сохраняет ее
    wos_clasterization.build_csv(articles, topic_name)
    # article_clasterization - разбивает статьи на кластеры
    wos_clasterization.article_clasterization(topic_name, showtfidf, showmds,
                                              showts, showhdc, showlda)
