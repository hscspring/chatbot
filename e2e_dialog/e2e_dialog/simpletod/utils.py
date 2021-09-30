import re


def insertSpace(token, text):
    sidx = 0
    while True:
        sidx = text.find(token, sidx)
        if sidx == -1:
            break
        if sidx + 1 < len(text) and re.match('[0-9]', text[sidx - 1]) and \
                re.match('[0-9]', text[sidx + 1]):
            sidx += 1
            continue
        if text[sidx - 1] != ' ':
            text = text[:sidx] + ' ' + text[sidx:]
            sidx += 1
        if sidx + len(token) < len(text) and text[sidx + len(token)] != ' ':
            text = text[:sidx + 1] + ' ' + text[sidx + 1:]
        sidx += 1
    return text


def normalize_for_sql(text):
    # lower case every word
    text = text.lower()

    # replace white spaces in front and end
    text = re.sub(r'^\s*|\s*$', '', text)

    # normalize phone number
    ms = re.findall('\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4,5})', text)
    if ms:
        sidx = 0
        for m in ms:
            sidx = text.find(m[0], sidx)
            if text[sidx - 1] == '(':
                sidx -= 1
            eidx = text.find(m[-1], sidx) + len(m[-1])
            text = text.replace(text[sidx:eidx], ''.join(m))

    # normalize postcode
    ms = re.findall('([a-z]{1}[\. ]?[a-z]{1}[\. ]?\d{1,2}[, ]+\d{1}[\. ]?[a-z]{1}[\. ]?[a-z]{1}|[a-z]{2}\d{2}[a-z]{2})',
                    text)
    if ms:
        sidx = 0
        for m in ms:
            sidx = text.find(m, sidx)
            eidx = sidx + len(m)
            text = text[:sidx] + re.sub('[,\. ]', '', m) + text[eidx:]

    # weird unicode bug
    text = re.sub(u"(\u2018|\u2019)", "'", text)

    # replace st.
    text = text.replace(';', ',')
    text = re.sub('$\/', '', text)
    text = text.replace('/', ' and ')

    # replace other special characters
    text = re.sub('[\":\<>@\(\)]', '', text)

    # insert white space before and after tokens:
    for token in ['?', '.', ',', '!']:
        text = insertSpace(token, text)

    # insert white space for 's
    text = insertSpace('\'s', text)

    # remove multiple spaces
    text = re.sub(' +', ' ', text)

    # concatenate numbers
    tmp = text
    tokens = text.split()
    i = 1
    while i < len(tokens):
        if re.match(u'^\d+$', tokens[i]) and \
                re.match(u'\d+$', tokens[i - 1]):
            tokens[i - 1] += tokens[i]
            del tokens[i]
        else:
            i += 1
    text = ' '.join(tokens)

    text = text.replace('marys', r"mary''s")
    text = text.replace('restaurant 17', 'restaurant one seven')
    text = text.replace('christ college', r"christ''s college")
    text = text.replace('city centre north bed and breakfast', 'city centre north b and b')
    text = text.replace('cambridge belfry', 'the cambridge belfry')
    text = text.replace('cow pizza kitchen and bar', 'the cow pizza kitchen and bar')
    text = text.replace("peoples portraits exhibition at girton college", r"people''s portraits exhibition at girton college")
    text = text.replace('golden curry', 'the golden curry')
    text = text.replace("shiraz", "shiraz restaurant")
    text = text.replace("queens college", r"queens'' college")
    text = text.replace('alpha milton guest house', 'alpha-milton guest house')
    text = text.replace('cherry hinton village centre', 'the cherry hinton village centre')
    text = text.replace('multiple sports', 'mutliple sports')
    text = text.replace('cambridge chop house', 'the cambridge chop house')
    text = text.replace("cambridge punter", "the cambridge punter")
    text = text.replace("rosas bed and breakfast", r"rosa''s bed and breakfast")
    text = text.replace('el shaddia guesthouse', "el shaddai")
    text = text.replace('swimming pool', 'swimmingpool')
    text = text.replace('night club', 'nightclub')
    text = text.replace("nirala", "the nirala")
    text = text.replace("kings college", r"king''s college")
    text = text.replace('copper kettle', 'the copper kettle')
    text = text.replace('cherry hinton village centre', 'the cherry hinton village centre')
    text = text.replace("kettles yard", r"kettle''s yard")
    text = text.replace("good luck", "the good luck chinese food takeaway")
    text = text.replace("lensfield hotel", "the lensfield hotel")
    text = text.replace("restaurant 2 two", "restaurant two two")
    text = text.replace("churchills college", "churchill college")
    text = text.replace("fitzwilliam museum", "the fitzwilliam museum")
    text = text.replace('cafe uno', 'caffe uno')
    text = text.replace('sheeps green and lammas land park fen causeway' , "sheep's green and lammas land park fen causeway")
    text = text.replace("cambridge contemporary art museum", "cambridge contemporary art")
    text = text.replace('graffton hotel restaurant', "grafton hotel restaurant")
    text = text.replace("saint catharine s college", r"saint catharine''s college")
    text = text.replace('meze bar', 'meze bar restaurant')

    return text