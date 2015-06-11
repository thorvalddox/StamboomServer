from flask import Flask

from flask import render_template,make_response

import core
import draw



app = Flask(__name__)

app.debug = True

#TODO image uploader
#TODO interactive site
#TODO command set
#TODO conversion


@app.route('/stamboom/commands/oldxml')
def show_old_xml():
    response = make_response(render_template("code_show.html",code=core.xmlTest().replace("\n","<br/>")))
    return response

@app.route('/stamboom/commands/handled')
def show_handled_code():
    response = make_response(render_template("code_show.html",code=core.bashTest().replace("\n","<br/>")))
    return response

@app.route('/stamboom/commands/raw')
def show_raw_code():
    response = make_response(render_template("code_show.html",code=core.rawCode().replace("\n","<br/>")))
    return response


@app.route('/stamboom/')
def show_fam_tree():
    f = core.FamilyTree()
    f.from_code("data.log")
    d = draw.drawPeople(f)
    response = make_response(render_template("famtree.html",canvas=d.get_html_canvas(),script=d.get_html_script()))
    return response


@app.route('/edit/<name>/')
def edit(name):
    f = core.FamilyTree()
    f.from_code("data.log")
    response = make_response(render_template("edit.html",name=name,image=f.get_person(name).image))
    return response

if __name__ == '__main__':
    app.run()
