
from ..io.importer import (speaker_data_to_csvs, import_speaker_csvs,
                            discourse_data_to_csvs, import_discourse_csvs)

class SpokenContext(object):
    def enrich_speakers(self, speaker_data, type_data = None):
        """
        Add properties about speakers to the corpus, allowing them to
        be queryable.

        Parameters
        ----------
        speaker_data : dict
            the data about the speakers to add
        type_data : dict
            Specifies the type of the data to be added, defaults to None

        """
        if type_data is None:
            type_data = {k: type(v) for k,v in next(iter(speaker_data.values())).items()}

        speakers = set(self.speakers)
        speaker_data = {k: v for k,v in speaker_data.items() if k in speakers}
        self.census.add_speaker_properties(speaker_data, type_data)
        speaker_data_to_csvs(self, speaker_data)
        import_speaker_csvs(self, type_data)
        self.hierarchy.add_speaker_properties(self, type_data.items())
        self.encode_hierarchy()

    def reset_speakers(self):
        pass

    def enrich_discourses(self, discourse_data, type_data = None):
        """
        Add properties about discourses to the corpus, allowing them to
        be queryable.

        Parameters
        ----------
        discourse_data : dict
            the data about the discourse to add
        type_data : dict
            Specifies the type of the data to be added, defaults to None

        """
        if type_data is None:
            type_data = {k: type(v) for k,v in next(iter(discourse_data.values())).items()}

        discourses = set(self.discourses)
        discourse_data = {k: v for k,v in discourse_data.items() if k in discourses}
        self.census.add_discourse_properties(discourse_data, type_data)
        discourse_data_to_csvs(self, discourse_data)
        import_discourse_csvs(self, type_data)
        self.hierarchy.add_discourse_properties(self, type_data.items())
        self.encode_hierarchy()

    def reset_discourses(self):
        pass
