#! coding: utf-8

import ctypes
from ctypes import windll
user32 = windll.user32

# http://msdn.microsoft.com/en-us/library/windows/desktop/dd375731(v=vs.85).aspx
# Winuser.h
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12

NULL = 0x00
KB_STATES_SIZE = 256
# high-order bit == 1 means the key is down
# See GetKeyboardState function for more information:
# http://msdn.microsoft.com/en-us/library/windows/desktop/ms646299(v=vs.85).aspx
KB_STATE_KEY_DOWN = 0xF0


def unichar_to_virtual_key(c):
    # return vk code and keyboard state
    rv = user32.VkKeyScanA(ord(c))
    virtual_key_code = rv & 0xFF
    keyboard_state = rv >> 8

    translated_states = dict(shift=False, ctrl=False, alt=False)

    if keyboard_state & 0x01 == 0x01:
        translated_states["shift"] = True
    if keyboard_state & 0x02 == 0x02:
        translated_states["ctrl"] = True
    if keyboard_state & 0x04 == 0x04:
        translated_states["alt"] = True

    return virtual_key_code, translated_states


def kb_to_unicode(unichar, shift=False, ctrl=False, alt=False, **kwd):
    # Converts key binding to unicode char on Windows
    virtual_key_code, _ = unichar_to_virtual_key(unichar)

    # See GetKeyboardState function for more information:
    # http://msdn.microsoft.com/en-us/library/windows/desktop/ms646299(v=vs.85).aspx
    states_as_bytes = (ctypes.c_byte * KB_STATES_SIZE)(*((NULL,) * KB_STATES_SIZE))
    if shift:
        states_as_bytes[VK_SHIFT] = KB_STATE_KEY_DOWN
    if ctrl:
        states_as_bytes[VK_CONTROL] = KB_STATE_KEY_DOWN
    if alt:
        states_as_bytes[VK_MENU] = KB_STATE_KEY_DOWN

    # will fail with dead keys
    rv = ctypes.create_string_buffer(1)
    user32.ToUnicode(
                virtual_key_code,
                None,
                states_as_bytes,
                rv,
                len(rv),
                0
                )

    return rv.value[0]


if __name__ == '__main__':
    # this will only make sense in one keyboard layout for Spanish
    print kb_to_unicode(u"2", ctrl=True, alt=True), "@"
    print kb_to_unicode(u"1", ctrl=True, alt=True), "|"
    print kb_to_unicode(u"1", ctrl=False, alt=False), "1"
    print kb_to_unicode(u"a", ctrl=False, alt=False), "a"
