__author__ = 'Thorvald'
import subprocess
#import threading

BASH_CHANGE = \
"""
if git diff-index --quiet HEAD --; then
  echo True
else
  echo False
fi
"""

def check_for_changes() -> bool:
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
    if check_for_changes():
        force_update()
        restart_server()


def force_update():
    print("Updating Code")
    proc = subprocess.Popen(["git pull"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print("git:", out)
    print("Done updating Code")

def restart_server():
    print("Restart Server")
    proc = subprocess.Popen(["touch /var/www/wsgi.py"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print("touch:", out)

def get_commit_number():
    pass