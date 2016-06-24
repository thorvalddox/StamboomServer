import json

def check_credentials(user_google=None,user_facebook=None):
    with open("userlist.json") as file:
        all_names = json.load(file)
        return user_google in all_names["Google"] or user_facebook in all_names["Facebook"]