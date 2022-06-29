from bs4 import BeautifulSoup
import requests
import os

def check_encodings(text_string):

    # This function iterates though each word in a string have iso-8859-1 encodings rather than ascii
    # and returning the indexes of the words that have iso-8859-1 encodings

    has_iso = False
    iso_indeces = []
    words = text_string.split()
    for index, word in enumerate(words):
        for element in word:
            if ord(element) in range(129, 255):
                has_iso = True
                iso_indeces.append(index)

    return has_iso, iso_indeces

def get_wiki_text(page_body, article_name):

    # This function scrapes the body of the webpage and adds the content into a text file within the specified directory

    title_element = page_body.find(['h1'], id="firstHeading")
    page_title = title_element.string
    content_element = page_body.find(['div'], class_="mw-parser-output")
    page_content = content_element.contents
    error_message = ''

    text_filepath = os.path.join('textfiles/' + article_name + '_Wikipedia_Article')
    wiki_textfile = open(text_filepath, mode="w")
    wiki_textfile.write('Source: en.wikipedia.org\n\n')
    wiki_textfile.write(page_title)
    wiki_textfile.close()

    for pc in page_content[1:]:
        ascii_writer = open(text_filepath, mode="a", encoding="ascii")
        iso_writer = open(text_filepath, mode="a", encoding="iso-8859-1")
        utf_writer = open(text_filepath, mode="a", encoding="utf-8")

        # This portion goes through the content of the p (paragraph) elements and writes the content to the text file

        if pc.name == 'p':
            paragraph_text = ''
            p_list = pc.contents
            for p_el in p_list:
                paragraph_line = p_el.string
                if p_el.name == 'span' or p_el.name == 'sup':
                    continue
                else:
                    if paragraph_line is not None:
                        has_iso, iso_indeces = check_encodings(paragraph_line)
                        if has_iso is True:
                            i = 0
                            line_words = paragraph_line.split()
                            for word in line_words:
                                spaced_word = word + ' '
                                if i not in iso_indeces:
                                    try:
                                        ascii_writer.write(spaced_word)
                                    except Exception:
                                        try:
                                            utf_writer.write(spaced_word)
                                        except Exception as e:
                                            print(e)
                                else:
                                    try:
                                        iso_writer.write(spaced_word)
                                    except Exception:
                                        try:
                                            utf_writer.write(spaced_word)
                                        except Exception as e:
                                            print(e)
                                i += 1
                        else:
                            paragraph_text += paragraph_line

            if paragraph_text:
                try:
                    ascii_writer.write(paragraph_text)
                except Exception:
                    paragraph_words = paragraph_text.split()
                    for word in paragraph_words:
                        spaced_word = word + ' '
                        try:
                            ascii_writer.write(spaced_word)
                        except Exception:
                            try:
                                iso_writer.write(spaced_word)
                            except Exception:
                                try:
                                    utf_writer.write(paragraph_text)
                                except Exception as e:
                                    print(e)

        # This portion goes through the content of the header elements and writes the content to the text file

        elif pc.name in ['h2', 'h3', 'h4']:
            header_el = pc.contents
            header_string = header_el[0].string
            if header_string is not None:
                try:
                    ascii_writer.write('\n\n')
                    ascii_writer.write(header_el[0].string)
                    ascii_writer.write('\n\n')
                except Exception as e:
                    error_message = e

        else:
            continue
        ascii_writer.close()
        iso_writer.close()
        utf_writer.close()
        return error_message

def get_articles_list(page_body, language_code):

    # This function finds the url name for the top 5 search results in cases where the specified url returned multiple results

    content_element = page_body.find(['div'], class_="mw-parser-output")
    page_content = content_element.contents
    i = 0
    error_message = ''
    for pc in page_content[1:]:
        if pc.name == 'ul':
            for x in pc.contents:
                if x.name == 'li':
                    for y in x.contents:
                        if i >= 5:
                            break
                        else:
                            if y.name == 'a':
                                article_url = y['href']
                                article_name = article_url.replace('/wiki/', '')
                                try:
                                    get_article_by_url(search_term=article_name, language_code=language_code, checked=True)
                                except Exception as e:
                                    error_message = e
                                i += 1
                            else:
                                continue
                else:
                    continue
        else:
            continue
    return  error_message

def check_for_multi_articles(page_body, language_code, article_name):

    # This function checks to see whether the specified url returned multiple results or just one article

    content_element = page_body.find(['div'], class_="mw-parser-output")
    page_content = content_element.contents
    for pc in page_content[1:]:
        multi_articles = False
        if pc.name == 'div' and language_code == 'pt' and pc.has_attr('id'):
            if pc['id'] == 'disambig':
                global pt_multi_articles
                pt_multi_articles = True
        if pc.name == 'div' and language_code == 'fr' and pc.has_attr('id'):
            if pc['id'] == 'homonymie':
                global fr_multi_articles
                fr_multi_articles = True
        if pc.name == 'table' and language_code == 'it' and pc.has_attr('class'):
            for cl in pc['class']:
                if cl == 'avviso-disambigua':
                    get_articles_list(page_body, language_code)

        if pc.name == 'p':
            p_list = pc.contents
            multi_articles_statements = {" may refer to:\n", " most often refers to:\n", " commonly refers to:\n", " most commonly refers to:\n"}
            fl_multi_articles_vars = ('fr_multi_articles', 'pt_multi_articles')
            for p_el in p_list:
                if p_el.string in multi_articles_statements and language_code == 'en':
                    multi_articles = True
            for fmav in fl_multi_articles_vars:
                if fmav in globals():
                    multi_articles = True
            if multi_articles is True:
                get_articles_list(page_body, language_code)
            else:
                get_wiki_text(page_body, article_name)
            break


def get_article_by_url(search_term, language_code, checked):

    # This function sends a get request to the wikipedia url for the given search term to check the response

    article_name = search_term.replace(' ', '_')
    https_heading = 'https://'
    wiki_url = '.wikipedia.org/wiki/'
    wiki_full_url = https_heading + language_code + wiki_url + article_name
    response = requests.get(wiki_full_url)
    error_message = ''
    if response.status_code == 200 and checked is False:
        wiki_page = BeautifulSoup(response.text, 'html.parser')
        page_body = wiki_page.body
        error_message = check_for_multi_articles(page_body, language_code, article_name)
    elif response.status_code == 200 and checked is True:
        wiki_page = BeautifulSoup(response.text, 'html.parser')
        page_body = wiki_page.body
        error_message = get_wiki_text(page_body, article_name)
    elif response.status_code == 404:
        error_message = 'Error: an article with this name in this language was not found'
    else:
        error_message = 'Error: ' + response.status_code

    return error_message

if __name__ == "__main__":
    get_article_by_url("Seattle", "en", checked=False)












