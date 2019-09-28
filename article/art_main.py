import sys
import wos_parser
import wos_graph
import wos_clasterization

if __name__ == "__main__":
    if "help" in sys.argv:
        print("Parameters:")
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
        cnt_articles = wos_parser.site_parser(topic_name)
    articles = []
    for i in range(1, cnt_articles+1):
        wos_parser.article_parser(topic_name + str(i), articles)
    articles = wos_parser.correct_articles(articles)

    articles = wos_graph.build_graph(articles, topic_name)

    showmds = 0
    showts = 0
    showhdc = 0
    showlda = 0
    if "showmds" in sys.argv:
        showmds = 1
    if "showts" in sys.argv:
        showts = 1
    if "showhdc" in sys.argv:
        showhdc = 1
    if "showlda" in sys.argv:
        showlda = 1

    wos_clasterization.build_csv(articles, topic_name)
    wos_clasterization.article_clasterization(topic_name, showmds, showts,
                                              showhdc, showlda)
