import sqlite3
import re
import time

class FamilyTree:
    def __init__(self):
        self.conn = sqlite3.connect('famtree.db')
        self.c = self.conn.cursor()
        self.execute = self.c.execute
    def create(self,command_source):
        try:
            self.execute("DROP TABLE people")
            self.execute("DROP TABLE parents")
        except sqlite3.OperationalError:
            pass
        #id = {firstname}_{lastname}.replace("non letter","_").lower()
        self.execute("CREATE TABLE people (ID INTEGER PRIMARY KEY AUTOINCREMENT, firstname VARCHAR(255), lastname VARCHAR(255), birth DATE, death DATE)")
        self.execute("CREATE TABLE parents (parent INTEGER references people(ID), "
                     "child INTEGER references people(ID))")
        import core
        f = core.FamilyTree()
        f.from_code("/../data.log", 2)
        for p in f.people_all:
            names = p.uname.split("_")
            if len(names) <= 1:
                firstname = names[0]
                lastname = ""
            elif names[1] == "???":
                firstname = names[0]
                lastname = ""
            elif len(names) == 2:
                firstname,lastname = names
            elif names[1].lower() in ("de","van"):
                firstname = names[0]
                lastname = " ".join(names[1:])
            else:
                firstname = " ".join(names[:-1])
                lastname = names[-1]
            self.add_person(firstname,lastname,p.ubirth,p.udead)

        print("\n".join(" ".join("{:<16}".format("\""+str(y)+"\"") for y in x[0:]) for x in \
                        self.execute("SELECT * FROM people").fetchall()))
        print("\n".join(" ".join("{:<16}".format("\""+str(y)+"\"") for y in x[0:]) for x in \
                        self.execute("SELECT * FROM people").fetchall()))
        self.save()

        print(self.get_person_id("Thorvald","Dox"))
    def add_person(self,firstname,lastname="",birth=None,death=None):
        if birth is not None:
            birth = time.strftime("%Y-%m-%d",birth)
        if death is not None:
            death = time.strftime("%Y-%m-%d",death)
        self.execute("INSERT INTO people (firstname,lastname,birth,death) values(?,?,?,?)",(firstname,lastname,birth,death))
        self.save()
    def get_data(self,person_id):
        return self.execute("SELECT * FROM people WHERE ID=?",(person_id,))


    def add_child(self,parent_id,child_id):
        self.execute("")


    def get_person_id(self,firstname,lastname):
        results = self.execute("SELECT * FROM people WHERE firstname=? AND lastname=?",(firstname,lastname))
        if not results:
            return None
        else:
            return results.fetchall()[0][0]

    def save(self):
        self.conn.commit()

    def finish(self):
        self.conn.close()
    def __del__(self):
        self.finish()

class Person:
    """
    just a set of handlers to use when handling Family tree data
    """
    def __init__(self,parent,index):
        self.parent = parent
        self.index = index
    def __eq__(self,other):
        return self.parent == other.parent and self.index == other.index
    @property
    def firstname(self):
        return self.parent.get_data[1]
    @property
    def lastname(self):
        return self.parent.get_data[2]
    @property
    def name(self):
        return "{} {}".format(self.firstname,self.lastname)
    def birth(self):
        return self.parent.get_data[3]
    def death(self):
        return self.parent.get_data[4]



if __name__ == "__main__":
    FamilyTree().create("autodata.log")