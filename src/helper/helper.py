from re import sub, findall
import nltk
from string import punctuation
from nltk.corpus import stopwords
from unidecode import unidecode
from notifiers import notify
from os import getenv
from re import compile, fullmatch
from src.settings import LIMITE

nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')


def data_pre_processing_portuguese(corpus):
    # truncate big texts
    corpus = truncate_message(corpus)
    # remove html tags
    corpus = sub(r'<.*?>', ' ', str(corpus))
    # replace non-ascii characters
    corpus = unidecode(corpus)
    # remove non-alphanumeric characters
    corpus = sub(r'[^a-z A-Z 0-9 \s]', ' ', str(corpus))
    # remove numbers
    corpus = sub("\d+", " ", corpus)
    # remove duplicated spaces
    corpus = sub(r' +', ' ', str(corpus))
    # capitalization
    corpus = corpus.lower()
    # tokenization
    corpus = findall(r"\w+(?:'\w+)?|[^\w\s]", corpus)
    # remove punctuation and remove stopwords
    stopwords_ = stopwords.words("portuguese")
    corpus = [t for t in corpus if t not in stopwords_ and t not in punctuation]
    return ' '.join(list(set(corpus)))


def select_with_like(terms, table, column):
    query = "select DISTINCT url from {} where {} like ''".format(table, column)
    for term in terms:
        query += " or description like '%{}%'".format(term)
    return query


def notify_by_email(to, message):
    notify( 'gmail', to=to,
        from_="vagaspramim.notifier@gmail.com",
        message=message,
        username="vagaspramim.notifier",
        password=getenv("APP_PASSWORD")
    )
    return True


def validate_email(email):
    regex = compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    return fullmatch(regex, email) is not None


def truncate_message(message):
    message = (message[:LIMITE]) if len(message) > LIMITE else message
    return message
