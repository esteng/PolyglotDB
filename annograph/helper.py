import numpy as np

def inspect_discourse(discourse):
    """
    Inspect an initial discourse data structure to extract relevant information

    Parameters
    ----------
    discourse : dict
        Initial discourse data structure

    Returns
    -------
    list
        List of base levels to form nodes the annotation graph
    bool
        Whether the discourse has a 'name' key
    dict
        Whether each annotation type has a 'label' key associated with them
    """
    has_name = 'name' in discourse.keys()

    keys = discourse['data'].keys()
    annotation_types = [x for x in keys]

    base_levels = []
    has_label = {}
    hierarchy = {}
    for k in annotation_types:
        v = discourse['data'][k]
        print(v)
        example = v[0]
        has_label[k] = 'label' in example.keys()
        found = list()
        for a in annotation_types:
            if a in example.keys():
                found.append(a)
        if not found:
            base_levels.append(k)
        else:
            hierarchy[k] = found
    return base_levels, has_name, has_label, hierarchy

def global_align(seqj, seqi, gap=-1, matrix=None, match=1, mismatch=-1):
    """
    >>> global_align('COELANCANTH', 'PELICAN')
    ('COELANCANTH', '-PEL-ICAN--')
    """
    UP, LEFT, DIAG, NONE = range(4)
    max_j = len(seqj)
    max_i = len(seqi)
    if matrix is not None:
        matrix = read_matrix(matrix)

    score   = np.zeros((max_i + 1, max_j + 1), dtype='f')
    pointer = np.zeros((max_i + 1, max_j + 1), dtype='i')
    max_i, max_j

    pointer[0, 0] = NONE
    score[0, 0] = 0.0


    pointer[0, 1:] = LEFT
    pointer[1:, 0] = UP

    score[0, 1:] = gap * np.arange(max_j)
    score[1:, 0] = gap * np.arange(max_i)

    for i in range(1, max_i + 1):
        ci = seqi[i - 1]
        for j in range(1, max_j + 1):
            cj = seqj[j - 1]

            if matrix is None:
                diag_score = score[i - 1, j - 1] + (cj == ci and match or mismatch)
            else:
                diag_score = score[i - 1, j - 1] + matrix[cj][ci]

            up_score   = score[i - 1, j] + gap
            left_score = score[i, j - 1] + gap

            if diag_score >= up_score:
                if diag_score >= left_score:
                    score[i, j] = diag_score
                    pointer[i, j] = DIAG
                else:
                    score[i, j] = left_score
                    pointer[i, j] = LEFT

            else:
                if up_score > left_score:
                    score[i, j ]  = up_score
                    pointer[i, j] = UP
                else:
                    score[i, j]   = left_score
                    pointer[i, j] = LEFT


    align_j = ""
    align_i = ""
    while True:
        p = pointer[i, j]
        if p == NONE: break
        s = score[i, j]
        if p == DIAG:
            align_j += seqj[j - 1]
            align_i += seqi[i - 1]
            i -= 1
            j -= 1
        elif p == LEFT:
            align_j += seqj[j - 1]
            align_i += "-"
            j -= 1
        elif p == UP:
            align_j += "-"
            align_i += seqi[i - 1]
            i -= 1
        else:
            raise Exception('wtf!')

    return align_j[::-1], align_i[::-1]