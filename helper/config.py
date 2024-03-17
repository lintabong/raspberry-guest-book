import os
import json

if not os.path.exists("config.json"):
    result = {
        "width": 600,
        "height": 400,
        "controll": {
            "width": 600,
            "height": 80
        }
    }
            
    with open("config.json", "w") as outfile:
        json.dump(result, outfile)
        
    outfile.close()


def read():
    with open("config.json", "r") as openfile:
        config = json.load(openfile)

    openfile.close()

    return config

def write(configuration):
    with open("config.json", "w") as outfile:
        json.dump(configuration, outfile)
        
    outfile.close()

    return 1