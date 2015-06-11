from flask import Flask

from flask import render_template,make_response

import core



app = Flask(__name__)

app.debug = True

#TODO image uploader
#TODO interactive site
#TODO command set
#TODO conversion


@app.route('/stamboom/commands')
def hello_world():
    response = make_response(render_template("code_show.html",code=core.xmlTest().replace("\n","<br/>")))
    return response


if __name__ == '__main__':
    app.run()
