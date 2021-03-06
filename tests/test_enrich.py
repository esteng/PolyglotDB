
import pytest
import os

from polyglotdb import CorpusContext

from polyglotdb.io.enrichment import (enrich_lexicon_from_csv, enrich_features_from_csv,
                                    enrich_discourses_from_csv, enrich_speakers_from_csv)

def test_lexicon_enrichment(timed_config, csv_test_dir):
    path = os.path.join(csv_test_dir, 'timed_enrichment.txt')
    with CorpusContext(timed_config) as c:
        enrich_lexicon_from_csv(c, path)

        q = c.query_graph(c.word).filter(c.word.neighborhood_density < 10)

        q = q.columns(c.word.label.column_name('label'))

        res = q.all()

        assert(all(x['label'] == 'guess' for x in res))

        q = c.query_graph(c.word).filter(c.word.label == 'i')

        res = q.all()

        assert(res[0]['frequency'] == 150)
        assert(res[0]['part_of_speech'] == 'PRP')
        assert(res[0]['neighborhood_density'] == 17)

        q = c.query_graph(c.word).filter(c.word.label == 'cute')

        res = q.all()

        assert(res[0]['frequency'] is None)
        assert(res[0]['part_of_speech'] == 'JJ')
        assert(res[0]['neighborhood_density'] == 14)

        levels = c.lexicon.get_property_levels('part_of_speech')
        assert(set(levels) == set(['NN','VB','JJ','IN','PRP']))

def test_feature_enrichment(timed_config, csv_test_dir):
    path = os.path.join(csv_test_dir, 'timed_features.txt')
    with CorpusContext(timed_config) as c:
        enrich_features_from_csv(c, path)

        q = c.query_graph(c.phone).filter(c.phone.vowel_height == 'lowhigh')

        q = q.columns(c.phone.label.column_name('label'))

        res = q.all()

        assert(all(x['label'] == 'ay' for x in res))

        q = c.query_graph(c.phone).filter(c.phone.place_of_articulation == 'velar')

        q = q.columns(c.phone.label.column_name('label'))

        res = q.all()

        assert(all(x['label'] in ['k','g'] for x in res))

def test_speaker_enrichment(fave_corpus_config, csv_test_dir):
    path = os.path.join(csv_test_dir, 'fave_speaker_info.txt')
    with CorpusContext(fave_corpus_config) as c:
        enrich_speakers_from_csv(c, path)

        q = c.query_graph(c.phone).filter(c.phone.speaker.is_interviewer == True)

        q = q.columns(c.phone.label.column_name('label'),
                    c.phone.speaker.name.column_name('speaker'))

        res = q.all()

        assert(all(x['speaker'] == 'Interviewer' for x in res))

def test_discourse_enrichment(fave_corpus_config, csv_test_dir):
    path = os.path.join(csv_test_dir, 'fave_discourse_info.txt')
    with CorpusContext(fave_corpus_config) as c:
        enrich_discourses_from_csv(c, path)

        q = c.query_graph(c.phone).filter(c.phone.discourse.noise_level == 'high')

        q = q.columns(c.phone.label.column_name('label'),
                    c.phone.discourse.name.column_name('discourse'))

        res = q.all()

        assert(all(x['discourse'] == 'fave_test' for x in res))
