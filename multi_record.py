import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pickle
import time
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.mouse import Controller as MouseController
import threading
from pynput.keyboard import Key, Controller as KeyboardController

# ========== 配置：全部用 .pkl 存在 pkl文件包中==========
MENU_FILES = [
    "role_1",
    "role_2",
    "role_3",
    "role_4",
    "load_game",
    "city",
    "union_location",
    "union_task",   
    "exit",
    "strong_location",
    "strong_task",
]
PREFIX = "pkl/"
COMMON_FILE = "common.pkl"
current_recording = []
btns=[]
labs=[]
labs_idx = 0
start_time = 0
is_recording = False
stop_play = False
recording_menu_name=""
current_file=""
# 鼠标、键盘控制器
mouse_controller = MouseController()
keyboard_controller = KeyboardController()
# ========== 录制 ==========
def on_click(x, y, button, pressed):
    if pressed:
        current_recording.append({
            "button":button,
            "type": "click",
            "x": x,
            "y": y,
            "time": time.time() - start_time
        })

def on_key_press(key): 
    global stop_play
    if key == keyboard.Key.end:
        stop_play = True        
        stop_record()
    # 按END停止录制     	    
    if is_recording:
       # current_recording.append(('key', key, time.time() - start_time))
        current_recording.append({
            "type": "key",
            "key": key,
            "time": time.time() - start_time
        })    

def start_record(btn, filename, id):   
    print(f"开始录制：{filename}")   
    setWinEnabled(False)
    stop_record()    
    global is_recording, current_recording, start_time, current_file, current_btn,labs_idx
    current_recording = []
    start_time = time.time()        
    is_recording = True    
    btn.config(state=tk.DISABLED)   
    current_btn = btn  
    current_file = filename
    labs_idx = id
    #lbl_status.config(text="正在录制：{filename}，按 END 结束")
    lbl_status.config(text="正在录制："+btn["text"]+"    按 END 结束")  
    #messagebox.showinfo("提示", "开始录制："+btn["text"]+"    按 END 结束")
   
def stop_record():   
    global is_recording
    if not is_recording:
        return    
    current_btn.config(state=tk.NORMAL)   
    labs[labs_idx].grid()
    is_recording = False
    with open(current_file, "wb") as f:        
        pickle.dump(current_recording, f)    
    lbl_status.config(text="状态：录制完成，可回放")
    setWinEnabled(True)
    #messagebox.showinfo("完成", "录制已保存！")

def check_stop():
    global stop_play
    return stop_play

# ========== 回放 ==========
def replay_file(filename):    
    try:
        with open(filename, "rb") as f:
            actions = pickle.load(f)
            print(actions)
    except:
        return
    last = 0
    for a in actions:
        dt = a["time"] - last               
        if dt > 0:
            time.sleep(dt)
        last = a["time"]
        if check_stop():   
            return; 
        if a["type"] == "click":
            mouse_controller.position = (a["x"], a["y"])
            time.sleep(0.05)
            mouse_controller.click(a["button"])
            time.sleep(0.1)

        elif a["type"] == "key":
            k = a["key"]              
            try: 
                keyboard_controller.press(k)
                keyboard_controller.release(k)                   
            except:		
                pass
             
def play_thread():
    # 用线程防止界面卡死
    t = threading.Thread(target=auto_play_all, daemon=True)    
    t.start()
def auto_play_all():
    global stop_play
    stop_play = False
    setWinEnabled(False)
    lbl_status.config(text="开始自动执行：菜单1→通用→菜单2→通用…  按END结束")
    root.update()
    time.sleep(1)
    for i in range(len(MENU_FILES)):          
        replay_file(MENU_FILES[i])    
        if check_stop():            
            setWinEnabled(True)
            lbl_status.config(text=" ❌ 菜单" + str(i+1) +"中途取消菜单！")
            return;        
        time.sleep(0.3)         
        replay_file(COMMON_FILE)     
        if check_stop():
            setWinEnabled(True)
            lbl_status.config(text="❌ 菜单" + str(i+1) +",通用流程中途取消菜单！")
            return;      
        time.sleep(0.5)

    lbl_status.config(text="✅ 全部执行完成！")
# ========== 界面 ==========
root = tk.Tk()
root.title("菜单自动工具（pkl版）")
root.geometry("450x620")
frame = ttk.Frame(root)
frame.pack(pady=15)

for i in range(len(MENU_FILES)):
    lab = MENU_FILES[i]   
    btn = ttk.Button(
        frame,
        text= lab         
    )              
    print(f"绑定按钮：{lab}，文件：{PREFIX+lab+'.pkl'}")
    btn.config(command=lambda  b=btn, m=PREFIX+lab+".pkl", idx=i: start_record(b, m, idx))    
    btn.grid(row=i, column=0, padx=1, pady=5, ipadx=1,sticky="")
    lab = ttk.Label(frame, text ="OK")
    labs.append(lab)
    lab.config(state=tk.HIDDEN) 
    lab.grid(row=i, column=1, padx=10, pady=5, ipadx=10)
    lab.grid_remove()
    btns.append(btn)

btn_common = ttk.Button(
    frame,
    text="通用流程录制",    
)

# btns.append(btn_common)
# btn_common.config(command=lambda bt=btn_common, mm=COMMON_FILE, idx=4: start_record(bt, mm, idx))
# btn_common.grid(row=5, column=0, padx=10, pady=8, ipadx=10)
# lab = ttk.Label(frame, text ="OK")
# lab.grid(row=5, column=1, padx=10, pady=5, ipadx=10)
# lab.grid_remove()
# labs.append(lab)
# btn_auto = ttk.Button(
#     root,
#     text="▶ 自动播放：菜单1-4 + 通用",
#     command=play_thread
# )
# btn_auto.pack(pady=10, ipadx=20, ipady=5)
# btns.append(btn_auto)

lbl_status = ttk.Label(root, text="状态：等待操作")
lbl_status.pack(pady=5)

mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_key_press)
mouse_listener.start()
keyboard_listener.start()
def setWinEnabled(enabled):
    if enabled:      
        root.attributes('-disabled', 0)
    else:
        root.attributes('-disabled', 1)

root.mainloop()

