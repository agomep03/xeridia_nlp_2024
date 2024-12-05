from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
import re

stop_words = set(stopwords.words('spanish'))

def lower_text(text):
    return text.lower()

def remove_special_char_and_numbers(text):
    return re.sub("(\\d|\\W)+"," ",text)

def remove_extra_spaces(text):
    return " ".join(word_tokenize(text))

def remove_stopwords(text):
    return " ".join([word for word in str(text).split() if word not in stop_words])

def extract_keywords(text):
    text = lower_text(text)
    text = remove_special_char_and_numbers(text)
    text = remove_extra_spaces(text)
    text = remove_stopwords(text)
    return text