import pytest
from polyglotdb.corpus import CorpusContext
from polyglotdb.config import CorpusConfig
from polyglotdb.io.enrichment import enrich_lexicon_from_csv
from polyglotdb.io import inspect_textgrid
import time


graph_db = {'graph_host':'localhost', 'graph_port': 7474,
            'graph_user': 'neo4j', 'graph_password': 'test'}

path = '/Users/Elias/Desktop/SCT enrichment and tests/German/GermanEnrichmentData.csv'
config = CorpusConfig('SubGE', **graph_db)


def test_time():
	print("starting")
	t0 = time.clock()
	with CorpusContext(config) as c:
		print("time to open corpus context: {}".format(time.clock()-t0))
		enrich_lexicon_from_csv(c,path)
		print("time elapsed: ")
		print(time.clock()-t0)


		q = c.query_graph(c.word).filter(c.word.label == 'hierüber')
		res = q.all()


		print("time for query: {}".format(time.clock()-t0))
		assert(res[0]['frequency'] == 1.54)