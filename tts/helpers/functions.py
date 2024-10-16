import configparser


def determine_sentiment(transformers_scores: dict, vader_scores: dict):
    """Determine if the text is genuinely negative based on both sentiment models.

    :param transformers_scores: (dict) The scores from the transformer model.
    :param vader_scores: (dict) The scores from the VADER model.
    :returns: (str) Final sentiment classification.
    """
    transformer_score = transformers_scores["score"]
    vader_score = vader_scores["compound"]

    if transformer_score < 0.5 and vader_score < 0:
        return "definitely negative"
    elif transformer_score >= 0.5 and vader_score < 0:
        return "possibly negative"
    elif transformer_score == 0.5 and vader_score == 0:
        return "neutral"
    elif transformer_score >= 0.5 or vader_score >= 0:
        return "definitely not negative"
    return "possibly not negative"



class Config:
    def __init__(self, file_path: str = "config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(file_path)

    def __getattr__(self, section):
        """Get a section as an attribute."""
        if section in self.config:
            return ConfigSection(self.config[section])
        raise AttributeError(f"Section '{section}' not found in configuration.")


class ConfigSection:
    def __init__(self, section):
        self.section = section

    def __getattr__(self, key):
        """Get a key as an attribute."""
        if key in self.section:
            return self.section[key]
        raise AttributeError(f"Key '{key}' not found in section.")
