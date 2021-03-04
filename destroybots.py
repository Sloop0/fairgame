import win32gui
import win32process
import win32api
import time
from utils.count_processes import count_processes
from utils.logger import log

start = time.perf_counter()
counters = count_processes()

def foreach_window(hwnd, lParam):
    global start
    title = win32gui.GetWindowText(hwnd).lower()
    if title.find("amazon") != -1:
        pid = win32process.GetWindowThreadProcessId(hwnd)
        if len(pid) <= 2:
            for p in pid:
                try:
                    count = counters[p]
                except KeyError:
                    count = 1
                if count < 2:
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