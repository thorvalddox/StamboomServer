__author__ = 'Thorvald'
import subprocess
#import threading

BASH_CHANGE = \
"""
cd StamboomServer
if git diff-index --quiet HEAD --; then
  echo False
else
  echo True
fi
"""

def check_for_changes() -> bool:
    """
    returns wheather github has a newer version
    """
    print("Checking for changes")
    proc = subprocess.Popen([BASH_CHANGE], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print("needs update:", out)
    print("Done checking")
    return out==b'True\n'


#Pythonanywhere free account doesn't allow threading. Do not use this function.
# def run_update_process():
#     threading.Timer(5.0, run_update_process).start()
#     update()

def update():
    if try_update():
        restart_server()
        return True
    return False


def try_update() -> bool:
    """
    tries to update to a newer version and returns if succesfull (returns false if 'Already up-to-date')
    """
    print("Updating Code")
    proc = subprocess.Popen(["cd StamboomServer;git pull"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print("git:", out)
    print("Done updating Code")
    return out not in  (b'Already up-to-date.\n',b'')

def restart_server():
    """
    resets the wsgi application, forcing the server to restart
    """
    print("Restart Server")
    proc = subprocess.Popen(["touch /var/www/lightning939_pythonanywhere_com_wsgi.py"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print("touch /var/www/lightning939_pythonanywhere_com_wsgi.py")

def get_commit_number():
    pass