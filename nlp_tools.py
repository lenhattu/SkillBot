import re
import requests
import json
import string
import spacy
import random
from collections import OrderedDict
from spacy.matcher import Matcher

nlp = spacy.load('en_core_web_sm')
nlp.add_pipe(nlp.create_pipe('sentencizer'))
matcher = Matcher(nlp.vocab)
QCAPI_AUTH = '' # get auth and documentation at https://www.harishtayyarmadabushi.com/research/questionclassification/question-classification-api-documentation/


def expand_contractions(text: str) -> str:
    ## https://en.wikipedia.org/wiki/Wikipedia:List_of_English_contractions

    flags = re.IGNORECASE | re.MULTILINE

    text = re.sub(r'`', "'", text, flags=flags)

    ## starts / ends with '
    text = re.sub(
        r"(\s|^)'(aight|cause)(\s|$)",
        '\g<1>\g<2>\g<3>',
        text, flags=flags
    )

    text = re.sub(
        r"(\s|^)'t(was|is)(\s|$)", r'\g<1>it \g<2>\g<3>',
        text,
        flags=flags
    )

    text = re.sub(
        r"(\s|^)ol'(\s|$)",
        '\g<1>old\g<2>',
        text, flags=flags
    )

    ## expand words without '
    text = re.sub(r"\b(aight)\b", 'alright', text, flags=flags)
    text = re.sub(r'\bcause\b', 'because', text, flags=flags)
    text = re.sub(r'\b(finna|gonna)\b', 'going to', text, flags=flags)
    text = re.sub(r'\bgimme\b', 'give me', text, flags=flags)
    text = re.sub(r"\bgive'n\b", 'given', text, flags=flags)
    text = re.sub(r"\bhowdy\b", 'how do you do', text, flags=flags)
    text = re.sub(r"\bgotta\b", 'got to', text, flags=flags)
    text = re.sub(r"\binnit\b", 'is it not', text, flags=flags)
    text = re.sub(r"\b(can)(not)\b", r'\g<1> \g<2>', text, flags=flags)
    text = re.sub(r"\bwanna\b", 'want to', text, flags=flags)
    text = re.sub(r"\bmethinks\b", 'me thinks', text, flags=flags)

    ## one offs,
    text = re.sub(r"\bo'er\b", r'over', text, flags=flags)
    text = re.sub(r"\bne'er\b", r'never', text, flags=flags)
    text = re.sub(r"\bo'?clock\b", 'of the clock', text, flags=flags)
    text = re.sub(r"\bma'am\b", 'madam', text, flags=flags)
    text = re.sub(r"\bgiv'n\b", 'given', text, flags=flags)
    text = re.sub(r"\be'er\b", 'ever', text, flags=flags)
    text = re.sub(r"\bd'ye\b", 'do you', text, flags=flags)
    text = re.sub(r"\be'er\b", 'ever', text, flags=flags)
    text = re.sub(r"\bd'ye\b", 'do you', text, flags=flags)
    text = re.sub(r"\bg'?day\b", 'good day', text, flags=flags)
    text = re.sub(r"\b(ain|amn)'?t\b", 'am not', text, flags=flags)
    text = re.sub(r"\b(are|can)'?t\b", r'\g<1> not', text, flags=flags)
    text = re.sub(r"\b(let)'?s\b", r'\g<1> us', text, flags=flags)

    ## major expansions involving smaller,
    text = re.sub(r"\by'all'dn't've'd\b", 'you all would not have had', text, flags=flags)
    text = re.sub(r"\by'all're\b", 'you all are', text, flags=flags)
    text = re.sub(r"\by'all'd've\b", 'you all would have', text, flags=flags)
    text = re.sub(r"(\s)y'all(\s)", r'\g<1>you all\g<2>', text, flags=flags)

    ## minor,
    text = re.sub(r"\b(won)'?t\b", 'will not', text, flags=flags)
    text = re.sub(r"\bhe'd\b", 'he had', text, flags=flags)

    ## major,
    text = re.sub(r"\b(I|we|who)'?d'?ve\b", r'\g<1> would have', text, flags=flags)
    text = re.sub(r"\b(could|would|must|should)n'?t'?ve\b", r'\g<1> not have', text, flags=flags)
    text = re.sub(r"\b(he)'?dn'?t'?ve'?d\b", r'\g<1> would not have had', text, flags=flags)
    text = re.sub(r"\b(daren|daresn|dasn)'?t", 'dare not', text, flags=flags)
    text = re.sub(r"\b(he|how|i|it|she|that|there|these|they|we|what|where|which|who|you)'?ll\b", r'\g<1> will', text,
                  flags=flags)
    text = re.sub(
        r"\b(everybody|everyone|he|how|it|she|somebody|someone|something|that|there|this|what|when|where|which|who|why)'?s\b",
        r'\g<1> is', text, flags=flags)
    text = re.sub(r"\b(I)'?m'a\b", r'\g<1> am about to', text, flags=flags)
    text = re.sub(r"\b(I)'?m'o\b", r'\g<1> am going to', text, flags=flags)
    text = re.sub(r"\b(I)'?m\b", r'\g<1> am', text, flags=flags)
    text = re.sub(r"\bshan't\b", 'shall not', text, flags=flags)
    text = re.sub(
        r"\b(are|could|did|does|do|go|had|has|have|is|may|might|must|need|ought|shall|should|was|were|would)n'?t\b",
        r'\g<1> not', text, flags=flags)
    text = re.sub(
        r"\b(could|had|he|i|may|might|must|should|these|they|those|to|we|what|where|which|who|would|you)'?ve\b",
        r'\g<1> have', text, flags=flags)
    text = re.sub(r"\b(how|so|that|there|these|they|those|we|what|where|which|who|why|you)'?re\b", r'\g<1> are', text,
                  flags=flags)
    text = re.sub(r"\b(I|it|she|that|there|they|we|which|you)'?d\b", r'\g<1> had', text, flags=flags)
    text = re.sub(r"\b(how|what|where|who|why)'?d\b", r'\g<1> did', text, flags=flags)

    return text


def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def correct_punctuation(paragraph):
    puncs = '''!)]};:",<>.?%&*~'''
    res = ""
    for index in range(0, len(paragraph)-1):
        res += paragraph[index]
        if paragraph[index] in puncs:
            if paragraph[index+1] != " " and paragraph[index+1] not in puncs:
                res += " "
    res += paragraph[len(paragraph)-1]
    return res


def search_keyword(word, sentence):
    if re.search(r"\b" + re.escape(word) + r"\b", sentence):
        return True
    return False


def classify_wh_question(question):
    #print(question)
    URL = 'http://qcapi.harishmadabushi.com/'
    auth = QCAPI_AUTH
    PARAMS = {'auth':auth, 'question':question}
    #req = requests.get(url=URL, params=PARAMS).json()
    req = requests.get(url=URL, params=PARAMS)
    j = re.search(r'{.*}', req.text)
    if j is None:
        return json.loads('{"status": "Fail"}')
    return json.loads(j.group(0))


def is_wh_question(doc):
    # Regular Wh syntax: "What is your name?"
    wh_tags = ["WDT", "WP", "WP$", "WRB"]
    wh_words = [t for t in doc if t.tag_ in wh_tags]
    #aux_words = [a for a in doc if a.pos_ == 'AUX']

    #if len(aux_words) > 0:
    #    is_regular_wh = wh_words and wh_words[0].i < aux_words[0].i
    #else:
    #    is_regular_wh = wh_words and doc[wh_words[0].i+1] and doc[wh_words[0].i+1].text == 'about'

    is_regular_wh = False
    if len(wh_words) > 0:
        is_regular_wh = True

    # Include pied-piping Wh syntax: "To whom did you tell the story?"
    is_pied_piping_wh = wh_words and wh_words[0].head.dep_ == "prep"

    # Exclude: "What you think is great"
    exclude1 = wh_words and wh_words[0].head.dep_ in ["csubj", "advcl"]
    if exclude1:
        return False

    # Exclude: "Whatever you like"
    exclude2 = wh_words and "ever" in wh_words[0].text
    if exclude2:
        return False

    return is_regular_wh or is_pied_piping_wh


def is_subject(token):
    subject_deps = {"csubj", "nsubj", "nsubjpass"}
    return token.dep_ in subject_deps


def is_yesno_question(doc):
    root = [t for t in doc if t.dep_ == "ROOT"][0]
    subj = [t for t in root.children if is_subject(t)]

    if is_wh_question(doc):
        return False

    # Be/Modal is an AUX at the beginning
    aux = [t for t in root.lefts if t.dep_ == "aux"]
    if subj and aux:
        return aux[0].i < subj[0].i

    # Be is the VERB itself
    root_is_inflected_copula = root.pos_ == "AUX" and root.tag_ != "VB"
    if subj and root_is_inflected_copula:
        return root.i < subj[0].i

    return False


def is_request(doc):
    pattern = [{'TAG': 'VB'}]
    matcher.add('imp', None, pattern)
    matches = matcher(doc)
    specific_results=[]
    if len(matches) > 0:
        for idx, start, end in matches:
            span = doc[start:end]
            specific_results.append(span.text)
            return True
    else:
        return False


def identify_question_in_paragraph(response):
    if response == "" or response is None:
        return ["", "o"]
    list_result = list()
    processed_response = correct_punctuation(expand_contractions(response))
    doc = nlp(processed_response)
    list_sentences = [sent.string.strip() for sent in doc.sents]
    for sentence in list_sentences:
        if all(j in string.punctuation for j in sentence):
            continue
        if is_wh_question(nlp(sentence)):
            list_result.append([sentence, "wh", processed_response])
        elif is_yesno_question(nlp(sentence)):
            list_result.append([sentence, "yn"])
        else:
            list_result.append([sentence, "o"])

    #res = list_result[len(list_result) - 1]
    for item in reversed(list_result):
        if item[1] in ["wh", "yn"]:
            return item
    return [processed_response, "o"]


def generate_answer_wh(question, statement):
    req = classify_wh_question(question)
    if req['status'] == 'Success':
        major_type = req['major_type']
        if major_type == 'ABBR':
            return ["I do not know"]
        elif major_type == 'DESC':
            if ":" in statement:
                return statement.split(":")[1].split(',')
            elif " choose from" in statement or " pick from" in statement or " select from" in statement:
                return statement.split(" from")[1].strip(',').split(',')
            elif " choose " in statement:
                return statement.split(" choose ")[1].strip(',').split(',')
            elif " say " in statement:
                return statement.split(" say ")[1].strip(',').split(',')
            elif " select " in statement:
                return statement.split(" select ")[1].strip(',').split(',')
            return ["I do not know"]
        elif major_type == 'ENTY':
            if ":" in statement:
                return statement.split(":")[1].split(',')
            elif " choose from" in statement or " pick from" in statement or " select from" in statement:
                return statement.split(" from")[1].strip(',').split(',')
            elif " choose " in statement:
                return statement.split(" choose ")[1].strip(',').split(',')
            elif " say " in statement:
                return statement.split(" say ")[1].strip(',').split(',')
            elif " select " in statement:
                return statement.split(" select ")[1].strip(',').split(',')
            return ["Anything"]
        elif major_type == 'HUM':
            if 'name' in question:
                return ["John"]
            elif ":" in statement:
                return statement.split(":")[1].split(',')
            elif " choose from" in statement or " pick from" in statement or " select from" in statement:
                return statement.split(" from")[1].strip(',').split(',')
            elif " choose " in statement:
                return statement.split(" choose ")[1].strip(',').split(',')
            elif " say " in statement:
                return statement.split(" say ")[1].strip(',').split(',')
            elif " select " in statement:
                return statement.split(" select ")[1].strip(',').split(',')
            sentences = [sent.string.strip() for sent in nlp(statement).sents]
            for sent in sentences:
                if ' or ' in sent or ' or,' in sent or ',or ' in sent or ',or,' in sent:
                    return sent.split('or')
            return ["Anyone"]
        elif major_type == 'LOC':
            return ["3119 Doctors Drive, Los Angeles, California, United States"]
        elif major_type == 'NUM':
            res = ["1"]
            if 'phone' in question or 'mobile' in question:
                res = ["3103413925"]
            elif 'zip' in question:
                res = ["90017"]
            elif 'birth' in question or 'born' in question:
                res = ["November 5, 2011"]
            elif 'age' in question or 'old' in question:
                res = ["9"]
            return res
    else:
        return ["I do not know"]


def generate_answer_yn():
    return ["yes", "no"]


# Find groups of strictly increasing numbers within
def findStrictlyIncreasingSequence(x):
    try:
        it = iter(x)
        prev, res = next(it), []

        while prev is not None:
            start = next(it, None)

            if prev + 1 == start:
                res.append(prev)
            elif res:
                yield list(res + [prev])
                res = []
            prev = start
    except StopIteration:
        return


def get_suggested_phrases(statement):
    sentences = [sent.string.strip() for sent in nlp(statement).sents]
    for sent in sentences:
        if all(j in string.punctuation for j in sent):
            continue


def generate_answer_quiz(statement):
    options = re.findall(r'\d+', statement)
    sequences = list(findStrictlyIncreasingSequence([int(i) for i in options]))
    is_option = False
    for seq in sequences:
        if seq[0] == 0 or seq[0] == 1:
            is_option = seq
    if is_option:
        res = list(OrderedDict.fromkeys([str(i) for i in is_option]))
        return res
    else:
        if '1' in options and '2' in options and '1.' in statement and '2.' in statement:
            return list(OrderedDict.fromkeys(options))
    return False


def generate_answer_other(statement):
    res = ["more"]
    # check imperative: Please tell me your name
    doc = nlp(statement)
    list_sentences = [sent.string.strip() for sent in doc.sents]
    for sent in list_sentences:
        if all(j in string.punctuation for j in sent):
            continue
        if is_request(nlp(sent)):
            if ":" in sent:
                return statement.split(":")[1].split(',')
            elif " choose from" in sent or " pick from" in sent or " select from" in sent:
                return sent.split(" from")[1].strip(',').split(',')
            elif " choose " in sent:
                return sent.split(" choose ")[1].strip(',').split(',')
            elif " say " in sent:
                return sent.split(" say ")[1].strip(',').split(',')
            elif " select " in sent:
                return sent.split(" select ")[1].strip(',').split(',')
            elif 'name' in sent:
                return ["John"]
            elif 'address' in sent or 'where you are from' in sent or 'where are you from' in sent:
                return ["3119 Doctors Drive, Los Angeles, California, United States"]
            elif 'phone' in sent or 'mobile' in sent:
                return ["3103413925"]
            elif 'zip' in sent:
                return ["90017"]
            elif 'birth' in sent or 'you were born' in sent or 'were you born' in sent:
                return ["November 5, 2011"]
        if '?' in sent:
            return ["yes", "no"]
    return res


if __name__ == '__main__':
    #response = "I will ask you 5 questions, try to get as many right as you can. Just say the number of the answer. Let's begin. Question 1. Which jewellery company offered partnership with Sanrio? 1. Simmons Jewelry Company. 2. Macys. 3. Ben Bridge. 4. Tiffanys.. "
    response = "I will ask you 5 questions, try to get as many right as you can. Just say the number of the answer. Let's begin. Question 1. Which jewellery company offered partnership with Sanrio? 1. 1992. 2. 1996. 3. 2003. 4. 2020.. "
    #response = "I did not understand. Which character would you like to play? Red riding hood, or, Big Bad Wolf. You can also say help or repeat.."
    #response = "I did not understand. Which character would you like to play? Red riding hood, or, Big Bad Wolf. You can also say help or repeat.. "
    #doc = nlp(response)
    #print(poss_is_you(nlp(response)))
    print(generate_answer_quiz(response))
