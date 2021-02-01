import ctypes
import win32gui

vdesks = ctypes.WinDLL("g:\\nvidia-bot\\VirtualDesktopAccessor.dll")

foundcount = 0


# parent = 0
#
# def getchildren(hwnd, firstornot):
#     global parent
#     if firstornot:
#         win32gui.SetParent(hwnd, parent)
#     return True

def foreach_window(hwnd, lParam):
    global foundcount
    global parent
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd).lower()
        thisdesk = vdesks.GetWindowDesktopNumber(hwnd)
        if title.find("amazon") != -1 and title.find("nvidia-bot") == -1 and thisdesk == 0:
            # if foundcount == 0:
            #     parent = hwnd
            # win32gui.EnumChildWindows(hwnd, getchildren, foundcount)
            foundcount += 1
            vdesks.MoveWindowToDesktopNumber(hwnd, 1)
    return True


def hidebots():
    while foundcount < 7:
        win32gui.EnumWindows(foreach_window, 0)
