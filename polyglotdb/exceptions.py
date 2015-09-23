import os
import sys
import traceback

## Base exception classes

class PGError(Exception):
    """
    Base class for all exceptions explicitly raised in corpustools.
    """
    pass

## Context Manager exceptions

class PGContextError(PGError):
    """
    Exception class for when context managers should be used and aren't.
    """
    pass

## Corpus loading exceptions

class PGOSError(PGError):
    """
    Exception class for when files or directories that are expected are missing.
    Wrapper for OSError.
    """
    pass

class CorpusIntegrityError(PGError):
    """
    Exception for when a problem arises while loading in the corpus.
    """
    pass

class DelimiterError(PGError):
    """
    Exception for mismatch between specified delimiter and the actual text
    when loading in CSV files and transcriptions.
    """
    pass

class ILGError(PGError):
    """
    Exception for general issues when loading interlinear gloss files.
    """
    pass

class ILGWordMismatchError(PGError):
    """
    Exception for when interlinear gloss files have different numbers of
    words across lines that should have a one-to-one mapping.

    Parameters
    ----------
    spelling_line : list
        List of words in the spelling line
    transcription_line : list
        List of words in the transcription line
    """
    def __init__(self, mismatching_lines):
        self.main = "There doesn't appear to be equal numbers of words in one or more of the glosses."

        self.information = ''
        self.details = 'The following glosses did not have matching numbers of words:\n\n'
        for ml in mismatching_lines:
            line_inds, line = ml
            self.details += 'From lines {} to {}:\n'.format(*line_inds)
            for k,v in line.items():
                self.details += '({}, {} words) '.format(k,len(v))
                self.details += ' '.join(str(x) for x in v) + '\n'

class ILGLinesMismatchError(PGError):
    """
    Exception for when the number of lines in a interlinear gloss file
    is not a multiple of the number of types of lines.

    Parameters
    ----------
    lines : list
        List of the lines in the interlinear gloss file
    """
    def __init__(self, lines):
        self.main = "There doesn't appear to be equal numbers of orthography and transcription lines"

        self.information = ''
        self.details = 'The following is the contents of the file after initial preprocessing:\n\n'
        for line in lines:
            if isinstance(line,tuple):
                self.details += '{}: {}\n'.format(*line)
            else:
                self.details += str(line) + '\n'

class TextGridTierError(PGError):
    """
    Exception for when a specified tier was not found in a TextGrid.

    Parameters
    ----------
    tier_type : str
        The type of tier looked for (such as spelling or transcription)
    tier_name : str
        The name of the tier specified
    tiers : list
        List of tiers in the TextGrid that were inspected
    """
    def __init__(self, tier_type, tier_name, tiers):
        self.main = 'The {} tier name was not found'.format(tier_type)
        self.information = 'The tier name \'{}\' was not found in any tiers'.format(tier_name)
        self.details = 'The tier name looked for (ignoring case) was \'{}\'.\n'.format(tier_name)
        self.details += 'The following tiers were found:\n\n'
        for t in tiers:
            self.details += '{}\n'.format(t.name)