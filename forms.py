__author__ = 'Thorvald'

import core
from collections import namedtuple


def create_person_dropdown_safe(pList, default=None,name="selector"):
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

def create_person_link(pList):
    return """
    <ul>
        {}
    </ul>
    """.format("\n".join(
        """<li><a href='/edit/{}'>{}</a></li>""".format(
            p.uname, p.name
        ) for p in pList
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
    return """<form action="addPartner/" method="post" enctype="multipart/form-data">
         Selecteer nieuwe partner:{}<br/>
         <input type="submit" value="Voeg toe">
    </form>""".format(addBox) + \
    """<form action="remPartner/" method="post" enctype="multipart/form-data">
         Verwijder partner:{}<br/>
         <input type="submit" value="Verwijder">
    </form>""".format(remBox)

def make_forms(tree,person):
    yield edit_parents_form(tree,person)
    yield edit_partners_form(tree,person)