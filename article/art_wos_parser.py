def site_parser(topic_name):
    driver = webdriver.Firefox()
    driver.get("http://www.webofknowledge.com")
    element = driver.find_element_by_xpath("//input[@id=" \
                                            "'value(input1)']")
    element.send_keys(topic_name)
    element.submit()
    cur_articles = driver.find_elements_by_xpath("//a[@class='smallV110']")
    cur_articles[0].click()
    page_content = driver.page_source

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

    ind_page = 0
    while ind_page < cnt_pages:
        print("Creating ../data/"+topic_name+str(ind_page+1))
        write_file = open("../data/"+topic_name+str(ind_page+1), "w")
        write_file.write(driver.page_source)
        write_file.close()

        if ind_page != cnt_pages-1:
            element2 = driver.find_element_by_xpath("//a[@class='paginationNext']")
            element2.click()
        ind_page += 1
    driver.close()
    return cnt_pages

def article_parser(file_name, articles):
    A = Article()
    # <...>
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
    # <...>
    articles.append(A)

def correct_articles(articles):
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
            # <...>
        new_articles.append(NA)
    return new_articles


