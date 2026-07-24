#! /usr/bin/env python3

import sys, os
import serial
import glob
import tkinter as tk
import tkinter.ttk as ttk
import time
from svbony_powerbox import SVBonyPowerBox


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

class Toplevel1:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''

        top.geometry("570x600")
        top.minsize(1, 1)
        top.resizable(0, 0)
        top.title("PowerHub Control")

        self.top = top

        # Top connection controls
        self.top_frame = ttk.Frame(self.top)
        self.top_frame.place(x=10, y=10, width=550, height=40)

        self.Label1 = ttk.Label(self.top_frame,text="Port:")
        self.Label1.grid(row=0, column=0, padx=(0, 8), pady=5, sticky="w")

        ports=serial_ports()
        f=open('port.txt','r')
        port=f.readlines()[0].strip()
        f.close()
        if not port in ports: port=''
    
        self.port = tk.StringVar(value=port)
        self.Entry1 = ttk.Combobox(self.top_frame,values=ports, textvariable=self.port,state="readonly",width=16)
        self.Entry1.grid(row=0, column=1, padx=5, pady=5)

        self.Button1 = ttk.Button(self.top_frame,text="Connect",command=self.connect)
        self.Button1.grid(row=0, column=2, padx=(15, 5), pady=5)

        self.Button1_1 = ttk.Button(self.top_frame,text="Disconnect",command=self.disconnect,state=tk.DISABLED)
        self.Button1_1.grid(row=0, column=3, padx=5, pady=5)

        # DC 12V frame
        self.Labelframe1 = ttk.LabelFrame(self.top, text="DC 12V")
        self.Labelframe1.place(x=10, y=50, width=550, height=170)

        # Frame holding channels
        dc_frame = ttk.Frame(self.Labelframe1)
        dc_frame.grid(row=0, column=0, padx=1, pady=0)

        # Master ON/OFF buttons
        master_frame = ttk.Frame(self.Labelframe1)
        master_frame.grid(row=0, column=1, padx=(5, 5), pady=10, sticky="ns")

        self.Button4 = ttk.Button(master_frame, text="ON", width=8,command=self.dc_on,state=tk.DISABLED)
        self.Button4.grid(row=0, column=0, pady=(20, 10))

        self.Button4_2 = ttk.Button(master_frame, text="OFF", width=8,command=self.dc_off,state=tk.DISABLED)
        self.Button4_2.grid(row=1, column=0, pady=10)


        # Create DC1 ... DC5
        self.dc_frames = []
        self.dc_on_buttons = []
        self.dc_off_buttons = []
        self.dc_labels = []
        self.dc = []

        for i in range(5):
                frame = ttk.LabelFrame(dc_frame, text=f"DC {i+1}")
                frame.grid(row=0, column=i, padx=1, pady=0, sticky="n")

                btn_on = ttk.Button(frame, text="ON", width=8, command=lambda ch=i: self.dc1_on(ch),state=tk.DISABLED)
                btn_on.grid(row=0, column=0, padx=5, pady=(8,4))

                btn_off = ttk.Button(frame, text="OFF", width=8, command=lambda ch=i: self.dc1_off(ch),state=tk.DISABLED)
                btn_off.grid(row=1, column=0, padx=5, pady=4)

                self.dc.append(tk.StringVar(value='OFF'))
                lbl = ttk.Label(frame, anchor="center", textvariable=self.dc[i])
                lbl.grid(row=2, column=0, pady=(8,8))

                self.dc_frames.append(frame)
                self.dc_on_buttons.append(btn_on)
                self.dc_off_buttons.append(btn_off)
                self.dc_labels.append(lbl)

        # USB Ports
        self.Labelframe1_1 = ttk.LabelFrame(self.top, text="USB Ports")
        self.Labelframe1_1.place(x=10, y=230, width=550, height=120)

        # Container for USB groups
        usb_frame = ttk.Frame(self.Labelframe1_1)
        usb_frame.grid(row=0, column=0, padx=(1,20), pady=0)

        # Master buttons
        master_usb = ttk.Frame(self.Labelframe1_1)
        master_usb.grid(row=0, column=1, padx=(20, 5), pady=5)

        self.Button4_1 = ttk.Button(master_usb, text="ON", width=8,command=self.usb_on,state=tk.DISABLED)
        self.Button4_1.grid(row=0, column=0, pady=(10, 5))

        self.Button4_1_1 = ttk.Button(master_usb, text="OFF", width=8,command=self.usb_off,state=tk.DISABLED)
        self.Button4_1_1.grid(row=1, column=0, pady=5)

        # USB groups
        self.usb_frames = []
        self.usb_on_buttons = []
        self.usb_off_buttons = []
        self.usb_labels = []
        self.usb = []

        usb_names = ["USB-C+1+2", "USB 3+4+5"]

        for i, name in enumerate(usb_names):
                frame = ttk.LabelFrame(usb_frame, text=name)
                frame.grid(row=0, column=i, padx=8, pady=0)

                btn_on = ttk.Button(frame, text="ON", width=8, command=lambda ch=i: self.usb1_on(ch),state=tk.DISABLED)
                btn_on.grid(row=0, column=0, padx=4, pady=(8, 4))

                btn_off = ttk.Button(frame, text="OFF", width=8, command=lambda ch=i: self.usb1_off(ch),state=tk.DISABLED)
                btn_off.grid(row=0, column=1, padx=4, pady=(8, 4))

                self.usb.append(tk.StringVar(value='OFF'))
                lbl = ttk.Label(frame, anchor="center", textvariable=self.usb[i])
                lbl.grid(row=1, column=0, columnspan=2, pady=(4, 0))

                self.usb_frames.append(frame)
                self.usb_on_buttons.append(btn_on)
                self.usb_off_buttons.append(btn_off)
                self.usb_labels.append(lbl)

        # Heaters
        self.Labelframe2 = ttk.LabelFrame(self.top, text="Heaters")
        self.Labelframe2.place(x=10, y=365, width=550, height=95)

        # Heater 1
        heater1_frame = ttk.Frame(self.Labelframe2)
        heater1_frame.grid(row=0, column=0, padx=15, pady=1)

        self.heat1=tk.IntVar(value=0)
        self.Spinbox1 = tk.Spinbox(heater1_frame,from_=0.0,to=100.0,increment=5,width=10,textvariable=self.heat1)
        self.Spinbox1.grid(row=0, column=0, pady=(0, 8))

        self.Button3 = ttk.Button(heater1_frame,text="Set 1",width=8,command=self.heat1set,state=tk.DISABLED)
        self.Button3.grid(row=1, column=0)

        self.heat1val=tk.StringVar(value='0 %')
        self.Label3 = ttk.Label(self.Labelframe2,anchor="center",width=6,textvariable=self.heat1val)
        self.Label3.grid(row=0, column=1, padx=15, pady=(0,20))

        # Heater 2
        heater2_frame = ttk.Frame(self.Labelframe2)
        heater2_frame.grid(row=0, column=2, padx=15, pady=1)

        self.heat2=tk.IntVar(value=0)
        self.Spinbox1_1 = tk.Spinbox(heater2_frame,from_=0.0,to=100.0,increment=5,width=10,textvariable=self.heat2)
        self.Spinbox1_1.grid(row=0, column=0, pady=(0, 8))

        self.Button3_1 = ttk.Button(heater2_frame,text="Set 2",width=8,command=self.heat2set,state=tk.DISABLED)
        self.Button3_1.grid(row=1, column=0)

        self.heat2val=tk.StringVar(value='0 %')
        self.Label4 = ttk.Label(self.Labelframe2,anchor="center",width=6,textvariable=self.heat2val)
        self.Label4.grid(row=0, column=3, padx=15, pady=(0,20))


        # Master OFF
        master_heater_frame = ttk.Frame(self.Labelframe2)
        master_heater_frame.grid(row=0, column=4, padx=(40, 15))

        self.Button7_1 = ttk.Button(master_heater_frame,text="OFF",width=8,command=self.heat_off,state=tk.DISABLED)
        self.Button7_1.grid(row=0, column=0, pady=20)


        # Regulated DC
        self.Labelframe3 = ttk.LabelFrame(self.top, text="Regulated DC")
        self.Labelframe3.place(x=10, y=475, width=550, height=70)

        self.reg=tk.DoubleVar(value=0)
        self.Spinbox1_2 = tk.Spinbox(self.Labelframe3,from_=0.0,to=15.0,increment=0.5,width=10,textvariable=self.reg)
        self.Spinbox1_2.grid(row=0, column=0, padx=(10, 15))

        self.Button6 = ttk.Button(self.Labelframe3,text="Set",width=8,command=self.reg_set,state=tk.DISABLED)
        self.Button6.grid(row=0, column=1, padx=10)

        self.reg_val=tk.StringVar(value='0 V')
        self.Label5 = ttk.Label(self.Labelframe3,anchor="center",width=6,textvariable=self.reg_val)
        self.Label5.grid(row=0, column=2, padx=15)

        self.Button7 = ttk.Button(self.Labelframe3,text="OFF",width=8,command=self.reg_off,state=tk.DISABLED)
        self.Button7.grid(row=0, column=3, padx=(10, 0))


        # Refresh button
        self.Button5 = ttk.Button(self.top,text="Refresh",width=10,command=self.refresh,state=tk.DISABLED)
        self.Button5.place(x=245, y=555)

    def connect(self):
        port=self.port.get()
        if not len(port)==-1: 
            #self.com=serial.Serial(port,baud,timeout=0.5)
            self.hub=SVBonyPowerBox(port)
            try: 
                self.refresh()
            except OSError: return
            #enable buttons
            self.Button1_1.config(state=tk.NORMAL)
            self.Button4.config(state=tk.NORMAL)
            self.Button4_2.config(state=tk.NORMAL)
            self.Button5.config(state=tk.NORMAL)
            self.Button7.config(state=tk.NORMAL)
            self.Button6.config(state=tk.NORMAL)
            self.Button7_1.config(state=tk.NORMAL)
            self.Button3_1.config(state=tk.NORMAL)
            self.Button3.config(state=tk.NORMAL)
            self.Button4_1.config(state=tk.NORMAL)
            self.Button4_1_1.config(state=tk.NORMAL)
            
            for i in range(5):
                self.dc_on_buttons[i].config(state=tk.NORMAL)
                self.dc_off_buttons[i].config(state=tk.NORMAL)
                
            for i in range(2):
                self.usb_on_buttons[i].config(state=tk.NORMAL)
                self.usb_off_buttons[i].config(state=tk.NORMAL)
            

    def disconnect(self):
        #self.com.close() 
        self.hub.close()       
        #disable buttons
        self.Button1_1.config(state=tk.DISABLED)
        self.Button4.config(state=tk.DISABLED)
        self.Button4_2.config(state=tk.DISABLED)
        self.Button5.config(state=tk.DISABLED)
        self.Button7.config(state=tk.DISABLED)
        self.Button6.config(state=tk.DISABLED)
        self.Button7_1.config(state=tk.DISABLED)
        self.Button3_1.config(state=tk.DISABLED)
        self.Button3.config(state=tk.DISABLED)
        self.Button4_1.config(state=tk.DISABLED)
        self.Button4_1_1.config(state=tk.DISABLED)
        
        for i in range(5):
            self.dc_on_buttons[i].config(state=tk.DISABLED)
            self.dc_off_buttons[i].config(state=tk.DISABLED)
            
        for i in range(2):
            self.usb_on_buttons[i].config(state=tk.DISABLED)
            self.usb_off_buttons[i].config(state=tk.DISABLED)

    def dc1_on(self,number):
        self.hub.set_dc(number,True)
        self.dc[number].set('ON')

    def dc1_off(self,number):
        self.hub.set_dc(number,False)
        self.dc[number].set('OFF')

    def dc_on(self):
        for i in range(5): self.dc1_on(i)

    def dc_off(self):
        for i in range(5): self.dc1_off(i)

    def usb1_on(self,number):
        self.hub.set_usb(number,True)
        self.usb[number].set('ON')

    def usb1_off(self,number):
        self.hub.set_usb(number,False)
        self.usb[number].set('OFF')

    def usb_on(self):
        for i in range(2): self.usb1_on(i)

    def usb_off(self):
        for i in range(2): self.usb1_off(i)

    def heat1set(self):
        val=int(self.heat1.get())
        self.hub.set_pwm(0,val)
        self.heat1val.set(f'{val} %')

    def heat2set(self):
        val=int(self.heat2.get())
        self.hub.set_pwm(1,val)
        self.heat2val.set(f'{val} %')

    def heat_off(self):
        self.hub.set_pwm(0,0)
        self.heat1.set(0)
        self.heat1val.set('0 %')
        self.hub.set_pwm(1,0)
        self.heat2.set(0)
        self.heat2val.set('0 %')

    def reg_set(self):
        val=float(self.reg.get())
        self.hub.set_regulated_voltage(val)
        self.reg_val.set(f'{val:.1f} V')

    def reg_off(self):
        self.hub.set_regulated_voltage(0)
        self.reg.set(0)
        self.reg_val.set('0 V')

    def refresh(self):
        status=self.hub.get_status()     
        for i in range(5): 
            if status['dc'][i]: self.dc[i].set('ON')
            else: self.dc[i].set('OFF')
        for i in range(2): 
            if status['usb'][i]: self.usb[i].set('ON')
            else: self.usb[i].set('OFF')
            
        self.heat1.set(round(status['pwm'][0]))
        self.heat1val.set(f'{status["pwm"][0]:.0f} %')
        self.heat2.set(round(status['pwm'][1]))
        self.heat2val.set(f'{status["pwm"][1]:.0f} %')
        self.reg.set(round(status["regulated_voltage"],1))
        self.reg_val.set(f'{status["regulated_voltage"]:.1f} V')
        return

    def on_closing(self):
        try: 
            self.disconnect()
            time.sleep(1)
        except: pass
        root.destroy()


if not os.path.isfile('port.txt'):
    f=open('port.txt','w')
    f.write('\n')
    f.close()

if __name__ == '__main__':
    '''Main entry point for the application.'''
    global root
    root = tk.Tk()
    #root.protocol( 'WM_DELETE_WINDOW' , root.destroy)
    # Creates a toplevel widget.
    global _top1, _w1
    _top1 = root
    _w1 = Toplevel1(_top1)
    root.protocol("WM_DELETE_WINDOW", _w1.on_closing)
    root.mainloop()




