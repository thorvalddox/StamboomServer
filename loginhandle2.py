import json

def check_credentials(session):
    with open("StamboomServer/userlist.json") as file:
        all_names = json.load(file)
        for k,v in all_names.items():
            if session.get(k,...) in v:
                return True
    return


def check_admin(session):
    with open("StamboomServer/userlist.json") as file:
        all_names = json.load(file)
        admin = all_names["UserGoogle"][0]
        if session.get("UserGoogle",...) == admin:
            return True
    return False