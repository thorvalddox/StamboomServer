from flask import Flask

from flask import make_response, url_for, request, redirect, session, send_file

from flask_mail import Mail, Message
from jinja2 import Environment, PackageLoader

import smtplib

import os, os.path
import glob
import random
import re
import json
from time import sleep
from functools import wraps, update_wrapper

import core
import draw
import imagechanger
import forms


from autoupdate import update
from datetime import datetime
from makedoc import makedocs
import loginhandle2


# Init Flask application
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=465,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME="stamboom.dox@gmail.com",
    MAIL_PASSWORD="d0xst4mb00m",
    DEFAULT_MAIL_SENDER="stamboom.dox@gmail.com",
)

app.secret_key = ''.join(chr(random.randrange(64) + 64) for _ in range(32))

# Init Flask_mail

mail = Mail(app)

# init jinja2 enviroment

env = Environment(loader=PackageLoader('StamboomServer', 'templates'))


def render_template(name, *args, **kwargs):
    """
    renders a flask template with the correct enviroment variables
    """
    template = env.get_template(name)
    return template.render(*args, **kwargs)

# fix path on local machines

OFFLINE = False  # true if the server is ran on a local machine.

print(os.getcwd())

print("status:", ["ONLINE", "OFFLINE/DEBUG"][OFFLINE])
# Init side processes



makedocs()

# Decorators from here.

def check_logged_in():
    """
    check if the currect user is logged in.
    """
    return loginhandle2.check_credentials(session)

def login_required(func):
    """
    Decorater. Put this after @app.route. Defines if you need to be logged in to access a certain page.
    """

    @wraps(func)
    def save_function(*args, **kwargs):
        if not check_logged_in():
            return redirect(request.path + "login/")
        return func(*args, **kwargs)
    return (save_function)


def admin_required(func):
    """
    Decorater. Put this after @app.route. Defines if you need to be an admin to access a certain page.
    """

    @wraps(func)
    def save_function(*args, **kwargs):
        if not check_logged_in() or not loginhandle2.check_admin(session):
            return redirect(request.path + "login/admin/")
        return func(*args, **kwargs)

    return (save_function)


def auto_update(func):
    """
    Decorater. Put this after @app.route. Defines if the page must check for updates before loading.
    It should be the default. Only f.e. the login page shouldn't have it.
    """

    @wraps(func)
    def updated_func(*args, **kwargs):
        if not OFFLINE:  # not updating when offline.
            if update():
                return make_response(render_template("update.html"))
        return func(*args, **kwargs)

    return updated_func


def catch_errors(func):
    """
    Decorater. Put this after @app.route. Catches the errors of the different functions
    """

    @wraps(func)
    def catch_erros(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            import traceback

            error_code = traceback.format_exc().replace("\n", '<br/>')
            traceback.print_exc()
            return make_response(render_template("error.html", log=error_code + "</p><p>")), 500

    return catch_erros


def update_jinja2_env(func):
    """
    Decorater. Put this after @app.route. Updates the global variables for the jinja 2 enviroment
    """

    @wraps(func)
    def update_jinja2(*args, **kwargs):
        env.globals["username"] = session.get("username", "")
        print("username:", env.globals["username"])
        return func(*args, **kwargs)

    return (update_jinja2)

def nocache(view): #Does not work. Use filename scrambling instead
    """
    Prevent sended images from being chached
    """
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


def default_page(func):
    """
    combines different decorators. (catch_errors, update_jinja2_env, auto_update)
    """
    return wraps(func)(catch_errors(auto_update(update_jinja2_env(func))))


def login_page(func):
    """
    combines different decorators. (default_page, login_required)
    """

    return wraps(func)(default_page(login_required(func)))


def admin_page(func):  # combines default_age with login_required
    """
    combines different decorators. (default_page, admin_required)
    """
    return wraps(func)(default_page(admin_required(func)))

# wrappers from here


# initilisize forms

forms.generate_basic_forms()

# apps from here

# webpages from here:

@app.route('/')
def index():
    update()
    # response = make_response(render_template("titlepage.html"))
    return redirect("/stamboom/")


@app.route('/stamboom/commands/oldxml/')
@login_page
def show_old_xml():
    response = make_response(render_template("code_show.html", code=core.xmlTest().replace("\n", "<br/>")))
    return response


@app.route('/stamboom/commands/handled/')
@login_page
def show_handled_code():
    response = make_response(render_template("code_show.html", code=core.bashTest().replace("\n", "<br/>")))
    return response


@app.route('/stamboom/commands/raw/')
@login_page
def show_raw_code():
    response = make_response(render_template("code_show.html", code=core.rawCode().replace("\n", "<br/>")))
    return response


@app.route('/stamboom/')
@default_page
def show_fam_tree():
    return redirect("/stamboom/view/Petrus_Ludovicus_Carolus_Dox")


@app.route('/stamboom/view/<name>/')
@default_page
def show_fam_tree_custom_redir(name):
    return redirect("/stamboom/view/{}/{}/".format(name,"120x150b10t8"))

@app.route('/stamboom/view/<name>/<fformat>/')
@default_page
def show_fam_tree_custom(name,fformat):
    f = core.FamilyTree()
    f.from_code("data.log", 2)
    person = f.get_person(name)
    localfam = f.build_new(person)
    d = draw.draw_people(localfam, *map(int,re.split(r"x|b|t",fformat)))
    response = make_response(render_template("famtree.html", canvas=d.get_html_canvas(),
                                             script=d.get_html_script(),pname=name))
    return response

@app.route('/stamboom/view/<name>/<fformat>/download/')
@default_page
def download_redirect(name,fformat):
    return redirect("/stamboom/view/{}/{}/download/{}/".format(name,fformat,hex(random.randrange(16**16))))


@app.route('/stamboom/view/<name>/<fformat>/download/<suffix>/')
@default_page
def download_fam_tree_custom(name,fformat,suffix):
    f = core.FamilyTree()
    f.from_code("data.log", 2)
    person = f.get_person(name)
    localfam = f.build_new(person)
    d = draw.draw_people_download(localfam, *map(int,re.split(r"x|b|t",fformat)))
    paths = glob.glob("StamboomServer/static/download_*.jpg")
    for i in paths:
        os.remove(i)
    d.image.save("StamboomServer/static/download_{}.jpg".format(suffix))
    response = send_file("static/download_{}.jpg".format(suffix), mimetype='image/jpg')
    return response

@app.route('/stamboom/edit/<name>/')
@default_page
def edit(name):
    f = core.FamilyTree()
    f.from_code("data.log", 2)
    person = f.get_person(name)
    data = [forms.create_person_link(i) for i in f.get_data(person)]
    localfam = f.build_new(person)
    tree = draw.draw_people(localfam, 80, 80, 8, 6)
    if check_logged_in():
        form = list(forms.make_forms(f, person))
    else:
        form = list(forms.disabled_forms(f, person))
    response = make_response(render_template("edit.html", pname=person.name, uname=name,
                                             image=url_for('static', filename=person.image), data=data, form=form,
                                             tree=tree.get_html_canvas(), tree_script=tree.get_html_script()))
    return response


@app.route('/stamboom/list/people/')
@default_page
def list_people():
    f = core.FamilyTree()
    f.from_code("data.log")
    data = forms.create_person_link(f.people)
    response = make_response(render_template("newperson.html", people=data))
    return response


@app.route('/stamboom/console/')
@login_page
def editRaw():
    response = make_response(render_template("rawcommand.html", code=core.rawCode().replace("\n", "<br/>")))
    return response


@app.route('/stamboom/console/rawcommand/', methods=['POST'])
@login_page
def rawcommand():
    print(request.form)
    command = request.form["command"]
    print(command)
    core.addcommand(request, session, command)
    return redirect('/stamboom/console/')


@app.route('/stamboom/edit/<name>/upload/', methods=['POST'])
@login_page
def upload_image(name):
    print(name)
    print(request.files)
    file = request.files["file"]
    core.addcommand(request,session,"image {} {}".format(name,imagechanger.change_image(file)))
    return redirect('/stamboom/edit/' + name)

@app.route('/stamboom/edit/<name>/rotate/', methods=['POST'])
@login_page
def rotate_image(name):
    clockwise = "cw" in request.form
    core.addcommand(request,session,"rotate {} {}".format(name,["left","right"][clockwise]))
    return redirect('/stamboom/edit/' + name)

""" #commented out for data-driven counterpart.
@app.route('/stamboom/edit/<name>/parents/', methods = ['POST'])
@login_page
def edit_parents(name):
    print(name)
    print(request.form)
    first = request.form["parent0"]
    second = request.form["parent1"]
    core.addcommand(request,session,"parents {} {} {}".format(name,first,second))
    return redirect('/stamboom/edit/'+name)

@app.route('/stamboom/edit/<name>/dates/', methods = ['POST'])
@login_page
def edit_dates(name):
    print(name)
    print(request.form)
    first = request.form["birth"]
    second = request.form["dead"]
    core.addcommand(request,session,"person {} {} {}".format(name,first,second))
    return redirect('/stamboom/edit/'+name)

@app.route('/stamboom/edit/<name>/addPartner/', methods = ['POST'])
@login_page
def edit_add_partner(name):
    print(name)
    print(request.form)
    partner = request.form["addPartner"]
    core.addcommand(request,session,"family {} {}".format(name,partner.replace(" ","_")))
    return redirect('/stamboom/edit/'+name)

@app.route('/stamboom/edit/<name>/remPartner/', methods = ['POST'])
@login_page
def edit_rem_partner(name):
    print(name)
    print(request.form)
    partner = request.form["remPartner"]
    core.addcommand(request,session,"disband {} {}".format(name,partner.replace(" ","_")))
    return redirect('/stamboom/edit/'+name)

@app.route('/stamboom/edit/<name>/divPartner/', methods = ['POST'])
@login_page
def edit_div_partner(name):
    print(name)
    print(request.form)
    partner = request.form["divPartner"]
    core.addcommand(request,session,"divorce {} {}".format(name,partner.replace(" ","_")))
    return redirect('/stamboom/edit/'+name)

@app.route('/stamboom/edit/<name>/child/', methods = ['POST'])
@login_page
def edit_child(name):
    partner = request.form["partner"]
    if "addChildPress" in request.form:
        child = request.form["addChild"]
        core.addcommand(request,session,"family {} {} {}".format(name,partner.replace(" ","_"),child.replace(" ","_")))
    elif "remChildPress" in request.form:
        child = request.form["remChild"]
        core.addcommand(request,session,"disconnect {} {} {}".format(name,partner.replace(" ","_"),child.replace(" ","_")))
    return redirect('/stamboom/edit/'+name)
"""


@app.route('/stamboom/edit/<name>/<action>/', methods=['POST'])
@login_page
def edit_person_prop(name, action):
    print(name)
    print(action)
    print(request.form)
    core.addcommand(request, session, forms.FormCom.get_command(action, name, request))
    return redirect('/stamboom/edit/' + name + '/')


@app.route("/templates/titlebar")
def render_titlebar():
    response = make_response(render_template("titlebar.html"))
    return response


@app.route("/<path:path>/login/")
def render_login(path):
    if not OFFLINE:
        response = make_response(render_template("google-login-button.html", message="", path=path))
        return response
    else:
        session["username"] = "local_user"
        return redirect("/" + path + "/")



@app.route("/<path:path>/login/invalid/")
@catch_errors
def render_login_invalid(path):
    if check_logged_in(): #check if really invalid
        return redirect("/" + path + "/")
    return make_response(render_template("google-login-button.html", message="Uw account is niet geaccepteerd op deze server. Neem contact op met de admin (Thorvald Dox) om deze te laten toevoegen op de lijst. Mail naar thorvalddx94@gmail.com", path=path))



@app.route("/<path:path>/login/admin/")
@catch_errors
def render_login_admin(path):
    response = make_response(
        render_template("google-login-button.html", message="You need to be an admin to view this page", path=path))
    return response


@app.route("/<path:path>/login/validate/")
@catch_errors
def validate_login(path):
    if check_logged_in():
        return redirect("/" + path + "/")
    else:
        sleep(3)
        with open("StamboomServer/not_aut_users.txt","a") as file:
            file.write("{}\n".format(session.get("username","<unknown>")))
            file.write("    google:{}\n".format(session.get("UserGoogle", "<None>")))
            file.write("    {}\n".format(str(dict(session))))
        return redirect("/" + path + "/login/invalid/")

@app.route("/global/login/sendcreds/", methods = ['GET','POST'])
@catch_errors
def receive_credentials():
    #with open("StamboomServer/not_aut_users.txt", "a") as file:
    #    file.write(str(json.loads(request.json))+"\nCREDS\n")
    return 403,''# render_template("info.html",info="????????")

@app.route("/<path:path>/logout/")
@catch_errors
def logout(path):
    core.addcommand(request, session, "logout")
    session.pop("username", None)
    session.pop("UserGoogle", None)
    session.pop("UserFacebook", None)
    return redirect("/" + path + "/")


def chain_strings(func):
    def chains(*args, **kwargs):
        return "<br/>".join(func(*args, **kwargs))

    return chains


@chain_strings
def send_mail(user, contents):
    print("sending email", user)

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

def render_raw(filename):
    with open("StamboomServer/"+filename) as file:
        return file.read()

@app.route("/stamboom/docs/<name>")
@default_page
def see_doc(name):
    return make_response(render_raw('doc/_build/html/{}'.format(name)).replace("\"_static","\"/static/_static"))

@app.route("/stamboom/docs/<folder>/<name>")
@default_page
def see_doc_folder(folder,name):
    return make_response(render_raw('doc/_build/html/{}/{}'.format(folder,name)).replace("\"_static","\"/static/_static"))

@app.route("/stamboom/admin/")
@admin_page
def email_form():
    response = make_response(render_template("send_emails.html", users=list(loginHandler.get_user_list())))
    return response







@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def permission_denied(e):
    return render_template('403.html'), 403

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html'), 405

if __name__ == '__main__':
    app.run()
