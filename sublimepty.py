import sublime
import sublime_plugin

from process import Supervisor, SublimeView, PtyProcess 

SUPERVISOR = Supervisor()

def read_all():
    SUPERVISOR.read_all()
    sublime.set_timeout(read_all, 20)

read_all()

def process(id):
    return SUPERVISOR.process(id)

class OpenPty(sublime_plugin.WindowCommand):
    def run(self):
        sv = SublimeView()
        proc = PtyProcess(SUPERVISOR)
        proc.attach_view(sv)
        proc.start()