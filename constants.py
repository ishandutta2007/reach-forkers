import os
import configparser
config = configparser.ConfigParser()
config.read("config.txt")

GOOG_ID = 'ishandutta2007'
GOOG_PASS = config.get("configuration", "goog_ishandutta2007_password")

GITHUB_ID = 'ishandutta2007'
GITHUB_PASS = config.get("configuration", "github_ishandutta2007_password")
