import re
with open("C:/Users/User/Desktop/texts.txt", 'r', encoding='utf-8') as texts:
    texts = texts.read()
    split_regex = re.compile(r'[.|!|?|…]')
    sentences = filter(lambda t: t, [t.strip() for t in split_regex.split(texts)])
    texts = []
    for temp in sentences:
        texts.append(temp)
    s_texts = sorted(texts, key=len)
    for s in s_texts:
        print(s)
