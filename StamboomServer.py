from flask import Flask

from flask import render_template,make_response,url_for,request,redirect,session

import os,os.path
import random
from functools import wraps

import core
import draw
import imagechanger
import forms

from loginhandle import loginHandler

app = Flask(__name__)

app.debug = True

app.config['UPLOAD_FOLDER'] = 'uploads/'

app.secret_key = ''.join(chr(random.randrange(64)+64) for _ in range(32))



if not os.getcwd().endswith("StamboomServer"):
    os.chdir("StamboomServer")

#TODO command set
#TODO conversion

def check_logged_in(session):
    if "username" not in session:
        return False
    else:
        return loginHandler.valid_user(session["username"])

def login_required(func):
    @wraps(func)
    def save_function(*args,**kwargs):
        if not check_logged_in(session):
            return redirect("/login")
        return func(*args,**kwargs)
    return(save_function)


@app.route('/')
def index():
    response = make_response(render_template("titlepage.html"))
    return response

@app.route('/stamboom/commands/oldxml')
@login_required
def show_old_xml():
    response = make_response(render_template("code_show.html",code=core.xmlTest().replace("\n","<br/>")))
    return response

@app.route('/stamboom/commands/handled')
@login_required
def show_handled_code():
    response = make_response(render_template("code_show.html",code=core.bashTest().replace("\n","<br/>")))
    return response

@app.route('/stamboom/commands/raw')
@login_required
def show_raw_code():
    response = make_response(render_template("code_show.html",code=core.rawCode().replace("\n","<br/>")))
    return response


@app.route('/stamboom/')
def show_fam_tree():
    f = core.FamilyTree()
    f.from_code("data.log",2)
    d = draw.draw_people(f)
    response = make_response(render_template("famtree.html",canvas=d.get_html_canvas(),script=d.get_html_script()
                                             ,titlebar=titlebar()))
    return response

@app.route('/stamboom/safe')
def show_fam_tree_safe():
    f = core.FamilyTree()
    f.from_code("data.log")
    d = draw.draw_people(f)
    response = make_response(render_template("famtree.html",canvas=d.get_html_canvas(),script=d.get_html_script()
                                             ,titlebar=titlebar()))
    return response


@app.route('/edit/<name>/')
@login_required
def edit(name):
    f = core.FamilyTree()
    f.from_code("data.log")
    person = f.get_person(name)
    data = [forms.create_person_link(i) for i in f.get_data(person)]
    form = list(forms.make_forms(f,person))
    response = make_response(render_template("edit.html",name=person.name,uname=name,
                                             image=url_for('static', filename=person.image),data=data,form=form,
                                             titlebar=titlebar()))
    return response

@app.route('/list/people')
@login_required
def list_people():
    f = core.FamilyTree()
    f.from_code("data.log")
    data = forms.create_person_link(f.people)
    response = make_response(render_template("newperson.html",people=data,titlebar=titlebar()))
    return response

@app.route('/edit/<name>/upload/', methods = ['POST'])
@login_required
def upload_image(name):
    print(name)
    print(request.files)
    file = request.files["file"]
    imagechanger.change_image(name,file)
    return redirect('/edit/'+name)


@app.route('/edit/')
@login_required
def editRaw():
    response = make_response(render_template("rawcommand.html",code=core.rawCode().replace("\n","<br/>"),titlebar=titlebar()))
    return response

@app.route('/edit/rawcommand/', methods = ['POST'])
@login_required
def rawcommand():
    print(request.form)
    command = request.form["command"]
    print(command)
    core.addcommand_ip(request,command)
    return redirect('/edit/')


@app.route('/edit/<name>/parents/', methods = ['POST'])
@login_required
def edit_parents(name):
    print(name)
    print(request.form)
    first = request.form["parent0"]
    second = request.form["parent1"]
    core.addcommand_ip(request,"parents {} {} {}".format(name,first,second))
    return redirect('/edit/'+name)


@app.route('/edit/<name>/addPartner/', methods = ['POST'])
@login_required
def edit_add_partner(name):
    print(name)
    print(request.form)
    partner = request.form["addPartner"]
    core.addcommand_ip(request,"family {}".format(name,partner))
    return redirect('/edit/'+name)

@app.route('/edit/<name>/remPartner/', methods = ['POST'])
@login_required
def edit_rem_partner(name):
    print(name)
    print(request.form)
    partner = request.form["remPartner"]
    core.addcommand_ip(request,"disband {}".format(name,partner))
    return redirect('/edit/'+name)


@app.route("/templates/titlebar")
def render_titlebar():
    response = make_response(render_template("titlebar.html"))
    return response

@app.route("/login/")
def render_login():
    response = make_response(render_template("login.html",message=""))
    return response

@app.route("/login/invalid/")
def render_login_invalid():
    response = make_response(render_template("login.html",message="The password combination was invalid"))
    return response


@app.route("/login/validate/",methods=["POST"])
def validate_login():
    if loginHandler.valid_login(request.form["name"],request.form["password"]):
        session["username"] = request.form["name"]
        return redirect("/")
    else:
        return redirect("/login/invalid")


def titlebar():
    with open("templates/titlebar.html") as fff:
        return fff.read().replace("{{ username }}",session["username"])

if __name__ == '__main__':
    app.run()
