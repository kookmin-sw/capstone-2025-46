import yaml

import utils

settings = None


def init_settings():
    global settings
    settings = load_settings_yaml("config.yaml")

    folder_list = ["requests", "done"]
    for folder in folder_list:
        from pathlib import Path

        if not Path(folder).exists():
            Path(folder).mkdir()


def load_settings_yaml(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


utils.init_settings()
print(1)