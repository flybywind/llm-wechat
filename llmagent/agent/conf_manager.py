import os
import json


class ConfigManager:
    """
    langchain相关的配置
    """
    def __init__(self):
        self.config_file = "app_config.json"
        self.config = self.load_config()
        self.command_prefix = ":"

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def get_config(self, key, default=None):
        return self.config.get(key, default)

    def set_config(self, key, value):
        self.config[key] = value
        self.save_config()
