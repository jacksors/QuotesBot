"""Import Sensitive Information"""

import json
import os
from pathlib import Path

directory = os.path.dirname(__file__)

if Path("config.json").exists():
    with open("config.json") as config_file:
        config: dict = json.load(config_file)
    try:
        BOT_TOKEN = config["bot_token"]
        MONGO_URL = config["mongo_url"]
        MONGO_DB = config["mongo_database"]
        QUOTES_COLLECTION = config["quotes_collection"]
        SERVERS_COLLECTION = config["servers_collection"]
        CONFIG_GUILD = int(config["config_guild"])
    except KeyError:
        print("Missing item in settings.json")
else:
    print("Missing config.json file")
