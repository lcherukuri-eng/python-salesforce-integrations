import json

TOKEN_FILE = "token.json"


def save_token(token_data):
    
    with open(
        TOKEN_FILE,
        "w"
    ) as f:
        json.dump(
            token_data,
            f,
            indent=4
        )    


def load_token():

    try:
        with open(
            TOKEN_FILE,
            "r"
        ) as f:
            return json.load(f)

    except FileNotFoundError:
        return {}