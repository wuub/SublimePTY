#!coding: utf-8
from __future__ import division
from __future__ import absolute_import

import subprocess
from weakref import WeakValueDictionary
import pyte
import keymap
import os
import sys
from collections import namedtuple

Coord = namedtuple("Coord", ["x", "y"])

try:
    import tty
    import pty
except ImportError:
    pass

sys.path.append(os.getcwdu())

class Supervisor(object):
    def __init__(self):
        self.processes = WeakValueDictionary()

    def register(self, process):
        self.processes[process.id] = process

    def process(self, process_id):
        if process_id in self.processes:
            return self.processes[process_id]
        return None

    def read_all(self):
        for process in self.processes.values():
            process.read()


class Process(object):
    DEFAULT_COLUMNS = 80
    DEFAULT_LINES   = 24
    MIN_COLUMNS     = 10
    MIN_LINES       = 2 

    def __init__(self, supervisor):
        from uuid import uuid4
        self.id = uuid4().hex
        self._supervisor = supervisor
        self._views = []
        self._columns = self.DEFAULT_COLUMNS
        self._lines = self.DEFAULT_LINES
        
        self._supervisor.register(self)

    def attach_view(self, view):
        """Connect a View(thing that displays Process output) to this Process"""
        self._views.append(view)
        view.process = self

    def detach_view(self, view):
        """Detaches a view that was previously added"""
        pass

    @property
    def columns(self):
        return self._columns

    @property
    def lines(self):
        return self._lines

    def available_columns(self):
        ac = min((v.available_columns() for v in self._views))
        return max(ac, self.MIN_COLUMNS)

    def available_lines(self):
        al = min((v.available_lines() for v in self._views))
        return max(al, self.MIN_LINES)

    def start(self):
        raise NotImplemented

    def stop(self):
        raise NotImplemented

    def is_running(self):
        raise NotImplemented

    def send_bytes(self, bytes):
        raise NotImplemented

    def send_keypress(self, key, ctrl=False, alt=False, shift=False, super=False):
        raise NotImplemented

    def send_click(self, row, col, **kwds):
        raise NotImplemented

    def read(self):
        raise NotImplemented



class PtyProcess(Process):
    
    DEFAULT_LOCALE = 'en_US.UTF8'
    KEYMAP = keymap.ANSI

    def __init__(self, supervisor, cmd=None, env=None, cwd=None):
        super(PtyProcess, self).__init__(supervisor)
        self._cmd = cmd or [os.environ.get("SHELL")]
        self._env = env or os.environ
        self._env["TERM"] = "linux"

        self._cwd = cwd or "."
        self._process = None
        self._master = None
        self._slave = None
        
        self._stream = pyte.ByteStream()
        self._dbg_steram = None #pyte.DebugStream()
        self._screens = {'diff': pyte.DiffScreen(self.DEFAULT_COLUMNS, self.DEFAULT_LINES)}
        for screen in self._screens.values():
            self._stream.attach(screen)


    def start(self):
        self._start()

    def _start(self):
        (self._master, self._slave) = pty.openpty()
        #ttyname = os.ttyname(self._slave)
        self._process = subprocess.Popen(self._cmd, stdin=self._slave, 
                                         stdout=self._slave, stderr=self._slave, shell=False, 
                                         env=self._env, close_fds=True, preexec_fn=os.setsid)
        
    def refresh_views(self):
        sc = self._screens['diff']
        dis = sc.display
        lines_dict = dict((lineno, dis[lineno]) for lineno in sc.dirty)
        sc.dirty.clear()
        cursor = self._screens['diff'].cursor
        for v in self._views:
            v.diff_refresh(lines_dict, cursor)

    def read(self):
        self._read()

    def _read(self):
        import select
        
        read = 0
        while True:
            (r,w,x) = select.select([self._master], [], [], 0)
            if not r:
                break # no input
            if not self.is_running(): 
                return # dont lock on exit!
            data = os.read(self._master, 1024)
            read += len(data)
            self._stream.feed(data)
            if self._dbg_steram:
                self._dbg_steram.feed(data)
        if read:
            self.refresh_views()
        return read

    def send_bytes(self, bytes):
        if self.is_running():
            os.write(self._master, bytes)

    def stop(self):
        self._process.kill()
        self._process = None 
        return 

    def is_running(self):
        return self._process is not None and self._process.poll() is None

    def send_ctrl(self, key):
        char = key.lower()
        a = ord(char)
        if a>=97 and a<=122:
            a = a - ord('a') + 1
            return self.send_bytes(chr(a))
        d = {'@':0, '`':0, '[':27, '{':27, '\\':28, '|':28, ']':29, '}': 29,
            '^':30, '~':30,'_':31, '?':127}
        if char not in d:
            return
        return self.send_bytes(chr(d[char]))

    def send_keypress(self, key, ctrl=False, alt=False, shift=False, super=False):
        if ctrl and len(key)==1:
            self.send_ctrl(key)
            self._read()
            return 
        bytes = key
        if key in self.KEYMAP:
            d = self.KEYMAP[key]
            flags = 0
            flags |= keymap.CTRL * ctrl
            if isinstance(d, dict):
                if flags in d:
                    bytes = d[flags]
                else:
                    bytes = key
            else:
                bytes = d
        self.send_bytes(bytes)
        self._read()


class Win32Process(Process):
    KEYMAP = keymap.WIN32
    SIZE_REFRESH_EACH = 20 # reads

    def start(self):
        from console.console_client import ConsoleClient
        self._cc = ConsoleClient("localhost", 8828)
        self._lines = {}
        self._reads = 1
        self._width = 0
        self._height = 0

    def stop(self):
        pass

    def is_running(self):
        return self.__cc.is_running

    def send_bytes(self, bytes):
        self._cc.write_console_input(bytes)

    def send_keypress(self, key, ctrl=False, alt=False, shift=False, super=False):
        self._cc.send_keypress(key, ctrl=ctrl, alt=alt, shift=shift, super=super)
        self.read()

    def send_click(self, row, col, **kwds):
        self._cc.send_click(row, col, **kwds)
        self.read()

    def read(self):
        full = False
        self._reads = (self._reads + 1) % self.SIZE_REFRESH_EACH
        if not self._reads:
            self._size_refresh()
            full = True

        (_lines, _cursor_pos) = self._cc.read(full)
        cursor_pos = Coord(*_cursor_pos) # we need .x .y access
        lines = {}
        for k,v in _lines.items():
            lines[int(k)] = v
        for v in self._views:
            if full:
                v.full_refresh(lines, cursor_pos)
            else:
                v.diff_refresh(lines, cursor_pos)

    def _size_refresh(self):
        height = self.available_lines()
        width = self.available_columns()
        if self._width == width and self._height == height:
            return 
        self._width = width
        self._height = height
        self._cc.set_window_size(width, height)


class SublimeView(object):
    def __init__(self, view=None):
        v = view or self._new_view()
        self._view = v
        self._process = None
        
        v.settings().set("sublimepty", True)
        v.settings().set("line_numbers", False)
        v.settings().set("caret_style", "blink")
        v.settings().set("auto_complete", False)
        v.settings().set("draw_white_space", "none")
        v.settings().set("word_wrap", False)
        v.settings().set("gutter", False)
        #v.settings().set("color_scheme", "Packages/SublimePTY/SublimePTY.tmTheme")
        v.set_scratch(True)
        v.set_name("TERMINAL")

    @property
    def process(self):
        return self._process

    @process.setter
    def process(self, new_process):
        if self._process:
            self._process.detach_view(self)
        self._process = new_process
        if new_process:
            self._view.settings().set("sublimepty_id", new_process.id)
            self._fill_stars(new_process._columns, new_process._lines)
        else:
            self._view.settings().set("sublimepty_id", None)
            
    def _fill_stars(self, columns, lines):
        self.full_refresh(["*"*columns]*lines)

    def _new_view(self):
        import sublime
        return sublime.active_window().new_file()

    def available_columns(self):
        (w, h) = self._view.viewport_extent()
        return int(w // self._view.em_width())

    def available_lines(self):
        (w, h) = self._view.viewport_extent()
        return int(h // self._view.line_height())

    def _set_cursor(self, cursor):
        import sublime
        if not cursor:
            return 
        self._view.sel().clear()
        tp = self._view.text_point(cursor.y, cursor.x)
        self._view.sel().add(sublime.Region(tp, tp))
        
    def full_refresh(self, lines, cursor=None):
        import sublime
        v = self._view
        ed = v.begin_edit()
        whole = sublime.Region(0, v.size())
        v.erase(ed, whole)
        for idx in range(len(lines)):
            l = lines[idx]
            p = v.text_point(idx, 0)
            v.insert(ed, p, l + "\n")
        if cursor:
            self._set_cursor(cursor)
        v.end_edit(ed)

    def diff_refresh(self, lines_dict, cursor=None):
        import sublime
        v = self._view
        ed = v.begin_edit()
        for lineno, text in lines_dict.items():
            p = v.text_point(lineno, 0)
            line_region = v.line(p)
            v.replace(ed, line_region, text)
        if cursor:
            self._set_cursor(cursor)
        v.end_edit(ed)
