import json
import urllib.request

def check_credentials(session):
    with open("StamboomServer/userlist.json") as file:
        all_names = json.load(file)
        for k,v in all_names.items():
            if session.get(k,...) in v:
                return True
    return False


def check_admin(session):
    return False #zolang login ni volledig veilig is, krijgt NIEMAND admin access
    with open("StamboomServer/userlist.json") as file:
        all_names = json.load(file)
        admin = all_names["UserGoogle"][0]
        if session.get("UserGoogle",...) == admin:
            return True
    return False

def get_google_public_key():
    with urllib.request.urlopen('https://www.googleapis.com/oauth2/v1/certs') as keyfile:
        data = keyfile.read().decode('utf-8')
        for k,v in json.loads(data).items():
            yield v