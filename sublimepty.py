import sublime
import sublime_plugin

from process import Supervisor, SublimeView, PtyProcess 

SUPERVISOR = Supervisor()

def process(id):
    return SUPERVISOR.process(id)

class OpenTerminal(sublime_plugin.WindowCommand):
    def run(self):
        sv = SublimeView()
        proc = PtyProcess(SUPERVISOR)
        proc.attach_view(sv)
        proc.start()