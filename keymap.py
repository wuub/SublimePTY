
CTRL = 0x01
ALT = 0x02
SHIFT = 0x04
SUPER = 0x08

ANSI = {
	"enter": "\n", 
	"tab": "\t", 
	"f10": "\x1b[21~", 
    "space": " ",
    "f8": "\e[[19~",
    "escape": "\x1b\x1b",
    "down": "\x1b[B",
    "up": "\x1b[A", 
    "right": "\x1b[C",
    "left": "\x1b[D",
    "backspace": "\b",
    "c": {CTRL: chr(3)}
}


WIN32 = {
    "enter": "\r",
    "tab": "\t",
    "backspace": "\b",
    "up": chr(38),
    "down": chr(40)
}