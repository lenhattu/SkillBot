import re
import string
from bs4 import BeautifulSoup
import nlp_tools


def is_opening_utterance(pathtoinfopage, utterance):
    invocation = None
    with open(pathtoinfopage, 'r', encoding='utf-8') as file_in:
        soup = BeautifulSoup(file_in.read(), 'html.parser')
        loc = soup.find('div', id='a2s-skill-details').find_all(text=re.compile('Invocation Name:'))
        tags = [tag.parent for tag in loc]
        if len(tags) > 0:
            names = BeautifulSoup(str(tags[0]), 'html.parser').find_all('span')
            # print(names[1].get_text())
            invocation = names[1].get_text()
    if invocation is None:
        tag_title = soup.find('h1', class_='a2s-title-content')
        # print(title.get_text().strip())
        if tag_title is not None:
            title = tag_title.get_text().strip()
            if nlp_tools.search_keyword(title, utterance):
                return True
    else:
        if nlp_tools.search_keyword(invocation, utterance):
            return True
    return False


def create_custom_opening_utterance(pathtoinfopage):
    invocation = None
    utterance = "open "
    with open(pathtoinfopage, 'r', encoding='utf-8') as file_in:
        soup = BeautifulSoup(file_in.read(), 'html.parser')
        loc = soup.find('div', id='a2s-skill-details').find_all(text=re.compile('Invocation Name:'))
        tags = [tag.parent for tag in loc]
        if len(tags) > 0:
            names = BeautifulSoup(str(tags[0]), 'html.parser').find_all('span')
            # print(names[1].get_text())
            invocation = names[1].get_text()
    if invocation is None:
        tag_title = soup.find('h1', class_='a2s-title-content')
        # print(title.get_text().strip())
        if tag_title is not None:
            title = tag_title.get_text().strip()
            utterance += title
            return utterance
    else:
        utterance += invocation

    return utterance


def get_all_sample_utterances(pathtoinfopage):
    list_utterances = list()
    with open(pathtoinfopage, 'r', encoding='utf-8') as file_in:
        soup = BeautifulSoup(file_in.read(), 'html.parser')
        details = soup.find('div', id='a2s-product-details')
        div_utterances = details.find('div', id='a2s-product-utterances')
        if div_utterances is not None:
            for div in div_utterances.find_all('li', class_='a-carousel-card'):
                list_utterances.append(div.get_text().replace('\u201d', '').replace('\u201c', '').replace('\"', '').replace('\n', '').translate(str.maketrans('', '', string.punctuation)).strip().lower())
                #.translate(str.maketrans('', '', string.punctuation))

    # trim the unnecessary wake word and store utterances
    for index, item in enumerate(list_utterances):
        if 'Alexa' in item[:5] or 'alexa' in item[:5]:
            for i, c in enumerate(item):
                if c != ',' and c != ' ' and i > 4:
                    trim = item[i:]
                    list_utterances[index] = trim
                    break
    return list_utterances


def get_additional_utterances_from_description(pathtoinfopage):
    list_utterances = list()
    # get description
    list_desc = list()
    with open(pathtoinfopage, 'r', encoding='utf-8') as file_in:
        soup = BeautifulSoup(file_in.read(), 'html.parser')
        div_desc = soup.body.find('div', attrs={'id': 'a2s-description'})
        for tag in div_desc.find_all(['span', 'a']):
            # print(tag.get_text())
            list_desc.append(tag.get_text())
    # identify utterances
    for item in list_desc:
        phrases_in_quotes = re.findall(r'"([^"]*)"', item)
        for phrase in phrases_in_quotes:
            if 'Alexa' in phrase[:5] or 'alexa' in phrase[:5]:
                list_utterances.append(phrase)
    return list_utterances