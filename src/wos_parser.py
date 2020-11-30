import time
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from abstract_data import CitedReference, Article


def correct_authors(authors):
    """Creates a valid array of authors. A valid array is:
    the last name starts with a capital letter, the rest are small.
    Further, if there is a name, then it becomes one capital letter.
    If there is a second name, then it becomes the second capital letter.
    
    Example: ULISS Dar Frog -> Uliss D F, REGER N.R. -> Reger N R

    Args:
        authors (str): string with authors in Web of Science format.

    Returns:
        list: valid array of authors.

    """
    cor_authors = []
    authors = authors.split("; ")
    for author in authors:
        if author.find("et al") != -1:
            continue
        auth_name = author.split(", ")
        n1 = ""
        n2 = ""
        surn = ""
        surn = auth_name[0].capitalize()
        if len(auth_name) > 1:
            initials = auth_name[1].split(" ")
            if len(initials[0]) == 1:
                n1 = initials[0].upper()
            elif (len(initials[0]) == 2 and
                  initials[0][1] == "."):
                n1 = initials[0][0].upper()
            elif (len(initials[0]) == 2 and
                  initials[0][1].isupper()):
                n1 = initials[0][0]
                n2 = initials[0][1]
            elif (len(initials[0]) == 3 and
                  initials[0][1] == "."):
                n1 = initials[0][0].upper()
                n2 = initials[0][2].upper()
            elif (len(initials[0]) == 3 and
                  initials[0][2] == "."):
                n1 = initials[0][0].upper()
                n2 = initials[0][1].upper()
            elif (len(initials[0]) == 4 and
                  initials[0][1] == "." and
                  initials[0][3] == "."):
                n1 = initials[0][0].upper()
                n2 = initials[0][2].upper()
            else:
                n1 = initials[0][0].upper()
            if len(initials) > 1:
                if len(initials[1]) == 1:
                    n2 = initials[1].upper()
                elif (len(initials[1]) == 2 and
                      initials[1][1] == "."):
                    n2 = initials[1][0].upper()
                else:
                    n2 = initials[1].upper()
        res_author = surn+" "+n1+" "+n2
        if res_author[-1] == " ":
            res_author = res_author[:-1]
        cor_authors.append(res_author)
    return cor_authors


def correct_articles(articles):
    """Create an object of class Article. 
    Removes unnamed articles.
    Creates a valid array of authors.

    Args:
        articles (list): list of articles.

    Returns:
        list: valid array of authors.

    """
    new_articles = []
    for A in articles:
        if not hasattr(A, "name") or not hasattr(A, "author"):
            continue
        NA = Article()
        NA.name = A.name
        NA.author = correct_authors(A.author)
        if hasattr(A, "abstract"):
            NA.abstract = A.abstract
        NA.CitedReferences = []
        for i in range(len(A.CitedReferences)):
            if (not hasattr(A.CitedReferences[i], "name") or
                not hasattr(A.CitedReferences[i], "author")):
                continue
            NCR = CitedReference()
            NCR.name = A.CitedReferences[i].name
            NCR.author = correct_authors(A.CitedReferences[i].author)
            NA.CitedReferences.append(NCR)
        new_articles.append(NA)
    return new_articles


def del_highlightings(line):
    """Removes highlighting of words that are formed as a result
    matches words from the search and from the article

    Args:
        line (str): html string.

    Returns:
        list: string without highlights

    """
    search_substring = '''<span class="hitHilite">'''
    ind_in_substr = line.find(search_substring)
    while ind_in_substr != -1:
        line = line[:ind_in_substr] + line[ind_in_substr+24:]
        ind_in_substr = line.find(search_substring)
    search_substring = '''</span>'''
    ind_in_substr = line.find(search_substring)
    while ind_in_substr != -1:
        line = line[:ind_in_substr] + line[ind_in_substr+7:]
        ind_in_substr = line.find(search_substring)
    return line


def article_parser(file_name, articles):
    """Parse the html page, recognizing from it the title of the article, the author,
    abstract and all articles referenced by this. Add result to articles.

    Args:
        file_name (str): html page from Web of Science
        articles (list): list of articles.

    """
    try:
        A = Article()
        # Парсим название статьи
        rfile = open("../data/"+file_name, "r")

        prev_article_name = 0
        search_string = "You will need to save or export"
        for line in rfile:
            ind_in_search = line.find(search_string)
            if prev_article_name == 1:
                line = line[7:-9]
                line = del_highlightings(line)
                A.name = line
                break
            if ind_in_search != -1:
                prev_article_name = 1
        rfile.close()
        # Парсим имена авторов
        rfile = open("../data/"+file_name, "r")

        search_string = "Find more records by this author"
        no_search_string = "Find more records by this author keywords"
        authors = []
        for line in rfile:
            ind_in_search = line.find(search_string)
            no_ind_in_search = line.find(no_search_string)
            if ind_in_search != -1 and no_ind_in_search == -1:
                search_substring = "hasautosubmit"
                ind_in_substr = line.find(search_substring)
                line = line[ind_in_substr+21:-10]
                search_substring = "</a>"
                ind_in_substr = line.find(search_substring)
                line = line[:ind_in_substr]
                line = del_highlightings(line)
                authors.append(line)
        res_author = ""
        for i in range(len(authors)):
            res_author += authors[i]
            if i != len(authors) - 1:
                res_author += "; "
        A.author = res_author
        rfile.close()
        # Парсим абстракт статьи
        rfile = open("../data/"+file_name, "r")
        prev_abstract = 0
        search_string = '''<div class="title3">Abstract</div>'''
        for line in rfile:
            if prev_abstract == 1:
                line = line[20:-5]
                line = del_highlightings(line)
                A.abstract = line
                break
            else:
                ind_in_search = line.find(search_string)
                if ind_in_search != -1:
                    prev_abstract = 1
        rfile.close()
        # Парсим статьи, на которые ссылается данная
        A.CitedReferences = []
        rfile = open("../data/"+file_name, "r")

        ind_ref = 1
        next_ref = '''<div id="RECORD_''' + str(ind_ref)
        CR = CitedReference()
        for line in rfile:
            is_new_ref = line.find(next_ref)
            is_main_item = line.find("search-results-item-mini")
            if is_new_ref != -1 and is_main_item == -1:
                if ind_ref != 1:
                    A.CitedReferences.append(CR)
                ind_ref += 1
                next_ref = '''<div id="RECORD_''' + str(ind_ref)
                CR = CitedReference()
            search_name_inside = "<value lang_id="
            search_name_outside = "</a>"
            ind_name_inside = line.find(search_name_inside)
            ind_name_outside = line.find(search_name_outside)
            if ind_name_inside != -1 and ind_name_outside == -1:
                line=line[1:]
                search_string = ">"
                beg_ind = line.find(search_string)
                line = line[beg_ind+1:-9]
                line = del_highlightings(line)
                CR.name = line
            search_author_inside = '''<span class="label">By:'''
            ind_author_inside = line.find(search_author_inside)
            if ind_author_inside != -1:
                line = line[31:-7]
                line = del_highlightings(line)
                CR.author = line
            if '''id="qoSentCloseActionTemplate"''' in line:
                A.CitedReferences.append(CR)

        rfile.close()
        articles.append(A)
    except:
        print("Error during reading "+file_name)
        sys.exit()


def site_parser(topic_name):
    """Downloads all html pages with articles given in the search engine
    of the Web of Science at the request of the user.

    Args:
        topic_name (str): request of the user.

    Returns:
        int: number of articles

    """
    driver = webdriver.Firefox()
    is_correct = 0
    while is_correct == 0:
        try:
            driver.get("http://www.webofknowledge.com")
            element = driver.find_element_by_xpath("//input[@id=" \
                                                   "'value(input1)']")
            element.send_keys(topic_name)
            element.submit()
            time.sleep(5)
            cur_articles = driver.find_elements_by_xpath("//a[@class='smallV110']")
            cur_articles[0].click()
            time.sleep(5)
            page_content = driver.page_source
            is_correct = 1
        except:
            print("Error while opening first article")
            time.sleep(20)

    search_string = 'This table has <b>'
    ind_in_search = page_content.find(search_string)
    ind_in_search += 19
    ind_end = ind_in_search
    while (page_content[ind_end] != ' '):
        ind_end += 1
    cnt_string = ""
    for l in page_content[ind_in_search:ind_end]:
        if l != ",":
            cnt_string += l
    cnt_pages = int(cnt_string)
    time.sleep(5)

    ind_page = 0
    while ind_page < cnt_pages:
        try:
            print("Creating ../data/"+topic_name+str(ind_page+1))
            write_file = open("../data/"+topic_name+str(ind_page+1), "w")
            write_file.write(driver.page_source)
            write_file.close()

            if ind_page != cnt_pages - 1:
                element2 = driver.find_element_by_xpath("//a[@class='paginationNext']")
                time.sleep(1)
                element2.click()
                time.sleep(2)
            ind_page += 1
        except:
            print("Error while creating article number", ind_page+1)
            time.sleep(20)
            is_refresh = 0
            while is_refresh == 0:
                try:
                    driver.refresh()
                    is_refresh = 1
                except:
                    pass

            time.sleep(5)
    driver.close()
    return cnt_pages


def show_articles(articles):
    """Displays articles before modification.

    Args:
        articles (list): list of articles.

    """
    for i in range(len(articles)):
        print("NAME:")
        if hasattr(articles[i], "name"):
            print(articles[i].name)
        else:
            print("No name")
        print("AUTHOR:")
        if hasattr(articles[i], "author"):
            print(articles[i].author)
        else:
            print("No author")
        print("ABSTRACT:")
        if hasattr(articles[i], "abstract"):
            print(articles[i].abstract)
        else:
            print("No abstract")
        print("CITED REFERENCE:")
        for CR in articles[i].CitedReferences:
            if hasattr(CR, "name"):
                print(CR.name)
            else:
                print("No name")
            if hasattr(CR, "author"):
                print(CR.author)
            else:
                print("No author")
            print("--------------------")
        print()


def show_correct_articles(articles):
    """Displays articles after modification.

    Args:
        articles (list): list of articles.

    """
    for i in range(len(articles)):
        print("NAME:")
        print(articles[i].name)
        print("AUTHOR:")
        for a in articles[i].author:
            print(a, "; ", sep='', end='')
        print()
        print("ABSTRACT:")
        if hasattr(articles[i], "abstract"):
            print(articles[i].abstract)
        else:
            print("No abstract")
        print("CITED REFERENCE:")
        for CR in articles[i].CitedReferences:
            print(CR.name)
            for a in CR.author:
                print(a, "; ", sep='', end='')
            print()
            print("--------------------")
        print()
