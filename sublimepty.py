import sublime
import sublime_plugin
import os
from process import Supervisor, SublimeView, PtyProcess, Win32Process

SUPERVISOR = Supervisor()
ON_WINDOWS = os.name == "nt" 

def read_all():
    SUPERVISOR.read_all()
    sublime.set_timeout(read_all, 200)

read_all()

def process(id):
    return SUPERVISOR.process(id)

class OpenPty(sublime_plugin.WindowCommand):
    def run(self, shell=None, encodings=None, title="TERMINAL"):
        sv = SublimeView()
        sv.view.set_name(title);
        if ON_WINDOWS:
            proc = Win32Process(SUPERVISOR)
        else:
            proc = PtyProcess(SUPERVISOR, cmd = shell, encodings = encodings)
        proc.attach_view(sv)
        proc.start()