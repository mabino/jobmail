import psutil
import win32api
import win32con
import win32gui_struct
import win32process
import smtplib
from email.mime.text import MIMEText

def get_processes():
    process_list = []
    for process in psutil.process_iter():
        try:
            process_list.append(process.name())
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return process_list

def get_process_id(process_name):
    for process in psutil.process_iter():
        if process.name() == process_name:
            return process.pid
    return None

def send_email(process_name):
    msg = MIMEText("The process '{}' has quit or exited.".format(process_name))
    msg['Subject'] = 'Process Quit or Exited'
    msg['From'] = 'your_email_address@example.com'
    msg['To'] = 'to_email_address@example.com'

    # Connect to an SMTP server
    server = smtplib.SMTP('smtp.example.com')
    server.login('your_email_address@example.com', 'password')
    server.send_message(msg)
    server.quit()

def taskbar_notify_icon(hwnd, msg, wparam, lparam):
    if lparam == win32con.WM_LBUTTONUP:
        pass
    elif lparam == win32con.WM_RBUTTONUP:
        win32api.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    return True

def add_to_system_tray(icon_path, hover_text):
    message_map = {
        win32con.WM_DESTROY: win32api.PostQuitMessage,
    }
    wc = win32gui.WNDCLASS()
    hinst = wc.hInstance = win32api.GetModuleHandle(None)
    wc.lpszClassName = "PythonTaskbarDemo"
    wc.lpfnWndProc = message_map
    classAtom = win32gui.RegisterClass(wc)
    style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
    hwnd = win32gui.CreateWindow(
        classAtom,
        "TaskbarDemo",
        style,
        0,
        0,
        win32con.CW_USEDEFAULT,
        win32con.CW_USEDEFAULT,
        0,
        0,
        hinst,
        None
    )
    hicon = win32gui.LoadImage(
        hinst,
        icon_path,
        win32con.IMAGE_ICON,
        0,
        0,
        win32con.LR_DEFAULTSIZE | win32con.LR_LOADFROMFILE
    )
    flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE
flags |= win32gui.NIF_TIP
nid = (hwnd, 0, flags, win32con.WM_USER+20, hicon, hover_text)
win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
win32gui.PumpMessages()

if __name__ == "__main__":
    processes = get_processes()
    print("Running Processes:")
    for i, process in enumerate(processes):
        print("{}. {}".format(i+1, process))
    process_index = int(input("Enter the number of the process to monitor: ")) - 1
    process_name = processes[process_index]
    process_id = get_process_id(process_name)

    add_to_system_tray("icon.ico", "Monitoring process: {}".format(process_name))
    process = psutil.Process(process_id)
    while process.is_running():
        pass

    send_email(process_name)
