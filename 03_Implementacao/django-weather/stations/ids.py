import re
import unicodedata
from .models import Station

def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)

def text_to_id(text):
    """
    Convert input text to id.
    """
    text = strip_accents(text.lower())
    text = re.sub('[ ]+', '', text)
    text = re.sub('[^a-zA-Z-]', '', text)
    return text

def name_to_topic(name, previous=None):
    name = text_to_id(name)
    prefix = name[:3].upper()
    if prefix == previous[:3]:
        return previous
    topics = list(Station.objects.filter(topic__contains=prefix).values_list('topic', flat=True))
    if topics:
        indexes = [ int(item.replace(prefix, "")) for item in topics ]
        next_idx = sorted(indexes, reverse=True)[0] + 1
    else:
        next_idx = 1
    return prefix + str(next_idx)