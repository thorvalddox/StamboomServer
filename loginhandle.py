__author__ = 'Thorvald'


class LoginHandler:
    def __init__(self,passwords):
        self.passworddict = passwords
    def valid_user(self,name):
        return name in self.passworddict
    def valid_login(self,name,password):
        print(name,self.passworddict.get(name,None))
        return password == self.passworddict.get(name,None)


class User:
    def __init__(self,name,email,password):
        self.name = name
        self.email = email
        self.password = password


loginHandler = LoginHandler({"Thorvald":"fire21","Anja":"maaktniuit"})
