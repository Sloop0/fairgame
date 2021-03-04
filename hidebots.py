import ctypes
import win32gui
import win32process
import win32api
from utils.count_processes import count_processes
from utils.logger import log
# from time import perf_counter

vdesks = ctypes.WinDLL("g:\\nvidia-bot\\VirtualDesktopAccessor.dll")

foundcount = 0
titles = {}
counters = count_processes()

def foreach_window(hwnd, lParam):
    global foundcount
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd).lower()
        thisdesk = vdesks.GetWindowDesktopNumber(hwnd)
        exe = ''
        if title.find("amazon") != -1 and thisdesk == 0:
            pid = win32process.GetWindowThreadProcessId(hwnd)
            if len(pid) <= 2:
                for p in pid:
                    try:
                        count = counters[p]
                    except KeyError:
                        count = 1
                    if count < 2:
                        try:
                            hndl = win32api.OpenProcess(0x0400 | 0x0010, False, p)
                            exe = win32process.GetModuleFileNameEx(hndl, False)
                        except:
                            exe = ''
                        if exe == 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe':
                            foundcount += 1
                            vdesks.MoveWindowToDesktopNumber(hwnd, 1)
                            win32gui.FlashWindowEx(hwnd, 0, 0, 0)
                            win32gui.ShowWindow(hwnd, 0)
                            titles[p] = hwnd
                            log.info(f'Moving window {title} to desktop #2.')
                            break
    return True


def hidebots(count, queue):
    # win32api.SetConsoleCtrlHandler(None, True)
    global foundcount
    while foundcount < count:
        win32gui.EnumWindows(foreach_window, 0)
    # foundcount = 0
    # start = perf_counter()
    # while foundcount < count and perf_counter() - start < 10:
    #     try:
    #         msg = queue.get(timeout=1)
    #         win32gui.FlashWindowEx(titles[msg], 0, 0, 0)
    #     except queue.empty:
    #         pass
    while True:
        msg = queue.get()
        if msg[1]:
            try:
                win32gui.ShowWindow(titles[msg[0]], 5)
                ES_CONTINUOUS = 0x80000000
                ES_SYSTEM_REQUIRED = 0x00000001
                ES_DISPLAY_REQUIRED = 0x00000002
                ctypes.windll.kernel32.SetThreadExecutionState(
                    ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
                log.info(f'Displaying window with pid {msg[0]}.')
            except win32gui.error:
                log.error(f'Error showing window with pid {msg[0]}.')
        else:
            try:
                win32gui.ShowWindow(titles[msg], 0)
                ES_CONTINUOUS = 0x80000000
                ES_SYSTEM_REQUIRED = 0x00000001
                ctypes.windll.kernel32.SetThreadExecutionState(
                    ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
                log.info(f'Hiding window with pid {msg[0]}.')
            except win32gui.error:
                log.error(f'Error hiding window with pid {msg[0]}.')