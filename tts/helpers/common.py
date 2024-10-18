import configparser


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
