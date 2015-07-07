__author__ = 'Thorvald'

import random

class LoginHandler:
    def __init__(self):
        self.users = dict(load_users())
    def valid_user(self,name):
        return name.lower() in self.users
    def valid_login(self,name,password):
        for i in self.users.values():
            print(i)
        return self.valid_user(name) and self.users[name.lower()].match_password(password)
    def get_user_list(self):
        return [{"name": k,"email": v.email} for k,v in self.users.items()]
    def check_admin(self,session):
        print(session.get("username","nope"),self.admins())
        return session.get("username","") in self.admins()
    def admins(self):
        return ("thorvalddx94","gerwind96","joran.dox")

def randomstring(lenght=12):
    return("".join(random.choice("azertyuiopqsdfghjklmwxcvbn0123456789") for _ in range(lenght)))

def load_users():
    with open("StamboomServer/users.txt") as fff:
        command = "#test"
        while command != "seed":
            line = fff.readline()
            if line.startswith("#"):
                continue
            command,seed = line.split(" ")

        random.seed(int(seed,16))
        print(int(seed,16))

        for line in fff:
            if line.startswith(("#","seed")):
                continue
            #name,email = line[:-1].split(" ") #[:-1] to ignore newline character
            email = line.strip(" \n\t")
            name = email.split("@")[0]
            yield name.lower(),User(name.lower(),email)


class User:
    def __init__(self,name,email):
        self.name = name
        self.email = email
        self.password = randomstring()
        print(self.name,self.email,self.password)
    def match_password(self,password):
        print(self.password,password)
        return self.password == password
    def __repr__(self):
        return "{}({},{})".format(self.name,self.email,self.password)




