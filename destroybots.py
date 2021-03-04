import win32gui
import win32process
import win32api
import time
from utils.logger import log

start = time.perf_counter()


def foreach_window(hwnd, lParam):
    global start
    title = win32gui.GetWindowText(hwnd).lower()
    exe = ''
    if title.find("amazon") != -1:
        pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in pid:
            try:
                hndl = win32api.OpenProcess(0x0400 | 0x0010 | 0x0001, False, p)
                exe = win32process.GetModuleFileNameEx(hndl, False)
            except:
                exe = ''
            if exe == 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe':
                try:
                    win32api.TerminateProcess(hndl, -1)
                    log.info(f'Terminated Chrome window {title}.')
                    start = time.perf_counter()
                except win32api.error:
                    log.info(f'Unable to terminate process {title}.')
                break
    return True


def destroybots():
    # win32api.SetConsoleCtrlHandler(None, True)
    global start
    while True:
        win32gui.EnumWindows(foreach_window, 0)
        if time.perf_counter() - start > 5:
            exit()

if __name__ == "__main__":
    destroybots()