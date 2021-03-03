import ctypes
import win32gui
import win32process
import win32api
from utils.logger import log
import time

vdesks = ctypes.WinDLL("g:\\nvidia-bot\\VirtualDesktopAccessor.dll")

foundcount = 0

def foreach_window(hwnd, lParam):
    global foundcount
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd).lower()
        thisdesk = vdesks.GetWindowDesktopNumber(hwnd)
        exe = ''
        if title.find("amazon") != -1 and thisdesk == 0:
            pid = win32process.GetWindowThreadProcessId(hwnd)
            for p in pid:
                try:
                    hndl = win32api.OpenProcess(0x0400 | 0x0010, False, p)
                    exe = win32process.GetModuleFileNameEx(hndl, False)
                except:
                    exe = ''
                if exe == 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe':
                    foundcount += 1
                    vdesks.MoveWindowToDesktopNumber(hwnd, 1)
                    win32gui.ShowWindow(hwnd, 1)
                    log.info(f'Moving window {title} to desktop #2.')
                    break
    return True


def hidebots(count):
    start = time.perf_counter()
    global foundcount
    while foundcount < count or time.perf_counter() - start < 60:
        win32gui.EnumWindows(foreach_window, 0)
