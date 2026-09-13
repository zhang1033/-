import tkinter as tk
import ctypes as c
class tkex:
    def Num_Spinbox(*args,**kw):
        num_spinbox=tk.Spinbox(*args,**kw)
        values={"per_value":None,"new_value":None}
        def while_checking(event=None):
            if num_spinbox.get().isdigit():
                values["per_value"]=num_spinbox.get()
                num_spinbox.after_idle(lambda:values.update({"new_value":num_spinbox.get()}))
            def while_checking_sub():
                if not str(values["new_value"]).isdigit():
                    values["new_value"]=values["per_value"]
                    num_spinbox.delete(0,"end")
                    num_spinbox.insert("end",values["per_value"])
                    num_spinbox.selection("range",0,"end")
                else:
                    values["per_value"]=num_spinbox.get()
                    num_spinbox.after(1,lambda:values.update({"new_value":num_spinbox.get()}))
            num_spinbox.after_idle(while_checking_sub)
            return True
        num_spinbox.config(validate="key",vcmd=while_checking)
        return(num_spinbox)
    class Progressbar_ex():
        def __init__(self,muster=None,frame_bg="#FFFFFF",progress_bg="#000000",mode="progress",relief="flat",style="x",maximum=100,value=0,*args,**kw):
            kw.pop("bg",None)
            kw.pop("relief",None)
            self.global_args=locals()
            progress_bar_frame=tk.Frame(muster,bg=frame_bg,relief=relief,*args,**kw)
            progress_bar_prog=tk.Frame(progress_bar_frame,bg=progress_bg)
            self.progress_bar=(progress_bar_frame,progress_bar_prog)
            self.after_while_check=None
            self.size={"pri":[None,None],"ori":[None,None]}
        def change_progress(self):
            if self.global_args["mode"]=="roll":
                def progress():
                    relwidth=20*self.progress_bar[0].winfo_pixels("1i")/96/{"x":self.progress_bar[0].winfo_width(),"y":self.progress_bar[0].winfo_height()}[self.global_args["style"]]
                    percentage=self.global_args["value"]/self.global_args["maximum"]
                    rel=percentage-relwidth*percentage
                    if percentage>1:
                        rel=1-relwidth
                        self.global_args["value"]=self.global_args["maximum"]
                    elif percentage<0:
                        rel=0
                        self.global_args["value"]=0
                    else:
                        pass
                    #self.progress_bar[1].update()
                    if self.global_args["style"]=="x":
                        self.progress_bar[1].place(
                            relx=rel,
                            rely=0,
                            relheight=1,
                            relwidth=0,
                            width=20*self.progress_bar[0].winfo_pixels("1i")/96,
                            anchor="nw"
                            )
                        #print(20*self.progress_bar[0].winfo_pixels("1i")/96)
                    elif self.global_args["style"]=="y":
                        self.progress_bar[1].place(
                            rely=1-rel,
                            relx=0,
                            relwidth=1,
                            relheight=0,
                            height=20*self.progress_bar[0].winfo_pixels("1i")/96,
                            anchor="sw"
                            )
                progress()
                def while_check():
                    self.progress_bar[0].after(5,lambda:self.size.update({"ori":[self.progress_bar[0].winfo_width(),self.progress_bar[0].winfo_height()]}))
                    if not self.size["pri"]==self.size["ori"]:
                        progress()
                        self.size.update({"pri":self.size["ori"]})
                    self.after_while_check=self.progress_bar[0].after(5,while_check)
                while_check()
            elif self.global_args["mode"]=="progress":
                if not self.after_while_check==None:
                    self.progress_bar[0].after_cancel(self.after_while_check)
                    self.after_while_check=None
                percentage=self.global_args["value"]/self.global_args["maximum"]
                if percentage>1:
                    self.global_args["value"]=self.global_args["maximum"]
                elif percentage<0:
                    self.global_args["value"]=0
                else:
                    pass
                if self.global_args["style"]=="x":
                    self.progress_bar[1].place(relx=0,rely=0,width=0,height=0,relheight=1,relwidth=self.global_args["value"]/self.global_args["maximum"],anchor="nw")
                elif self.global_args["style"]=="y":
                    self.progress_bar[1].place(relx=0,rely=1,height=0,width=0,relheight=self.global_args["value"]/self.global_args["maximum"],relwidth=1,anchor="sw")
            else:
                raise ValueError("\"mode\"参数只能为roll 或 progress（默认值）")
        def pack_ex(self,change=False,*args,**kw):
            if change:
                self.progress_bar[0].pack_configure(*args,**kw)
            else:
                if not "ipadx" in kw:
                    kw["ipadx"]=50*self.progress_bar[0].winfo_pixels("1i")/96
                if not "ipady" in kw:
                    kw["ipady"]=10*self.progress_bar[0].winfo_pixels("1i")/96
                self.progress_bar[0].pack(*args,**kw)
            self.progress_bar[0].update()
            self.change_progress()
        def place_ex(self,change=False,*args,**kw):
            if change:
                self.progress_bar[0].place_configure(*args,**kw)
            else:
                if not "width" in kw:
                    kw["width"]=100*self.progress_bar[0].winfo_pixels("1i")/96
                if not "height" in kw:
                    kw["height"]=20*self.progress_bar[0].winfo_pixels("1i")/96
                self.progress_bar[0].place(*args,**kw)
            self.progress_bar[0].update()
            self.change_progress()
        def grid_ex(self,change=False,*args,**kw):
            if change:
                self.progress_bar[0].grid_configure(*args,**kw)
            else:
                if not "ipadx" in kw:
                    kw["ipadx"]=50*self.progress_bar[0].winfo_pixels("1i")/96
                if not "ipady" in kw:
                    kw["ipady"]=10*self.progress_bar[0].winfo_pixels("1i")/96
                self.progress_bar[0].grid(*args,**kw)
            self.progress_bar[0].update()
            self.change_progress()
        def config_ex(self,*args,**kw):
            def _sub(self,muster=self.global_args["muster"],frame_bg=self.global_args["frame_bg"],progress_bg=self.global_args["progress_bg"],mode=self.global_args["mode"],relief=self.global_args["relief"],style=self.global_args["style"],maximum=self.global_args["maximum"],value=self.global_args["value"],*args,**kw):
                kw.pop("bg",None)
                kw.pop("relief",None)
                self.global_args=locals()
                self.progress_bar[0].config(bg=frame_bg,relief=relief,*args,**kw)
                self.progress_bar[1].config(bg=progress_bg)
                self.change_progress()
            _sub(self,*args,**kw)
        def get_ex(self):
            return self.global_args["value"]
