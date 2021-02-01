import subprocess
def killdupes():
    subprocess.call(["powershell", "Stop-Process -ErrorAction SilentlyContinue -Name 'chromedriver_win32'"])