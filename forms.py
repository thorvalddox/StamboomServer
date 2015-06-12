__author__ = 'Thorvald'

import core
from collections import namedtuple


def create_person_dropdown(pList, default=None,name="selector"):
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
    print(selectBoxes[0])
    return """<form action="parents/" method="post" enctype="multipart/form-data">
         Ouder1:{}<br/>
         Ouder2:{}<br/>
         <input type="submit" value="Verzend wijzigingen">
    </form>""".format(*selectBoxes)

def make_forms(tree,person):

    yield edit_parents_form(tree,person)