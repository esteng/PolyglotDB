import os

from polyglotdb.structure import Hierarchy

from ..helper import text_to_lines

from .base import BaseParser, DiscourseData

class TranscriptionTextParser(BaseParser):
    '''
    Parser for transcribed text files.

    Parameters
    ----------
    annotation_types: list
        Annotation types of the files to parse
    stop_check : callable, optional
        Function to check whether to halt parsing
    call_back : callable, optional
        Function to output progress messages
    '''
    def __init__(self, annotation_types,
                    stop_check = None, call_back = None):
        self.annotation_types = annotation_types
        self.hierarchy = Hierarchy({'word': None})
        self.make_transcription = False
        self.make_label = True
        self.stop_check = stop_check
        self.call_back = call_back

    def parse_discourse(self, path):
        '''
        Parse a text file for later importing.

        Parameters
        ----------
        path : str
            Path to text file

        Returns
        -------
        :class:`~polyglotdb.io.discoursedata.DiscourseData`
            Parsed data from the file
        '''

        name = os.path.splitext(os.path.split(path)[1])[0]


        for a in self.annotation_types:
            a.reset()

        lines = text_to_lines(path)
        if self.call_back is not None:
            self.call_back('Processing file...')
            self.call_back(0, len(lines))
            cur = 0

        num_annotations = 0
        for line in lines:
            if self.stop_check is not None and self.stop_check():
                return
            if self.call_back is not None:
                cur += 1
                if cur % 20 == 0:
                    self.call_back(cur)
            if not line:
                continue
            a.add(((x, num_annotations + i) for i, x in enumerate(line)))
            num_annotations += len(line)

        pg_annotations = self._parse_annotations()

        data = DiscourseData(name, pg_annotations, self.hierarchy)
        for a in self.annotation_types:
            a.reset()
        return data
