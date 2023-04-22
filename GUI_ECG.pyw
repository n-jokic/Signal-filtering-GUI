# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 11:37:36 2022

@author: Milosh Yokich
"""
import tkinter as tk

from tkinter import filedialog

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
import scipy 
matplotlib.rcParams['figure.autolayout'] = True

import numpy as np

global up_data
global up_time_plot
global up_filtered

global sig
global time
global sig_sl
global time_sl
global ax

global old_sig
global old_filt




root = tk.Tk()
root.wm_title("GUI MAS_3_1")

filters = ["butter", "cheby1", "cheby2", "ellip", "bessel"]
options = [ "Butterworth LP filter", 
           "Chebyshev I LP filter",
           "Chebyshev II LP filter", 
           "Elliptic filter", 
           "Bessel filter"]




up_data = False

up_time_plot = False
up_filtered = False

picked = tk.StringVar()

filt_freq = tk.StringVar()
filt_size = tk.StringVar()




start =0
end = 2



#Variables
delimiter = tk.StringVar()
fs = tk.StringVar()
file_path = tk.StringVar()
fs.set(1000)
delimiter.set('\\n')


def fs_btn(win):
    global up_data
    
    if float(fs.get()) <=0:
        tk.messagebox.showwarning("Warning", "Sampling rate must be grater than 0")
    else:
        win.destroy() 
        up_data = True
    
    return

def delimiter_btn(win):
    
    if delimiter .get() == '':
        tk.messagebox.showwarning("Warning", "Delimiter must not be an empty string")
    else:
        if delimiter .get() == '\\n':
            delimiter .set('\n')
         
        win.destroy() 
        
        top = tk.Toplevel(root)
        frame = tk.Frame(top)
        frame.pack()
        fs_entry = tk.Entry(frame, textvariable=fs)
        fs_entry.pack(side=tk.RIGHT , padx =10)
        tk.Label(frame, text = "Enter Sampling Rate:").pack(side=tk.LEFT)
        tk.Button(top, text = "Submit", command= \
                  lambda: fs_btn(top)).pack(side=tk.BOTTOM, pady=10, \
                                            padx=10, ipadx=100) 
    return

def open_f():
    root.filename = tk.filedialog.askopenfilename(initialdir="/vezba 9", \
                    title = "Sel. a File", filetypes=(("txt files", "*.txt"), \
                    ("csv files", "*.csv")))
        
    file_path.set(root.filename)

    
    if file_path.get() == '':
        tk.messagebox.showwarning("Warning", "File was not selected")
    else:
        top = tk.Toplevel()
        frame = tk.Frame(top)
        frame.pack()
        del_entry = tk.Entry(frame, textvariable=delimiter)
        del_entry.pack(side=tk.RIGHT , padx =10)
        tk.Label(frame, text = "Enter Data Delimiter:").pack(side=tk.LEFT)
        tk.Button(top, text = "Submit", command= \
                  lambda: delimiter_btn(top)\
                  ).pack(side=tk.BOTTOM, pady=10, padx=10, ipadx=100)
    return


fig_time = Figure(figsize=(5, 4), dpi=60)
fig_freq = Figure(figsize=(5, 4), dpi=60)


canvas = FigureCanvasTkAgg(fig_time, master=root)  # A tk.DrawingArea.

canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


def update_data():
    global sig, sig_sl, time_sl
    global time, up_data, up_time_plot, up_freq_plot
    if(up_data):
        sig = open(file_path.get()).read().split(delimiter.get())

        sig = [float(x) for x in sig]

        N = len(sig)
        Fs = float(fs.get())
        time = [i/Fs for i in range(N)]
        up_data = False
        
        up_time_plot = True
        
        start = 0
        end = 2
        data_slice = lambda y, start, end: [x for x, data in enumerate(y) \
                                            if y[x] >= start and y[x]<= end]
        idx = data_slice(time, start, end)

        time_sl = [time[i] for i in idx]
        sig_sl = [sig[i] for i in idx]
        
    root.after(100, update_data)
    return

def update_time_plot():
    global sig, up_time_plot, ax
    
    if(up_time_plot):
        up_time_plot = False
        ax = fig_time.add_subplot(111)
        ax.plot(time, sig,color = 'black', label = 'original', linewidth = 1.5)
        ax.set_title('ECG measurment')
        ax.set_ylabel('$y(t)$ [mV]')
        ax.set_xlabel('$t$ [s]')
        ax.set_xlim([start, end])
        ax.grid('on')
        
        if(len(ax.lines) > 1):
            ax.lines.pop(0)
        
        canvas.draw()
        
        
    
    root.after(100, update_time_plot)
    return

def picked_filter():
    global up_filtered
    up_filtered = True
    return

def update_filtered():
    global up_filtered
    
    
    if(up_filtered):
        up_filtered = False
        
        if(not picked.get() in filters ):
            tk.messagebox.showwarning("Warning", "Filter type must be selected")
            
            root.after(100, update_filtered)
            return
   
        try:
            N = abs(int(filt_size.get()))
        except:
            tk.messagebox.showwarning("Warning", "Filter size must be an integer")
            root.after(100, update_filtered)
            return
        
        try:
            f = abs(float(filt_freq.get()))
        except:
            tk.messagebox.showwarning("Warning", "Cutoff frequency must be a float")
            root.after(100, update_filtered)
            return
        
        sos = scipy.signal.iirfilter(N, f, rp=1, rs=40, btype='lowpass', \
            analog=False, ftype=picked.get(), output='sos', fs=float(fs.get()))
        sig_filt = scipy.signal.sosfiltfilt(sos, sig)
        
        ax.plot(time, sig_filt,color = 'r', label = 'filtered')
        ax.set_title('ECG measurment')
        ax.set_ylabel('$y(t)$ [mV]')
        ax.set_xlabel('$t$ [s]')
        ax.set_xlim([start, end])
        ax.grid('on')
        
        if(len(ax.lines) > 2):
            ax.lines.pop(1)
            
        ax.legend()
        
        canvas.draw()
        
    root.after(100, update_filtered)

    return
    





button = tk.Button(master=root, text="Quit", command=_quit)
button.pack(side=tk.BOTTOM)
sel_file = tk.Button(root, text="Load Data", command=open_f).pack(side=tk.BOTTOM)



frame = tk.Frame(root)
frame.pack(side=tk.LEFT)
filt_freq.set(80)
freq_entry = tk.Entry(frame, textvariable=filt_freq)
freq_entry.pack(side=tk.RIGHT , padx =10)
tk.Label(frame, text = "Filter Cutoff Freqnuency [Hz]:").pack(side=tk.LEFT)



frame = tk.Frame(root)
frame.pack(side=tk.LEFT)
filt_size.set(10)
size_entry = tk.Entry(frame, textvariable=filt_size)
size_entry.pack(side=tk.RIGHT , padx =10)
tk.Label(frame, text = "Filter Order:").pack(side=tk.LEFT)

picked.set("Select a Filter")
drop = tk.OptionMenu(root, picked, *filters)
drop.pack(side=tk.BOTTOM)


filt_btn = tk.Button(root, text="Apply Filter", command =  picked_filter)
filt_btn.pack(side = tk.BOTTOM)


update_data()
update_time_plot()
update_filtered()
tk.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.