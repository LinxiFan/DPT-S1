# Group tags into Box Sync folders
TAG_FOLDER = [
    ('Algopolis', []),
    ('App', []),
    ('Survey', ['Tutorial']),
    ('Transfer', ['Curriculum',
                  'One-shot']),
    ('Meta', []),
    ('Evolution', []),
    ('Extracurricular', ['Entertain',
                         'Symposium']),
    ('Misc', ['Communication',
              'Interdiscipline',
              'Medical',
              'Safety',
              'Neuroscience',
              'Legacy']),
    ('Engineering', ['Dataset']),
    ('Vision', ['ObjRecog',
                'Segmentation',
                'Video',
                'Visualize']),
    ('NLP', ['LangModel',
             'Semantic',
             'QA',
             'Speech',
             'Translation']),
    ('GAN', []),
    ('Foundation', ['Theory',
                    'Variational',
                    'Optimization',
                    'ClassicML']),
    ('Turing', []),
    ('RL', ['RL-App',
            'RL-Exploration',
            'RL-HRL',
            'RL-Imitation',
            'RL-OffPolicy',
            'Robotics',
            'RL-PG']),
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


def _order_idx_autocorrect(tag):
    tag = tag.lower()
    ordering = list(map(str.lower, _ORDERING))
    if tag in ordering:
        return ordering.index(tag)
    # see if tag is a prefix
    for i, stdtag in enumerate(ordering):
        if stdtag.startswith(tag):
            return i
    # see if tag is contained
    for i, stdtag in enumerate(ordering):
        if tag in stdtag:
            return i
    import Levenshtein
    dists = [Levenshtein.distance(tag, stdtag) for stdtag in ordering]
    return dists.index(min(dists))

def _autocorrect_tag(tag):
    return _ORDERING[_order_idx_autocorrect(tag)]

def tag_path(tag, *, autocorrect=False):
    """
    If tag is a list, return the path with the most priority according to
    TAG_FOLDER ordering
    Returns: `NLP/LangModel`
    """
    if not isinstance(tag, list):
        tag = [tag]
    if len(tag) == 0:
        return ''
    if autocorrect:
        tag = sorted(tag, key=_order_idx_autocorrect)[0]
        tag = _autocorrect_tag(tag).lower()
    else:
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
    print(tag_path(['hrl', 'imita', 'explora'], autocorrect=True))
    print(tag_path(['intredicipline'], autocorrect=True))
    print(tag_path(['curiculum'], autocorrect=True))
    print(tag_path(['extracu', 'classic'], autocorrect=True))
