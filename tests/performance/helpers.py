import itertools
import json


class JSONFileIteratorSentimentAnalysisPayload:
    """Iterator for JSON file with positive and negative messages."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self._file = open(self.filepath, "r")
        self.data = json.load(self._file)
        self._file.close()

        self.positive_iterator = itertools.cycle(self.data["positive_messages"])
        self.negative_iterator = itertools.cycle(self.data["negative_messages"])

    def get_next_positive(self):
        """Retrieve the next positive message in a cycle."""
        return next(self.positive_iterator)

    def get_next_negative(self):
        """Retrieve the next negative message in a cycle."""
        return next(self.negative_iterator)
