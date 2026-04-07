import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pyautogui
import keyboard
import mouse
import time
import pickle
import threading
from pynput.keyboard import Key, Controller as KeyboardController
from image_tool import ImageTool, ColorChannel
import numpy as np
# ========== 配置：NPC对话气泡寻找 ==========

class Error:
    code = 0
    info = ""
    def __init__(self, code=0, info=""):
        self.code = code
        self.info = info        
PREFIX = "pkl/"
CHAT_ICON_PATH = "npc_icon.jpg"
ACTION_SUCCESS = 0
ACTION_BREAK = 2
ACTION_NOT_FOUND = 1
# ========== 配置：NPC对话气泡寻找 ==========
ICON_PATH = "npc_icon.jpg"
DETECT_REGION = (0, 0, 1300, 1300)
CONFIDENCE = 0.7
LOCATION_DELAY_TIME=5*60 #地图界面寻找时间，单位秒
role_ID=1

keyboard_controller = KeyboardController()
# ========== 查找NPC对话框，并打开 ==========
chat_ok = False
def chat_to_npc():
    global chat_ok
    chat_ok = False
    while True:
        if keyboard.is_pressed('end'):
            print("退出")
            break
         # 还没找到图标时，才去检测
        if not chat_ok:
            try: 
                pos = pyautogui.locateOnScreen(CHAT_ICON_PATH, region=DETECT_REGION, confidence=CONFIDENCE)
                print(pos)
                if pos:
                    print("检测到图标 → 双击")
                    #x, y = pyautogui.center(pos)
                    pyautogui.click(pos)
                    keyboard_controller.press("q")
                    chat_ok = True  # 标记已经点过
                    time.sleep(0.5)
                    keyboard_controller.release("a")
                    break
                # else:
                #     # 没找到就轻微动鼠标
                #     pyautogui.moveRel(8, 0, duration=0.15)
                #     pyautogui.moveRel(-8, 0, duration=0.15)
                #     time.sleep(1)
            except Exception as e:
                    # pyautogui.moveRel(8, 0, duration=0.15)
                    # pyautogui.moveRel(-8, 0, duration=0.15)
                    # time.sleep(1)
                    print(f"##chat_to_npc npc定位失败: {e}")   
                 # 没找到就轻微动鼠标
        print(chat_ok)
        if not chat_ok:            
            # 已经双击过了 → 循环按 A
            #pyautogui.press('w')
            keyboard_controller.press("a")              
            print("循环按 A")       
            time.sleep(0.2)  # 按A的间隔，数字越小按得越快
         
# ========== 地图 ==========
LOC_ICON_PATH="loc_icon.png"
location_ok = False
# 地图定位
def locate(locPos):    
    while True:
        if keyboard.is_pressed('end'):
            print("退出")
            return 0        
        time.sleep(0.1)
        try: 
            pos = pyautogui.locateOnScreen(LOC_ICON_PATH, region= DETECT_REGION, confidence=0.8)   
            print(pos)     
            if pos :    
                print(f"##locate 完成地图寻路 x:{pos.left}, y:{pos.top}") 
                return 1               
                if(abs(locPos[0]-pos.left)<10 and abs(locPos[1]-pos.top)<10 ):
                    print(f"##locate 完成地图寻路 x:{pos.left}, y:{pos.top}")                     
                    return 1                  
                      
        except Exception as e:
            print(f"##locate 地图定位失败: {e}") 
            
#LOC_CLOSE_POS = (100,100)
def go_to_map(locPos, closePos):
    global location_ok
    location_ok = False
    time.sleep(1)
   # pyautogui.press('m')
    print("m")
    time.sleep(0.3)
    #pyautogui.rightClick(locPos)   
    print("rightClick") 
    print(LOC_ICON_PATH)
    #lastPos = pyautogui.locateOnScreen(LOC_ICON_PATH, region=DETECT_REGION, confidence=CONFIDENCE)  
    lastPosx=0
    lastPosy=0
    while True:
        if keyboard.is_pressed('end'):
            print("退出")
            return            
        time.sleep(0.1)
        try: 
            pos = pyautogui.locateOnScreen(LOC_ICON_PATH, confidence=CONFIDENCE)   
            print(pos)     
            if pos :  
                if(lastPosx == pos.left and lastPosy == pos.top): 
                    print(pos.left)
                    print(pos.top)  
                    print(f"##go_to_map 完成地图寻路 x:{pos.left}, y:{pos.top}") 
                    location_ok = True
                    break
                lastPosx = pos.left
                lastPosy = pos.top        
            #lastPos = pos            
        except Exception as e:
            print(f"##go_to_map 地图定位失败: {e}") 
            
    pyautogui.click(closePos)

def find_icon(path, times):  
    _times = 0
    while _times < times:
        if keyboard.is_pressed('end'):
            print("退出")
            return            
        time.sleep(0.1)
        try: 
            pos = pyautogui.locateOnScreen(path, region=DETECT_REGION, confidence=0.8)   
            return pos      
            #lastPos = pos            
        except Exception as e:
            print(f"##find_icon 定位失败: {e}")          
        _times = _times + 1
    
# ========== 工会助手 ==========
UNION_LOCATION_ACTION_ERROR = 400
UNION_LOCATION_ERROR = 401
UNION_TASK_ERROR = 410
def go_to_union():    
    time.sleep(3)        
    actions = load_action_file(PREFIX +"union_location.pkl" )    
    ok = play_action(actions)
    print(f"工会助手定位流程播放, {ok}") 
    if(not ok == ACTION_SUCCESS):
       return Error(UNION_LOCATION_ACTION_ERROR,"工会定位流程播放失败" )  
        
    time.sleep(60)
    icon_path = "union_icon.png"
    times = 0
    found = False
    while times < LOCATION_DELAY_TIME:
        if keyboard.is_pressed('end'):
            print("进入工会任务中断")
            break
        times = times + 1
        keyboard_controller.press('q')
        time.sleep(1)
        keyboard_controller.release('q')
        pos = find_icon(icon_path, 1)
        if pos:                 
            print(f"进入工会任务成功") 
            found = True
            break
        else:
            print(f"进入工会任务失败") 
            
    if found:
        actions = load_action_file(PREFIX +"union_task.pkl" )    
        ok = play_action(actions)
        print(f"工会任务流程执行, {ok}") 
        if ok == ACTION_SUCCESS:
            return Error(ACTION_SUCCESS,"工会任务流程执行，成功")
        else:
            return Error(UNION_TASK_ERROR,"工会任务流程执行，失败")
    else:
        return Error(UNION_LOCATION_ERROR,"进入工会任务失败")
        
# ========== 强化 ==========
STRONG_LOCATION_ACTION_ERROR = 500
STRONG_LOCATION_ERROR = 501
STRONG_MENU_ERROR = 510
STRONG_TASK_ERROR = 520
STRONG_FIND_EQUIP_ERROR = 530

def find_strong_equip_icon(page_btn_pos, page_num):
    lower_green = np.array([40, 80, 80])
    upper_green = np.array([75, 255, 255])
    num = 0
    while(num < page_num):
        equips, frame = ImageTool.find_color_boxes_on_screen(lower_green, upper_green, 100*100)
        if len(equips) > 0:
            equip = equips[0]
            x = equip[0] + equip[2]/2
            y = equip[1] + equip[3]/2
            return [x, y, 1]
        time.sleep(0.5)
        num = num + 1
        pyautogui.click(page_btn_pos)
    
    return [0, 0, 0]

def go_to_strong():    
    #装备页换页按钮位置
    equip_page_btn_pos = (100, 100)
    #定位到铁匠铺    
    actions = load_action_file(PREFIX +"strong_location.pkl" )    
    ok = play_action(actions)
    print(f"强化定位流程播放, {ok}") 
    if(not ok == ACTION_SUCCESS):
       return Error(STRONG_LOCATION_ACTION_ERROR,"强化定位流程播放失败" )  
        
    time.sleep(1)
    icon_path = "strong_icon.png"
    times = 0
    found = False
    while times < LOCATION_DELAY_TIME:
        if keyboard.is_pressed('end'):
            print("进入铁匠店界面中断")
            break
        times = times + 1
        keyboard_controller.press('q')
        time.sleep(1)
        pos = find_icon(icon_path, 1)
        if pos:                 
            print(f"进入铁匠店界面成功") 
            found = True
            break
        else:
            print(f"尝试进入铁匠店界面") 
    #是否成功打开铁匠店界面 找到后执行强化菜单流程      
    if found:
        actions = load_action_file(PREFIX +"strong_menu.pkl" )    
        ok = play_action(actions)
        print(f"强化菜单选择流程执行, {ok}") 
        if not ok == ACTION_SUCCESS:
            return Error(STRONG_MENU_ERROR,"强化菜单流程执行，失败")                    
    else:
        return Error(STRONG_LOCATION_ERROR,"进入铁匠店界面失败")
    #查找绿框装备并选择
    x, y, z = find_strong_equip_icon(equip_page_btn_pos, 5)
    if( z == 0 ):
        return  Error(STRONG_FIND_EQUIP_ERROR, "强化装备没找到")    
    pyautogui.click(x, y)
        
    actions = load_action_file(PREFIX +"strong_task.pkl" )    
    ok = play_action(actions)
    print(f"强化任务流程播放, {ok}") 
    if ok == ACTION_SUCCESS:
        return Error(ACTION_SUCCESS,"强化任务流程执行，成功")
    else:
        return Error(STRONG_TASK_ERROR,"强化任务流程执行，失败")
    
# ========== 选择角色 ==========
SEL_ROLE_ERROR = 100
def sel_role():         
    actions = load_action_file(PREFIX + f"role_{role_ID}.pkl" )    
    ok = play_action(actions) 
    print(f"选择角色{role_ID}, {ok}") 
    if ok == ACTION_SUCCESS:
        return Error(ACTION_SUCCESS, "角色选择执行成功")
    return Error(SEL_ROLE_ERROR, "角色选择执行失败")
# ========== 游戏下载选择 ==========
LOAD_GAME_ERROR = 200
def load_game():
    actions = load_action_file(PREFIX + "load_game.pkl" )    
    ok = play_action(actions)  
    print(f"游戏下载选择, {ok}") 
    if ok == ACTION_SUCCESS:
        return Error(ACTION_SUCCESS, "游戏下载执行成功")
    return Error(LOAD_GAME_ERROR, "游戏下载执行失败")  

# ======== 进入主城 ==========
CITY_INTO_ERROR=300 #主城界面失败
CITY_TASK_ERROR=310 #主城任务失败
def city_manager():
    icon_path = "city_icon.png"
    pos = find_icon(icon_path, 10*60*10)
    if pos:      
        actions = load_action_file(PREFIX +"city.pkl" )    
        ok = play_action(actions)
        print(f"进入主城操作, {ok}") 
        if ok == ACTION_SUCCESS:
            return Error( ACTION_SUCCESS, "主城操作成功"  ) 
        return  Error( CITY_TASK_ERROR,"主城任务操作错误" )        
    else:
        print(f"进入主城界面失败") 
        return  Error( CITY_INTO_ERROR,"进入主城界面失败" )   
# ======== 退出角色 ==========  
EXIT_ERROR=900
def exit_manager():                       
    actions = load_action_file(PREFIX +"exit.pkl" )    
    ok = play_action(actions)
    print(f"退出角色操作, {ok}") 
    if ok == ACTION_SUCCESS:
        return Error( ACTION_SUCCESS, "退出角色操作成功"  ) 
    return  Error(EXIT_ERROR,"退出角色任务操作错误" ) 

# ========== 下载动作 ==========
def load_action_file(filename):
    try:
        with open(filename, "rb") as f:
            actions = pickle.load(f)
            print("##", filename)
            print(actions)
            return actions
    except:
        return
    

# ========== 播放 ==========
def play_action(actions):  
    if actions is None:
        return ACTION_NOT_FOUND
    last = 0
    for a in actions:
        if keyboard.is_pressed('end'):
            print("退出")
            return ACTION_BREAK   
        dt = a["time"] - last
        
        if dt > 0:
            time.sleep(dt)
            last = a["time"]
        
        if a["type"] == "click":  
            time.sleep(0.05)
            pos =(a["x"], a["y"])
            print(a["x"], a["y"])   
            button = 'left' 
            if(button not in str(a["button"])):
                button='right'  
            pyautogui.click(x=a["x"], y=a["y"], button=button)            
            time.sleep(0.05)  
        elif a["type"] == "key":
            k = a["key"]                         
            try:                 
                print(f"按键: {k}" )                
                keyboard_controller.press(k)       
                time.sleep(2)      
                keyboard_controller.release(k)
                                               
            except:		
                pass 
    return ACTION_SUCCESS

def on_click_func(event):   
    #x = event.x
    #print(event) 
    #print(type(event) )
    #<class 'mouse._mouse_event.ButtonEvent'>
    #ButtonEvent(event_type='down', button='left', time=1774231583.7773118)
    if(type(event)==mouse._mouse_event.ButtonEvent):
        x, y = pyautogui.position()       
        #print(f"定位: {x}, {y}")    
    try:
        pos = pyautogui.locateOnScreen(ICON_PATH, confidence=0.8)
        if pos:
            print("找到图标了！执行后续操作...")
            # 这里写你要做的事，比如点击图标
            pyautogui.click(pyautogui.center(pos))
            
    except Exception as e:
        print(f"定位失败: {e}")    
        #  
isdoing = False
def main():   
    global isdoing
    if isdoing:
        print("正在执行中，无法重复执行")
        return
    isdoing = True
    time.sleep(5)         
    global role_ID   
    if role_ID > 4 :
        role_ID =1
        print("所有角色执行完成，等待60秒后重新开始...")
        time.sleep(60)
        isdoing = False
        return
    
    print("当前角色: {role_ID}")
    result = sel_role()
    print(result.info) 
    if not result.code == ACTION_SUCCESS: 
        isdoing = False       
        return
    result = load_game()
    print(result.info) 
    if not result.code == ACTION_SUCCESS:  
        isdoing = False     
        return    
    result = city_manager()
    print(result.info) 
    if result.code == CITY_INTO_ERROR:    
        isdoing = False    
        return    
                 
    result = go_to_union()
    print(result.info)    
    
    result = exit_manager()
    print(result.info)    
    time.sleep(60) 
    isdoing = False
    role_ID = role_ID + 1       
    main()
    #setWinEnabled(True)
   
def play_thread():
    print("play_thread")
    # 用线程防止界面卡死
    t = threading.Thread(target=main, daemon=True)    
    t.start()

root = tk.Tk()
root.title("菜单自动工具（pkl版）")
combo=ttk.Combobox(root, values=["角色1", "角色2", "角色3", "角色4"], state="readonly")
combo.current(0)
def on_combo_change(event):
    global role_ID
    role_ID = combo.current() + 1
    print(f"选择了角色{role_ID}")
combo.bind("<<ComboboxSelected>>", on_combo_change)
combo.pack(pady=10, ipadx=10, ipady=5)

screen_w, screen_h =pyautogui.size()
win_w, win_h = 350, 320
x= screen_w-win_w
y= 100
root.geometry(f"{win_w}x{win_h}+{x}+{y}")
frame = ttk.Frame(root)
frame.pack(pady=15)
btn_common = ttk.Button(
    frame,
    text="通用流程录制",    
)

btn_common.config(command=play_thread)

#btn_common.place(x=100, y=100)
btn_common.pack(pady=10, ipadx=30, ipady=20)
#go_to_union()
def setWinEnabled(enabled):
    if enabled:      
        root.attributes('-disabled', 0)
    else:
        root.attributes('-disabled', 1)
root.mainloop()