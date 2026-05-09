import re

def to_pascal_case(text):
    return "".join(word.capitalize() for word in re.findall(r'[a-zA-Z0-9]+', text))

def to_snake_case(text):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
