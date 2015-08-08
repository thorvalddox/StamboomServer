__author__ = 'Thorvald'

import random
import json
from passlib.hash import bcrypt

class LoginHandler:
    """
    An object handling the logins
    """
    def __init__(self):
        self.users = dict(load_users())
    def valid_user(self,name):
        """
        check if a username exists
        """
        return name.lower() in self.users
    def valid_login(self,name,password):
        """
        check if a username exists and has the correct password
        """
        for i in self.users.values():
            print(i)
        return self.valid_user(name) and self.users[name.lower()].match_password(password)
    def get_user_list(self):
        """
        returns a list of directiroes containing user data
        """
        return [{"name": k,"email": v.email} for k,v in self.users.items()]
    def check_admin(self,session):
        """
        check if the currently logged in user is an admin
        """
        print(session.get("username","nope"),self.admins())
        return session.get("username","") in self.admins()
    def user(self,session):
        """
        returns the same of the currently logged in user, or an empty string if no user has logged in.
        """
        return session.get("username","")
    def admins(self):
        """
        returns a list of users with admin access
        """
        return ("thorvalddx94","gerwind96","joran.dox")

def randomstring(lenght=12):
    """
    generates a random lower alphanumerical string with a given lenght
    """
    return("".join(random.choice("azertyuiopqsdfghjklmwxcvbn0123456789") for _ in range(lenght)))

def load_users():
    try:
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
    except FileNotFoundError:
        return []
    User.saveall()


class User:
    all_ = []
    def __init__(self,name,email,password_hash=None):
        User.all_.append(self)
        self.name = name
        self.email = email
        if password_hash is None:
            self.password_hash = bcrypt.encrypt(randomstring())
        else:
            self.password_hash = password_hash
        print(self)
    def match_password(self, password):
        return bcrypt.verify(self.password_hash, password)
    def __repr__(self):
        return "{}({},{})".format(self.name, self.email, self.password_hash)
    @classmethod
    def saveall(cls):
        with open("StamboomServer/users.json","w") as jsonfile:
            json.dump([s.__dict__ for s in cls.all_],jsonfile)




