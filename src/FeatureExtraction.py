import nltk
from nltk import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import treebank
from nltk.corpus import PlaintextCorpusReader
from nltk.corpus import wordnet as wn
from nltk.parse.stanford import StanfordDependencyParser
import string
import spacy
from nltk.corpus import stopwords
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import Pipeline
from os.path import join
from spacy import displacy
import webbrowser
from nltk.corpus import wordnet as wn

# def load_corpus(dir):
#     wordlists = PlaintextCorpusReader(dir, '.*')
#     # wordlists.fileids()
#     return wordlists


def get_sentences(context):
    sentences = sent_tokenize(context)
    return sentences


def get_sentences_using_spacy(doc):
    return doc.sents


def remove_stopwords(wordsList):
    stopwords = stopwords.words('english')
    wordsList = [w for w in wordsList if not w in stopwords]
    return wordsList


# def get_words(sentence):
#     lowers = sentence.lower()
#     # no_punctuation = lowers.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
#     no_punctuation = lowers.translate(str.maketrans('', '', string.punctuation))
#     tokens = word_tokenize(no_punctuation)
#     # print(tokens)
#     # tokens = word_tokenize(sentence.lower())
#     tokens = remove_stopwords(tokens)
#     return tokens

def get_words(doc):
    token_text_list = [token.text for token in doc]
    return token_text_list


def get_words_and_synonyms(sentence):
    tokens = get_words(sentence)
    word_list = []
    for token in tokens:
        word_list = (set(word_list) | get_synonym(token))
    word_set = set([])
    for word in word_list:
        word_set.add(get_lemmars(word))
    return word_set


# def get_lemmars(word):
#     lemmatizer = WordNetLemmatizer()
#     lemmatized_words = lemmatizer.lemmatize(word)
#     return lemmatized_words

def get_lemmars(doc):
    lemmatized_tokens_list = [token.lemma_ for token in doc]
    return lemmatized_tokens_list


# def get_pos(tokens):
#     tagged = nltk.pos_tag(tokens)
#     # print(tagged[0:6])
#     return tagged

def get_pos(doc):
    POS_list = [(token.text, token.tag_) for token in doc]
    return POS_list


# check how to do this????
# https://stackoverflow.com/questions/7443330/how-do-i-do-dependency-parsing-in-nltk
# def get_parse_tree():
#     path_to_jar = 'path_to/stanford-parser-full-2014-08-27/stanford-parser.jar'
#     path_to_models_jar = 'path_to/stanford-parser-full-2014-08-27/stanford-parser-3.4.1-models.jar'
#
#     dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)
#
#     result = dependency_parser.raw_parse('I shot an elephant in my sleep')
#     dep = result.next()
#
#     list(dep.triples())


def get_parse_tree(sentences, nlp, nth):
    counter = 0
    for sentence in sentences:
        s = nlp(str(sentence))
        if counter == nth:
            displacy.serve(s, style='dep',page=True)
        counter = counter + 1


def get_entities(tagged):
    entities = nltk.chunk.ne_chunk(tagged)
    # print(entities)
    return entities


def get_synonym(word):
    synonyms = set([word])
    synonym_set = wn.synsets(word)
    for syn in synonym_set:
        for l in syn.lemmas():
            synonyms.add(l.name())
    return synonyms


def get_hyponyms(sense):
    hyponym_set = sense.hyponyms()
    return hyponym_set


def get_hypernyms(sense):
    hypernym_set = sense.hypernyms()
    return hypernym_set


def get_general_hypernyms(sense):
    general_hypernym = sense.root_hypernyms()
    return general_hypernym


def get_meronyms(sense):
    meronym_set = sense.member_meronyms()
    return meronym_set


def get_holonyms(sense):
    holonym_set = sense.member_meronyms()
    return holonym_set


def get_word_set_using_spacy(input):
    input = re.sub('\n', '', input)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(input)
    stop_words = set(stopwords.words('english'))
    tokens = []
    for token in doc:
        if token.lemma_ not in stop_words and not token.is_punct and token.lemma_ != "-PRON-":
            tokens.append(token.lemma_)
    return tokens


def convert(word):
    """ Transform words given from/to POS tags """
    synsets = wn.synsets(word)

    # Word not found
    if not synsets:
        return []

    # Get all lemmas of the word (consider 'a'and 's' equivalent)
    lemmas = [l for s in synsets
              for l in s.lemmas()]

    # Get related forms
    derivationally_related_forms = [(l, l.derivationally_related_forms()) for l in lemmas]
    related_noun_lemmas = [l for drf in derivationally_related_forms
                           for l in drf[1]]

    # Extract the words from the lemmas
    words = [l.name() for l in related_noun_lemmas]
    return words


# get word and synonyms and noun and verb sets
def get_all_word_set_using_spacy(input):
    input = re.sub('\n', '', input)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(input)
    stop_words = set(stopwords.words('english'))
    tokens = []
    for token in doc:
        if token.lemma_ not in stop_words and not token.is_punct and token.lemma_ != "-PRON-":
            tokens.append(token.lemma_)
            for word in get_synonym(token.text):
                tokens.append(word)
                # for w in convert(word):
                #     tokens.append(w)
    return tokens


def get_tf_idf(context):
    tfidf = TfidfVectorizer(tokenizer=get_all_word_set_using_spacy)
    tfs = tfidf.fit_transform(context)
    return tfidf, tfs
    # print(tfs)
    # print(tfs.shape)
    # feature_names = tfidf.get_feature_names()
    # for col in tfs.nonzero()[1]:
    #     print(feature_names[col], ' - ', tfs[0, col])


def get_lsi(context):
    tfidf = TfidfVectorizer(tokenizer=get_all_word_set_using_spacy)
    svd_model = TruncatedSVD(n_components=500, n_iter=7, random_state=42)
    svd_transformer = Pipeline([('tfidf', tfidf), ('svd', svd_model)])
    svd_matrix = svd_transformer.fit_transform(context)
    return svd_transformer, svd_matrix


if __name__ == "__main__":
    path = "WikipediaArticles_All/"
    document_name = "AppleInc.txt"
    f = open(join(path, document_name), "r")
    data = f.read()
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(data)
    sentences = get_sentences_using_spacy(doc)
    for sentence in sentences:
        print(sentence)
    tokens = get_words(doc)
    for token in tokens:
        print(token)
    lemmatized_tokens = get_lemmars(doc)
    for lemmatized_token in lemmatized_tokens:
        print(lemmatized_token)
    POS_list = get_pos(doc)
    for POS in POS_list:
        print(POS)
    get_parse_tree(sentences, nlp, 5)
    word = wn.synset('dog.n.01')
    print(get_hypernyms(word))
    print(get_hyponyms(word))
    print(get_meronyms(word))
    print(get_holonyms(word))