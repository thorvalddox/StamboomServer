__author__ = 'Thorvald'

import core
from collections import namedtuple


class FormCom:
    """
    Changes form ouput to data command
    """
    all_ = []
    def __init__(self,pathname,command,*info,submit=[]):
        self.pathname = pathname
        self.command = command
        self.info = info
        self.submit = submit
        FormCom.all_.append(self)
    def getreq(self,data,name,request):
        """
        get data from request
        """
        if data == "name":
            return name
        else:
            return str(request.form[data]).replace(" ","_")
    def buildcommand(self,command,name,request):
        """
        build a command from a request.form data if the command matches
        """
        if self.pathname != command:
            return None
        if not all(s in request.form for s in self.submit):
            return None
        return self.command + " " + " ".join(self.getreq(i,name,request) for i in self.info)
    @staticmethod
    def get_command(command,name,request):
        """
        build a command from a request.form data. searches the correct command.
        """
        for i in FormCom.all_:
            s = i.buildcommand(command,name,request)
            if s is not None:
                return s


def generate_basic_forms():
    """
    generates the correct FormCom objects to the edit ui
    """
    FormCom("parents","parents","name","parent0","parent1")
    FormCom("dates","person","name","birth","dead")
    FormCom("addPartner","family","name","addPartner")
    FormCom("remPartner","delete","remPartner")
    FormCom("divPartner","divorce","name","divPartner")
    FormCom("rmrPartner","remarry","name","rmrPartner")
    FormCom("child","family","name","partner","addChild",submit=["addChildPress"])
    FormCom("child","disconnect","name","partner","remChild",submit=["remChildPress"])

def create_person_dropdown_safe(pList, default=None,name="selector"):
    """
    creates a dropdown list, forcing you to take a given option
    """
    return """
    <select name="{0}">
        <option value="*" {2}> -- geen --</option>
        {1}
    </select>
    """.format(name,"\n".join(
        ("""<option value="{}" {}>{}</option>""".format(
            p.uname, "selected='selected'" if p == default else "", p.name
        ) for p in pList)),"selected='selected'" if default is None else ""
    )

def create_person_dropdown(pList, default=None,name="selector"):
    """
    creates a dropdown list, where the user can select a person or type the name of a new one
    """
    return """
    <input name="{0}" list="{0}_data" value="{3}">
    <datalist id="{0}_data">
        <option value="*" {2}> -- geen --</option>
        {1}
    </datalist>
    """.format(name,"\n".join(
        ("""<option value="{}" {}>{}</option>""".format(
            p.uname, "selected='selected'" if p == default else "", p.name
        ) for p in pList)),"selected='selected'" if default is None else "",
               (default.uname if default is not None else "")
    )

def create_person_link(pList,split=50):
    """
    Creates aa list of people, splitting it in columns after a given amount.
    """
    return """
    <table>
    <tr>
    <td>
    <ul>
        {}
    </ul>
    </td>
    </tr>
    </table>
    """.format("\n".join(
        """<li><a href='/stamboom/edit/{}'>{}</a></li>{}""".format(
            p.uname, p.name, ["</ul></td><td><ul>",""][bool((i+1)%split)]
        ) for i,p in enumerate(pList)
    ))

invalidPerson = namedtuple("InvalidPerson","name,uname")("--none--","")

def edit_parents_form(tree:core.FamilyTree,person):
    parents = list(tree.get_parents(person))
    if len(parents) < 2:
        parents += [None]*(2-len(parents))
    selectBoxes = [create_person_dropdown(tree.people_all,p,"parent"+str(i)) for i,p in enumerate(parents)]
    return """<form action="parents/" method="post" enctype="multipart/form-data">
         Ouder1:{}<br/>
         Ouder2:{}<br/>
         <input type="submit" value="Verzend wijzigingen">
    </form>""".format(*selectBoxes)


def edit_partners_form(tree:core.FamilyTree,person):
    partners = list(tree.get_partners(person))
    addBox =  create_person_dropdown(tree.people_all,None,"addPartner")
    remBox =  create_person_dropdown(tree.get_partners(person),None,"remPartner")
    divBox =  create_person_dropdown(filter(lambda x:not tree.get_family(x.name,person.name).divorced,tree.get_partners(person))
                                     ,None,"divPartner")
    rmrBox =  create_person_dropdown(filter(lambda x:tree.get_family(x.name,person.name).divorced,tree.get_partners(person))
                                     ,None,"rmrPartner")
    return """<form action="addPartner/" method="post" enctype="multipart/form-data">
         Selecteer nieuwe partner:{}<br/>
         <input type="submit" value="Voeg toe & Verzend">
    </form>""".format(addBox) + \
    """<form action="remPartner/" method="post" enctype="multipart/form-data">
         Verwijder partner:{}<br/>
         <input type="submit" value="Verwijder & Verzend">
    </form>""".format(remBox) + \
    """<form action="divPartner/" method="post" enctype="multipart/form-data">
         Scheiden van:{}<br/>
         <input type="submit" value="Scheid & Verzend">
    </form>""".format(divBox) + \
    """<form action="rmrPartner/" method="post" enctype="multipart/form-data">
         Hertrouwen:{}<br/>
         <input type="submit" value="Hertrouw & Verzend">
    </form>""".format(rmrBox)

def edit_children_form(tree:core.FamilyTree,person):
    partBox = create_person_dropdown(tree.get_partners(person),None,"partner")
    addBox =  create_person_dropdown(tree.people_all,None,"addChild")
    remBox =  create_person_dropdown(tree.get_children(person),None,"remChild")
    return """<form action="child/" method="post" enctype="multipart/form-data">
         Selecteer Partner:{}<br/>
         Selecteer nieuw kind:{}<br/>
         <input type="submit" name="addChildPress" value="Voeg toe & Verzend"><br/>
         Verwijder kind:{}<br/>
         <input type="submit" name="remChildPress" value="Verwijder & Verzend">
    </form>""".format(partBox,addBox,remBox)

def edit_date_form(person):
    return """<form action="dates/" method="post" enctype="multipart/form-data">
         Geboren op:<input type="text" name="birth" value="{}"></br>
         Gestorven op:<input type="text" name="dead" value="{}"></br>
         <input type="submit" value="Verzend wijzigingen">
    </form>""".format(person.birth,person.dead)

def edit_image_form():
    return """
        <form action="upload/" method="post" enctype="multipart/form-data">
        selecteer .jpg bestand :<input type="file" name="file"><br />
        <input type="submit" value="Upload"><br/>
    </form>
    """

def make_forms(tree,person):
    yield edit_parents_form(tree,person)
    yield edit_partners_form(tree,person)
    yield edit_children_form(tree,person)
    yield edit_date_form(person)
    yield edit_image_form()

def disabled_forms(tree,person):
    yield "<a href='login/'>log in om</br>te bewerken</a>"
    yield "<a href='login/'>log in om</br>te bewerken</a>"
    yield "<a href='login/'>log in om</br>te bewerken</a>"
    yield """<form action="dates/" method="post" enctype="multipart/form-data">
         Geboren op:{}</br>
         Gestorven op:{}</br>
         <a href='login/'>log in om te bewerken</a>
    </form>""".format(person.birth,person.dead)
    yield "<a href='login/'>log in om</br>te bewerken</a>"