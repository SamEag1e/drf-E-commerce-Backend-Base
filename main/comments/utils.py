import re

from .models import RestrictedWord


# ---------------------------------------------------------------------
def censor_content(content):
    restricted_words = RestrictedWord.objects.values_list("word", flat=True)
    for word in restricted_words:
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        content = pattern.sub(word[0] + "*" * (len(word) - 1), content)
    return content
