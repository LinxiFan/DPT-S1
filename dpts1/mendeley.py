# Group tags into Box Sync folders
TAG_FOLDER = [
    ('Algopolis', []),
    ('App', []),
    ('Survey', ['Tutorial']),
    ('Meta', []),
    ('Evolution', []),
    ('Extracurricular', ['Philosophy', 'Entertain']),
    ('Misc', ['Communication', 'Interdiscipline', 'Medical', 'Neuroscience']),
    ('Engineering', ['Dataset']),
    ('Transfer', ['Curriculum', 'One-shot']),
    ('Vision', ['ObjRecog', 'Video', 'Visualize']),
    ('NLP', ['LangModel', 'Semantic', 'QA', 'Speech', 'Translation']),
    ('GAN', []),
    ('Mathy', ['Theory', 'Variational', 'Optimization', 'ClassicML']),
    ('Turing', []),
    ('RL', ['HRL', 'Imitation', 'Robotics']),
    # other non-tags
    ('Books', []),
    ('Vault', []),
]

def _get_ordering():
    ordering = []
    for sup, subs in TAG_FOLDER:
        ordering.extend(subs)
        ordering.append(sup)
    return ordering

_ORDERING = _get_ordering()

def _order_idx(tag):
    tag = tag.lower()
    ordering = list(map(str.lower, _ORDERING))
    if tag not in ordering:
        return 10000
    else:
        return ordering.index(tag)

def tag_path(tag):
    """
    If tag is a list, return the path with the most priority according to
    TAG_FOLDER ordering
    Returns: `NLP/LangModel`
    """
    if not isinstance(tag, list):
        tag = [tag]
    if len(tag) == 0:
        return ''
    tag = sorted(tag, key=_order_idx)[0].lower()
    for sup, _ in TAG_FOLDER:
        if sup.lower() == tag:
            return sup
    for sup, subs in TAG_FOLDER:
        for sub in subs:
            if sub.lower() == tag:
                return '{}/{}'.format(sup, sub)
    return ''


if __name__ == '__main__':
    print(tag_path(['Gan', 'nlp']))
    print(tag_path(['visualize', 'nlp']))
