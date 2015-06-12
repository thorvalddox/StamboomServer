__author__ = 'Thorvald'

import core


def create_person_dropdown(pList, default=None):
    return """
    <select>
        {}
    </select>
    """.format("\n".join(
        """<option value="{}" {}>{}</option>""".format(
            p.uname, "selected='selected'" if p == default else "", p.name
        ) for p in pList
    ))
