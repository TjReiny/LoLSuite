# -*- coding: utf-8 -*-
import tkinter.filedialog
import ctypes
import urllib.request
import os
import os.path
import configparser
import customfont
from psutil import *
from time import sleep
from webbrowser import open_new
from base64 import b64decode
from _thread import start_new_thread
from tkinter import *
from shutil import rmtree
from configparser import ConfigParser
# functions
def launch_core(mode):
    main.patch_button.config(state=DISABLED)
    main.restore_button.config(state=DISABLED)
    main.unblock_button.config(state=DISABLED)
    main.window.update()

    if download_core() == None: # no error
        create_core_ini()

    main.window.withdraw()

    if mode == 0:
        patch()

    elif mode == 1:
        restore()

    elif mode == 2:
        unblock_dx()

    elif mode == 3:
        patch_game()

    elif mode == 4:
        patch_client()

    main.patch_button.config(state=NORMAL)
    main.restore_button.config(state=NORMAL)
    main.unblock_button.config(state=NORMAL)
    main.window.deiconify()

def download_core():
    global DOWNLOAD_CHAR, UPTODATE_CHAR, UPDATE_FAILED_CHAR

    main.progress_label.config(text =DOWNLOAD_CHAR)
    write_output("Downloading core..")

    try:
        data = get_data("http://lolupdater.com/downloads/MOBAUpdater.exe")
        with open("core.exe", "wb") as core_exe:
            core_exe.write(data)
        
        main.progress_label.config(text =UPTODATE_CHAR)
        write_output("Core has been successfully downloaded")

        return None

    except:
        main.progress_label.config(text =UPDATE_FAILED_CHAR)
        write_output("Error while downloading core", "red")

        return False

def create_core_ini():
    global options

    write_output("Creating core ini file..")

    with open("LoLUpdater.ini", "w") as lucore_ini:
        lucore_ini.write(options["lolPath"])

    write_output("Successfully created core ini file")

def patch_client():
    os.system("core.exe -p -co")

def patch_game():
    os.system("core.exe -p -go")

def unblock_dx():
    os.system("core.exe -d")

def restore():
    os.system("core.exe -r")

def patch():
    os.system("core.exe -p")

def x3D_edit(mode):
    global config
    path = options["lolPath"]+"/Config/game.cfg"
    config.read(path)

    if mode == 0:
        config.set("General", "x3d_platform", "0")
        main.x3d0.state_set(True)
        main.x3d1.state_set(False)
        main.x3d5.state_set(False)

    elif mode == 1:
        config.set("General", "x3d_platform", "1")
        main.x3d1.state_set(True)
        main.x3d0.state_set(False)
        main.x3d5.state_set(False)

    elif mode == 5:
        config.set("General", "x3d_platform", "5")
        main.x3d5.state_set(True)
        main.x3d1.state_set(False)
        main.x3d0.state_set(False)

    else:
        config.remove_option("General", "x3d_platform")
        main.x3d5.state_set(False)
        main.x3d1.state_set(False)
        main.x3d0.state_set(False)

    with open(path, "w") as game_cfg:
        config.write(game_cfg)

    if mode != -1:
        write_output("Some modes of the new x3D engine can throw error messages", "red")

def get_data(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        return urllib.request.urlopen(req).read()

    except:
        return False

def write(content, tag):
    try:
        main.out.configure(state =NORMAL)
        main.out.insert(END, content+'\n', tag)
        main.out.see(END)
        main.out.configure(state =DISABLED)
        main.out.update()
    except:
        pass

def write_output(content, tag="default"):
    write(content, tag)

def check_for_lol_processes():
    global clientProcs
    for process in process_iter():
        if process.name() in clientProcs:
            return True
    return False

def check_for_ingame():
    for process in process_iter():
        if process.name() == 'League of Legends.exe':
            return True
    return False

def ask_for_lol_path():
    lolPath = filedialog.askdirectory(title = 'Select your League of Legends installation folder')
    if lolPath == "":
        quit()
    else:
        return lolPath

def configure_cfg(section, option, value):
    global config, cfg_path

    config.read(cfg_path)

    config.set(section, option, value)

    with open(cfg_path, 'w') as game_cfg:
        config.write(game_cfg)

def nice_lol_process():
    global wait
    wait = True
    for process in process_iter():
        if process.name() == "League of Legends.exe":
            if main.real_time.state:
                process.nice(REALTIME_PRIORITY_CLASS)
                write_output("Real time priority has been set for League of Legends.exe")

            else:
                process.nice(HIGH_PRIORITY_CLASS)
                write_output("High priority has been set for League of Legends.exe")
            
            wait = False
            return True
    wait = False
    return False

def idle_lu():
    global SELF_PROCESS
    SELF_PROCESS.nice(IDLE_PRIORITY_CLASS)

def restore_lu():
    global SELF_PROCESS
    SELF_PROCESS.nice(NORMAL_PRIORITY_CLASS)

def start():
    global suspend, report_bool, REPORT_CHARACTER
    suspend = True

    while suspend:

        if nice_lol_process():
            idle_lu()
            if not report_bool:
                main.report_button.button.config(state=NORMAL, cursor="hand2")

        else:
            if report_bool:
                start_new_thread(report_notification, ())
                report_bool = False
            main.report_button.config(state=DISABLED, cursor="arrow", text=REPORT_CHARACTER)

            restore_lu()

        sleep(10)

def stop():
    global suspend
    suspend = False
    restore_lol_processes()
    save_data()
    
def restore_lol_processes():
    mainOpened = 'main' in globals()
    if mainOpened:
        for process in process_iter():
            name = process.name()
            if name == 'League of Legends.exe':
                process.nice(NORMAL_PRIORITY_CLASS)
                write_output('NORMAL priority has been set for '+name)

    else:
        for process in process_iter():
            name = process.name()
            if name == 'League of Legends.exe':
                process.nice(NORMAL_PRIORITY_CLASS)

def elevate():
    save_data()
    create_temp_file()
    if ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1) == 5:
        write_output('We need admin permissions for "Real time" option to work!', "red")
        if main.real_time.state:
            main.real_time.switch()
        if options["real_time"]:
            options["real_time"] = False
        delete_temp_file()

    else:
        root.splash_elevate()

def create_data():
    DEFAULT_DATA = "[General]\nlol_path = NoPath\nfont_installed = 0\n\n[Prefferencies]\nreal_time_enabled = False\n\n[UserInterface]\noutput_visible = True\n"

    with open('data.lpb', 'w') as lpb_data:
        lpb_data.write(DEFAULT_DATA)
    
    ctypes.windll.kernel32.SetFileAttributesW("data.lpb", 0x02)

def save_data():
    global options
    ctypes.windll.kernel32.SetFileAttributesW("data.lpb", 0x00)

    saver = ConfigParser()
    saver.read("data.lpb")
    saver.set("General", "lol_path", options["lolPath"])
    saver.set("Prefferencies", "real_time_enabled", str(options["real_time"]))
    saver.set("UserInterface", "output_visible", str(options["output"]))
    saver.set("General", "font_installed", str(options["font_installed"]))

    with open('data.lpb', 'w') as lpb_data:
        saver.write(lpb_data)

    ctypes.windll.kernel32.SetFileAttributesW("data.lpb", 0x02)

    del saver

def read_data():
    global options
    if not os.path.exists("data.lpb"):
        create_data()

    try:
        reader = ConfigParser()
        reader.read("data.lpb")
        
        lol_path = reader.get("General", "lol_path")
        real_time_enabled = reader.getboolean("Prefferencies", "real_time_enabled")
        write_output_visible = reader.getboolean("UserInterface", "output_visible")
        font_installed = reader.getboolean("General", "font_installed")

        if lol_path == "NoPath":
            lol_path = ask_for_lol_path()

        options = {"lolPath": lol_path, "real_time": real_time_enabled, "output": write_output_visible, "font_installed": font_installed}

    except:
        delete_data()
        create_data()
        read_data()

    del reader

def delete_data():
    try:
        ctypes.windll.kernel32.SetFileAttributesW("data.lpb", 0x00)
        os.remove("data.lpb")
    except FileNotFoundError:
        pass

def update_options():
    global options, output_visible
    options = {"write_output": output_visible,
               "real_time": main.real_time.state if "main" in globals() else False,
               "lolPath": options["lolPath"]}



def clickwin(event, window):
    window.offsetx=event.x
    window.offsety=event.y

def dragwin(event, window):
    window.lift()
    x = window.winfo_pointerx()-window.offsetx
    y = window.winfo_pointery()-window.offsety
    window.geometry('+%d+%d' % (x, y))

def decode_images():
    global bgImage

    bgImage = \
    """
    R0lGODlhMwAyAOcAAAAAAAAAMwAAZgAAmQAAzAAA/wArAAArMwArZgArmQArzAAr/wBVAABVMwBV
    ZgBVmQBVzABV/wCAAACAMwCAZgCAmQCAzACA/wCqAACqMwCqZgCqmQCqzACq/wDVAADVMwDVZgDV
    mQDVzADV/wD/AAD/MwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMrADMrMzMrZjMrmTMr
    zDMr/zNVADNVMzNVZjNVmTNVzDNV/zOAADOAMzOAZjOAmTOAzDOA/zOqADOqMzOqZjOqmTOqzDOq
    /zPVADPVMzPVZjPVmTPVzDPV/zP/ADP/MzP/ZjP/mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2Yr
    AGYrM2YrZmYrmWYrzGYr/2ZVAGZVM2ZVZmZVmWZVzGZV/2aAAGaAM2aAZmaAmWaAzGaA/2aqAGaq
    M2aqZmaqmWaqzGaq/2bVAGbVM2bVZmbVmWbVzGbV/2b/AGb/M2b/Zmb/mWb/zGb//5kAAJkAM5kA
    ZpkAmZkAzJkA/5krAJkrM5krZpkrmZkrzJkr/5lVAJlVM5lVZplVmZlVzJlV/5mAAJmAM5mAZpmA
    mZmAzJmA/5mqAJmqM5mqZpmqmZmqzJmq/5nVAJnVM5nVZpnVmZnVzJnV/5n/AJn/M5n/Zpn/mZn/
    zJn//8wAAMwAM8wAZswAmcwAzMwA/8wrAMwrM8wrZswrmcwrzMwr/8xVAMxVM8xVZsxVmcxVzMxV
    /8yAAMyAM8yAZsyAmcyAzMyA/8yqAMyqM8yqZsyqmcyqzMyq/8zVAMzVM8zVZszVmczVzMzV/8z/
    AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8Amf8AzP8A//8rAP8rM/8rZv8rmf8rzP8r//9VAP9V
    M/9VZv9Vmf9VzP9V//+AAP+AM/+AZv+Amf+AzP+A//+qAP+qM/+qZv+qmf+qzP+q///VAP/VM//V
    Zv/Vmf/VzP/V////AP//M///Zv//mf//zP///wAAAAAAAAAAAAAAACH+EUNyZWF0ZWQgd2l0aCBH
    SU1QACH5BAEKAP8ALAAAAAAzADIAAAj+AEkIHEiwoMGDCBMqXGgQQAyHEB8ynEjxYQwDMS5qxAiR
    okeCEQ2ssLhCZIySGTnG+MjQoUaHIlXGtOiyI8uDMEfWzJgTI0qUGCXeJBgUpsWZO2WWRAlgKAmH
    Sy+O9Bl0ZlSTWHmyTAmUqVSrGJWqZPox5E+qUl+eDOt15kqKRs8ejZqRZ1qsU2lOTOr1box9gAFn
    lNvX5UK7YNei/Bs48NejFiE3TZhT7UyTjTNbbrvUQEKZkV36ZJy5cV28foUaPDvVq8PSsE9q5GwS
    IWi3LmHrpvlYcsO1ilVm1E1cLe+jBjd2TUu8ecrISn+zVunc+Vy8nokCX0669GCMxR/+4ybIWWN3
    zXPPm6baGiPB65HDi5ZdHGho7Ytz776+uLjJyiB9hVJ9d+UF3m75XfTefOo5BlpPIzUoWGeqkdBX
    eF4lyNxuRb0lEFr1oaVST3UVVxNRA+732FUFYoage+9JuE9w4un0mEsyVijQDRICRxJalWHX4w2/
    1WVkaMqhBd9OR56GE3BuIQUciXIlBt0KB6nlGmJT1qgkiVAhFBKSiYnW2o3pYZVdlv+tqBSaWSUo
    pUJZ8QWnXGYJdyKdcqZ5ppQFbjYRb2Xe2eFlXnk0m4gG5lVeTH96RKFREKJ5ZYc6MhQok4kBSqmH
    LD24GVstBueUQIShJiSJa576lHgeS1oqkqvJQbooknPRmlCXnaKka0Vm+vTrsMQWy1JAADs=
    """

    bgImage = b64decode(bgImage)
    bgImage = bgImage = PhotoImage(data = bgImage)

def option_modify(option, value):
    global options, suspend
    options[option] = value
    if option == "real_time":
        if value:
            if not ctypes.windll.shell32.IsUserAnAdmin(): elevate()
        nice_lol_process()

def check_for_updates(view_changelog):
    global VERSION_NUMBER, latest, DOWNLOAD_CHAR
    main.progress_label.config(text="")
    try:
        req = urllib.request.Request("https://lolupdater.com/LPB/version.lpb", headers={'User-Agent': 'Mozilla/5.0'})
        cloudData = urllib.request.urlopen(req).read().decode()
        if cloudData != str(VERSION_NUMBER):
            main.progress_label.config(text=DOWNLOAD_CHAR)
            req = urllib.request.Request("https://lolupdater.com/downloads/LPB.exe", headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req).read()
            newName = "LPB_%s.exe" % str(cloudData)
            with open(newName, "wb") as newLpb:
                newLpb.write(data)
            main.progress_label.config(text="")
            temp()
            os.startfile('"' + os.getcwd() + chr(92) + newName + '"')
            root.splash_update()

        else:
            latest = True
            main.progress_label.config(text=str(VERSION_NUMBER) + " ")
            if view_changelog:
                changelog()

    except urllib.error.URLError:
        main.progress_label.config(text="")

def delete_logs():
    try:
        rmtree(getLolPath()+"\Logs")
        write_output("Deleted logs")
    except FileNotFoundError:
        pass
    except:
        write_output("Error while deleting logs!")

def source_update():
    try:
        req = urllib.request.Request("https://lolupdater.com/LPB/status.lpb", headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req).read().decode()
        write_output(data, "red")
    except:
        pass

def changelog():
    try:
        req = urllib.request.Request("https://lolupdater.com/LPB/changelog.lpb", headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req).read().decode()
        write_output(data)
    
    except:
        write_output("Server connection error!")

def _help():
    write_output("Help:")
    source_update()
    write_output("Disabling per pixel point lighting - FPS+\nDisabling grass swaying - FPS+\nUsing real time priority can make your system unstable while playing LoL. Not recommended to users with one core processor. Can drastically improve FPS and keyboard latency.\nThanks for using LPB, ©LoLUpdater team 2017\n LPB"+str(VERSION_NUMBER))

def logout():
    for process in process_iter():
        if process.name() == "LeagueClient.exe":
            process.kill()

    with open(options["lolPath"]+"\Config\LeagueClientSettings.yaml", "r") as file:
        data = file.read()

    data = data.replace("rememberMe: true", "rememberMe: false")
    username = data.split('"')[9]
    data = data.replace(username, "")
    with open(options["lolPath"]+"\Config\LeagueClientSettings.yaml", "w") as file:
        file.write(data)

    delete_logs()

    startLol()

def set_report():
    global report_bool
    report_bool = True
    main.report_button.button.config(state=DISABLED, cursor="arrow")

def report_notification():
    global report_bool
    notif = Notification(text="You wanted to report someone.")
    report_bool = False

def start_lol():
    if not check_for_lol_processes():
        write_output("Starting League of Legends..")
        os.startfile('"'+options["lolPath"]+'\LeagueClient.exe"')
        write_output("Started League of Legends")

def close_app():
    global main, root
    root.window.destroy()
    stop()

def create_temp_file():
    open("temp.lpb", 'a').close()

def delete_temp_file():
    try:
        os.remove("temp.lpb")
    except:
        pass

def sync_with_server():
    check_for_updates(False)
    source_update()

def font_prompt():
    test_prompt = Prompt("We need to install custom font on your system for our app to work.\nIf the font will not be installed items in our app can look weird.\nDo you agree with font installation?")
    result = test_prompt.result
    del test_prompt
    return result

def center_window(window):
    window.update()
    screen_width = window.winfo_screenwidth() #obtaining information
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    x = (screen_width/2)-(window_width/2) #calculating position
    y = (screen_height/2)-(window_height/2)

    window.geometry('+%d+%d' % (x, y)) #setting position

def load_icon_font():
    global DOWNLOAD_CHAR, UPTODATE_CHAR, VERSION_NUMBER, UPDATE_FAILED_CHAR

    write_output("Downloading font file..")
    main.progress_label.config(text =DOWNLOAD_CHAR)
    main.progress_label.update()

    font_data = get_data("http://lolupdater.com/downloads/segmdl2.ttf")

    if font_data == None:
        write_output("Error while getting font from the server!", "red")
        main.progress_label.config(text = UPDATE_FAILED_CHAR)
        return

    with open("segmdl2.ttf", 'wb') as font_file:
        font_file.write(font_data)

    customfont.loadfont("segmdl2.ttf", private =False, enumerable =False)
    os.remove("segmdl2.ttf")
    options["font_installed"] = True

    main.progress_label.config(text =VERSION_NUMBER+' '+UPTODATE_CHAR)
    write_output("Font has been successfully installed")

def is_icon_font():
    write_output("Checking for required font..")
    from tkinter.font import families
    if "Segoe MDL2 Assets" in families():
        write_output("Font already installed")
        return True

    else:
        write_output("Font is not installed")
        return False

def error_message(error_type):
    try:
        main.window.withdraw()
    except:
        pass

    error_prompt = Prompt(message ="Error has occured. If you will be reporting this error\nplease describe what were you doing\nand take a screenshot of this error message.\n(error: %s)\nWhat do you want to do now?" % str(error_type), first_option ="Report error", second_option ="Quit")

    if error_prompt.result:
        report_bug()
    
    quit()

def report_bug():
    open_new(r'https://discord.gg/mwsvDnw')

def _main():
    global root, config, main, cfg_path, tippy
    delete_temp_file()
    config = ConfigParser()
    root = AppRoot()
    read_data()
    tippy = Tooltip()
    cfg_path = options["lolPath"]+"/Config/game.cfg"
    main = AppMain()
    main.update_checks()
    start_new_thread(sync_with_server, ())
    start_new_thread(start, ())
    write_output(" "*50+"! BETA !", "green")
    if not options["font_installed"]:
        if not is_icon_font():
            if font_prompt():
                load_icon_font()
            else:
                write_output("You have choose to not install custom font! You will be prompted next time you will start our app", "red")
        else:
            options["font_installed"] = True

    if not options["output"]:
        main.hide_output()

    mainloop()
    
# classes
class Prompt:
    def __init__(self, message, first_option ="Yes", second_option ="No"):
        global BG, BUTTON_ACTIVE_FACE_COLOR, PRIMARY_COLOR
        self.message = message
        self.result = None
        
        self.window = Toplevel(root.window)
        self.window.attributes("-topmost", True, "-alpha", 0)
        self.window.overrideredirect(True)
        self.window.configure(background =BUTTON_ACTIVE_FACE_COLOR, padx =1, pady =1)
        
        self.message_frame = Frame(self.window, bg =BG, padx =10, pady =10)
        self.buttons_frame = Frame(self.window, bg =BG, padx =0, pady =0)
        self.message_label = Label(self.message_frame, text =self.message, bg =BG, foreground =PRIMARY_COLOR)
        self.accept_button = StyledButton(self.window, text =first_option, command =self.accept)
        self.refuse_button = StyledButton(self.window, text =second_option, command =self.refuse)

        self.message_frame.pack()
        self.message_label.pack()
        self.buttons_frame.pack()
        self.accept_button.pack(expand =True, fill =X)
        self.refuse_button.pack(expand =True, fill =X)
        
        center_window(self.window)
        
        self.window.attributes("-alpha", 0.98)
        
        self.window.wait_window()

    def accept(self):
        self.result = True
        self.window.destroy()
    
    def refuse(self):
        self.result = False
        self.window.destroy()

class StyledLabelFrame:
    def __init__(self, master, text, x, y, width, height):
        global BG, PRIMARY_COLOR

        width+=10
        height+=10

        self.global_frame = Frame(master =master, bg =BG)
        self.outer_frame = Frame(master =self.global_frame, bg =BUTTON_ACTIVE_FACE_COLOR, width =width, height =height-10)
        self.inner_frame = Frame(master =self.outer_frame, bg =BG, width =width-2, height =height-12)
        self.content_frame = Frame(master =self.inner_frame, bg =BG, width =width-2, height =height-22)
        self.text_label = Label(master =self.global_frame, bg =BG, foreground =PRIMARY_COLOR, text =text, font =FONT)
        
        self.global_frame.place(x =x, y =y, anchor ="nw", width =width, height =height+4)
        self.outer_frame.place(x =0, y =14, anchor ="nw")
        self.inner_frame.place(x =1, y =1, anchor ="nw")
        self.content_frame.place(x =0, y =10, anchor ="nw")
        self.text_label.place(x =10, y =0, anchor ="nw")

class Tooltip:
    def __init__(self):
        global BG, FOREGROUND
        self.tooltipw = Toplevel(root.window)
        self.tooltipw.overrideredirect(True)
        self.tooltipw.attributes("-topmost", True, "-alpha", 0.90)
        self.tooltipw.configure(padx =1, pady =1, bg =BUTTON_ACTIVE_FACE_COLOR, cursor ="hand2")

        self.tooltipw.label = Label(self.tooltipw, bg =BG, foreground =PRIMARY_COLOR, font =FONT)
        self.tooltipw.label.pack()

        self.tooltipw.withdraw()

    def show(self, window, text):
        x, y = window.winfo_pointerxy()
        widget = window.winfo_containing(x, y)
        sleep(0.1)
        if window.winfo_containing(window.winfo_pointerx(), window.winfo_pointery()) == widget:
            tippy.tooltipw.label.configure(text =text)
            tippy.tooltipw.geometry("+%d+%d" % (x+30, y))
            tippy.tooltipw.deiconify()
            
            for i in range(0, 101, 20):
                tippy.tooltipw.attributes("-alpha", i/100)
                sleep(0.02)

    def hide(self):
        self.tooltipw.withdraw()

class Notification:
    def __init__(self, text=""):
        global BG, FOREGROUND
        self.window = Tk()
        self.window.attributes("-topmost", True, "-alpha", 0.99)
        self.window.overrideredirect(True)
        scw = self.window.winfo_screenwidth()
        sch = self.window.winfo_screenheight()
        self.window.geometry("300x100+%d+%d" % (scw-310, sch-140))

        self.label = Label(self.window, text=text, bg=BG, foreground=FOREGROUND, font=(FONT_NAME, 16))

        self.label.place(x=0, y=0, width=300, height=100)

        self.window.update()

        sleep(10)

        self.window.destroy()
        del self

class AppRoot:
    def __init__(self):
        self.window = Tk()
        self.window.attributes('-topmost', True, '-transparentcolor', '#00ff00', '-alpha', 0.50)
        self.window.title('LoLPriorityBooster')
        self.window.overrideredirect(True)
        
        decode_images()

        self.root_label=Label(self.window, font=('Calibri', 14, 'bold'), bg=BG, foreground='#fefefe', image=bgImage, compound=CENTER, cursor='hand2')
        self.root_label.pack(expand=True, fill=BOTH)
        self.root_label.bind("<Button-1>", lambda event: main.change_status())

        self.window.update()
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry('50x50+%d+%d' % (screen_width-60, 10))

        self.window.bind('<Button-1>', lambda event: clickwin(event, self.window))
        self.window.bind('<B1-Motion>', lambda event: dragwin(event, self.window))

        self.window.update()

    def splash_update(self):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width/2)-200
        y = (screen_height/2)-25
        self.window.geometry("400x50+%d+%d" % (x, y))
        self.root_label.config(image='', text="Please wait until new version of LPB starts")
        main.change_status()
        
        while os.path.isfile("temp.lpb"):
            sleep(1)

        close()

    def splash_elevate(self):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width/2)-160
        y = (screen_height/2)-25
        self.window.geometry("320x50+%d+%d" % (x, y))
        self.root_label.config(image='', text="Please wait until elevated LPB starts")
        self.window.update()
        main.change_status()
        
        while os.path.isfile("temp.lpb"):
            sleep(1)

        close()

class AppMain:
    status = True

    def __init__(self):
        global BG
        self.window = Toplevel()
        self.window.configure(bg=BG, padx=0, pady=0)
        self.window.overrideredirect(True)
        self.window.transient(root.window)
        self.window.attributes('-alpha', 0.97, "-transparentcolor", "green", "-topmost", True)   

        self.head_frame = Frame(self.window, bg =BG, padx =4, pady =0)
        self.content_frame = Frame(self.window, bg =BG, width =380, height =160)
        self.checks_frame = Frame(self.content_frame, bg=BG, padx=10)
        self.settings_frame = Frame(self.content_frame, bg =BG)
        self.x3d_frame = StyledLabelFrame(master =self.checks_frame, text ="X3D mode", width =120, height =50, x=180, y=56)
        self.lu_buttons_frame =Frame(self.checks_frame, bg =BG, height =34, width =380)
        self.adbutton_frame = Frame(self.window, bg=BG, padx=6, pady=0)
        self.close_button = StyledButton(self.head_frame, text='×', command=close_app, font=(ICON_FONT))
        self.minimize_button = StyledButton(self.head_frame, text='-', command=self.change_status, font=(ICON_FONT))
        self.out = Text(self.window, height = 11, width=70, state=DISABLED, wrap=WORD, font=("Calibri", 10), foreground = FOREGROUND, bg=BG, relief = FLAT, padx=10)
        self.x3d0 = X3dModeCheckbox(self.x3d_frame.content_frame, text="0", on=lambda: x3D_edit(0), off=lambda: x3D_edit(-1), x =4, y =0)
        self.x3d1 = X3dModeCheckbox(self.x3d_frame.content_frame, text="1", on=lambda: x3D_edit(1), off=lambda: x3D_edit(-1), x =44, y =0)
        self.x3d5 = X3dModeCheckbox(self.x3d_frame.content_frame, text="5", on=lambda: x3D_edit(5), off=lambda: x3D_edit(-1), x =84, y =0)
        self.bug_button = StyledButton(self.adbutton_frame, command=report_bug, text='', font=(ICON_FONT), side=RIGHT, tooltiptext ="Report a bug")
        self.progress_label = StyledButton(self.adbutton_frame, text=str(VERSION_NUMBER), command =lambda: start_new_thread(check_for_updates, (True,)), tooltiptext ="Check for updates")
        self.head_lb = Label(self.head_frame, text='    LoLUpdater', font = ("Calibri", 10), bg=BG, foreground=FOREGROUND, pady=0)
        self.colb = StyledButton(self.adbutton_frame, text='', command=self.switch_write_output, font=(ICON_FONT, 10), tooltiptext ="Collapses/expands console")
        self.settings_button =StyledButton(self.adbutton_frame, command =self.open_settings, font =ICON_FONT, text ="", tooltiptext ="Settings")
        self.logout_button = StyledButton(self.adbutton_frame, text="", command=logout, font=ICON_FONT, tooltiptext ="Logs you out from the Client")
        self.report_button = StyledButton(self.adbutton_frame, command=set_report, font=ICON_FONT, tooltiptext ="You will be notified that you wanted to report someone after the game ends")
        self.fill_label = Label(self.window, bg="green", image=PhotoImage(data=b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")))
        self.patch_button = LuActionButton(self.lu_buttons_frame, "Patch", lambda: launch_core(0), 0, 0)
        self.restore_button = LuActionButton(self.lu_buttons_frame, "Restore", lambda: launch_core(1), 134, 0)
        self.unblock_button = LuActionButton(self.lu_buttons_frame, "DirectX", lambda: launch_core(2), 216, 0)
        self.patch_game_button =LuActionSmallButton(self.lu_buttons_frame, "Game", lambda: launch_core(3), 82, 0)
        self.patch_client_button =LuActionSmallButton(self.lu_buttons_frame, "Client", lambda: launch_core(4), 82, 16)
        self.blank_label = Label(self.settings_frame, text ="\nWork in progress", bg =BG, foreground =PRIMARY_COLOR, font =("Calibri", 30))# temporary

        self.content_frame.pack_propagate(False)  
        self.lu_buttons_frame.pack_propagate(False)  

        self.head_frame                        .pack(anchor='w', fill=X)
        self.head_lb                           .place(x =0, y =0)
        self.close_button                      .pack(side =RIGHT)
        self.minimize_button                   .pack(side =RIGHT)
        self.content_frame                     .pack(side =TOP)
        self.checks_frame                      .pack(side=TOP, fill=X)
        self.lu_buttons_frame                  .pack()
        self.dis_per_pixel_point_lighting = StyledCheckbox(self.checks_frame, text='Disable per pixel point lighting', on=lambda: configure_cfg("Performance", "perpixelpointlighting", "0"), off=lambda: configure_cfg("Performance", "perpixelpointlighting", "1"))
        self.dis_grass_swaying = StyledCheckbox(self.checks_frame, text='Disable grass swaying', on=lambda: configure_cfg("Performance", "enablegrassswaying", "0"), off=lambda: configure_cfg("Performance", "enablegrassswaying", "1"))
        self.real_time = StyledCheckbox(self.checks_frame, text='Use real time priority', on=lambda: option_modify("real_time", True), off=lambda: option_modify("real_time", False))
        self.fxaa = StyledCheckbox(self.checks_frame, text = "Enable FXAA", on=lambda: configure_cfg("Performance", "enablefxaa", "1"), off=lambda: configure_cfg("Performance", "enablefxaa", "0"))
        self.fill_label                        .pack(side=TOP, fill=X)
        self.out                               .pack(anchor='w', side=TOP, fill=X)
        self.adbutton_frame                    .pack(side=BOTTOM, fill=X)
        self.bug_button                        .pack(side =RIGHT)
        self.colb                              .pack()
        self.settings_button                   .pack()
        self.logout_button                     .pack()
        self.report_button                     .pack()
        self.progress_label                    .pack(side=RIGHT)
        self.blank_label                       .pack(expand =True, fill =BOTH)
        
        self.out.tag_config("default", foreground ="#cccccc")
        self.out.tag_config("red", foreground ="red")
        self.out.tag_config("green", foreground =PRIMARY_COLOR)

        self.head_frame.bind('<Button-1>', lambda event: clickwin(event, self.window))
        self.head_frame.bind('<B1-Motion>', lambda event: dragwin(event, self.window))

        self.dis_grass_swaying.widget.bind("<Enter>", lambda event: start_new_thread(self.show_tooltip, ("Disabling grass swaying improves fps",)))
        self.dis_per_pixel_point_lighting.widget.bind("<Enter>", lambda event: start_new_thread(self.show_tooltip, ("Disabling per pixel point lighting improves fps",)))
        self.real_time.widget.bind("<Enter>", lambda event: start_new_thread(self.show_tooltip, ("Sets the highest possible priority for League of Legends.exe process.\nCan drastically improve ingame performance. Not recommended to users with one core CPU.\nAdmin permissions are required. Audio can lag.",)))
        #self.x3d0.widget.bind("<Enter>", lambda event: self.show_tooltip(""))
        #self.x3d1.widget.bind("<Enter>", lambda event: self.show_tooltip(""))
        self.x3d5.widget.bind("<Enter>", lambda event: start_new_thread(self.show_tooltip, ("Caps fps at 60, window mode, antialiasing off, not recommended",)))
        self.patch_button.widget.bind("<Enter>", lambda event: start_new_thread(self.show_tooltip, ("Patches dll files for better ingame performance and client performance",)))
        self.patch_game_button.widget.bind("<Enter>", lambda event: start_new_thread(self.show_tooltip, ("Patches dll files for better ingame performance",)))
        self.patch_client_button.widget.bind("<Enter>", lambda event: start_new_thread(self.show_tooltip, ("Patches dll files for better client performance",)))
        self.restore_button.widget.bind("<Enter>", lambda event: start_new_thread(self.show_tooltip, ("Restores official dlls",)))
        self.unblock_button.widget.bind("<Enter>", lambda event: start_new_thread(self.show_tooltip, ("Removes tag at the end of DirectX files",)))
        self.fxaa.widget.bind("<Enter>", lambda event: start_new_thread(self.show_tooltip, ("Enables Fast approximate anti-aliasing",)))

        self.dis_grass_swaying.widget.bind("<Leave>", self.hide_tooltip)
        self.dis_per_pixel_point_lighting.widget.bind("<Leave>", self.hide_tooltip)
        self.real_time.widget.bind("<Leave>", self.hide_tooltip)
        self.x3d0.widget.bind("<Leave>", self.hide_tooltip)
        self.x3d1.widget.bind("<Leave>", self.hide_tooltip)
        self.x3d5.widget.bind("<Leave>", self.hide_tooltip)
        self.patch_button.widget.bind("<Leave>", self.hide_tooltip)
        self.patch_game_button.widget.bind("<Leave>", self.hide_tooltip)
        self.patch_client_button.widget.bind("<Leave>", self.hide_tooltip)
        self.restore_button.widget.bind("<Leave>", self.hide_tooltip)
        self.unblock_button.widget.bind("<Leave>", self.hide_tooltip)
        self.fxaa.widget.bind("<Leave>", self.hide_tooltip)

        self.window.lift()
        self.window.update()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width/2)-190
        y = (screen_height/2)-200
        self.window.geometry('380x400+%d+%d' % (x, y))

    def change_status(self):
        if self.status:
            self.window.withdraw()
            for i in range(50, 80, 2):
                root.window.attributes("-alpha", i/100)
                sleep(0.01)

        else:
            self.window.deiconify()
            for i in range(80, 50, -2):
                root.window.attributes("-alpha", i/100)
                sleep(0.01)

        self.status = not self.status

    def show_tooltip(self, text):
        global tippy
        x, y = self.window.winfo_pointerxy()
        widget = self.window.winfo_containing(x, y)
        sleep(0.1)
        if self.window.winfo_containing(self.window.winfo_pointerx(), self.window.winfo_pointery()) == widget:
            tippy.tooltipw.label.configure(text =text)
            tippy.tooltipw.geometry("+%d+%d" % (x+30, y))
            tippy.tooltipw.deiconify()
            
            for i in range(0, 101, 20):
                tippy.tooltipw.attributes("-alpha", i/100)
                sleep(0.02)

    def hide_tooltip(self, event =None):
        tippy.tooltipw.withdraw()

    def update_checks(self):
        if options['real_time']: main.real_time.switch()

        config.read(options["lolPath"]+"/Config/game.cfg")

        if not config.getboolean("Performance", "enablegrassswaying"):
            main.dis_grass_swaying.switch()
            
        if not config.getboolean("Performance", "perpixelpointlighting"):
            main.dis_per_pixel_point_lighting.switch()

        if config.getboolean("Performance", "enablefxaa"):
            main.fxaa.state_set(True)

        try: 
            x3d_platform = config.getint("General", "x3d_platform")
        except configparser.NoOptionError:
            x3d_platform = 4
        
        if  x3d_platform == 0:
            main.x3d0.state_set(True)
        
        elif x3d_platform == 1:
            main.x3d1.state_set(True)
        
        elif x3d_platform == 5:
            main.x3d5.state_set(True)

    def hide_output(self):
        self.window.geometry("380x220")
        self.colb.config(text='')
        self.fill_label.pack_forget()
        self.out.pack_forget()

    def show_output(self):
        self.colb.config(text='')
        self.out.pack(side=BOTTOM, fill=X)
        self.fill_label.pack(side=BOTTOM, expand=True, fill=X)
        self.window.geometry("380x400")

    def switch_write_output(self):
        if options['output']:
            self.hide_output()
        else:
            self.show_output()

        options['output'] = not options['output']

    def open_settings(self):
        self.checks_frame.pack_forget()
        self.settings_frame.pack()
        self.settings_button.config(foreground =PRIMARY_COLOR, text ="", command =self.close_settings)
        self.settings_button.tooltiptext = "Go back"
        self.head_lb.config(text ="Settings", foreground =PRIMARY_COLOR)

    def close_settings(self):
        self.settings_frame.pack_forget()
        self.checks_frame.pack()
        self.settings_button.config(foreground =FOREGROUND, text ="", command =self.open_settings)
        self.settings_button.tooltiptext = "Settings"
        self.head_lb.config(text ="LoLUpdater", foreground =FOREGROUND)

class LuActionButton:
    def __init__(self, master, text, command, x, y):
        global BG, FOREGROUND, PRIMARY_COLOR, BUTTON_ACTIVE_FACE_COLOR, SECONDARY_COLOR, BUTTON_FOREGROUND, FONT_NAME
        self.frame = Frame(master, bg=SECONDARY_COLOR) # frame for border
        
        # self.rounding_label_1 = Label(self.frame, bg =BG) # corners to make buttons rounded
        # self.rounding_label_2 = Label(self.frame, bg =BG)
        # self.rounding_label_3 = Label(self.frame, bg =BG)
        # self.rounding_label_4 = Label(self.frame, bg =BG)

        self.widget = Button(self.frame, text =text, command =command, bg =PRIMARY_COLOR, foreground =BUTTON_FOREGROUND, #
                            relief =FLAT, font =(FONT_NAME, 12), activebackground =BUTTON_ACTIVE_FACE_COLOR,
                            activeforeground ="white", bd =0, cursor ="hand2")
        self.frame.place(x =x, y =y, anchor ="nw", width =80, height =30)
        self.widget.place(x =1, y =1, width =78, height =28)

        # self.rounding_label_1.place(x =0, y =0, anchor ="nw", width =2, height =2) #placing corners
        # self.rounding_label_2.place(x =80, y =0, anchor ="ne", width =2, height =2)
        # self.rounding_label_3.place(x =0, y =30, anchor ="sw", width =2, height =2)
        # self.rounding_label_4.place(x =80, y =30, anchor ="se", width =2, height =2)

    def config(self, **args):
        self.widget.config(**args)

class LuActionSmallButton:
    def __init__(self, master, text, command, x, y):
        global BG, FOREGROUND, PRIMARY_COLOR, BUTTON_ACTIVE_FACE_COLOR, BUTTON_FOREGROUND, FONT_NAME, SECONDARY_COLOR
        self.frame =Frame(master, bg =SECONDARY_COLOR)
        
        # self.rounding_label_1 = Label(self.frame, bg =BG) #corners to make buttons rounded
        # self.rounding_label_2 = Label(self.frame, bg =BG)
        # self.rounding_label_3 = Label(self.frame, bg =BG)
        # self.rounding_label_4 = Label(self.frame, bg =BG)
        
        self.widget = Button(self.frame, text =text, command =command, bg =PRIMARY_COLOR, foreground =BUTTON_FOREGROUND, #button
                            relief =FLAT, font =(FONT_NAME, 8), activebackground =BUTTON_ACTIVE_FACE_COLOR,
                            activeforeground ="white", bd =0, cursor ="hand2")
        
        self.frame.place(x =x, y =y, anchor ="nw", width =50, height =14)
        self.widget.place(x =1, y =1, anchor ="nw", width =48, height =12)
        # self.rounding_label_1.place(x =0, y =0, anchor ="nw", width =2, height =2) #placing corners
        # self.rounding_label_2.place(x =50, y =0, anchor ="ne", width =2, height =2)
        # self.rounding_label_3.place(x =0, y =14, anchor ="sw", width =2, height =2)
        # self.rounding_label_4.place(x =50, y =14, anchor ="se", width =2, height =2)

    def config(self, **args):
        self.widget.config(**args)

class StyledButton:
    def __init__(self, master, command, font =("Segoe UI", 11), side =LEFT, text ="", tooltiptext =""):
        global PRIMARY_COLOR, BUTTON_ACTIVE_FACE_COLOR, BG, FONT

        self.tooltiptext = tooltiptext

        self.widget = Button(master = master, text = text, command = command,
                             bg = BG, foreground = FOREGROUND,
                             relief = FLAT, cursor = 'hand2', font=FONT,
                             activebackground=BG,
                             activeforeground='white', bd=0, padx=4, pady=0)

        self.widget.bind("<Enter>", lambda event: self.widget.config(foreground =PRIMARY_COLOR))
        self.widget.bind("<Leave>", lambda event: self.widget.config(foreground =FOREGROUND))

        if tooltiptext != "":
            self.widget.bind("<Enter>", self.enter)
            self.widget.bind("<Leave>", self.leave)

    def pack(self, side =LEFT, expand =False, fill =None):
        self.widget.pack(side =side, expand =expand, fill =fill)

    def config(self, **args):
        self.widget.config(**args)

    def enter(self, event):
        global main

        self.widget.config(foreground =PRIMARY_COLOR)
        start_new_thread(tippy.show, (main.window, self.tooltiptext,))

    def leave(self, event):
        self.widget.config(foreground =FOREGROUND)
        tippy.hide()

class StyledCheckbox:
    state = False

    def __init__(self, master, text, state=NORMAL, on=None, off=None):
        global BG, FONT, PRIMARY_COLOR, BUTTON_ACTIVE_FACE_COLOR
        self.widget = Frame(master, bg =BG)
        self.check = Button(self.widget, text = '', state = state,
                             bg = BG, command = self.switch, relief = FLAT, foreground = FOREGROUND,
                             cursor='hand2', activebackground=BUTTON_ACTIVE_FACE_COLOR, activeforeground='white', bd=0,
                             font=ICON_FONT, padx=0, pady=0)
        self.text = Label(self.widget, bg =BG, foreground =FOREGROUND, font =FONT, text =text)
        self.widget.pack(anchor = 'w')
        self.check.pack(side =LEFT, anchor = 'w')
        self.text.pack(side =LEFT, anchor ="w")
        self.on = on
        self.off = off
    
    def switch(self):
        global options, FOREGROUND, PRIMARY_COLOR
        self.state = not self.state
        
        if self.state:
            self.state_set(True)
            self.check.update()
            self.on()

        else:
            self.state_set(False)
            self.check.update()
            self.off()

    def state_set(self, state):
        global CHECKED_CHARACTER, UNCHECKED_CHARACTER
        if state:
            self.check.config(text = CHECKED_CHARACTER, foreground =PRIMARY_COLOR)
            self.state = True

        else:
            self.check.config(text = UNCHECKED_CHARACTER, foreground =FOREGROUND)
            self.state = False

class X3dModeCheckbox:
    state = False
    
    def __init__(self, master, text, x, y, state=NORMAL, on=None, off=None):
        global BG, FONT
        self.widget = Button(master = master, text = text, state = state, bg = BG, command = self.switch, relief = FLAT, foreground = FOREGROUND, cursor='hand2', activebackground=BG, activeforeground='white', bd=0, font=FONT, padx=0, pady=0, width =2)
        self.widget.place(anchor = 'nw', x =x, y =y)
        self.on = on
        self.off = off
    
    def switch(self):
        global options
        self.state = not self.state
        
        if self.state == False:
            self.state_set(True)
            self.widget.update()
            self.off()

        else:
            self.state_set(False)
            self.widget.update()
            self.on()

    def state_set(self, state):
        global FOREGROUND
        if state:
            self.widget.config(foreground =PRIMARY_COLOR, font=("Calibri", 13, "bold"), underline=0)
            self.state = True

        else:
            self.widget.config(foreground =FOREGROUND, font=("Calibri", 11), underline=-1)
            self.state = False
# program
VERSION_NUMBER = "1.0 BETA"
FONT = ("Segoe UI", 11)
FONT_NAME = "Calibri"
ICON_FONT = ("Segoe MDL2 Assets", 11)
BG = "#334"
PRIMARY_COLOR = "#a4addf"
SECONDARY_COLOR = "#6f7dcd"
BUTTON_ACTIVE_FACE_COLOR = "#3C4D54"
BUTTON_FOREGROUND = "#555555"
FOREGROUND = "#ccc"
SELF_PROCESS = Process(os.getpid())
REPORT_CHARACTER = ''
CHECKED_CHARACTER = ''
UNCHECKED_CHARACTER = ''
DOWNLOAD_CHAR = ''
UPTODATE_CHAR = ''
UPDATE_FAILED_CHAR = ''
latest = False
suspend = False
wait = False
output_visible = True
report_bool = False

if __name__ == "__main__":
    try:
        _main()
    except Exception as ex:
        error_message(ex)
