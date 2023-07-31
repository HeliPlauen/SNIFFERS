import configparser
import datetime
import logging
import os
import shutil
import subprocess
import time
import winreg
import json

import pyautogui
import requests

import sys
import threading

import snifferclass
import moneycounter


# Logging  and parsing system
logging.basicConfig(filename='logging.log', encoding='utf-8', level=logging.INFO)

config = configparser.ConfigParser()
config.read("settings.ini")


# Global variables
computer_id = config["Miraplay"]["id"].split('"')[1]
url = config["Miraplay"]["url"].split('"')[1]

play_flag = False
waiting_counter = 0
print(computer_id)
print(url)


# Global variables FOR TEST !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
TRAFFIC_SIZE_LIMIT_FOR_TEST = 100000000
REST_MONEY_FOR_TEST = 14
GAME_PRICE_FOR_TEST = 5
session_start = False


def get_status_computer():
    global computer_id
    try:
        response = requests.post(url,
                                 data={'action': 'get_comp_status', 'computer_id': computer_id})
        return response.text
    except ConnectionError:
        logging.info(get_time_str() + " ConnectionError")


def set_ready_status():
    global computer_id
    try:
        response = requests.post(url,
                                 data={'action': 'set_comp_ready', 'computer_id': computer_id})
        return response.text
    except ConnectionError:
        logging.info(get_time_str() + " ConnectionError")


def get_time_str():
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")


def check_pin_box():
    pos_nvlogin_window = pyautogui.locateCenterOnScreen('img.png', confidence=0.5)
    return pos_nvlogin_window


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def enter_pin_code(pos_nvlogin_window, pin_code):
    global play_flag

    if play_flag == False:
        stop_mine() #
    play_flag = True
    pyautogui.moveTo(pos_nvlogin_window)

    # Input pin-box - TEST!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    pin_code = input("Input pin-code: ")

    for i in pin_code:
        pyautogui.press(i)
    pyautogui.press('enter')
    time.sleep(5)


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def start():
    print("BOT STARTS...........................................................................................")
    global play_flag, session_start

    checks_per_minute = 1
    check_seconds = 0

    pos_nvlogin_window = True
    while True:
        try:
            print("TRY TO CREATE SESSION!!!!!!!!!..................................................................")
            pos_nvlogin_window = check_pin_box()  
            
            # FOR TEST ONLY !!!!!!!!!!!!!!!!
            #play_flag = True
            # FOR TEST ONLY !!!!!!!!!!!!!!!!

            if pos_nvlogin_window is not None:
                print("Window exists!!!")
                computer_status = get_status_computer()
                print(computer_status)

                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                #if computer_status == "waiting"

                # The comp is out of the system - TEST !!!!!!!!!!!!!!!!
                if computer_status == "":
                    if session_start == False:
                        print("Session started!!") #
                    enter_pin_code(pos_nvlogin_window, "0000")
                    print("Explorer turns off by the next step!!!")
                    time.sleep(5)
                    if session_start == False:
                        off_background() #                        
            if check_seconds == 60 / checks_per_minute:
                check_online_client()
                check_seconds = 0
                print("User checked!!!")
            else:
                check_seconds += 1
                if not play_flag:
                    print("Window ERROR!!!!")
            time.sleep(1)
        except Exception as e:
            print(f"Start was not started or was aborted {e}")
            logging.info(get_time_str() + " Error: " + str(e))
            time.sleep(20)


def check_online_client():
    global play_flag, waiting_counter
    print(f"Enumerate: {threading.enumerate()}")
    computer_status = get_status_computer()
    if computer_status == "waiting":
        waiting_counter += 1
        if waiting_counter == 2:
            computer_restart()

    if computer_status == "cleaning":
        computer_restart()


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def start_mine():
    global miner_pid
    print("START MINING!!!!")

    parent_dir = os.path.dirname(os.getcwd())
    print(f"PARENT_DIR IS: {parent_dir}")
    parent_dir += "\\mirabot\\NBMiner_Win"
    print(f"PARENT_DIR IS: {parent_dir}")
    print(os.path.exists(parent_dir))

    # parent_dir = "C:\\Users\\rx470-2\\Desktop\\server_compgame_AND_ME\\server\\mirabot\\NBMiner_Win"
    try:
        miner_pid = subprocess.Popen(parent_dir + "\\start_eth.bat", cwd=parent_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        print(f"The Miner Exception is {e}")


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def stop_mine():
    global miner_pid

    if os.system("TASKKILL /F /T /PID " + str(miner_pid.pid)) == 0:
        print("Miner successfully stoped!!!!")
    else:
        print("Miner was NOT stppped and it is still working!!!")


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def clear_steam_users():
    if os.system("taskkill /f /im  steam.exe") == 0:
        print("Steam termination Success!!!")
    else:
        print("Steam termination ERROR!!!")

    time.sleep(1)
    try:
        with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as root:
            with winreg.OpenKey(root, "SOFTWARE\Valve\Steam", 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "AutoLoginUser", 0, winreg.REG_SZ, "")
        print("Steam cleaning Success!!!")
    except:
        print("Steam registry cleaning FAILED!!!")


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def clear_origin_users():
    if os.system('taskkill /f /im  "Origin.exe"') == 0:
        print("Origin termination Success!!!")
    else:
        print("Origin termination ERROR!!!")

    time.sleep(1)
    origin_user_info_path = os.path.expandvars(r'%APPDATA%\Origin')
    if os.path.isdir(origin_user_info_path):
        try:
            shutil.rmtree(origin_user_info_path)
            print("Origin cleaning Success!!!")
        except:
            print("Origin cleaning FAILED!!!")
    else:
        print("Origin path DOES NOT EXIST!!!")


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def clear_battlenet_users():
    if os.system('taskkill /f /im  "Battle.net.exe"') == 0:
        print("Battlenet termination Success!!!")
    else:
        print("Battlenet termination ERROR!!!")

    time.sleep(1)
    battlenet_user_info_path = os.path.expandvars(r'%APPDATA%\Battle.net\Battle.net.config')
    try:
        with open(battlenet_user_info_path, "r") as config_file:
            battlenet_config_json = config_file.read()
            battlenet_config = json.loads(battlenet_config_json)
            battlenet_config["Client"]["SavedAccountNames"] = ""
            battlenet_config["Client"]["AutoLogin"] = "false"
            config_file.close()

        battlenet_config_json = json.dumps(battlenet_config)
        with open(battlenet_user_info_path, "w") as config_file:
            config_file.write(battlenet_config_json)
        print("Battlenet cleaning Success!!!")
    except:
        print("Battlenet cleaning FAILED!!!")


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def clear_epicgames_users():
    if os.system('taskkill /f /im  "EpicGamesLauncher.exe"') == 0:
        print("Epicgames termination Success!!!")
    else:
        print("Epicgames termination ERROR!!!")

    time.sleep(1)
    epicgames_user_info_path = os.path.expandvars(r'%LOCALAPPDATA%\EpicGamesLauncher')
    if os.path.isdir(epicgames_user_info_path):
        try:
            shutil.rmtree(epicgames_user_info_path)
            print("Epicgames cleaning Success!!!")
        except:
            print("Epicgames cleaning FAILED!!!")
    else:
        print("Epicgames path DOES NOT EXIST!!!")


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def clear_wargaming_users():
    if os.system('taskkill /f /im  "wgc.exe"') == 0:
        print("Wargaming termination Success!!!")
    else:
        print("Wargaming termination ERROR!!!")

    time.sleep(1)
    wargaming_user_info_path = os.path.expandvars(r'%APPDATA%\Wargaming.net\GameCenter\user_info.xml')
    if os.path.isfile(wargaming_user_info_path):
        if os.remove(wargaming_user_info_path) == 0:
            print("Wargaming cleaning Success!!!")
        else:
            print("Wargaming cleaning FAILED!!!")
    else:
        print("Wargaming path DOES NOT EXIST!!!")


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def clear_document_dirs():
    docs_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Documents')
    if docs_path:
        for filename in os.listdir(docs_path):
            path = docs_path + "\\" + filename
            if path:
                print("PATH EXISTS")
                print(os.path.isfile(path))
                if os.path.isfile(path):
                    try:
                        shutil.rmtree(path)
                        print(f"The {filename} tree was deleted!!!")
                    except:
                        print(f"The {filename} tree was NOT deleted!!!")

                    if os.remove(path) == 0:
                        print(f"The {filename} path was deleted!!!")
                    else:
                        print(f"The {filename} path was NOT deleted!!!")
                else:
                    print(f"{filename} is not a file!!!!")
            else:
                print(f"The path to {filename} does not exist!!!!")
    else:
        print("User dirs path does not exist!!!!!")


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def clear_nvidia_process():
    if os.system('taskkill /f /im  "nvstreamer.exe"') == 0:
        print("NVIDIA termination Success!!!")
    else:
        print("NVIDIA termination ERROR!!!")


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def off_background():
    global session_start
    session_start == True
    if os.system('taskkill /f /im  "explorer.exe"') == 0:
        print("Explorer.exe was killed!!!")
    else:
        print("Explorer.exe is already turned off or still working!!!!!!!!")


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def on_background():
    try:
        subprocess.Popen("explorer.exe")
        print("Background turned on successfully!!!")
    except Exception as e:
        print(f"Explorer.exe was not started!! Error: {e}")


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def computer_restart():
    logging.info(get_time_str() + "REBOOTING")
    if os.system("shutdown -t 0 -r -f") == 0:
        print("Computer RESTARTS!!!!")
    else:
        print("Computer WAS NOT restarted and still working!!!!!!!")


# NEW: Turn on the sniffer !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def on_sniffing_and_count_money():    
    while True:
        print(f"Active thread: {threading.active_count()}")
        print(f"Enumerate: {threading.enumerate()}")
        if play_flag == True:
            while True:
                Sniff = snifferclass.Sniffer(60)
                try:
                    # Start sniffing
                    traffic_size = Sniff.sniff(None)
                    print(f"TRAFFIC SIZE: {traffic_size}")
                    if traffic_size > TRAFFIC_SIZE_LIMIT_FOR_TEST:
                        print("DOWNLOAD PROCESSING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!") 
                    else:
                        print("Start take to rent for game!!!!")
                        start_date_time = datetime.datetime.now()
                        print(f"Current date and time: {start_date_time}")

                        # Take rent for game
                        global REST_MONEY_FOR_TEST
                        rest_resourses = moneycounter.coin_counter(start_date_time, GAME_PRICE_FOR_TEST, REST_MONEY_FOR_TEST)
                        print(f"REST MONEY: {rest_resourses['rest_money']}")
                        print(f"GAME TIME: {rest_resourses['game_time']}")
                        print(f"REST GAME TIME: {rest_resourses['remain_game_time']}")  
                        print(f"Enumerate: {threading.enumerate()}")
                        REST_MONEY_FOR_TEST = rest_resourses["rest_money"]
                        if REST_MONEY_FOR_TEST <= -1:
                            print("YOR MONEY IS OVER !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                            time.sleep(10)
                            #sys.exit(0)     # Kills only current thread
                            os._exit(0)
                            #computer_restart()
                except Exception as e:
                    print(f"Sniffer Error!!! Exception: {e}!!!!")
        else:
            print("The game mode is off!!!!!")
            time.sleep(1)


# My changes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def bot_init():
    print("INITIALIZATION.........................................................................................")
    global play_flag, session_start

    try:
        print("Bot started")
        clear_steam_users()
        clear_origin_users()
        clear_battlenet_users()
        clear_epicgames_users()
        clear_wargaming_users()
        clear_nvidia_process()

        start_mine()
        set_ready_status()
        play_flag = False
        session_start = False
        
        clear_document_dirs()

        # Start Sniffing in new thread !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        thr = threading.Thread(target=on_sniffing_and_count_money, args=())
        thr.start()

        print("BOT INITIALIZED.....................................................................................")
    except Exception as e:
        print(f"The Bot was not started or was aborted {e}")
        logging.info(get_time_str() + " Error: " + str(e))
        time.sleep(20)


# Start rpogram 
bot_init()
start()
