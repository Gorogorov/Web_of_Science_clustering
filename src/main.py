import sys
import wos_parser
import wos_graph
import wos_clusterization
import test_articles

if __name__ == "__main__":
    if "help" in sys.argv:
        print("Parameters:")
        print("showbm - show articles before modification")
        print("showam - show articles after modification")
        print("addta - add test articles")
        print("showtfidf - show tf-idf matrix, 500 columns")
        print("showmds - show multidimensional scaling")
        print("nodownload - do not download new article, use old")
        print("showts - show titles for every cluster")
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
        cnt_articles = wos_parser.site_parser(topic_name)
    articles = []
    for i in range(1, cnt_articles + 1):
        wos_parser.article_parser(topic_name + str(i), articles)

    if "showbm" in sys.argv:
        wos_parser.show_articles(articles)
    articles = wos_parser.correct_articles(articles)
    if "addta" in sys.argv:
        test_articles.add_test_articles(articles)
    if "showam" in sys.argv:
        wos_parser.show_correct_articles(articles)

    articles = wos_graph.build_graph(articles, topic_name)

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

    wos_clusterization.build_csv(articles, topic_name)
    wos_clusterization.article_clusterization(topic_name, showtfidf, showmds,
                                              showts, showhdc, showlda)
