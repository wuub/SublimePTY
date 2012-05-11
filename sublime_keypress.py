import sublime_plugin

import sublimepty

class SublimeptyKeypress(sublime_plugin.TextCommand):
    def run(self, edit, key, ctrl=False, alt=False, shift=False, super=False):
        process_id = self.view.settings().get("sublimepty_id")
        process = sublimepty.process(process_id)
        if not process:
            return
        process.send_keypress(key, ctrl, alt, shift, super)


class SublimeptyClick(sublime_plugin.TextCommand):
    def run(self, edit, **kwds):
        process_id = self.view.settings().get("sublimepty_id")
        process = sublimepty.process(process_id)
        row, col = self.view.rowcol(self.view.sel()[0].a) # Thanks quarnster
        print("sublimeclik", row, col)
        if not process:
            return
        process.send_click(row, col, **kwds)