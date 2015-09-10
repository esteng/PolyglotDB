import os
import pytest

from annograph.graph.util import GraphContext
from annograph.graph.models import Anchor, Annotation

def test_basic_query(graph_db):
    with GraphContext(corpus_name = 'untimed', **graph_db) as g:
        q = g.query('word').filter(Annotation.label == 'are')
        assert(all(x['label'] == 'are' for x in q.all()))

def test_query_previous(graph_db):
    with GraphContext(corpus_name = 'untimed', **graph_db) as g:
        q = g.query('word').filter(Annotation.label == 'are')
        q = q.filter(Annotation.previous.label == 'cats')
        print(q.cypher())
        assert(len(list(q.all())) == 1)

def test_query_following(graph_db):
    with GraphContext(corpus_name = 'untimed', **graph_db) as g:
        q = g.query('word').filter(Annotation.label == 'are')
        q = q.filter(Annotation.following.label == 'too')
        print(q.cypher())
        print(list(q.all()))
        assert(len(list(q.all())) == 1)

def test_query_time(graph_db):
    with GraphContext(corpus_name = 'timed', **graph_db) as g:
        q = g.query('word').filter(Annotation.label == 'are')
        q = q.filter(Annotation.begin > 2)
        print(q.cypher())
        assert(len(list(q.all())) == 1)
    with GraphContext(corpus_name = 'timed', **graph_db) as g:
        q = g.query('word').filter(Annotation.label == 'are')
        q = q.filter(Annotation.begin < 2)
        print(q.cypher())
        assert(len(list(q.all())) == 1)

def test_query_contains(graph_db):
    with GraphContext(corpus_name = 'untimed', **graph_db) as g:
        q = g.query('word').filter_contains('phone', Annotation.label == 'aa')
        print(q.cypher())
        print(list(q.all()))
        assert(len(list(q.all())) == 3)

def test_query_contained_by(graph_db):
    with GraphContext(corpus_name = 'untimed', **graph_db) as g:
        q = g.query('phone').filter(Annotation.label == 'aa')
        q = q.filter_contained_by('word',Annotation.label == 'dogs')
        assert(len(list(q.all())) == 1)

def test_query_left_aligned_line(graph_db):
    with GraphContext(corpus_name = 'untimed', **graph_db) as g:
        q = g.query('phone').filter(Annotation.label == 'k')
        q = q.filter_left_aligned('line')
        assert(len(list(q.all())) == 1)

def test_query_phone_in_line_initial_word(graph_db):
    with GraphContext(corpus_name = 'untimed', **graph_db) as g:
        word_q = g.query('word').filter_left_aligned('line')
        assert(len(list(word_q.all())) == 3)
        q = g.query('phone').filter(Annotation.label == 'aa')
        q = q.filter_contained_by('word', Annotation.id.in_(word_q))
        assert(len(list(q.all())) == 1)

def test_query_coda_phone(graph_db):
    with GraphContext(corpus_name = 'syllable_morpheme_srur', **graph_db) as g:
        q = g.query('sr').filter(Annotation.label == 'k')
        q = q.filter_right_aligned('syllable')
        assert(len(list(q.all())) == 1)

@pytest.mark.xfail
def test_query_frequency(graph_db):
    with GraphContext(corpus_name = 'untimed', **graph_db) as g:
        q = g.query('word').filter(Annotation.frequency > 1)
    assert(False)

