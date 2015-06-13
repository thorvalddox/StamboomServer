__author__ = 'Thorvald'

import random

class LoginHandler:
    def __init__(self):
        self.users = dict(load_users())
    def valid_user(self,name):
        return name.lower() in self.users
    def valid_login(self,name,password):
        print(self.users)
        return self.valid_user(name) and self.users[name.lower()].match_password(password)

def randomstring(lenght=12):
    return("".join(random.choice("azertyuiopqsdfghjklmwxcvbn0123456789") for _ in range(lenght)))

def load_users():
    random.seed(159357456)
    with open("users.txt") as fff:
        for i in fff.readlines():
            name,email = i.split(" ")
            yield name,User(name.lower(),email)


class User:
    def __init__(self,name,email):
        self.name = name
        self.email = email
        self.password = randomstring()
        print(self.name,self.email,self.password)
    def match_password(self,password):
        print(self.password,password)
        return self.password == password



loginHandler = LoginHandler()
