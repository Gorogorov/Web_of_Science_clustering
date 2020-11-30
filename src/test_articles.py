from abstract_data import Article, CitedReference

def add_test_articles(articles):
    A1 = Article()
    A1.name = "Test Article 1"
    A1.author = ["Me A B"]
    A1.CitedReferences = []
    CR1 = CitedReference()
    CR1.name = "Test Cited Reference"
    CR1.author = ["Notme C"]
    A1.CitedReferences.append(CR1)
    articles.append(A1)

    A2 = Article()
    A2.name = "Test Article 2"
    A2.author = ["Me A B", "Nobody D F"]
    A2.CitedReferences = []
    CR2 = CitedReference()
    CR2.name = "Test Article 1"
    CR2.author = ["Me A B"]
    A2.CitedReferences.extend([CR1, CR2])
    articles.append(A2)

    A3 = Article()
    A3.name = "Test Article 3"
    A3.author = ["Brain M Y"]
    A3.CitedReferences = []
    CR31 = CitedReference()
    CR31.name = "Test Cited Reference"
    CR31.author = ["Notme", "Error N E"]
    CR32 = CitedReference()
    CR32.name = "Test Article 1"
    CR32.author = ["Me A C"]
    CR33 = CitedReference()
    CR33.name = "Test Article 2"
    CR33.author = ["Me A B", "Nobody D", "Error"]
    A3.CitedReferences.extend([CR31, CR32, CR33])
    articles.append(A3)
