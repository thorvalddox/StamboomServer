from flask import Flask

from flask import render_template,make_response,url_for,request,redirect,session

from jinja2 import Environment, PackageLoader

from flask_mail import Mail,Message
from jinja2 import Environment, PackageLoader

import smtplib

import os,os.path
import random
from functools import wraps

import core
import draw
import imagechanger
import forms

from loginhandle import LoginHandler
from autoupdate import update


#Init Flask application
app = Flask(__name__)

app.debug = True

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config.update(
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL= True,
    MAIL_USERNAME = "stamboom.dox@gmail.com",
    MAIL_PASSWORD = "d0xst4mb00m",
    DEFAULT_MAIL_SENDER  = "stamboom.dox@gmail.com",
)


app.secret_key = ''.join(chr(random.randrange(64)+64) for _ in range(32))

#Init Flask_mail

mail = Mail(app)

#init jinja2 enviroment

env = Environment(loader=PackageLoader('yourapplication', 'templates'))

#Init side processes


loginHandler = LoginHandler()

print(os.getcwd())

if os.getcwd().endswith("StamboomServer/"):
    os.chdir("../")

#Function from here.

def check_logged_in(session):
    if "username" not in session:
        return False
    else:
        return loginHandler.valid_user(session["username"])

def login_required(func):
    @wraps(func)
    def save_function(*args,**kwargs):
        if not check_logged_in(session):
            return redirect(request.path +"login/")
        return func(*args,**kwargs)
    return(save_function)

def admin_required(func):
    @wraps(func)
    def save_function(*args,**kwargs):
        if not check_logged_in(session) or not loginHandler.check_admin(session):
            return redirect(request.path +"login/admin/")
        return func(*args,**kwargs)
    return(save_function)


def auto_update(func):
    @wraps(func)
    def updated_func(*args,**kwargs):
        update()
        return func(*args,**kwargs)
    return(updated_func)

def catch_errors(func):
    @wraps(func)
    def catch_erros(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except Exception:
            import traceback
            error_code = traceback.format_exc().replace("\n",'<br/>')
            out = send_mail('thorvalddx','<h1>stamboom error<h1>'+error_code)
            return make_response(render_template("error.html",error=error_code)),500
    return catch_erros

def update_jinja2_env(func):
    @wraps(func)
    def update_jinja2(*args,**kwargs):
        env.globals["session"] = session
        return func(*args,**kwargs)

def catch_update(func):
    return catch_errors(auto_update(update_jinja2_env(func)))


#apps from here

@app.route('/')
def index():
    update()
    #response = make_response(render_template("titlepage.html"))
    return redirect("/stamboom/")

@app.route('/stamboom/commands/oldxml/')
@catch_errors
@login_required
@auto_update
def show_old_xml():
    response = make_response(render_template("code_show.html",code=core.xmlTest().replace("\n","<br/>")))
    return response

@app.route('/stamboom/commands/handled/')
@catch_errors
@login_required
@auto_update
def show_handled_code():
    response = make_response(render_template("code_show.html",code=core.bashTest().replace("\n","<br/>")))
    return response

@app.route('/stamboom/commands/raw/')
@catch_errors
@login_required
@auto_update
def show_raw_code():
    response = make_response(render_template("code_show.html",code=core.rawCode().replace("\n","<br/>")))
    return response

@app.route('/stamboom/')
@catch_errors
@auto_update
def show_fam_tree():
    # f = core.FamilyTree()
    # f.from_code("data.log",2)
    # d = draw.draw_people(f,120,150,10,8)
    # response = make_response(render_template("famtree.html",canvas=d.get_html_canvas(),script=d.get_html_script()))
    return redirect("/stamboom/view/Petrus_Ludovicus_Carolus_Dox")

@app.route('/stamboom/view/<name>/')
@catch_errors
@auto_update
def show_fam_tree_custom(name):
    f = core.FamilyTree()
    f.from_code("data.log",2)
    person = f.get_person(name)
    localfam = f.build_new(person)
    d = draw.draw_people(localfam,120,150,10,8)
    response = make_response(render_template("famtree.html",canvas=d.get_html_canvas(),script=d.get_html_script()))
    return response

@app.route('/stamboom/safe/')
@catch_errors
@auto_update
def show_fam_tree_safe():
    f = core.FamilyTree()
    f.from_code("data.log")
    d = draw.draw_people(f)
    response = make_response(render_template("famtree.html",canvas=d.get_html_canvas(),script=d.get_html_script()))
    return response


@app.route('/stamboom/edit/<name>/')
@catch_errors
@auto_update
def edit(name):
    f = core.FamilyTree()
    f.from_code("data.log",2)
    person = f.get_person(name)
    data = [forms.create_person_link(i) for i in f.get_data(person)]
    localfam = f.build_new(person)
    tree = draw.draw_people(localfam,80,80,8,6)
    if check_logged_in(session):
        form = list(forms.make_forms(f,person))
    else:
        form = list(forms.disabled_forms(f,person))
    response = make_response(render_template("edit.html",name=person.name,uname=name,
                                             image=url_for('static', filename=person.image),data=data,form=form,
                                             tree=tree.get_html_canvas(),tree_script=tree.get_html_script()))
    return response

@app.route('/stamboom/list/people/')
@catch_errors
@auto_update
def list_people():
    f = core.FamilyTree()
    f.from_code("data.log")
    data = forms.create_person_link(f.people)
    response = make_response(render_template("newperson.html",people=data))
    return response

@app.route('/stamboom/edit/<name>/upload/', methods = ['POST'])
@catch_errors
@login_required
@auto_update
def upload_image(name):
    print(name)
    print(request.files)
    file = request.files["file"]
    imagechanger.change_image(name,file)
    return redirect('/stamboom/edit/'+name)


@app.route('/stamboom/console/')
@catch_errors
@login_required
@auto_update
def editRaw():
    response = make_response(render_template("rawcommand.html",code=core.rawCode().replace("\n","<br/>")))
    return response

@app.route('/stamboom/console/rawcommand/', methods = ['POST'])
@catch_errors
@login_required
@auto_update
def rawcommand():
    print(request.form)
    command = request.form["command"]
    print(command)
    core.addcommand(request,session,command)
    return redirect('/stamboom/console/')


@app.route('/stamboom/edit/<name>/parents/', methods = ['POST'])
@catch_errors
@login_required
@auto_update
def edit_parents(name):
    print(name)
    print(request.form)
    first = request.form["parent0"]
    second = request.form["parent1"]
    core.addcommand(request,session,"parents {} {} {}".format(name,first,second))
    return redirect('/stamboom/edit/'+name)

@app.route('/stamboom/edit/<name>/dates/', methods = ['POST'])
@catch_errors
@login_required
@auto_update
def edit_dates(name):
    print(name)
    print(request.form)
    first = request.form["birth"]
    second = request.form["dead"]
    core.addcommand(request,session,"person {} {} {}".format(name,first,second))
    return redirect('/stamboom/edit/'+name)

@app.route('/stamboom/edit/<name>/addPartner/', methods = ['POST'])
@catch_errors
@login_required
@auto_update
def edit_add_partner(name):
    print(name)
    print(request.form)
    partner = request.form["addPartner"]
    core.addcommand(request,session,"family {} {}".format(name,partner.replace(" ","_")))
    return redirect('/stamboom/edit/'+name)

@app.route('/stamboom/edit/<name>/remPartner/', methods = ['POST'])
@catch_errors
@login_required
@auto_update
def edit_rem_partner(name):
    print(name)
    print(request.form)
    partner = request.form["remPartner"]
    core.addcommand(request,session,"disband {} {}".format(name,partner.replace(" ","_")))
    return redirect('/stamboom/edit/'+name)

@app.route('/stamboom/edit/<name>/child/', methods = ['POST'])
@catch_errors
@login_required
@auto_update
def edit_child(name):
    partner = request.form["partner"]
    if "addChildPress" in request.form:
        child = request.form["addChild"]
        core.addcommand(request,session,"family {} {} {}".format(name,partner.replace(" ","_"),child.replace(" ","_")))
    elif "remChildPress" in request.form:
        child = request.form["remChild"]
        core.addcommand(request,session,"disconnect {} {} {}".format(name,partner.replace(" ","_"),child.replace(" ","_")))
    return redirect('/stamboom/edit/'+name)


@app.route("/templates/titlebar")
def render_titlebar():
    response = make_response(render_template("titlebar.html"))
    return response

@app.route("/<path:path>/login/")
def render_login(path):
    response = make_response(render_template("login.html",message="",path=path))
    return response

@app.route("/<path:path>/login/invalid/")
@catch_errors
def render_login_invalid(path):
    response = make_response(render_template("login.html",message="The password combination was invalid",path=path))
    return response

@app.route("/<path:path>/login/admin/")
@catch_errors
def render_login_admin(path):
    response = make_response(render_template("login.html",message="You need to be an admin to view this page",path=path))
    return response


@app.route("/<path:path>/login/validate/",methods=["POST"])
@catch_errors
def validate_login(path):
    if loginHandler.valid_login(request.form["name"],request.form["password"]):
        session["username"] = request.form["name"]
        core.addcommand_ip(request,"loginas #{}".format(session["username"]))
        return redirect("/"+path+"/")
    else:
        return redirect("/" + path+"/login/invalid/")

@app.route("/<path:path>/logout/")
@catch_errors
def logout(path):
    core.addcommand(request,session,"logout")
    session.pop("username",None)
    return redirect("/"+path+"/")




def send_mail(user,contents):
    print("sending email")
    yield "sending email to " + repr(user.email)
    yield "username=" + repr(user.name)
    try:
        mail.send(Message("stamboom dox website",
                          sender="stamboom.dox@gmail.com",
                          html=contents,
                          recipients=[user.email]))
        yield "mailing succesfull"
        yield "-> check spam"
    except smtplib.SMTPAuthenticationError as e:
        import traceback
        yield traceback.format_exc()
        yield "Authentication not valid"
    except smtplib.SMTPDataError as e:
        import traceback
        yield traceback.format_exc()
        yield "Data limit exceeded"
    except Exception as e:
        import traceback
        yield traceback.format_exc()


@app.route("/stamboom/admin/")
@catch_errors
@admin_required
@auto_update
def email_form():
    response = make_response(render_template("send_emails.html",users=list(loginHandler.get_user_list())))
    return response



@app.route("/stamboom/admin/sendemails/", methods=["POST"])
@catch_errors
@admin_required
@auto_update
def send_user_mails():
    msg = ""
    #app.config.update(MAIL_PASSWORD=request.form.get("password",""))
    for u in loginHandler.users.values():
        print(request.form)
        if "name_"+u.name in request.form:
            if request.form["name_"+u.name]:
                msg += "<br/>".join(send_mail(u,render_template("email.html",username=u.name,password=u.password))) + "<br/><br/>"
            else:
                msg += "no mail was send to " + u.email +  "<br/><br/>"
        else:
            msg += "no form data about " + u.email +  "<br/><br/>"
    return(msg)

@app.route("/stamboom/admin/seeUsers/")
@catch_errors
@admin_required
@auto_update
def see_users():
    msg = "<table>"
    #msg += "logged in with "+app.config["MAIL_USERNAME"] + "\n"
    #msg += "password: "+app.config["MAIL_PASSWORD"] + "\n"
    for u in loginHandler.users.values():
        msg += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(u.name,"*"*12,u.email)
    msg += "</table>"
    return(msg)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
