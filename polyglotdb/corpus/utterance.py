

from .base import BaseContext

from ..io.importer import time_data_to_csvs, import_utterance_csv
from ..graph.func import Max, Min
from ..graph.query import DiscourseGraphQuery

from ..exceptions import GraphQueryError

class UtteranceCorpus(BaseContext):
    def reset_utterances(self):
        """
        Remove all utterance annotations.
        """
        try:
            q = DiscourseGraphQuery(self, self.utterance)
            q.delete()
            self.hierarchy.annotation_types.remove('utterance')
            del self.hierarchy['utterance']
            self.encode_hierarchy()
            self.refresh_hierarchy()
        except GraphQueryError:
            pass

    def encode_utterances(self, min_pause_length = 0.5, min_utterance_length = 0,
                            call_back = None, stop_check = None):
        """
        Encode utterance annotations based on minimum pause length and minimum
        utterance length.  See `get_pauses` for more information about
        the algorithm.

        Once this function is run, utterances will be queryable like other
        annotation types.

        Parameters
        ----------
        min_pause_length : float, defaults to 0.5
            Time in seconds that is the minimum duration of a pause to count
            as an utterance boundary

        min_utterance_length : float, defaults to 0.0
            Time in seconds that is the minimum duration of a stretch of
            speech to count as an utterance
        """
        self.reset_utterances()

        self.hierarchy[self.word_name] = 'utterance'
        self.hierarchy['utterance'] = None
        self.encode_hierarchy()
        self.refresh_hierarchy()

        discourses = self.discourses
        if call_back is not None:
            call_back(0, len(discourses))
        for i, d in enumerate(discourses):
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                call_back(i)
                call_back('Encoding utterances for discourse {} of {} ({})...'.format(i, len(discourses), d))
            utterances = self.get_utterance_ids(d, min_pause_length, min_utterance_length)
            time_data_to_csvs('utterance', self.config.temporary_directory('csv'), d, utterances)
            import_utterance_csv(self, d)

    def get_utterance_ids(self, discourse,
                min_pause_length = 0.5, min_utterance_length = 0):
        """
        Algorithm to find utterance boundaries in a discourse.

        Pauses with duration less than the minimum will
        not count as utterance boundaries.  Utterances that are shorter
        than the minimum utterance length (such as 'okay' surrounded by
        silence) will be merged with the closest utterance.

        Parameters
        ----------
        discourse : str
            String identifier for a discourse

        min_pause_length : float, defaults to 0.5
            Time in seconds that is the minimum duration of a pause to count
            as an utterance boundary

        min_utterance_length : float, defaults to 0.0
            Time in seconds that is the minimum duration of a stretch of
            speech to count as an utterance
        """
        word_type = self.word_name
        statement = '''MATCH p = (prev_node_word:{word_type}:speech:{corpus})-[:precedes_pause*1..]->(foll_node_word:{word_type}:speech:{corpus}),
        (prev_node_word)-[:spoken_in]->(d:Discourse:{corpus})
        WHERE d.name = {{discourse}}
WITH nodes(p)[1..-1] as ns,foll_node_word, prev_node_word
WHERE foll_node_word.begin - prev_node_word.end >= {{node_pause_duration}}
AND NONE (x in ns where x:speech)
WITH foll_node_word, prev_node_word
RETURN prev_node_word.end AS begin, prev_node_word.id AS begin_id, foll_node_word.begin AS end, foll_node_word.id AS end_id, foll_node_word.begin - prev_node_word.end AS duration
ORDER BY begin'''.format(corpus = self.corpus_name, word_type = word_type)
        results = list(self.execute_cypher(statement, node_pause_duration = min_pause_length, discourse = discourse))

        collapsed_results = []
        for i, r in enumerate(results):
            if len(collapsed_results) == 0:
                collapsed_results.append(r)
                continue
            if r['begin'] == collapsed_results[-1]['end']:
                collapsed_results[-1]['end'] = r['end']
            else:
                collapsed_results.append(r)
        utterances = []
        word_ids = []
        word = getattr(self, word_type)
        statement = '''MATCH (w:{word_type}:{corpus}:speech)-[:spoken_in]->(d:Discourse:{corpus})
        where d.name = {{discourse}}
        with max(w.end) as max_end, min(w.begin) as min_begin, collect(w) as words
        with filter(x in words where x.begin = min_begin or x.end = max_end) as c UNWIND c as w
        return w.id as id, w.begin as begin, w.end as end
        order by w.begin
        '''.format(corpus = self.corpus_name, word_type = word_type)
        end_words = list(self.execute_cypher(statement, discourse = discourse))

        if len(results) < 2:
            begin = end_words[0]['begin']
            begin_id = end_words[0]['id']
            if len(results) == 0:
                return [(begin_id, end_words[1]['id'])]
            if results[0]['begin'] == 0:
                return [(results[0]['end_id'], end_words[1]['id'])]
            if results[0]['end'] == end_words[1]['end']:
                return [(begin_id, end_words[1]['end_id'])]

        if results[0]['begin'] != 0:
            current = 0
            current_id = end_words[0]['id']
        else:
            current = None
            current_id = None
        min_begin = 1000
        max_begin = 0
        prev = None
        for i, r in enumerate(collapsed_results):
            if current is not None:
                if current < min_begin:
                    min_begin = current
                if r['begin'] - current > min_utterance_length:
                    utterances.append((current_id, r['begin_id']))
                elif i == len(results) - 1:
                    utterances[-1] = (utterances[-1][0], r['begin_id'])
                elif len(utterances) != 0:
                    dist_to_prev = current - utterances[-1][1]
                    dist_to_foll = r['end'] - r['begin']
                    if dist_to_prev <= dist_to_foll:
                        utterances[-1] = (utterances[-1][0], r['begin_id'])
            prev = current
            current = r['end']
            current_id = r['end_id']
        if current < end_words[1]['end']:
            if end_words[1]['end'] - current > min_utterance_length:
                utterances.append((current_id, end_words[1]['id']))
            else:
                utterances[-1] = (utterances[-1][0], end_words[1]['id'])
        return utterances

    def get_utterances(self, discourse,
                min_pause_length = 0.5, min_utterance_length = 0):
        """
        Algorithm to find utterance boundaries in a discourse.

        Pauses with duration less than the minimum will
        not count as utterance boundaries.  Utterances that are shorter
        than the minimum utterance length (such as 'okay' surrounded by
        silence) will be merged with the closest utterance.

        Parameters
        ----------
        discourse : str
            String identifier for a discourse

        min_pause_length : float, defaults to 0.5
            Time in seconds that is the minimum duration of a pause to count
            as an utterance boundary

        min_utterance_length : float, defaults to 0.0
            Time in seconds that is the minimum duration of a stretch of
            speech to count as an utterance
        """
        word_type = self.word_name
        statement = '''MATCH p = (prev_node_word:{word_type}:speech:{corpus})-[:precedes_pause*1..]->(foll_node_word:{word_type}:speech:{corpus}),
        (prev_node_word)-[:spoken_in]->(d:Discourse:{corpus})
        WHERE d.name = {{discourse}}
WITH nodes(p)[1..-1] as ns,foll_node_word, prev_node_word
WHERE foll_node_word.begin - prev_node_word.end >= {{node_pause_duration}}
AND NONE (x in ns where x:speech)
WITH foll_node_word, prev_node_word
RETURN prev_node_word.end AS begin, foll_node_word.begin AS end, foll_node_word.begin - prev_node_word.end AS duration
ORDER BY begin'''.format(corpus = self.corpus_name, word_type = word_type)
        results = list(self.execute_cypher(statement, node_pause_duration = min_pause_length, discourse = discourse))

        collapsed_results = []
        for i, r in enumerate(results):
            if len(collapsed_results) == 0:
                collapsed_results.append(r)
                continue
            if r['begin'] == collapsed_results[-1]['end']:
                collapsed_results[-1]['end'] = r['end']
            else:
                collapsed_results.append(r)
        utterances = []
        word = getattr(self, word_type)
        q = self.query_graph(word).filter(word.discourse.name == discourse)
        times = q.aggregate(Min(word.begin), Max(word.end))

        if len(results) < 2:
            begin = times['min_begin']
            if len(results) == 0:
                return [(begin, times['max_end'])]
            if results[0]['begin'] == 0:
                return [(results[0]['end'], times['max_end'])]
            if results[0]['end'] == times['max_end']:
                return [(begin, results[0]['end'])]

        if results[0]['begin'] != 0:
            current = 0
        else:
            current = None
        for i, r in enumerate(collapsed_results):
            if current is not None:
                if r['begin'] - current > min_utterance_length:
                    utterances.append((current, r['begin']))
                elif i == len(results) - 1:
                    utterances[-1] = (utterances[-1][0], r['begin'])
                elif len(utterances) != 0:
                    dist_to_prev = current - utterances[-1][1]
                    dist_to_foll = r['end'] - r['begin']
                    if dist_to_prev <= dist_to_foll:
                        utterances[-1] = (utterances[-1][0], r['begin'])
            current = r['end']
        if current < times['max_end']:
            if times['max_end'] - current > min_utterance_length:
                utterances.append((current, times['max_end']))
            else:
                utterances[-1] = (utterances[-1][0], times['max_end'])
        if utterances[-1][1] > times['max_end']:
            utterances[-1] = (utterances[-1][0], times['max_end'])
        if utterances[0][0] < times['min_begin']:
            utterances[0] = (times['min_begin'], utterances[0][1])
        return utterances

    def encode_utterance_position(self, call_back = None, stop_check = None):
        """ Encodes position_in_utterance for a word """
        w_type = self.word_name
        if self.config.query_behavior == 'speaker':
            statement = '''MATCH (node_utterance:utterance:speech:{corpus_name})-[:spoken_by]->(speaker:Speaker:{corpus_name}),
            (node_word_in_node_utterance:{w_type}:{corpus_name})-[:contained_by]->(node_utterance)
            WHERE speaker.name = {{split_name}}
            WITH node_utterance, node_word_in_node_utterance
            ORDER BY node_word_in_node_utterance.begin
            WITH node_utterance,collect(node_word_in_node_utterance) as nodes
            WITH node_utterance,nodes,
            range(0, size(nodes)) as pos
            UNWIND pos as p
            WITH node_utterance, p, nodes[p] as n
            SET n.position_in_utterance = p + 1
            '''.format(w_type = w_type, corpus_name = self.corpus_name)
            split_names = self.speakers
        elif self.config.query_behavior == 'discourse':
            statement = '''MATCH (node_utterance:utterance:speech:{corpus_name})-[:spoken_in]->(discourse:Discourse:{corpus_name}),
            (node_word_in_node_utterance:{w_type}:{corpus_name})-[:contained_by]->(node_utterance)
            WHERE discourse.name = {{split_name}}
            WITH node_utterance, node_word_in_node_utterance
            ORDER BY node_word_in_node_utterance.begin
            WITH node_utterance, collect(node_word_in_node_utterance) as nodes
            WITH node_utterance, nodes,
            range(0, size(nodes)) as pos
            UNWIND pos as p
            WITH node_utterance, p, nodes[p] as n
            SET n.position_in_utterance = p + 1
            '''.format(w_type = w_type, corpus_name = self.corpus_name)
        else:
            statement = '''MATCH (node_utterance:utterance:speech:{corpus_name}),
            (node_word_in_node_utterance:{w_type}:{corpus_name})-[:contained_by]->(node_utterance)
            WITH node_utterance, node_word_in_node_utterance
            ORDER BY node_word_in_node_utterance.begin
            WITH node_utterance, collect(node_word_in_node_utterance) as nodes
            WITH node_utterance, nodes,
            range(0, size(nodes)) as pos
            UNWIND pos as p
            WITH node_utterance, p, nodes[p] as n
            SET n.position_in_utterance = p + 1
            '''.format(w_type = w_type, corpus_name = self.corpus_name)


        if split_names is None:
            if call_back is not None:
                call_back('Encoding utterance position...')
                call_back(0,0)
            self.execute_cypher(statement)
        else:
            if call_back is not None:
                call_back(0,len(split_names))
            for i, s in enumerate(split_names):
                if stop_check is not None and stop_check():
                    return
                if call_back is not None:
                    call_back(i)
                    call_back('Encoding utterance positions for {} {} of {} ({})...'.format(self.config.query_behavior,
                                                                i, len(split_names), s))
                self.execute_cypher(statement, split_name = s)
        self.hierarchy.add_token_properties(self, w_type, [('position_in_utterance', float)])
        self.save_variables()

    def reset_utterance_position(self):
        """resets position_in_utterance"""
        self.reset_property(self.word_name, 'position_in_utterance')

    def encode_speech_rate(self, subset_label, call_back = None, stop_check = None):
        """ 
        Encodes speech rate

        Parameters
        ----------
        subset_label : str
            the name of the subset to encode

        """
        self.encode_rate('utterance', self.phone_name, 'speech_rate', subset = subset_label)

    def reset_speech_rate(self):
        """ resets speech_rate """
        self.reset_property('utterance', 'speech_rate')
