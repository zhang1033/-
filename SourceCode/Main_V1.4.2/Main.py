#导入
import threading
import random as rand
import tkinter as tk
import tkinter.font as tkf
import tkinter.ttk as ttk
import tkinter.messagebox as msg
import ctypes as c
import ctypes.wintypes as cw
import traceback as tb
import threading as thd
import os,sys,json,time,gc
import main_strings as mainstr
import tkinter_external as tkex
import platform as plfm
LOCAL_MESSAGE={}
view_redundant_window=[]
pre_window_errors={}
no_value=object()
self_settings_default={"is_rollcall_once":False,"apply_config_noerror":False,"window_topmost":False,"delay_rollcall":False,"delay_rollcall_time_ms":2000}
self_settings=dict(self_settings_default)
def args_kw_data(*args,**kw):
    return(args,kw)
def configs_access(item,value=no_value,action="load",widget=None):
    global self_settings,self_settings_default
    def access_action():
        nonlocal item,value,action
        if action=="load":
            return(self_settings[item])
        elif action=="change":
            if not value is no_value:
                self_settings[item]=value
                try:
                    with open("./config.json","w",encoding="utf-8") as apply_config:
                        json.dump(self_settings,apply_config,ensure_ascii=False)
                except Exception:
                    try:
                        if configs_access("apply_config_noerror") and (item=="apply_config_noerror"):
                            raise
                        elif (not configs_access("apply_config_noerror")) and (item!="apply_config_noerror"):
                            raise
                        else:
                            pass
                    except PermissionError as e:
                        pre_window_error_show(f"未能写入配置,但配置已经生效，原因：\n{str(e)}","随机抽取-写入json配置失败", 0x10,parent=main.nametowidget(widget).winfo_toplevel())
                    except Exception as e:
                        pre_window_error_show(f"写入配置时出现未预料的错误，但配置已经生效，原因：\n{str(tb.format_exc())}","随机抽取-写入json配置失败",0x10,parent=main.nametowidget(widget).winfo_toplevel())
            else:
                raise ValueError("没有值")
        else:
            raise AttributeError(f"无效操作项-\"{action}\"")
    if item in self_settings:
        return(access_action())
    else:
        if item in self_settings_default:
            self_settings[item]=self_settings_default[item]
            return(access_action())
        else:
            raise KeyError(f"没有设置项-\"{item}\"")
def tcl_configs_change_func(widget,arg_data):
    arg_data=eval(arg_data)
    if type(arg_data).__name__ in ("tuple","list"):
        __arg_data_length=len(arg_data)
        if __arg_data_length>=2:
            __arg_data_values=tuple(arg_data[1:__arg_data_length:1])
            if len(__arg_data_values)==1:
                __arg_data_values=__arg_data_values[0]
            configs_access(arg_data[0],value=__arg_data_values,action="change",widget=widget)
        else:
            raise AttributeError("参数长度不够")
    else:
        raise TypeError("非元组或列表类型")
def pre_window_error_show(text,title,types,parent=None,action=None):
    global pre_window_errors
    pre_window_errors[title]=[text,types,parent,action]
def show_pre_window_error():
    global pre_window_errors
    def process():
        global pre_window_errors
        for error in dict(pre_window_errors):
            if pre_window_errors[error][2] != None:
                wid=pre_window_errors[error][2].winfo_id()
            else:
                wid=None
            return_code=c.windll.user32.MessageBoxW(wid,pre_window_errors[error][0],error,pre_window_errors[error][1])
            if pre_window_errors[error][3]!=None:
                if str(return_code) in list(pre_window_errors[error][3].keys()):
                    pre_window_errors[error][3][str(return_code)]()
                else:
                    if "other" in pre_window_errors[error][3]:
                        pre_window_errors[error][3]["other"]()
            del pre_window_errors[error]
        if len(pre_window_errors)!=0:
            process()
    while True:
        #print("clock")
        if Process_Local_Message("WM_QUIT","GLOBAL","exist"):
            break
        else:
            if len(pre_window_errors)!=0:
                process()
            time.sleep(0.01)
def program_exit():
    Process_Local_Message("WM_QUIT","GLOBAL","boardcast")
    main.destroy()
    sys.exit()
sys_version=plfm.version().split(".")
for index in range(0,len(sys_version),1):
    sys_version[index]=int(sys_version[index])
if (sys_version[0]==6) and (sys_version[1]<3):
    c.windll.user32.SetProcessDPIAware() #兼容Windows Vista到Windows8的系统
elif ((sys_version[0]==6) and (sys_version[1]>3)) or (sys_version[0]>=10):
    c.windll.shcore.SetProcessDpiAwareness(2) ##这个就是声明高dpi缩放替代中的“应用程序”选项，千万不要使用，在200%以上4k分辨率中会出BUG。现在已解决。
else:
    pass
#改变工作路径为当前程序运行目录（工作目录，顾名思义就是“.”，类似于cmd的%cd%）
if os.path.isfile(sys.argv[0]):
    cwd_path=os.path.abspath(sys.argv[0])
else:
    cwd_path=sys.executable
os.chdir(os.path.dirname(cwd_path))
#创建主窗口
main_window_time=time.perf_counter()#设置主窗口创建时的时间
main=tk.Tk()
dpi=main.winfo_pixels("1i")/96 #查看缩放大小
dpi_window_size=int(500*dpi),int(500*dpi) #窗口大小 (宽, 高)
main.minsize(*dpi_window_size)#设置最小大小
main.title("随机抽取")#标题
main.config(bg="#90f4b3")#设置背景颜色
main.attributes("-alpha",0.8)#设置窗口透明度
main.protocol("WM_DELETE_WINDOW",program_exit)
tcl_configs_access=main.register(tcl_configs_change_func)
main.call("bind","all","<<Configs_Change>>",f"{tcl_configs_access} %W %d")

def load_settings(encoding=None):
    global self_settings
    def write_default_config():
        try:
            with open("./config.json","w",encoding="utf-8") as config_write:
                json.dump(self_settings,config_write, ensure_ascii=False)
        except PermissionError as e:
            pre_window_error_show(f"未能写入默认配置，原因：\n{str(e)}","随机抽取-写入json配置失败",0x10,parent=main)
        except Exception as e:
            pre_window_error_show(f"写入默认配置时出现未预料的错误，原因：\n{str(tb.format_exc())}","随机抽取-写入json配置失败",0x10,parent=main)
    if os.path.isfile("./config.json"):
        try:
            bom=None#预留变量，并设置为空
            #自动检测编码
            if encoding==None:
                with open("./config.json","rb") as encodes:#用二进制形式打开文件，用with语句是为了能够完全打开或关闭文件
                    bom=encodes.read(3)#读配置文件的前三个字节
                if bom==b"\xef\xbb\xbf":#判断文件前3个字节是否有utf-8-bom的特征
                    encoding="utf-8-sig"#使用utf-8-bom编码
                else:
                    encoding="utf-8"#使用utf-8编码
            with open("./config.json","r",encoding=encoding) as r:
                self_settings=json.loads(r.read())
        #except ValueError as json_error:#检查json语法是否正确（Python3.4兼容）
        #    pre_window_error_show("json文件\"config.json\"的语法不正确，已使用默认配置，原因：\n"+str(json_error),"随机抽取-json配置错误",0x10)
        except json.decoder.JSONDecodeError as json_error:#检查json语法是否正确
            pre_window_error_show("json文件\"config.json\"的语法不正确，已使用默认配置，原因：\n"+str(json_error),"随机抽取-json配置错误",0x10,parent=main)
        except FileNotFoundError as json_error:#检查文件存在性（基本被上面的if-else代码优先执行）
            pre_window_error_show("找不到json文件\"config.json\"，已自动创建并使用默认配置，原因：\n"+str(json_error),"随机抽取-找不到json配置",0x30,parent=main)
            write_default_config()
        except PermissionError as json_error:#检查是否被拒绝访问
            pre_window_error_show("json文件\"config.json\"被拒绝读取，已使用默认配置，原因：\n"+str(json_error),"随机抽取-json配置读取失败",0x10,parent=main)
        except Exception as json_error:#检测其它异常来输出详细信息
            pre_window_error_show("未知错误：\n"+str(tb.format_exc()),"随机抽取-错误",0x10,parent=main)
    else:
        if os.path.isdir("./namelist.json")==True:#检测配置是否为文件夹
            pre_window_error_show("json配置为目录，请在当前目录下的\"config.json\"文件夹删除，然后再创建此文件。\n目前已使用默认配置。","随机抽取-找不到json配置",0x10,parent=main)
        else:
            pre_window_error_show("未找到json配置，已自动创建\"config.json\"文件。\n目前已使用默认配置。","随机抽取-找不到json配置",0x30,parent=main)
            write_default_config()
load_settings()
def Process_Local_Message(Message_Class,Message_String,action):
    global LOCAL_MESSAGE
    if action=="boardcast":
        if Message_Class not in LOCAL_MESSAGE:
            LOCAL_MESSAGE[Message_Class]=[]
        if not Message_String in LOCAL_MESSAGE[Message_Class]:
            LOCAL_MESSAGE[Message_Class].append(Message_String)
    elif action=="remove":
        if (Message_Class in LOCAL_MESSAGE) and (Message_String in LOCAL_MESSAGE[Message_Class]):
            del LOCAL_MESSAGE[Message_Class][LOCAL_MESSAGE[Message_Class].index(Message_String)]
    elif action=="exist":
        if Message_Class not in LOCAL_MESSAGE:
            return False
        else:
            return(Message_String in LOCAL_MESSAGE[Message_Class])
def ttk_style(widget,*args,**kw):
    ttk.Style().configure(f"{widget}.{widget.winfo_class()}",*args,**kw)
    return(f"{widget}.{widget.winfo_class()}")
##touch=c.windll.user32.RegisterTouchWindow(main.winfo_id(),1)
##class MSG(c.Structure):
##    _fields_=[
##        (main.winfo_id(),cw.HWND),
##        (0x240,c.c_uint),
##        c.windll.user32.GetTouchInputInfo()
##        ]
name_font=tkf.Font(family="楷体",size=75,weight="bold")#设置姓名显示字体
start_button_font=tkf.Font(family="楷体",size=40)#设置开始按钮显示字体
name=tk.Label(main,text="",font=name_font,wraplength=490*dpi,bg="#90f4b3")#设置姓名显示标签，font为在上面的字体样式
name.pack(pady=100*dpi)#排放姓名显示标签
name_database=[]#定义一个空姓名数据集
rollcall_once_namelist=[]
#定义一个布尔值数据，为后面调整显示或隐藏标题栏作铺垫
hide_title_state=tk.BooleanVar()
hide_title_state.set(False)#默认为不隐藏
window_topmost=tk.BooleanVar()
window_topmost.set(configs_access("window_topmost"))
main.attributes("-topmost",configs_access("window_topmost"))
#不随机抽取的开关
rollcall_once=tk.BooleanVar()
rollcall_once.set(configs_access("is_rollcall_once"))
apply_config_noerror=tk.BooleanVar()
apply_config_noerror.set(configs_access("apply_config_noerror"))
#随机抽取部分
def name_rand(name_rand_times=0):
    global LOCAL_MESSAGE
    if rollcall_once.get():
        namelist_local=rollcall_once_namelist
    else:
        namelist_local=name_database
    if name_rand_times<=24:#设置抽取频率
        name.config(text=name_database[rand.randint(0,len(name_database)-1)])#用random模块来实现在名单范围内随机（len(name_database)-1是为了防止到最大值时溢出）
        start.config(state="disable")#抽取期间按钮禁用            
    else:
        #抽取完成
        if name_rand_times==25:
            randint_local=rand.randint(0,len(namelist_local)-1)
            name_local=namelist_local[randint_local]
            name.config(text=name_local)
            if rollcall_once.get():
                del namelist_local[randint_local]
                if len(namelist_local)==0:
                    def finish_rollcall_once():
                        global rollcall_once_namelist
                        rollcall_once_namelist=list(name_database)
                        del rollcall_once_namelist[rollcall_once_namelist.index(name_local)]
                        start.config(state="normal")
                    pre_window_error_show("""名单内的名字已抽完。
是否进行重新抽取？

是-重新进行
否-取消""",
                                                "随机抽取",
                                                0x44,
                                          parent=main,
                                                action={"6":lambda:finish_rollcall_once(),"other":lambda:start.config(state="disable")}
                                                )
                else:
                    if configs_access("delay_rollcall"):
                        delay_rollcall=main.after(configs_access("delay_rollcall_time_ms"),lambda:start.config(state="normal"))
                    else:
                        start.config(state="normal")#按钮变得可点击
            else:
                if configs_access("delay_rollcall"):
                    delay_rollcall=main.after(configs_access("delay_rollcall_time_ms"),lambda:start.config(state="normal"))
                else:
                    start.config(state="normal")
    #if "STOP_SELECTION" in LOCAL_MESSAGE["NAMELIST_UPDATED"]:
    if Process_Local_Message("NAMELIST_UPDATED","STOP_SELECTION","exist"):
        Process_Local_Message("NAMELIST_UPDATED","STOP_SELECTION","remove")
        if "delay_rollcall" in locals():
            main.after_cancel(delay_rollcall)
        start.config(state="normal")
    else:
        if name_rand_times<=25:
            main.after(60,name_rand,name_rand_times+1)#防止tkintr线程阻塞，界面卡死，隔60ms再进行随机数
start=tk.Button(main,text="随机抽选",relief="groove",command=name_rand,font=start_button_font,bg="#50E885",activebackground="#79DBB2",state="disable")
start.pack(pady=40*dpi,side="bottom",anchor="s")
#创建菜单和标题栏
menu=tk.Frame(main,bg="#50E885")
#随窗口大小变化而变长的菜单栏（优化性能）
main.update() #更新主窗口配置
menu.place(x=0,y=0,height=35*dpi,width=main.winfo_width())

    #def shown_menu(event):#事件的def定义的括号内必须含有event，否则会报错
    #    print(1)
    #    menu.place(x=0,y=0,height=35*dpi,width=main.winfo_width())
    #main.bind("<Visibility>",shown_menu)#检测窗口出现（防止菜单栏初始化错误）。这就是事件监听。
    #上面的注释代码不可用，会影响性能，甚至卡死。
    
#调整窗口大小的控件
resize_tool=ttk.Sizegrip(main)
resize_tool.config(style=ttk_style(resize_tool,background="#90f4b3"))#改变控件主底色
resize_tool.place(x=main.winfo_width(),y=main.winfo_height(),anchor="se")
def menu_size(event):
    menu.place(width=main.winfo_width())
    name.config(wraplength=main.winfo_width()-10)
    name_font.configure(size=75+int(min(main.winfo_width()-dpi_window_size[0],main.winfo_height()-dpi_window_size[1])/5/dpi))
    start_button_font.config(size=40+int(min(main.winfo_width()-dpi_window_size[0],main.winfo_height()-dpi_window_size[1])/10/dpi))
    resize_tool.place(x=main.winfo_width(),y=main.winfo_height(),anchor="se")
    if hide_title_state.get()==True:#判断是否隐藏标题栏
        #隐藏标题栏后的控件设置
        min_window.place(x=main.winfo_width()-70*dpi)#最小化
        max_window.place(x=main.winfo_width()-50*dpi)#最大化
        exit_button.place(x=main.winfo_width()-30*dpi)#退出
main.bind("<<SizeChanged>>",menu_size)#绑定窗口变化事件
#全屏按钮
fullscr=tk.Label(menu,text="全屏",bg="#50E885",anchor="w")
fullscr.pack(side="right",padx=12*dpi)
#设置一个整数值表示全屏状态
fullscreen_state=tk.IntVar()
fullscreen_state.set(0)#默认为不全屏
#全屏后的控件设置
exit_button=tk.Label(menu,text="×",bg="#50E885",font=20)
max_window=tk.Label(menu,text="▢",bg="#50E885",font=20)
min_window=tk.Label(menu,text="-",bg="#50E885",font=30)

###关于全屏的
def fullscr_button(event):
    if fullscreen_state.get()==0:#检测是否没有全屏
        if hide_title_state.get()==True:#检测是否隐藏标题栏
            main.overrideredirect(boolean=False)#这里取消隐藏标题栏是为了防止在全屏时报错或异常
        main.attributes("-fullscreen",True)#全屏
        fullscr.config(text="退出全屏")#改变内容
        fullscr.pack(padx=80*dpi)#改变取消全屏的位置（向左）
        max_window.place(x=main.winfo_width()-50*dpi,y=16*dpi,anchor="w")
        exit_button.place(x=main.winfo_width()-30*dpi,y=18*dpi,anchor="w")
        min_window.place(x=main.winfo_width()-70*dpi,y=17*dpi,anchor="w")
        fullscreen_state.set(1)#设置全屏状态数值
    else:
        main.attributes("-fullscreen",False)#取消全屏
        fullscr.config(text="全屏")
        #恢复正常菜单栏
        if hide_title_state.get()==False:
            fullscr.pack(padx=10*dpi)#全屏按钮恢复到初始位置
            #隐藏控件
            min_window.place_forget()
            max_window.place_forget()
            exit_button.place_forget()
        fullscreen_state.set(0)
        #还原隐藏标题栏状态
        if hide_title_state.get()==True:
            main.overrideredirect(boolean=True)
fullscr.bind("<Button-1>",fullscr_button)#监听鼠标左键点击“全屏”或“取消全屏”
#按esc键退出全屏
def esc_exit(event):
    if fullscreen_state.get()==1:
        main.attributes("-fullscreen",False)
        fullscr.config(text="全屏")
        fullscr.pack(padx=10*dpi)
        fullscreen_state.set(0)
        if hide_title_state.get()==True:
            main.overrideredirect(boolean=True)
main.bind("<Key-Escape>",esc_exit)#监听esc键
#隐藏标题栏的退出按钮命令
def exit_p(event):
    main.destroy()
    sys.exit()
#最大化命令（目的如上同）
#这儿有一点小BUG
become_max=0#设置未最大化的数值（关键在这）
def max_window_1(event):
    global become_max#声明全局变量
    if become_max==0:#判断是否没有最大化
        main.state("zoomed")#最大化
        become_max=1#最大化数值
    else:
        main.state("normal")#窗口变为最大化前的大小
        become_max=0
#最小化命令
#由于我的技术原因，最小化之后变成显示标题栏，这也许是反人类的BUG了，此更新已修复。
def min_window_1(event):
    global hide_title_state
    if hide_title_state.get()==True:#检测标题栏是否隐藏
        #取消隐藏标题栏
        main.overrideredirect(boolean=False)
        #hide_title_state.set(False)
        min_window.place_forget()
        max_window.place_forget()
        exit_button.place_forget()
        fullscr.pack(padx=10*dpi)
    main.iconify()#最小化
    def restore_window(event):
        if (main.state() != "iconic") and (hide_title_state.get()):
            main.overrideredirect(boolean=True)
            min_window.place(x=main.winfo_width()-70*dpi,y=16*dpi,anchor="w")
            max_window.place(x=main.winfo_width()-50*dpi,y=16*dpi,anchor="w")
            exit_button.place(x=main.winfo_width()-30*dpi,y=16*dpi,anchor="w")
            fullscr.pack(padx=80*dpi)
            main.unbind("<Map>")
    main.bind("<Map>",restore_window)
exit_button.bind("<Button-1>",exit_p)
max_window.bind("<Button-1>",max_window_1)
min_window.bind("<Button-1>",min_window_1)
#隐藏标题栏
def hide_title():
    global hide_title_state
    if hide_title_state.get()==True:
        #隐藏标题栏
        main.overrideredirect(boolean=True)
        fullscr.pack(padx=80*dpi)
        max_window.place(x=main.winfo_width()-50*dpi,y=16*dpi,anchor="w")
        exit_button.place(x=main.winfo_width()-30*dpi,y=18*dpi,anchor="w")
        min_window.place(x=main.winfo_width()-70*dpi,y=17*dpi,anchor="w")
    else:
        main.overrideredirect(boolean=False)#取消隐藏标题栏
        if fullscreen_state.get()==0:
            min_window.place_forget()
            max_window.place_forget()
            exit_button.place_forget()
            fullscr.pack(padx=10*dpi)
    if hide_title_state.get()==True:
        menu.bind("<Button-1>",replace_xy)
main_window_finish_time=time.perf_counter()
def topmost_window():
    main.attributes("-topmost",window_topmost.get())
    main.event_generate("<<Configs_Change>>",data=("window_topmost",window_topmost.get()))
    #configs_access("window_topmost",value=window_topmost.get(),action="change")
#不重复抽取的名单检测
def rollcall_once_cmd():
    global rollcall_once_namelist
    rollcall_once.set(not(rollcall_once.get()))
    if len(name_database)<=3 and rollcall_once.get()==False:
        def continue_to_rollcall_once():
            if len(name_database)<=1:
                rollcall_once.set(False)
                main.event_generate("<<Configs_Change>>",data=("is_rollcall_once",False))
                #configs_access("is_rollcall_once",value=False,action="change")
            else:
                rollcall_once.set(True)
                main.event_generate("<<Configs_Change>>",data=("is_rollcall_once",True))
                #configs_access("is_rollcall_once",value=True,action="change")
        if rollcall_once_namelist==[]:
            rollcall_once_namelist=list(name_database)
        pre_window_error_show(
            """    检测到名单元素低于4个，在不重复抽选下不会达到预期效果。如果此时再进行抽取，会有大问题。
    所以如果在1个以上，虽然能正常进行，但就跟顺序抽没什么区别。
    如果元素数量少于2个，会出现BUG，所以无论选任何选项都无效。

是否继续？""",
            "随机抽取-不重复抽取",
            0x34,
            parent=main,
            action={"6":lambda:continue_to_rollcall_once()}
            )
    else:
        rollcall_once.set(not(rollcall_once.get()))
        main.event_generate("<<Configs_Change>>",data=("is_rollcall_once",rollcall_once.get()))
        #configs_access("is_rollcall_once",value=rollcall_once.get(),action="change")
        if rollcall_once_namelist==[]:
            rollcall_once_namelist=list(name_database)
def apply_config_noerror_cmd():
    main.event_generate("<<Configs_Change>>",data=("apply_config_noerror",apply_config_noerror.get()))
    #configs_access("apply_config_noerror",value=apply_config_noerror.get(),action="change")
delay_rollcall=tk.BooleanVar()
delay_rollcall.set(configs_access("delay_rollcall"))
def delay_rollcall_cmd():
    main.event_generate("<<Configs_Change>>",data=("delay_rollcall",delay_rollcall.get()))
    #configs_access("delay_rollcall",value=delay_rollcall.get(),action="change")
#关于我的弹出子窗口
about_me_window=None
def about_me(exist=None):
    global about_me_window
    try:
        def create():
            window=tk.Toplevel(bg="#000000")
            window.title("关于我")
            window.minsize(int(340*dpi),int(300*dpi))
            window.resizable(False,False)
            def close_window():
                window.destroy()
            window.protocol("WM_DELETE_WINDOW",close_window)
            about_me_canvas=tk.Canvas(window,bg="#D5F7F0")
            about_me_canvas.pack(fill="both",expand=True)
            about_me_canvas_scroll=tk.Scrollbar(about_me_canvas,command=about_me_canvas.yview)
            about_me_canvas_scroll.pack(side="right",fill="y")
            about_me_canvas.update()
            about_me_buttons=tk.Frame(window,bg="#7BB3AA")
            about_me_buttons.pack(fill="x",ipady=25*dpi,side="bottom")
            about_me_button_ok=ttk.Button(about_me_buttons,text="确定",command=close_window)
            about_me_button_ok.config(style=ttk_style(about_me_button_ok,background="#7BB3AA"))
            about_me_button_ok.place(x=about_me_canvas.winfo_width()-10*dpi,anchor="ne")
            about_me_button_ok.update()
            about_me_button_ok.focus_set()
            about_me_button_ok.place(y=(50*dpi-about_me_button_ok.winfo_height())/2)
            about_me_canvas.create_polygon((0,0),fill="#D5F7F0")
            about_me=[
                (args_kw_data(anchor="nw",text=mainstr.About_strings.about_me_leader()[0],font=("楷体",18,"bold"),fill="#0E5F61"),
                 5*dpi,20*dpi),
                (args_kw_data(anchor="ne",text=mainstr.About_strings.about_me_leader()[1],font=("楷体",16),fill="#0E5F61"),
                 window.winfo_width()-int(about_me_canvas_scroll.cget("width"))-5*dpi,20*dpi),
                (args_kw_data(anchor="nw",text=mainstr.About_strings.about_me(),font=("仿宋",12),width=window.winfo_width()-int(about_me_canvas_scroll.cget("width"))-5*dpi,justify="left",fill="#183C4D"),
                 5*dpi,20*dpi)
                      ]
            for widget in about_me:
                about_me_canvas.create_text((widget[1],about_me_canvas.bbox("all")[3]+widget[2]),*widget[0][0],**widget[0][1])
            about_me_canvas.config(yscrollcommand=about_me_canvas_scroll.set,scrollregion=about_me_canvas.bbox("all"))
            def mouse_wheel(event):
                if str(event.widget.winfo_toplevel())==str(window) and (str(event.widget).split(".")[2]==str(about_me_canvas).split(".")[2]):
                    about_me_canvas.yview_scroll(-int(event.delta/60),"units")
            about_me_canvas.bind_all("<MouseWheel>",mouse_wheel)
            return(window)
        if exist==None:
            about_me_window=create()
        else:
            about_me_window.deiconify()
    except tk.TclError as e:
        if str(e)==f"bad window path name \"{about_me_window}\"":
            about_me_window=create()
        else:
            raise
about_program_window=None
#关于此程序
def about_program(exist=None):
    global about_program_window
    try:
        def create():
            window=tk.Toplevel(bg="#000000")
            window.minsize(int(700*dpi),int(500*dpi))
            window.title("关于此程序")
            window.resizable(False,False)
            def close_window():
                about_program_canvas.unbind("<ButtonPress-1>")
                about_program_canvas.unbind("<B1-Motion>")
                window.destroy()
            window.protocol("WM_DELETE_WINDOW",close_window)
            about_program_buttons=tk.Frame(window,bg="#7BB3AA")
            about_program_buttons.pack(fill="x",ipady=25*dpi,side="bottom")
            about_program_buttons.update()
            about_program_colnums=tk.Frame(window,bg="#00594B")
            about_program_colnums.pack(fill="y",side="left",ipadx=100*dpi)
            about_program_canvas=tk.Canvas(window,bg="#D5F7F0")
            about_program_canvas.pack(fill="both",expand=True)
            about_program_canvas_scroll=tk.Scrollbar(about_program_canvas,command=about_program_canvas.yview)
            about_program_canvas_scroll.pack(side="right",fill="y")
            about_program_canvas.update()
            about_program_button_ok=ttk.Button(about_program_buttons,text="确定",command=close_window)
            about_program_button_ok.config(style=ttk_style(about_program_button_ok,background="#7BB3AA"))
            about_program_button_ok.place(x=about_program_buttons.winfo_width()-10*dpi,anchor="ne")
            about_program_button_ok.update()
            about_program_button_ok.place(y=(50*dpi-about_program_button_ok.winfo_height())/2)
            wrpleng=about_program_canvas.winfo_width()-int(about_program_canvas_scroll.cget("width"))-10*dpi
            about_program_canvas.create_polygon((0,0),fill="#D5F7F0")
            about_program=[
                args_kw_data((5*dpi,0),anchor="nw",text=mainstr.About_strings.program_new(),font=("楷体",12),fill="#0E5F61",width=wrpleng,justify="left"),
                args_kw_data((5*dpi,10*dpi),anchor="nw",text=mainstr.About_strings.about_program(),font=("仿宋",12),fill="#0E5F61",width=wrpleng,justify="left"),
                args_kw_data((5*dpi,0),anchor="nw",text=mainstr.About_strings.no_using_electron(),font=("仿宋",12),fill="#020E47",width=wrpleng,justify="left"),
                args_kw_data((5*dpi,0),anchor="nw",text=mainstr.About_strings.my_truth_opinion(),font=("仿宋",12),fill="#472722",width=wrpleng,justify="left"),
                args_kw_data((5*dpi,0),anchor="nw",text=mainstr.About_strings.about_program_handout(),font=("仿宋",12),fill="#0E5F61",width=wrpleng,justify="left"),
                args_kw_data((5*dpi,20*dpi),anchor="nw",text=mainstr.About_strings.tested_list(),font=("仿宋",12),fill="#0A334A",width=wrpleng,justify="left")
                      ]
            about_program_ids=[]
            about_program_colnum=[]
            about_program_colnum_title=tk.Label(about_program_colnums,text=list(mainstr.About_strings.labels_page().keys())[0],bg="#00594B",fg="#D5F7F0",font=("楷体",25,"bold"))
            about_program_colnum_title.place(x=10*dpi,y=12*dpi,anchor="nw")
            def change_page(event):
                for i in about_program_colnum:
                    if i[0]==event.widget:
                        i[0].config(font=("仿宋",14,"bold","underline"))
                        place_text(is_place=True,skipped_index=list(mainstr.About_strings.labels_page().values())[about_program_colnum.index(i)+1],change_page=True)
                    else:
                        i[0].config(font=("仿宋",14))
            for page_code in range(1,len(mainstr.About_strings.labels_page()),1):
                about_program_colnum.append([tk.Label(about_program_colnums,text=list(mainstr.About_strings.labels_page().keys())[page_code],bg="#00594B",fg="#D5F7F0",font=("仿宋",14),cursor="hand2"),5*dpi,(40+50*page_code)*dpi,"nw"])
                about_program_colnum[-1][0].place(x=about_program_colnum[-1][1],y=about_program_colnum[-1][2],anchor=about_program_colnum[-1][3])
                about_program_colnum[-1][0].bind("<Button-1>",change_page)
            about_program_colnum[0][0].config(font=("仿宋",14,"bold","underline"))
            widget_total_y=10*dpi
            def place_text(is_place=False,skipped_index=[],change_page=False):
                nonlocal about_program_ids
                about_program_canvas.delete(*about_program_ids)
                for widget in about_program:
                    if is_place:
                        if about_program.index(widget) in skipped_index:
                            places=about_program_canvas.bbox("all")[3]+widget[0][0][1]
                            about_program_ids.append(about_program_canvas.create_text((widget[0][0][0],places),**widget[1]))
                print(places)
                if about_program_canvas.bbox("all")[3]<about_program_canvas.winfo_height():
                    about_program_ids.append(about_program_canvas.create_polygon((0,about_program_canvas.bbox("all")[3],about_program_canvas.winfo_width(),about_program_canvas.bbox("all")[3],about_program_canvas.winfo_width(),about_program_canvas.winfo_height()-6,0,about_program_canvas.winfo_height()-6),fill="#D5F7F0"))
                about_program_canvas.config(scrollregion=about_program_canvas.bbox("all"))
            place_text(is_place=True,skipped_index=range(0,7,1))
            about_program_canvas.config(yscrollcommand=about_program_canvas_scroll.set,scrollregion=about_program_canvas.bbox("all"))
            def mouse_wheel(event):
                if str(event.widget.winfo_toplevel())==str(window) and (str(event.widget).split(".")[2]==str(about_program_canvas).split(".")[2]):
                    about_program_canvas.yview_scroll(-int(event.delta/60),"units")
            about_program_canvas.bind_all("<MouseWheel>",mouse_wheel)
            return(window)
        if exist==None:
            about_program_window=create()
        else:
            about_program_window.deiconify()
    except tk.TclError as e:
        if str(e)==f"bad window path name \"{about_program_window}\"":
            about_program_window=create()
        else:
            raise
delay_rollcall_set_window=None
def delay_rollcall_set(exist=None):
    global delay_rollcall_set_window
    try:
        def create():
            window=tk.Toplevel(bg="#B6EEFF")
            window.minsize(int(300*dpi),int(200*dpi))
            window.title("设置延迟点名时间-随机抽取")
            window.resizable(False,False)
            window.transient(main)
            window.grab_set()
            delay_rollcall_label=tk.Label(window,text="输入延迟点名时间",bg="#B6EEFF",fg="#06212B",font=("仿宋",18),justify="left")
            delay_rollcall_label.pack(ipady=5*dpi,ipadx=5*dpi,side="top",anchor="nw")
            delay_rollcall_time=tk.IntVar()
            delay_rollcall_time.set(configs_access("delay_rollcall_time_ms"))
            delay_rollcall_time_frame=tk.Frame(window)
            delay_rollcall_time_frame.pack(side="top",anchor="center",pady=15*dpi)
            delay_rollcall_time_entry=tkex.tkex.Num_Spinbox(delay_rollcall_time_frame,from_=0,to=2**64-1,textvariable=delay_rollcall_time,bg="#D3FEFF",font=("楷体",20),buttonbackground="#D3E6F5",width=6)
            print(type(delay_rollcall_time_entry.master).__name__)
            delay_rollcall_time_entry.grid(row=0,column=0,sticky="ns")
            delay_rollcall_time_unit_label=tk.Label(delay_rollcall_time_frame,text="毫秒",font=("楷体",16),bg="#B6EEFF",fg="#06212B")
            delay_rollcall_time_unit_label.grid(row=0,column=1,sticky="ns")
            delay_rollcall_time_entry.focus_set()
            def apply_delay_rollcall_time():
                window.event_generate("<<Configs_Change>>",data=("delay_rollcall_time_ms",min(
                                                        max(0,delay_rollcall_time.get()),
                                                        2**64-1
                                                        )))
            delay_rollcall_time_button=ttk.Button(window,text="确定",command=apply_delay_rollcall_time)
            delay_rollcall_time_button.config(style=ttk_style(delay_rollcall_time_button,background="#B6EEFF"))
            delay_rollcall_time_button.pack(side="right",anchor="s",padx=10*dpi,pady=10*dpi)
            return(window)
        if exist==None:
            delay_rollcall_set_window=create()
        else:
            delay_rollcall_set_window.deiconify()
    except tk.TclError as e:
        if str(e)==f"bad window path name \"{delay_rollcall_set_window}\"":
            delay_rollcall_set_window=create()
        else:
            raise
edit_config_window=None
def edit_config(exist=None):
    global edit_config_window
    try:
        def create():
            start_create_time=time.perf_counter()
            window=tk.Toplevel()
            window.title("编辑名单文件")
            window.minsize(int(500*dpi),int(410*dpi))
            window.config(bg="#b3c2ff")
            window.attributes("-alpha",0.95)
            window.resizable(False,False)
            window.transient(main)
            window.grab_set()
            window.update()
            edit_frame=tk.Frame(window,bg="#a0a0ff")
            edit_frame.place(x=10*dpi,y=50*dpi,height=340*dpi,width=150*dpi)
            name_list_title=tk.Label(edit_frame,text="名称列表",bg="#a0a0ff",fg="#0a0a0a",font=("楷体",16,"bold"))
            name_list_title.pack(padx=5*dpi,pady=5*dpi,anchor="nw")
            edit_list_frame=tk.Frame(edit_frame,bg="#0a0aff")
            edit_list_frame.pack(fill="both",side="left")
            list_bar=tk.Scrollbar(edit_list_frame)
            list_bar.pack(side="right",fill="y")
            name_list=tk.Listbox(edit_list_frame,yscrollcommand=list_bar.set)
            name_list.pack(fill="both",side="left",expand=True)
            name_list.config(bg="#a0a0ff",font=("楷体",16,"bold"),fg="#0a0a0a",selectbackground="#0000e0",activestyle="dotbox",selectmode="single",bd=5,relief="flat",highlightbackground="#0a0aff",highlightcolor="#0a0aff")
            control_frame=tk.Frame(window,bg="#a0a0ff")
            control_frame.place(x=170*dpi,y=50*dpi,height=340*dpi,width=320*dpi)
            search_label=tk.Label(control_frame,text="搜索名称",bg="#a0a0ff",fg="#0a0a0a",font=("楷体",16,"bold"))
            search_label.place(x=10*dpi,y=5*dpi)
            search_entry=tk.Entry(control_frame,bg="#8383d3",relief="flat",fg="#fefeff",font=("楷体",18),insertbackground="#fefeff")
            search_entry.place(x=10*dpi,y=35*dpi,width=300*dpi,height=40*dpi)
            name_db_temp=list(name_database)
            selected_name=tk.Label(control_frame,bg="#a0a0ff",fg="#0a0a0a",font=("楷体",16,"bold"))
            selected_name.place(x=10*dpi,y=80*dpi)
            selected_entry=tk.Entry(control_frame,bg="#8383d3",relief="flat",fg="#fefeff",font=("楷体",18),insertbackground="#fefeff")
            selected_entry.place(x=10*dpi,y=115*dpi,width=300*dpi,height=40*dpi)
            replace_list=tk.Button(control_frame,text="修改",bg="#8383d3",fg="#fefeff",relief="flat",activebackground="#8080d0",activeforeground="#dedee3",state="disable",font=("楷体",14),wraplength=45*dpi)
            replace_list.place(x=15*dpi,y=225*dpi,height=30*dpi,width=50*dpi)
            delete_list_t=tk.Button(control_frame,text="删除",bg="#8383d3",fg="#fefeff",relief="flat",activebackground="#8080d0",activeforeground="#dedee3",state="disable",font=("楷体",14),wraplength=45*dpi)
            delete_list_t.place(x=70*dpi,y=225*dpi,height=30*dpi,width=50*dpi)
            add_list_t=tk.Button(control_frame,text="添加",bg="#8383d3",fg="#fefeff",relief="flat",activebackground="#8080d0",activeforeground="#dedee3",state="disable",font=("楷体",14),wraplength=45*dpi)
            add_list_t.place(x=125*dpi,y=225*dpi,height=30*dpi,width=50*dpi)
            clean_list=tk.Button(control_frame,text="清空",bg="#8383d3",fg="#fefeff",relief="flat",activebackground="#8080d0",activeforeground="#dedee3",state="disable",font=("楷体",14),wraplength=45*dpi)
            clean_list.place(x=180*dpi,y=225*dpi,height=30*dpi,width=50*dpi)
            add_del_label=tk.Label(control_frame,text="插入方式",bg="#a0a0ff",fg="#0a0a0a",font=("楷体",14,"bold"))
            add_del_label.place(x=25*dpi,y=260*dpi)
            add_del_opinion=tk.Menubutton(control_frame,state="disable",bg="#8383d3",fg="#fefeff",relief="flat",activebackground="#5456b0",activeforeground="#b4c1ef",font=("楷体",14),wraplength=210*dpi)
            add_del_opinion.place(x=15*dpi,y=290*dpi,width=215*dpi,height=30*dpi)
            add_del_opinion_menu=tk.Menu(add_del_opinion,tearoff=False,bg="#8383d3",fg="#fefeff",activebackground="#5454a0",activeforeground="#c0c0e0")
            add_del_opinion.config(menu=add_del_opinion_menu)
            save_list=tk.Button(control_frame,text="保存",bg="#8383d3",fg="#fefeff",relief="flat",activebackground="#8080d0",activeforeground="#dedee3",state="disable",font=("楷体",14),wraplength=68*dpi)
            save_list.place(x=235*dpi,y=225*dpi,height=30*dpi,width=70*dpi)
            save_list_apply=tk.Button(control_frame,text="直接使用而不保存",bg="#8383d3",fg="#fefeff",relief="flat",activebackground="#8080d0",activeforeground="#dedee3",state="disable",font=("楷体",14),wraplength=68*dpi)
            save_list_apply.place(x=235*dpi,y=260*dpi,height=60*dpi,width=70*dpi)
            weight_num_label=tk.Label(control_frame,text="最大数量",bg="#a0a0ff",fg="#0a0a0a",font=("楷体",16,"bold"))
            weight_num_label.place(x=10*dpi,y=185*dpi)
            weight_num_entry=tk.Entry(control_frame,bg="#8383d3",relief="flat",fg="#fefeff",font=("楷体",18),insertbackground="#fefeff")
            weight_num_entry.place(x=130*dpi,y=185*dpi,width=180*dpi,height=30*dpi)
            enable_weight=tk.BooleanVar()
            enable_weight.set(False)
            is_enabme_weight=tk.Checkbutton(control_frame,text="启用概率抽取",variable=enable_weight,bg="#a0a0ff",activebackground="#a0a0ff",relief="flat",selectcolor="#a0a0ff")
            is_enabme_weight.place(x=20*dpi,y=160*dpi)
            def check_changed():
                if not name_database == name_db_temp:
                    Process_Local_Message("NAMELIST_CHANGED", "namelist", "boardcast")
                window.after(50,check_changed)
            window.after(50,check_changed)
            edit_direction=tk.IntVar()
            def edit_config_exit():
                Process_Local_Message("NAMELIST_CHANGED", "namelist", "remove")
                window.destroy()
            window.protocol("WM_DELETE_WINDOW",edit_config_exit)
            name_list.insert("end",*name_db_temp)
            del start_create_time
            search_result=list(name_db_temp)
            def check_name_database_none():
                if name_database==[]:
                    start.config(state="disable")
                else:
                    start.config(state="normal")
            def save_list_command(done=1):
                def save_list_choice(is_save):
                    nonlocal done
                    def save_list_1(is_direct=False):
                        def save_list_sub():
                            global rollcall_once_namelist
                            if len(name_db_temp) <= 1:
                                rollcall_once.set(False)
                                window.event_generate("<<Configs_Change>>",data=("is_rollcall_once",False))
                            name_database.clear()
                            for names in name_db_temp:
                                name_database.append(names)
                            rollcall_once_namelist=list(name_db_temp)
                            Process_Local_Message("TEMPLY_SAVED_RAM", "namelist", "boardcast")
                            Process_Local_Message("NAMELIST_CHANGED", "namelist", "remove")
                            save_list_apply.config(state="disable")
                            success_saved=1
                            if is_save==1:
                                if os.path.isdir("./namelist.json")==True:
                                    pre_window_error_show("配置文件\"namelist.json\"为目录，请在保存之前删除此目录。","编辑配置文件",0x10,parent=window)
                                    success_saved=0
                                else:
                                    try:
                                        with open("./namelist.json","w",encoding="utf-8") as save_list_file:
                                            save_list_file.write(json.dumps(name_db_temp,ensure_ascii=False))
                                    except PermissionError as e:
                                        pre_window_error_show(f"配置文件\"namelist.json\"被拒绝访问，原因：\n{e}","编辑配置文件",0x10,parent=window)
                                        success_saved=0
                                    except Exception as e:
                                        pre_window_error_show(f"未知错误：\n{str(tb.format_exc())}","编辑配置文件",0x10,parent=window)
                                        success_saved=0
                                if success_saved==1:
                                    save_list.config(state="disable")
                                    Process_Local_Message("FILE_NOT_SAVED", "namelist", "remove")
                                    Process_Local_Message("TEMPLY_SAVED_RAM", "namelist", "remove")
                                    Process_Local_Message("NAMELIST_CHANGED", "namelist", "remove")
                            else:
                                Process_Local_Message("NAMELIST_CHANGED", "namelist", "remove")
                                Process_Local_Message("TEMPLY_SAVED_RAM", "namelist", "boardcast")
                            check_name_database_none()
                            save_list_command(0)
                        if is_direct == True:
                            save_list_sub()
                    if rollcall_once.get():
                        pre_window_error_show(
                            """    在打开不重复抽取后，您所抽剩余的名单将替换成所编辑的名单。
    如果名单元素少于4个，不重复抽取将不会达到预期效果。
    如果少于两个元素，程序会自动关闭不重复抽选。

是否继续？""",
                            "随机抽取-保存",
                            0x34,
                            parent=window,
                            action={"6":lambda:save_list_1(is_direct=True)}
                            )
                    else:
                        save_list_1(is_direct=True)
                if done==0:
                    if Process_Local_Message("NAMELIST_CHANGED", "namelist", "exist"):
                        save_list_apply.config(state="normal",command=lambda:save_list_choice(0))
                        save_list.config(state="normal",command=lambda:save_list_choice(1))
                    elif (Process_Local_Message("TEMPLY_SAVED_RAM", "namelist", "exist") or Process_Local_Message("FILE_NOT_SAVED", "namelist", "exist")):
                        save_list.config(state="normal",command=lambda:save_list_choice(1))
                    save_list_command(1)
                else:
                    pass
                if done==0:
                    window.after(100,save_list_command,done)
            save_list_command(0)
            def add_del_opinions(selected=0,behind=1,pre_set=1):
                opinions=[["插入在最前面","插入在最后面"],["插入在前面","插入在后面"]]
                add_del_opinion.config(text=opinions[selected][behind])
                def set_a_opinion(behind_i):
                    add_del_opinion.config(text=opinions[selected][behind_i])
                    edit_direction.set(behind_i)
                if pre_set==0:
                    edit_direction.set(behind)
                    for i in range(0,len(opinions[selected]),1):
                        add_del_opinion_menu.add_command(label=opinions[selected][i],command=lambda i=i:set_a_opinion(i))
                else:
                    for i in range(0,len(opinions[selected]),1):
                        add_del_opinion_menu.entryconfig(i,label=opinions[selected][i],command=lambda i=i:set_a_opinion(i))
            add_del_opinions(pre_set=0)
            def entry_type(selected=0,name=""):
                if name_db_temp==[]:
                    selected_name.config(text="列表为空，请添加一项。")
                    delete_list_t.config(state="disable")
                    clean_list.config(state="disable")
                    add_del_opinion.config(state="disable")
                    add_list_t.config(command=lambda:add_t(0))
                else:
                    if selected==1:
                        selected_name.config(text=f"修改已选择：{name}")
                        add_del_opinions(selected=1,behind=edit_direction.get())
                        delete_list_t.config(state="normal")
                    else:
                        selected_name.config(text="未选择")
                        add_del_opinions(selected=0,behind=edit_direction.get())
                        delete_list_t.config(state="disable")
                        add_list_t.config(command=lambda:add_t(0))
                    clean_list.config(state="normal")
                    add_del_opinion.config(state="normal")
                def check_entry():
                    is_selected=(not name_list.curselection()==())
                    if selected_entry.get()=="":
                        replace_list.config(state="disable")
                        add_list_t.config(state="disable")
                    else:
                        add_list_t.config(state="normal")
                        if is_selected==True:
                            replace_list.config(state="normal")
                        else:
                            replace_list.config(state="disable")
                    window.after(100,check_entry)
                check_entry()
            entry_type()
            def search_selection_conv():
                if not name_list.curselection()==():
                    print(search_result)
                    return([name_db_temp.index(search_result[name_list.curselection()[0]]),search_result[name_list.curselection()[0]] in name_db_temp])
                else:
                    return([None,False])
            def search_in_namedatabase(key_word):
                #split_key_word=[]
                selected_name_before=None
                if not len(name_list.curselection())==0:
                    selected_name_before=name_list.get(name_list.curselection()[0])
                search_result.clear()
                search_result_temp=[]
                name_list.delete(0,"end")
                def searching():
                    for name_index in range(0,len(name_db_temp),1):
                        if name_index<len(name_db_temp):
                            if key_word in str(name_db_temp[name_index]):
                                search_result.append(name_db_temp[name_index])
                    name_list.insert("end",*search_result)
                    if selected_name_before in search_result:
                        name_list.selection_set(search_result.index(selected_name_before))
                        name_list.see(search_result.index(selected_name_before))
                    else:
                        entry_type(selected=0)
                window.after(10,searching)
            primary_word=search_entry.get()
            def search_namelist(entered=0):
                nonlocal primary_word
                nonlocal search_result
                if not primary_word==search_entry.get():
                    primary_word=search_entry.get()
                    search_in_namedatabase(search_entry.get())
                window.after(5,search_namelist,entered)
            search_namelist()
            def cancel_selection(event=None):
                name_list.selection_clear(0,"end")
                entry_type(selected=0)
            selected_name.bind("<Button-1>",cancel_selection)
            def add_t(selected,name_index=None):
                if selected_entry.get() in name_db_temp:
                    pre_window_error_show(f"\"{selected_entry.get()}\"已在列表中存在。","编辑配置文件",0x10,parent=window)
                else:
                    if selected==1:
                        if search_result==[]:
                            name_db_temp.insert(name_index+edit_direction.get(),selected_entry.get())
                        else:
                            name_db_temp.insert(name_db_temp.index(search_result[name_list.curselection()[0]])+edit_direction.get(),selected_entry.get())
                        name_list.insert(name_index+edit_direction.get(),selected_entry.get())
                        name_list.see(name_index)
                    else:
                        if ((edit_direction.get()==0) or (name_db_temp==[])):
                            name_db_temp.insert(0,selected_entry.get())
                            name_list.insert(0,selected_entry.get())
                            name_list.see(0)
                        else:
                            name_db_temp.insert(len(name_db_temp),selected_entry.get())
                            name_list.insert(len(name_db_temp),selected_entry.get())
                            name_list.see("end")
                    selected_entry.delete(0,len(selected_entry.get()))
                    if not name_index==None:
                        name_list.see(name_index+edit_direction.get()+(-1)**edit_direction.get())
                        entry_type(selected=1,name=name_db_temp[name_index+edit_direction.get()+(-1)**edit_direction.get()])
                    else:
                        entry_type(0)
            def delete_t(name_index):
                def state_add_del_opinion():
                    if name_db_temp==[]:
                        delete_list_t.config(state="disable")
                        add_del_opinion.config(state="disable")
                        return False
                    else:
                        return True
                _selected_name=name_list.get(name_index)
                name_list.delete(name_index)
                if _selected_name in search_result:
                    search_result.remove(_selected_name)
                name_db_temp.pop(name_db_temp.index(_selected_name))
                if name_index==name_list.size():
                    _selected_name=name_list.get(name_list.size()-1)
                    name_index-=1
                else:
                    _selected_name=name_list.get(name_index)
                name_list.selection_set(name_index)
                name_list.see(name_index)
                entry_type(selected=1,name=_selected_name)
             ##推到重做吧（已完善一些输入机制）
            def replace_name(name_index=None):
                if selected_entry.get() in name_db_temp:
                    pre_window_error_show(f"\"{selected_entry.get()}\"已在列表中存在。","编辑配置文件",0x10,parent=window)
                else:
                    if search_result==[]:
                        name_db_temp[name_list.curselection()[0]]=selected_entry.get()
                    else:
                        name_db_temp[name_db_temp.index(search_result[name_list.curselection()[0]])]=selected_entry.get()
                        search_result[name_list.curselection()[0]]=selected_entry.get()
                    name_list.insert(name_index,selected_entry.get())
                    name_list.delete(name_index+1)
                    selected_entry.delete(0,len(selected_entry.get()))
                    name_list.selection_set(name_index)
                    entry_type(selected=1,name=name_db_temp[name_list.curselection()[0]])
                    replace_list.config(state="disable")
            def clean_name_list():
                nonlocal name_db_temp
                name_db_temp.clear()
                name_list.delete(0,"end")
                entry_type()
            clean_list.config(command=clean_name_list)
            def selected_action(event):
                if name_list.curselection()==():
                    entry_type(selected=0)
                else:
                    if search_entry.get()=="":
                        entry_type(selected=1,name=name_db_temp[name_list.curselection()[0]])
                    else:
                        entry_type(selected=1,name=search_result[name_list.curselection()[0]])
                    delete_list_t.config(command=lambda:delete_t(name_list.curselection()[0]))
                    replace_list.config(command=lambda:replace_name(name_index=name_list.curselection()[0]))
                    add_list_t.config(command=lambda:add_t(1,name_list.curselection()[0]))
            name_list.bind("<<ListboxSelect>>",selected_action)
            list_bar.config(command=name_list.yview)
            list_bar.config(activebackground="#a0a0ff")
            return(window)
        if exist==None:
            edit_config_window=create()
        else:
            edit_config_window.deiconify()
    except tk.TclError as e:
        if str(e)==f"bad window path name \"{edit_config_window}\"":
            edit_config_window=create()
        else:
            raise

##设置菜单项
#设置菜单栏命令
file_menu=tk.Menubutton(menu,text="文件",bg="#50E885",anchor="e",activebackground="#50d385")#创建菜单按钮
file_menu.pack(padx=10*dpi,side="left")
config_menu=tk.Menubutton(menu,text="总选项",bg="#50E885",anchor="e",activebackground="#50d385")#创建菜单按钮
config_menu.pack(padx=10*dpi,side="left")
window_config_menu=tk.Menubutton(menu,text="窗口",bg="#50E885",anchor="e",activebackground="#50d385")#创建菜单按钮
window_config_menu.pack(padx=10*dpi,side="left")
about=tk.Menubutton(menu,text="关于",bg="#50E885",anchor="e",activebackground="#50d385")
about.pack(padx=10*dpi,side="left")
#创建菜单
file_menus=tk.Menu(file_menu,tearoff=False,bg="#50E885",activebackground="#73d3A0",activeforeground="#102305")
file_menu.config(menu=file_menus)#菜单绑定在菜单按钮上，点击后 展开
reload=tk.Menu(file_menus,tearoff=False,bg="#50E885",activebackground="#73d3A0",activeforeground="#102305")#设置子菜单，foreground结尾为字体颜色，background结尾为背景颜色
file_menus.add_cascade(label="重新加载",menu=reload)#把子菜单绑定在一个主菜单项上
file_menus.add_command(label="编辑配置文件",command=lambda:edit_config(exist=edit_config_window))
about_menu=tk.Menu(about,tearoff=False,bg="#50E885",activebackground="#73d3A0",activeforeground="#102305")
about.config(menu=about_menu)
about_menu.add_command(label="关于我",command=lambda:about_me(exist=about_me_window))
about_menu.add_command(label="关于此程序",command=lambda:about_program(exist=about_program_window))
window_menus=tk.Menu(window_config_menu,tearoff=False,bg="#50E885",activebackground="#73d3A0",activeforeground="#102305")
window_config_menu.config(menu=window_menus)
window_menus.add_checkbutton(label="隐藏标题栏",command=hide_title,variable=hide_title_state)#设置可勾选菜单项，variable为显示或控制变量
window_menus.add_checkbutton(label="窗口置顶",command=topmost_window,variable=window_topmost)
config_menus=tk.Menu(config_menu,tearoff=False,bg="#50E885",activebackground="#73d3A0",activeforeground="#102305")
config_menu.config(menu=config_menus)
config_menus.add_checkbutton(label="启用不重复抽取",command=rollcall_once_cmd,variable=rollcall_once)
config_menus.add_checkbutton(label="启用延迟点名",command=delay_rollcall_cmd,variable=delay_rollcall)
config_menus.add_command(label="延迟点名时间设置",command=lambda:delay_rollcall_set(exist=delay_rollcall_set_window))
config_menus.add_checkbutton(label="应用配置时无报错弹窗",command=apply_config_noerror_cmd,variable=apply_config_noerror)
#重新加载UTF-8编码
def reload_utf_8():
    start.config(state="normal")#开始按钮变得可点击
    json_config(encoding="utf-8")#传参编码utf-8（小写）
#重新加载utf-8-bom编码（我在这里踩过坑）
def reload_utf_8_bom():
    start.config(state="normal")
    json_config(encoding="utf-8-sig")#uff-8-bom编码名称
def reload_locals():
    start.config(state="normal")
    json_config(encoding="ansi")
def reload_normal():
    start.config(state="normal")
    json_config()
reload.add_command(label="直接重新加载",command=reload_normal)
reload.add_command(label="以UTF-8编码重新加载",command=reload_utf_8)#设置菜单项
reload.add_command(label="以UTF-8-BOM编码重新加载（针对windows10早期版本）",command=reload_utf_8_bom)
reload.add_command(label="以系统语言编码重新加载（即ANSI）",command=reload_locals)

##无标题栏状态下的移动窗口
def replace_xy(event):
    def replace_xy1(event):
        if hide_title_state.get()==True:
            #获取移动后的窗口位置（event.x和event.y持续获取，并分别与primary_x和primary_y来作差值表示移动距离，最后再分别与main.winfo_x()和main.winfo_y()相加来获取新窗口位置。）
            window_x=str(main.winfo_x()+(event.x-primary_x))
            window_y=str(main.winfo_y()+(event.y-primary_y))
            main.geometry(f"+{window_x}+{window_y}")#设置移动后窗口位置，这里只能用符号“+”来表示窗口位置，否则会报错
    menu.bind("<B1-Motion>",replace_xy1)#按下左键在菜单栏上移动时移动窗口
    #获取当前鼠标点击位置（为移动窗口作铺垫）
    primary_x=event.x
    primary_y=event.y
is_error_empty=0

##加载配置文件namelist.json
def json_config(encoding=None,event=None):#encoding默认值为空
    global name_database#声明全局变量
    global is_error_empty
    global main_window_time
    global LOCAL_MESSAGE
    global rollcall_once_namelist
    #捕捉异常
    try:
        #检查配置文件是否存在
        if os.path.isfile("./namelist.json")==True:
            bom=None#预留变量，并设置为空
            #自动检测编码
            if encoding==None:
                with open("./namelist.json","rb") as encodes:#用二进制形式打开文件，用with语句是为了能够完全打开或关闭文件
                    bom=encodes.read(3)#读配置文件的前三个字节
                if bom==b"\xef\xbb\xbf":#判断文件前3个字节是否有utf-8-bom的特征
                    encoding="utf-8-sig"#使用utf-8-bom编码
                else:
                    encoding="utf-8"#使用utf-8编码
            #用文本形式打开配置文件
            with open("./namelist.json","r",encoding=encoding) as namelist:
                names=json.load(namelist)#加载配置文件
                if is_error_empty==1:
                    Process_Local_Message("NAMELIST_UPDATED","STOP_SELECTION","boardcast")
                name_database.clear()
                name_database=names
                if not len(name_database)==len(list(set(name_database))):
                    Process_Local_Message("FILE_NOT_SAVED","namelist","boardcast")
                    def MessageBox_Return():
                        global name_database,LOCAL_MESSAGE
                        #nonlocal view_redundant_window
                        #if is_view_redundant_teams.MessageBox_return==6:
                        def create_window(exist=None):
                            global view_redundant_window
                            Process_Local_Message("NAMELIST_UPDATED","STOP_SELECTION","remove")
                            try:
                                def create():
                                    global view_redundant_window
                                    after_time_cancel=[None,None]
                                    def end_view_redundant():
                                        Process_Local_Message("WM_QUIT","Redundant_Window","boardcast")
                                        Process_Local_Message("WM_CREATE","Start_Redundant_Window_Main",action="remove")
                                        main.after_cancel(after_time_cancel[0])
                                        main.after_cancel(after_time_cancel[1])
                                        view_redundant_window[0].destroy()
                                    view_redundant_teams=tk.Toplevel(main,bg="#000000")
                                    view_redundant_teams.minsize(int(400*dpi),int(300*dpi))
                                    view_redundant_teams.title("随机抽取-名单重复元素查看")
                                    ttk.Style().configure("Treeview",rowheight=int(20*dpi))
                                    buttons_below=tk.Frame(
                                        view_redundant_teams,
                                        bg="#f0f0f0"
                                        )
                                    buttons_below.pack(fill="x",ipady=10*dpi,side="bottom")
                                    button_ok=ttk.Button(buttons_below,text="确定",command=end_view_redundant)
                                    button_ok.pack(side="right",anchor="center",padx=10*dpi,pady=3*dpi)
                                    view_redundant_teams_columns=["重复的名称","出现次数"]
                                    redundant_teams_table_scroll=tk.Scrollbar(view_redundant_teams)
                                    redundant_teams_table_scroll.pack(side="right",fill="y")
                                    redundant_teams_table=ttk.Treeview(
                                        view_redundant_teams,
                                        columns=view_redundant_teams_columns,
                                        show="headings",
                                        style="Treeview",
                                       yscrollcommand=redundant_teams_table_scroll.set
                                        )
                                    redundant_teams_table.pack(side="left",expand=True,fill="both")
                                    for i in view_redundant_teams_columns:
                                        redundant_teams_table.heading(i,text=i)
                                    view_redundant_window=[view_redundant_teams]
                                    view_redundant_teams.protocol("WM_DELETE_WINDOW",end_view_redundant)
                                    def view_redundant(lists):
                                        nonlocal after_time_cancel
                                        def insert_redundant_teams(count=0):
                                            if count<=len(ori_list)-1:
                                                name=ori_list[count]
                                                print(name,lists.count(name))
                                                if not Process_Local_Message("WM_RESTORE","Window_Already_Opened",action="exist"):
                                                    if not lists.count(name)==1:
                                                        redundant_teams_table.insert("","end",values=[name,str(lists.count(name))])
                                                    if (not Process_Local_Message("WM_QUIT","GLOBAL","exist")) and (not Process_Local_Message("WM_QUIT","Redundant_Window","exist")):
                                                        after_time_cancel[0]=main.after(20,insert_redundant_teams,count+1)
                                        if Process_Local_Message("WM_RESTORE","Window_Already_Opened",action="exist"):
                                            ori_list=list(dict.fromkeys(lists))
                                            TreeView_Redudant_list=redundant_teams_table.get_children()
                                            redundant_teams_table.delete(*TreeView_Redudant_list)
                                            Process_Local_Message("WM_RESTORE","Window_Already_Opened",action="remove")
                                            insert_redundant_teams()
                                        else:
                                            if not Process_Local_Message("WM_CREATE","Start_Redundant_Window_Main",action="exist"):
                                                ori_list=list(dict.fromkeys(lists))
                                                insert_redundant_teams()
                                                Process_Local_Message("WM_CREATE","Start_Redundant_Window_Main",action="boardcast")
                                            else:
                                                pass
                                        if (not Process_Local_Message("WM_QUIT","GLOBAL","exist")) and (not Process_Local_Message("WM_QUIT","Redundant_Window","exist")):
                                            after_time_cancel[1]=main.after(400,view_redundant,lists)
                                    view_redundant(name_database1)
                                if exist==None:
                                    create()
                                else:
                                    view_redundant_window[0].deiconify()
                                    Process_Local_Message("WM_RESTORE","Window_Already_Opened",action="boardcast")
##新功能，因某些原因，暂时弃用
                            except tk.TclError as e:
                                if str(e)==f"bad window path name \"{view_redundant_window[0]}\"":
                                    Process_Local_Message("WM_RESTORE","Window_Already_Opened",action="remove")
                                    create()
                                else:
                                    raise
                        if not view_redundant_window==[]:
                            Process_Local_Message("WM_QUIT","Redundant_Window","remove")
                            create_window(exist=view_redundant_window[0])
                        else:
                            Process_Local_Message("WM_QUIT","Redundant_Window","remove")
                            create_window()
                    main.bind("<<Redundant_Window>>",lambda event:MessageBox_Return())
                    pre_window_error_show("""检测到配置文件中的元素重复，程序已自动应用去重的名单，名单不会保存到配置文件中。
是否立即查看重复的元素的情况？""",
                            "随机抽取-配置文件的元素重复",
                            0x34,
                            action={"6":lambda:main.event_generate("<<Redundant_Window>>")},
                            parent=main
                            )
                    name_database1=list(name_database)
                    name_database=list(dict.fromkeys(name_database))
                if configs_access("is_rollcall_once"):
                    rollcall_once_namelist=list(name_database)
                del names
            if name_database==[]:#检查是否为空列表
                pre_window_error_show("json配置为空，请在当前目录下的\"namelist.json\"中写入一个列表。","随机抽取-json配置为空",0x10,parent=main)#弹窗报错                
                start.config(state="disable")#禁用开始按钮
            else:
                is_error_empty=1#设置为非空列表
                start.config(state="normal")
        else:
            if os.path.isdir("./namelist.json")==True:#检测配置是否为文件夹
                pre_window_error_show("json名单为目录，请在当前目录下的\"namelist.json\"文件夹删除，然后再创建此文件","随机抽取-找不到json名单",0x10,parent=main)
            else:
                pre_window_error_show("未找到json名单，请在当前目录下新建\"namelist.json\"文件","随机抽取-找不到json名单",0x10,parent=main)
            if is_error_empty==0:
                start.config(state="disable")
    except Exception:
        try:
            raise
        #except ValueError as json_error:#检查json语法是否正确（Python3.4兼容）
        #    pre_window_error_show("json语法不正确，原因：\n"+str(json_error),"随机抽取-json名单格式错误",0x10)
        except json.decoder.JSONDecodeError as json_error:#检查json语法是否正确
            pre_window_error_show("json语法不正确，原因：\n"+str(json_error),"随机抽取-json名单格式错误",0x10,parent=main)
        except FileNotFoundError as json_error:#检查文件存在性（基本被上面的if-else代码优先执行）
            pre_window_error_show(main.winfo_id(),"找不到json文件，原因：\n"+str(json_error),"随机抽取-找不到json名单",0x10,parent=main)
        except PermissionError as json_error:#检查是否被拒绝访问
            pre_window_error_show("json文件被拒绝读取，原因：\n"+str(json_error),"随机抽取-json名单读取失败",0x10,parent=main)
        except UnicodeDecodeError:
            if not encoding==None:
                pre_window_error_show("名单文件的文本编码错误，原因：\n"+str(tb.format_exc()),"随机抽取-名单文本编码错误",0x10,parent=main)
            else:
                encodes=["ansi","utf-16","utf-16-bom","utf-32","unicode_escape"]
                for encodings in encodes:
                    try:
                        with open("./namelist.json","r",encoding=encodings) as namelist:
                            names=json.load(namelist)
                    except Exception as e:
                        if encodes.index(encodings) == len(encodes)-1:
                            try:
                                raise
                            except UnicodeDecodeError as e:
                                pre_window_error_show("无法识别名单所保存的文本编码，这可能是非纯文本文件，或者纯文本文件本身已经乱码。","随机抽取-无法识别的名单文本编码",0x10,parent=main)
                            except Exception as e:
                                pre_window_error_show("未知错误：\n"+str(tb.format_exc()),"随机抽取-错误",0x10,parent=main)
                        else:
                            print(i)
        except Exception as json_error:#检测其它异常来输出详细信息
            pre_window_error_show("未知错误：\n"+str(tb.format_exc()),"随机抽取-错误",0x10,parent=main)
        if is_error_empty==0:#检查是否为异常配置文件
            start.config(state="disable")
    try:
        del main_window_time
        del main_window_finish_time
    except Exception:
        pass
    if (len(name_database)<2) and (rollcall_once.get()):
        rollcall_once.set(False)
        main.event_generate("<<Configs_Change>>",data=("is_rollcall_once",False))
        #configs_access("is_rollcall_once",value=False,action="change")
        pre_window_error_show("json名单元素少于2个，已自动禁用不重复抽取。","随机抽取-json名单检测",0x30,parent=main)
#延迟执行json_config的代码，主要是为了防止在加载界面时提前弹出错误窗口
try:
    main.iconbitmap(default=cwd_path)
except tk.TclError as icon_error:
    if ("bitmap \"" and "\" not defined") in str(icon_error):
        main.after_idle(lambda:main.iconbitmap(default=cwd_path))
    else:
        raise
#test=thd.Thread(target=json_config)
#test.start()
main.after_idle(json_config)
def event_case():
    window_size_main=(main.winfo_width(),main.winfo_height())
    def is_window_size_changed():
        nonlocal window_size_main
        if (window_size_main[0]!=main.winfo_width()) or (window_size_main[1]!=main.winfo_height()):
            main.event_generate("<<SizeChanged>>")
            print("Configure")
        window_size_main=(main.winfo_width(),main.winfo_height())
    main.after(5,is_window_size_changed)
    main.after(5,event_case)
main.after(0,event_case)

def key_event():
    ken_events=[("<Control-Alt-r>",lambda event:reload.invoke(0)),
                ("<Control-Alt-F1>",lambda event:reload.invoke(1)),
                ("<Control-Alt-F2>",lambda event:reload.invoke(2)),
                ("<Control-Alt-F3>",lambda event:reload.invoke(3)),
                ("<Key-Right>",lambda event:start.invoke()),
                ("<Key-Down>",lambda event:start.invoke()),
                ("<Key-Next>",lambda event:start.invoke()),
                ("<Control-Alt-e>",lambda event:file_menus.invoke(1)),
                ("<Control-Shift-T>",lambda event:window_menus.invoke(1)),
                ("<Shift-F1>",lambda event:about_menu.invoke(0)),
                ("<F1>",lambda event:about_menu.invoke(1)),
                ("<F11>",fullscr_button),
                ("<Control-O>",lambda event:config_menus.invoke(0))
                ]
    for hotkey in ken_events:
        main.bind(*hotkey)
key_event()
show_error=thd.Thread(target=show_pre_window_error)
show_error.start()
#防止主窗口消失
main.mainloop()
