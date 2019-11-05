#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import string
import time
import tkinter as tk

import main

def create_mainwindow():
    global win_main
    win_main = tk.Tk()
    win_main.title(f"Python Battleships")
    win_main.protocol("WM_DELETE_WINDOW", close_main)
    return win_main

def close_main():
    global win_main
    win_main.destroy()
    print('Action cancelled by user. Exiting...')
    time.sleep(2)
    raise SystemExit

def nothing():
    pass

def exit():
    global win
    win.destroy()
    try:
        close_main()
    except:
        pass
    print('Action cancelled by user. Exiting...')
    time.sleep(2)
    raise SystemExit

""" USELESS SINCE CONFIG FILE ADDED
def input_boat():
    global win,e,var
    win = tk.Tk()
    win.title("Python Battleships - Nbr Boats")
    win.protocol("WM_DELETE_WINDOW", exit)
    
    tk.Label(win,text="How many boats do you want to play with :").grid(row=1,column=1)
    e = tk.Entry(win)
    e.grid(row=1,column=2)
    win.bind("<Return>",callback_boat)
    tk.Button(win,text="Validate!",command=callback_coords).grid(row=2,column=1,columnspan=2)

    e.focus_force()
    win.mainloop()
    return var

def callback_boat(tk_event=None):
    global win,e,var
    try:
        var = int(e.get())
        win.destroy()
    except:
        e.delete(0, tk.END)
        e.insert(0, "use only numbers")
"""
def input_coords(capacity,player_nbr,boat_id):
    global win, cap, var_x, var_y, var_rotation, x, y, rotation
    win = tk.Tk()
    win.title(f"Player {player_nbr} - Place Boat {boat_id}")
    win.protocol("WM_DELETE_WINDOW", exit)
    win.bind("<Return>",callback_coords)
    
    tk.Label(win,text="boat's capacity :").grid(row=1,column=1)
    cap = tk.StringVar()
    cap.set(capacity)
    tk.Entry(win,justify="center",textvariable=cap,state="disabled",width=2).grid(row=1,column=2)

    tk.Label(win,text="Enter the x position of the boat :").grid(row=2,column=1)
    x = tk.Scale(win,from_=1,to=10,orient="horizontal",takefocus=1)
    x.grid(row=2,column=2)
    
    tk.Label(win,text="Enter the y position of the boat :").grid(row=3,column=1)
    y = tk.Scale(win,from_=1,to=10,orient="horizontal",takefocus=1)
    y.grid(row=3,column=2)

    tk.Label(win,text="Choose the boat's rotation :").grid(row=4,column=1)
    choices = ['Horizontal','Vertical']
    rotation = tk.StringVar(win)
    rotation.set(choices[0])
    tk.OptionMenu(win,rotation,*choices).grid(row=4,column=2)

    tk.Button(win,text="Validate!",command=callback_coords).grid(row=5,column=1,columnspan=2)

    x.focus_force()
    win.mainloop()

    return (int(cap.get()),(var_x,var_y,var_rotation))

def callback_coords(tk_event=None):
    global win, cap, var_x, var_y, var_rotation, x, y, rotation
    errors = []

    var_x = x.get()
    var_y = y.get()
    var_rotation = 0 if rotation.get() =='Horizontal' else 1

    if not((main.size[0]+1)-int(cap.get()) >= var_x > 0) and not(var_rotation):
        errors.append("x OOB")
        x.set(1)

        popup(win,"The boat must fit in the grid!")

    elif not((main.size[1]+1)-int(cap.get()) >= var_y > 0) and var_rotation:
        errors.append("y OOB")
        y.set(1)

        popup(win,"The boat must fit in the grid!")

    if errors == []:
        del(x,y)
        win.destroy()
        
def popup(window,msg,note=""):
    global popup_win
    popup_win = tk.Toplevel(master=window)
    popup_win.title("Next turn")
    popup_win.protocol("WM_DELETE_WINDOW", nothing)
    tk.Label(popup_win,text=msg).pack()
    if note != "":
        tk.Label(popup_win,text=note).pack()
    ok = tk.Button(popup_win,text="OK",command=popup_close)
    popup_win.bind("<Return>",popup_close)
    ok.pack()
    ok.focus_force()
    window.wait_window(popup_win)
    return 1

def popup_close(tk_event=None):
    global popup_win
    popup_win.destroy()

def input_target(window,player_id):
    global target, x_target, y_target, win
    win = tk.Toplevel(master=window)
    win.title(f"Player {player_id} - target selector")
    win.protocol("WM_DELETE_WINDOW",nothing)
    tk.Label(win,text="Enter your target's coordinates : ").grid(row=1,column=1)
    target = tk.Entry(win,width=27)
    target.grid(row=1,column=2)
    win.bind("<Return>",callback_target)
    tk.Button(win,text="Validate!",command=callback_target).grid(row=2,column=1,columnspan=2)

    target.focus_force()
    win.wait_window()
    return (x_target,y_target)

def callback_target(tk_event=None):
    global win, target, x_target, y_target
    var = target.get()
    errors = []
    try:
        x_target = int( "".join(var[1:]) )
    except:
        errors.append("x_target")

        target.delete(0,tk.END)
        target.insert(0,"target is incorrect")
        x_target = 0
    
    try:
        y_target = main.letter.index(var[0].upper())+1
    except ValueError:
        errors.append("y_target")

        target.delete(0,tk.END)
        target.insert(0,"target is incorrect")
        y_target = 0

    if x_target < 0 or x_target > main.size[0]:
        errors.append("x_target OOB")

        target.delete(0,tk.END)
        target.insert(0,"the target isn't in the ocean!")

    if y_target < 0 or y_target > main.size[1]:
        errors.append("y_target OOB")

        target.delete(0,tk.END)
        target.insert(0,"the target isn't in the ocean!")

    if errors == []:
        win.destroy()

if __name__ == '__main__':
    os.system("main.py")
