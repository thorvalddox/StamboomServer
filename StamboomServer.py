from flask import Flask

from flask import render_template,make_response,url_for,request,redirect
import os,os.path
import core
import draw
import imagechanger



app = Flask(__name__)

app.debug = True

app.config['UPLOAD_FOLDER'] = 'uploads/'


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
    f.from_code("data.log",2)
    d = draw.draw_people(f)
    response = make_response(render_template("famtree.html",canvas=d.get_html_canvas(),script=d.get_html_script()))
    return response

@app.route('/stamboom/safe')
def show_fam_tree_safe():
    f = core.FamilyTree()
    f.from_code("data.log")
    d = draw.draw_people(f)
    response = make_response(render_template("famtree.html",canvas=d.get_html_canvas(),script=d.get_html_script()))
    return response


@app.route('/edit/<name>/')
def edit(name):
    f = core.FamilyTree()
    f.from_code("data.log")
    person = f.get_person(name)
    response = make_response(render_template("edit.html",name=person.name,uname=name,image=url_for('static', filename=person.image)))
    return response

@app.route('/edit/<name>/upload/', methods = ['POST'])
def upload_image(name):
    print(name)
    print(request.files)
    file = request.files["file"]
    imagechanger.change_image(name,file)
    return redirect('/edit/'+name)


@app.route('/edit/')
def editRaw():
    response = make_response(render_template("rawcommand.html"))
    return response

@app.route('/edit/rawcommand/', methods = ['POST'])
def rawcommand():
    print(request.form)
    command = request.form["command"]
    print(command)
    core.addcommand_ip(request,command)
    return redirect('/edit/')

if __name__ == '__main__':
    app.run()
