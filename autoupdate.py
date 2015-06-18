__author__ = 'Thorvald'
import subprocess
import threading

BASH_CHANGE = \
"""
if [[ `git status --porcelain` ]]; then
  echo True
else
  echo False
fi
"""

def check_for_changes() -> bool:
    print("Checking for changes")
    proc = subprocess.Popen([BASH_CHANGE], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print("git:", out)
    print("Done checking")


#Pythonanywhere free account doesn't allow threading. Do not use this function.
def run_update_process():
    threading.Timer(5.0, run_update_process).start()
    update()

def update():
    check_for_changes()