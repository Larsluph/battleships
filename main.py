#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import random
import socket
import string
import sys
import time
import tkinter as tk
import tkinter.colorchooser
import tkinter.font
import tkinter.messagebox
from typing import Iterable, Union

import custom_module
from custom_module.utilities import menu_generator, strfill


class Board:
  """board object"""
  def __init__(self, colors=None):
    self.scale = (500/get_cfg("size")[0], 500/get_cfg("size")[1]) # store the length of a tile
    self.color = get_cfg(param='colors') if not colors else colors # stores board's colors in a dict
    self._width = 5

    self.size = get_cfg("size") # get the size of the board
    self.history = list() # stores all canvas' drawing history
    self.status_var = tk.StringVar(value='{dmg_status}') # stores last shot's status ('hit' / 'sunk' / 'miss')
    self.highlighted = (None, None) # stores the highlighted tile's coordinates
    self.grid_font = ("Helvetica", 18, "bold") # font to use when drawing columns / rows index

  def generate(self, win: tk.Tk, player: int):
    """generate label and canvas"""
    # set the board's title
    if player == 1:
      self.txt = "Your Playboard"
    else:
      self.txt = "Enemy's Playboard"

    # create board related widgets
    self.txt = tk.Label(win, text=self.txt)
    self.board = tk.Canvas(win, height=(self.size[0]+1)*self.scale[1], width=(self.size[1]+1)*self.scale[0], bg=self.color["background"])

    return

  def get_tile_coords(self, coordinates: tuple):
    """return (x, y) from the canvas' coordinates or (None, None) if it isn't a valid tile"""
    errors = []
    if not(1 <= (target_x := coordinates[0] // self.scale[0]) <= self.size[0]): # if x_target isn't in the grid
      errors.append("x OOB")

    if not(1 <= (target_y := coordinates[1] // self.scale[1]) <= self.size[1]): # if y_target isn't in the grid
      errors.append("y OOB")

    if not(errors):
      return (round(target_x), round(target_y))
    else:
      return (None, None)

  def draw_grid(self):
    """draw the canvas' grid"""
    self.board.create_line(self.scale[0], 3, (self.size[0]+1)*self.scale[0], 3, width=self._width, fill=self.color["grid"])
    self.board.create_line(3, self.scale[1], 3, (self.size[1]+1)*self.scale[1], width=self._width, fill=self.color["grid"])

    i=self.scale[0]
    while i <= (self.size[0]+1)*self.scale[0]:
      self.board.create_line(0, i, (self.size[0]+1)*self.scale[0], i, width=self._width, fill=self.color["grid"]) # draw x lines
      i+=self.scale[0]

    i=self.scale[1]
    while i <= (self.size[1]+1)*self.scale[1]:
      self.board.create_line(i, 0, i, (self.size[1]+1)*self.scale[1], width=self._width, fill=self.color["grid"]) # draw y lines
      i+=self.scale[1]

    for x in range(self.size[0]):
      self.board.create_text( ( (self.scale[0]*x)+(self.scale[0]*1.5), self.scale[1]/2 ) , text=str(x+1), font=self.grid_font)

    letter = list(string.ascii_uppercase)
    for y in range(self.size[1]):
      self.board.create_text( ( self.scale[0]/2, (self.scale[1]*y)+(self.scale[1]*1.5) ) , text=letter[y], font=self.grid_font)

  def draw_boat(self, boat: "Boat"):
    """draw a boat on the canvas"""
    if boat.base_coordinates[2] == 0:
      # if boat's rotation is horizontal
      self.board.create_oval(
        boat.base_coordinates[0]*self.scale[0], boat.base_coordinates[1]*self.scale[1],
        (boat.base_coordinates[0]*self.scale[0])+(boat.capacity*self.scale[0]), (boat.base_coordinates[1]*self.scale[1])+self.scale[1],
        outline=self.color["boat"], fill=self.color["boat"], width=1)
    else:
      # if boat's rotation is vertical
      self.board.create_oval(
        boat.base_coordinates[0]*self.scale[0], boat.base_coordinates[1]*self.scale[1],
        (boat.base_coordinates[0]*self.scale[0])+self.scale[0], (boat.base_coordinates[1]*self.scale[1])+(boat.capacity*self.scale[1]),
        outline=self.color["boat"], fill=self.color["boat"], width=1)

  def draw_hit(self, coordinates: tuple):
    """draw a hit on the canvas"""
    self.board.create_line(
      coordinates[0]*self.scale[0], (coordinates[1]+1)*self.scale[1],
      (coordinates[0]+1)*self.scale[0], coordinates[1]*self.scale[1],
      width=self._width, fill=self.color["hit"])

  def draw_drown(self, boat: "Boat"):
    """draw a drown boat"""
    if not(boat.base_coordinates[2]):
      # if boat's rotation is horizontal
      for x in range(boat.capacity):
        self.board.create_line(
          (boat.base_coordinates[0]+x)*self.scale[0], (boat.base_coordinates[1])*self.scale[1],
          (boat.base_coordinates[0]+x+1)*self.scale[0], (boat.base_coordinates[1]+1)*self.scale[1],
          width=self._width, fill=self.color["hit"])
        self.board.create_line(
          (boat.base_coordinates[0]+x)*self.scale[0], (boat.base_coordinates[1]+1)*self.scale[1],
          (boat.base_coordinates[0]+x+1)*self.scale[0], (boat.base_coordinates[1])*self.scale[1],
          width=self._width, fill=self.color["hit"])
    else:
      # if boat's rotation is vertical
      for x in range(boat.capacity):
        self.board.create_line(
          (boat.base_coordinates[0])*self.scale[0], (boat.base_coordinates[1]+x)*self.scale[1],
          (boat.base_coordinates[0]+1)*self.scale[0], (boat.base_coordinates[1]+x+1)*self.scale[1],
          width=self._width, fill=self.color["hit"])
        self.board.create_line(
          (boat.base_coordinates[0]+1)*self.scale[0], (boat.base_coordinates[1]+x)*self.scale[1],
          (boat.base_coordinates[0])*self.scale[0], (boat.base_coordinates[1]+x+1)*self.scale[1],
          width=self._width, fill=self.color["hit"])

  def draw_miss(self, coordinates: tuple):
    """draw a missed shot"""
    self.board.create_line(
      (coordinates[0]+1)*self.scale[0], (coordinates[1]+1)*self.scale[1],
      coordinates[0]*self.scale[0], coordinates[1]*self.scale[1],
      width=self._width, fill=self.color["miss"])
    self.board.create_line(
      (coordinates[0])*self.scale[0], (coordinates[1]+1)*self.scale[1],
      (coordinates[0]+1)*self.scale[0], coordinates[1]*self.scale[1],
      width=self._width, fill=self.color["miss"])

  def highlight_tile(self, coordinates: tuple):
    """highlight a tile on the board"""
    if coordinates == (None, None):
      self.clear_highlight()
    else:
      self.board.create_rectangle(
        coordinates[0]*self.scale[0], coordinates[1]*self.scale[1],
        (coordinates[0]+1)*self.scale[0], (coordinates[1]+1)*self.scale[1],
        width=self._width, outline=self.color["highlight"])

      self.highlighted = coordinates

  def clear_highlight(self):
    """clear the highlighted tile"""
    self.highlighted = (None, None)


class Boat:
  """Boat object"""
  def __init__(self, properties: tuple):
    self.capacity = properties[0]
    self.base_coordinates = properties[1]
    self.list_coordinates = []
    self.hp = self.capacity
    self.damages = list()
    for _ in range(self.capacity):
      self.damages.append(1)

    for x in range(self.capacity):
      if self.base_coordinates[2] == 0:
        self.list_coordinates.append( (self.base_coordinates[0]+x, self.base_coordinates[1]) )
      else:
        self.list_coordinates.append( (self.base_coordinates[0], self.base_coordinates[1]+x) )

  def hit(self, player: "Player", board: "Board", damaged_tile: int):
    """hit a boat"""
    self.damages[damaged_tile] = 0
    self.hp -= 1
    player.hp -= 1

    board.draw_hit(self.list_coordinates[damaged_tile])
    board.history.append(["hit", self.list_coordinates[damaged_tile]])


class Player:
  """Player object"""
  def __init__(self, id: int, boatnbr: int):
    self.id = id
    self.boatnbr = boatnbr
    self.hp = 0
    self.boats = []
    self.list_coordinates = [None]
    self.list_shots = []
    self.ammo = get_cfg("ammo")
    self.stats = {
      "shots": 0,
      "miss": 0,
      "hits": 0,
      "sunk": 0
    }

  def create_boards(self):
    """generate boards"""
    self.board_player = Board()
    self.board_opponent = Board()

    return


class ApplicationClass:
  """main game object"""
  def __init__(self, players: Iterable, nbr_players: int, net: bool, is_host: bool, server: "server socket", connection: "remote socket connection"):
    self.p1, self.p2 = players
    self.players = players
    self.nbr_players = nbr_players

    self.net = net
    self.is_host = is_host
    self.server = server
    self.connection = connection

    self.win = tk.Tk()
    self.win.title(f"Python Battleships")
    self.win.resizable(False, False)
    self.win.protocol("WM_DELETE_WINDOW", self.close)

  def close(self):
    """close main window and exit game"""
    try:
      self.win.destroy()
    except:
      pass
    print('Action cancelled by user. Exiting...')
    time.sleep(2)
    raise SystemExit

  def set_player_turn(self, player: "Player", opponent: "Player"):
    "set current player's turn"
    self.player = player
    self.opponent = opponent

  def gen_boards(self):
    """regenerate whole board"""
    for player in self.players:
      player.board_player.generate(self.win, 1)
      player.board_opponent.generate(self.win, 2)
      player.board_opponent.board.bind("<Button-1>", self.callback_highlight)

      for boat in player.boats:
        player.board_player.draw_boat(boat)

      for board in [player.board_player, player.board_opponent]:
        board.draw_grid()
        for status, arg in board.history:
          if status == "miss":
            board.draw_miss(arg)
          elif status == "hit":
            board.draw_hit(arg)
          elif status == "drown":
            board.draw_drown(arg)
          elif status == "boat":
            board.draw_boat(arg)

    grid_set(*self.players)

    return

  def callback_highlight(self, event: "tkinter event"):
    self.gen_boards()
    if self.net:
      if self.is_host:
        show_win(self.p1, self.p2)
      else:
        show_win(self.p2, self.p1)
    else:
      show_win(self.player, self.opponent)
    update_window(self.win)
    self.player.board_opponent.highlight_tile(self.player.board_opponent.get_tile_coords((event.x, event.y)))


class InputCoords:
  """Boats window selector"""
  def __init__(self, capacity: int, player_nbr: int, boat_id: int):
    self.win = tk.Tk()
    self.win.title(f"Player {player_nbr} - Place Boat {boat_id}")
    self.win.resizable(False, False)
    self.win.protocol("WM_DELETE_WINDOW", self.close)
    self.win.bind("<Return>", self.callback)
    self.win.bind("<space>", self.callback)

    tk.Label(self.win, text="boat's capacity :").grid(row=1, column=1)
    self.cap = tk.StringVar()
    self.cap.set(capacity)
    tk.Entry(self.win, justify="center", textvariable=self.cap, state="disabled", width=2).grid(row=1, column=2)

    tk.Label(self.win, text="Enter the x position of the boat :").grid(row=2, column=1)
    self.x = tk.Scale(self.win, from_=1, to=get_cfg("size")[0], orient="horizontal", takefocus=1)
    self.x.grid(row=2, column=2)

    tk.Label(self.win, text="Enter the y position of the boat :").grid(row=3, column=1)
    self.y = tk.Scale(self.win, from_=1, to=get_cfg("size")[1], orient="horizontal", takefocus=1)
    self.y.grid(row=3, column=2)

    tk.Label(self.win, text="Choose the boat's rotation :").grid(row=4, column=1)
    choices = ['Horizontal', 'Vertical']
    self.rotation = tk.StringVar(self.win)
    self.rotation.set(choices[0])
    tk.OptionMenu(self.win, self.rotation, *choices).grid(row=4, column=2)

    tk.Button(self.win, text="Confirm!", command=self.callback).grid(row=5, column=1, columnspan=2)

    self.x.focus_force()
    self.win.mainloop()

    return

  def callback(self, *args):
    errors = []

    self.var_x = self.x.get()
    self.var_y = self.y.get()
    self.var_rotation = 0 if self.rotation.get() =='Horizontal' else 1

    if not((get_cfg("size")[0]+1) - int(self.cap.get()) >= self.var_x > 0) and not(self.var_rotation):
        errors.append("x OOB")
        self.x.set(1)

        tk.messagebox.showwarning("Warning", "The boat must fit in the grid!")

    elif not((get_cfg("size")[1]+1) - int(self.cap.get()) >= self.var_y > 0) and self.var_rotation:
        errors.append("y OOB")
        self.y.set(1)

        tk.messagebox.showwarning("Warning", "The boat must fit in the grid!")

    if errors == []:
        del(self.x, self.y)
        self.win.destroy()

        self.data = (int(self.cap.get()), (self.var_x, self.var_y, self.var_rotation))

  def close(self):
    """close main window and exit game"""
    try:
      self.win.destroy()
    except:
      pass
    print('Action cancelled by user. Exiting...')
    time.sleep(2)
    raise SystemExit


class InputTarget:
  """Target selector addons on main window"""
  def __init__(self, win: "tkinter window", player: "Player", opponent: "Player"):
    self.win = win
    self.player = player
    self.opponent = opponent
    self.target_coordinates = (None, None)
    self.win.bind("<Return>", self.callback)
    self.win.bind("<space>", self.callback)
    self.loop = True
    confirm_button = tk.Button(self.win, text='Fire !', command=self.callback, height=2, width=26, relief='groove', bd=4, padx=5, pady=5, justify='center')
    confirm_button.grid(row=10, column=1, columnspan=2)

    target_type_frame = tk.LabelFrame(self.win, text="Ammo Selection", height=(self.player.board_player.size[0]+1)*self.player.board_player.scale[1], width=125, padx=4, pady=4, relief='ridge', bd=3)
    target_type_frame.grid_propagate(0)
    target_type_frame.grid(row=2, column=3, rowspan=4)

    vals = ["Basic", "Heavy"]
    self.var_target_type = tk.StringVar()
    self.var_target_type.set("Basic Ammo")
    for i in range(len(vals)):
      tk.Radiobutton(target_type_frame, indicatoron=0, padx=2, pady=2, variable=self.var_target_type, text=f"{vals[i]} Shot", value=f"{vals[i]} Ammo").grid(row=i, column=0)
      if player.ammo[f'{vals[i]} Ammo'] > -1:
        tk.Label(target_type_frame, text=strfill(f"{player.ammo[f'{vals[i]} Ammo']} left", 7, before=True)).grid(row=i, column=1)

    while self.loop:
      update_window(self.win)
    else:
      self.win.unbind("<Return>")
      self.win.unbind("<space>")
      confirm_button.destroy()
      target_type_frame.destroy()

    return

  def callback(self, event: "tkinter event" = None):
    self.target_coordinates = self.player.board_opponent.highlighted
    if self.target_coordinates == (None, None):
      tk.messagebox.showerror(message="Target is invalid.\nUnable to fire.")
    elif self.var_target_type.get() != "Basic Ammo" and self.player.ammo[self.var_target_type.get()] == 0:
      tk.messagebox.showerror(message="You don't have any more ammo of this type.\nUnable to fire.")
    else:
      self.player.ammo[self.var_target_type.get()] -= 1
      self.loop = False


class Config:
  """Configuration window"""
  def __init__(self, restore: bool = False):
    self.cfg_win = tk.Tk()
    if restore:
      self.restore_cfg()
      return
    self.cfg_win.geometry('600x565+650+100')
    self.cfg_win.resizable(False, False)
    self.cfg_win.wm_protocol("WM_DELETE_WINDOW", self.close)

    size, boatnbr, caps, ammo, colors = get_cfg()

    monospaced_font = tk.font.nametofont("TkDefaultFont").copy()
    monospaced_font.config(family="Consolas")

    ####################
    self.boats_frame = tk.LabelFrame(self.cfg_win, text="Boats Configuration", padx=10, pady=10)
    self.boats_frame.place(x=10, y=7)

    tk.Label(self.boats_frame, text="Enter number of boats per team :").grid(row=1, column=1)

    self.boatnbr_scale = tk.Scale(self.boats_frame, from_=1, to=min(size), orient="horizontal")
    self.boatnbr_scale.set(boatnbr)
    self.boatnbr_scale.grid(row=1, column=2)

    self.caps_frame = tk.Frame(self.boats_frame, padx=4, pady=4, relief='ridge', bd=2)
    self.caps_frame.grid(row=2, column=1, columnspan=2)

    self.caps = []
    for i in range(len(caps)):
      lbl = tk.Label(self.caps_frame, text=f"boat{i+1}'s capacity")
      lbl.grid(row=i, column=0)
      cap = tk.Scale(self.caps_frame, from_=2, to=min(size), orient="horizontal")
      cap.set(caps[i])
      cap.grid(row=i, column=1)
      self.caps.append([lbl, cap])
    ####################
    self.missiles_frame = tk.LabelFrame(self.cfg_win, text="Ammo Configuration", padx=10, pady=10)
    self.missiles_frame.place(x=338, y=7)

    tk.Label(self.missiles_frame, text=strfill("Basic Ammo", 15)).grid(row=0, column=0)
    basic_shot = tk.StringVar()
    basic_shot.set("∞")
    tk.Entry(self.missiles_frame, textvariable=basic_shot, state='disabled', width=3, font=monospaced_font).grid(row=0, column=1)

    self.missiles = {}
    self.missiles_list = ["Heavy Ammo"]
    for i in range(len(self.missiles_list)):
      lbl = tk.Label(self.missiles_frame, text=strfill(self.missiles_list[i], 15))
      lbl.grid(row=1+i, column=0)
      shot = tk.IntVar()
      shot.set(ammo[self.missiles_list[i]])
      entry = tk.Entry(self.missiles_frame, textvariable=shot, width=3, font=monospaced_font)
      entry.grid(row=1+i, column=1)

      self.missiles[self.missiles_list[i]] = shot

    ####################
    self.color_frame = tk.LabelFrame(self.cfg_win, text="Colors Configuration", padx=10, pady=10)
    self.color_frame.place(x=338, y=107)

    self.presets = ["Light Mode", "Night Mode", "User Defined"]
    self.selected_preset = tk.StringVar(self.color_frame)
    self.selected_preset.set(self.presets[-1])
    tk.OptionMenu(self.color_frame, self.selected_preset, *self.presets, command=self.change_preset).grid(row=0, column=0, columnspan=3)

    self.colors = []
    for i in range(len(colors)):
      lbl = tk.Label(self.color_frame, text=f"{strfill(list(colors.keys())[i], 11)}:", font=monospaced_font)
      lbl.grid(row=1+i, column=1, sticky='e')
      color = tk.Entry(self.color_frame, width=8, font=monospaced_font)
      color.insert(0, list(colors.values())[i])
      color.grid(row=1+i, column=2)

      self.colors.append([lbl, color])

    button = tk.Button(self.color_frame, text="Color picker utility", command=self.color_selector)
    button.grid(row=2+len(colors), column=1, columnspan=2)
    self.color_lbl = tk.Entry(self.color_frame, width=8)
    self.color_lbl.grid(row=3+len(colors), column=1, columnspan=2)

    tk.Button(self.color_frame, text="Preview Board", command=self.preview_board).grid(row=4+len(colors), column=1, columnspan=2)
    ####################
    tk.Button(self.cfg_win, text="Confirm", command=self.save_cfg).place(x=230, y=530)
    tk.Button(self.cfg_win, text="Reset", command=self.restore_cfg).place(x=325, y=530)
    ####################
    self.boatnbr_scale.config(command=self.caps_gen)
    self.boatnbr_scale.focus_set()
    self.cfg_win.mainloop()
    return

  def caps_gen(self, boatnbr: int):
    """gen caps lbls/scales in config window"""
    self.caps_frame.destroy()
    self.caps_frame = tk.Frame(self.boats_frame, padx=4, pady=4, relief='ridge', bd=3)
    self.caps_frame.grid(row=2, column=1, columnspan=2)

    boatnbr = int(boatnbr)
    self.caps = []

    for i in range(boatnbr):
      lbl = tk.Label(self.caps_frame, text=f"boat{i+1}'s capacity")
      lbl.grid(row=i, column=0)
      cap = tk.Scale(self.caps_frame, from_=2, to=10, orient="horizontal")
      cap.grid(row=i, column=1)
      self.caps.append([lbl, cap])

  def change_preset(self, event=None):
    colors = get_cfg("colors")
    if self.selected_preset.get() == self.presets[0]:
      for i in range(len(self.colors)):
        self.colors[i][1].delete(0,tk.END)
        self.colors[i][1].insert(0, ["#61c5ff", "#808080", "#000000", "#ff0000", "#0c00ed", "#fdb100"][i])
    elif self.selected_preset.get() == self.presets[1]:
      for i in range(len(self.colors)):
        self.colors[i][1].delete(0,tk.END)
        self.colors[i][1].insert(0, ['#4d4d4d', '#663300', '#000000', '#b30000', '#000085', '#006000'][i])
    else:
      pass

  def color_selector(self, event=None):
    pxl, hexa = tk.colorchooser.askcolor()
    if hexa != None:
      self.color_lbl.delete(0,tk.END)
      self.color_lbl.insert(0, hexa)

  def preview_board(self, event=None):
    colors = {}
    color_name = ['background', 'boat', 'grid', 'hit', 'miss', 'highlight']
    for i in range(len(color_name)):
      color = self.colors[i][1].get()
      try:
        int(color[1:], 16)
        assert len(color) == 7
      except:
        self.colors[i][1].delete(0,tk.END)
        self.colors[i][1].insert(0, 'invalid')
        return
      else:
        colors[color_name[i]] = color

    preview = tk.Toplevel(self.cfg_win)
    preview.grab_set()

    sample = Board(colors=colors)
    sample.generate(preview, 1)

    boat1 = Boat((3, (4, 7, 0)))
    boat2 = Boat((4, (3, 3, 1)))
    sample.draw_boat(boat1)
    sample.draw_boat(boat2)
    sample.draw_miss((6, 4))
    sample.draw_hit((3, 5))
    sample.draw_drown(boat1)

    sample.draw_grid()
    sample.txt.pack()
    sample.board.pack()

    preview.mainloop()

  def save_cfg(self):
    """save all configurations in a local file"""
    size = get_cfg("size")
    boatnbr = self.boatnbr_scale.get()
    caps = [cap.get() for lbl, cap in self.caps]
    ammo = [self.missiles[x].get() for x in self.missiles_list]
    colors = [color.get() for lbl, color in self.colors]

    assert isinstance(size, tuple)
    for x in size:
      assert isinstance(x, int)

    assert isinstance(boatnbr, int)
    assert boatnbr == len(caps)

    assert isinstance(caps, list)
    for x in caps:
      assert isinstance(x, int)

    assert isinstance(ammo, list)
    for x in ammo:
      assert isinstance(x,int)

    assert isinstance(colors, list)
    for x in colors:
      assert isinstance(x, str)

    with open("battleships.save", mode="w") as f:
      for x in size:
        f.write(f"{x}\n")

      f.write(f"{boatnbr}\n")

      for x in caps:
        f.write(f"{x}\n")

      for x in ammo:
        f.write(f"{x}\n")

      for i in range(len(colors)):
        f.write(f"{colors[i]}\n")

    self.cfg_win.destroy()

  def restore_cfg(self):
    """restore default configuration to a file"""
    size = (10, 10)
    boatnbr = 5
    caps = [2, 3, 3, 4, 5]
    ammo = {
      "Heavy Ammo": 0
    }
    colors = {
        "background": "#61c5ff",
        "boat"      : "#808080",
        "grid"      : "#000000",
        "hit"       : "#ff0000",
        "miss"      : "#0c00ed",
        "highlight" : "#fdb100"
      }

    with open("battleships.save", mode="w") as f:
      for x in size:
        f.write(f"{x}\n")

      f.write(f"{boatnbr}\n")

      for x in caps:
        f.write(f"{x}\n")

      for x in ammo:
        f.write(f"{ammo[x]}\n")

      for i in colors:
        f.write(f"{colors[i]}\n")

    self.cfg_win.destroy()

  def close(self):
    """window close protocol callback"""
    user = tk.messagebox.askyesnocancel("Save", "Do you want to save changes ?", default='yes', icon='question')
    if user == True:
      self.save_cfg()
    elif user == False:
      self.cfg_win.destroy()
    else:
      pass
############################################################################################
def grid_set(p1: "Player", p2: "Player"):
  p1.board_player.txt.grid(row=1, column=1)
  p1.board_player.board.grid(row=2, column=1)

  p1.board_opponent.txt.grid(row=1, column=2)
  p1.board_opponent.board.grid(row=2, column=2)

  p2.board_player.txt.grid(row=4, column=1)
  p2.board_player.board.grid(row=5, column=1)

  p2.board_opponent.txt.grid(row=4, column=2)
  p2.board_opponent.board.grid(row=5, column=2)

def show_win(player: "Player", opponent: "Player"):
  opponent.board_player.txt.grid_remove()
  opponent.board_player.board.grid_remove()

  opponent.board_opponent.txt.grid_remove()
  opponent.board_opponent.board.grid_remove()

  player.board_player.txt.grid()
  player.board_player.board.grid()

  player.board_opponent.txt.grid()
  player.board_opponent.board.grid()

def hide_win(player: "Player", opponent: "Player"):
  player.board_player.txt.grid_remove()
  player.board_player.board.grid_remove()
  player.board_opponent.txt.grid_remove()
  player.board_opponent.board.grid_remove()

  opponent.board_player.txt.grid_remove()
  opponent.board_player.board.grid_remove()
  opponent.board_opponent.txt.grid_remove()
  opponent.board_opponent.board.grid_remove()

def update_window(win: "tkinter window"):
  "update TKinter window"
  win.update()
  win.update_idletasks()

def popup_block(master: tk.Tk, title, msg):
  block = tk.Toplevel(master)
  block.grab_set()
  block.focus_set()
  block.title(title)
  block.bind('<Return>', lambda x: block.destroy())
  block.bind('<space>', lambda x: block.destroy())

  tk.Label(block, text=msg).pack()
  but = tk.Button(block, text='Ok', command=block.destroy)
  but.pack()

  master.wait_window(block)
############################################################################################
def init_game(net: bool, nbr_players: int):
  "game prerequirements"
  os.system('cls')

  if net:
    is_host = menu_generator("What do you want to do ?", ["Host","Join"], [1, 0])

    if is_host:
      nic = custom_module.networking.get_net_addrs()
      nic_name = []
      nic_addrs = []
      for x in nic:
        nic_name.append(x)
        nic_addrs.append(nic[x])
      ip = ('', 50001)

      server = socket.socket()
      server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      try:
        server.bind(ip)
        print(f"Server binded\nWaiting for a connection...")
        server.listen(1)
        connection, _ = server.accept()
      except:
        print("Can't create server. Try again later.")
        time.sleep(2)
        main_menu()
      else:
        print("Connected!\nSending game configuration...")
        with open("battleships.save", mode='rb') as f:
          connection.send(f.read(1024))
        connection.recv(1024)
        print("Game configuration sent!")
    else:
      ip = (input("Enter ip to connect : "), 50001)
      connection = socket.socket()
      print("Connecting...")
      try:
        connection.connect(ip)
      except:
        print("Can't connect. Try again later.")
        time.sleep(2)
        main_menu()
      else:
        print("Connected!\nReceiving game configuration...")
        with open("battleships.save.tmp", mode='wb') as f:
          f.write(connection.recv(1024))
        connection.send(b'200')
        print("Game configuration received!")

  print("init game...")
  size, boatnbr, caps, *_ = get_cfg()
  p1 = Player(1, boatnbr)
  p2 = Player(2, boatnbr)

  for p in [p1, p2]:
    if net and p.id == 2:
      print("Waiting for the opponent...")
    i = 0
    while i < boatnbr:
      if nbr_players == 2 or (nbr_players == 1 and p.id == 1): # if human's turn
        if net: # if wireless
          if p.id == 1: # first enter data
            boat = InputCoords(caps[i], p.id, i+1).data
            connection.send(strfill(repr(boat),128).encode())
          else: # then receive opponent's
            boat = eval(connection.recv(128).decode().rstrip(" "))
        else:
          boat = InputCoords(caps[i], p.id, i+1).data
      else:
        rot = random.randint(0, 1)
        if not(rot):
          boat = (caps[i], (random.randint(1, size[0]+1-caps[i]), random.randint(1, size[1]), rot))
        else:
          boat = (caps[i], (random.randint(1, size[0]), random.randint(1, size[1]+1-caps[i]), rot))

      boat_obj = Boat(boat)

      restart = False
      for x in range(len(boat_obj.list_coordinates)):
        if boat_obj.list_coordinates[x] in p.list_coordinates:
          if nbr_players == 2 or (nbr_players == 1 and p.id == 1):
            tk.messagebox.showerror(f"Battleships - Player {p.id}", "This boat is on another one\nYou can only place a boat in the water")
          else:
            pass
          restart = True
          break
      if restart:
        continue

      p.boats.append(boat_obj)
      p.list_coordinates += boat_obj.list_coordinates + [None]
      p.hp += boat[0]
      i += 1
    del p.list_coordinates[len(p.list_coordinates)-1]

  if net and not(is_host): # switch vars to match players' id on both computer
    t = p1
    p1 = p2
    p2 = t
    del t

  ########## game initiated ##########

  if net:
    if is_host:
      app = ApplicationClass([p1, p2], nbr_players, net, is_host, server, connection)
    else:
      app = ApplicationClass([p1, p2], nbr_players, net, None, None, connection)
  else:
    app = ApplicationClass([p1, p2], nbr_players, None, None, None, None)

  for p in [p1, p2]:
    p.create_boards()

    p.board_player.generate(app.win, 1)
    p.board_opponent.generate(app.win, 2)
    p.board_opponent.board.bind("<Button-1>", app.callback_highlight)

    for boat in p.boats:
      p.board_player.draw_boat(boat)

    p.board_player.draw_grid()
    p.board_opponent.draw_grid()

  grid_set(p1, p2)

  show_win(p1, p2)
  hide_win(p1, p2)
  update_window(app.win)
  app.win.focus_set()
  print('Starting game...')

  return (p1, p2, app)
############################################################################################
def game(net: bool, nbr_players: int):
  # rules()
  if nbr_players == 1:
    ai_strength = 0
    target_id = 0
    while ai_strength == 0:
      ai_strength = menu_generator(
        "Select the AI's difficulty",
        ["Easy", "Normal (in development)", "Hardcore"],
        [1, 0, 3]
      )
  p1, p2, app = init_game(net, nbr_players)
  window = app.win

  if False:
    print(p1.list_coordinates)
    print(p2.list_coordinates)

  current_player = random.randint(1, 2)
  app.start_time = time.perf_counter()
  if app.net:
    if app.is_host:
      app.connection.send(repr(current_player).encode())
    else:
      current_player = eval(app.connection.recv(8).decode())
  while p1.hp != 0 and p2.hp != 0:
    if app.net:
      if app.is_host:
        player = p1
        opponent = p2
      else:
        player = p2
        opponent = p1
    else:
      player = eval(f"p{current_player}")
      opponent = eval(f"p{int(not(current_player-1))+1}")
    app.set_player_turn(eval(f"p{current_player}"), eval(f"p{int(not(current_player-1))+1}"))
    window.title(f"Battleships - Player {current_player}")

    if nbr_players == 2 or (nbr_players == 1 and current_player == 1): # if player's turn
      msg = f"Player {current_player}'s turn"
      if not(app.net):
        msg += "\nThe player's board will be displayed when this window will be closed"
      popup_block(window, f"Battleships - Player {current_player}", msg)
      show_win(player, opponent)
      update_window(window)

    ### user action
    if nbr_players == 2 or (nbr_players == 1 and current_player == 1): # if player's turn
      if app.net:
        if (app.is_host and current_player == 1) or (not(app.is_host) and current_player == 2):
          while (target := InputTarget(window, app.player, app.opponent)).target_coordinates in app.player.list_shots:
            tk.messagebox.showerror(f"Battleships - Player {current_player}", "You already shot at that point !")
          target_type = target.var_target_type.get()
          target = target.target_coordinates
          app.connection.send(repr((target, target_type)).encode())
        else:
          # print("Waiting for your opponent...")
          target, target_type = eval(app.connection.recv(1024).decode())
      else:
        while (target := InputTarget(window, app.player, app.opponent)).target_coordinates in app.player.list_shots:
          tk.messagebox.showerror(f"Battleships - Player {current_player}", "You already shot at that point !")
        target_type = target.var_target_type.get()
        target = target.target_coordinates

    ### AI action
    elif nbr_players == 1 and current_player == 2: # elif AI's turn
      # Easy
      if ai_strength == 1:
        while (target := (random.randint(1, get_cfg("size")[0]), random.randint(1, get_cfg("size")[1]))) in app.player.list_shots:
          pass
        target_type = "Basic Ammo"

      # Normal
      elif ai_strength == 2:
        raise NotImplementedError

      # Hardcore
      elif ai_strength == 3:
        if app.opponent.list_coordinates[target_id] == None:
          success_chances = 20 # % chance to hit the player
          if random.randint(1, 100) <= success_chances:
            target_id += 1
            target = app.opponent.list_coordinates[target_id]
            while target in app.player.list_shots or target == None:
              target_id += 1
              target = app.opponent.list_coordinates[target_id]
          else:
            while ( target := (random.randint(1, get_cfg("size")[0]), random.randint(1, get_cfg("size")[1])) ) in app.player.list_shots or target == None:
              pass
        else:
          target_id += 1
          target = app.opponent.list_coordinates[target_id]
          while target in app.player.list_shots or target == None:
            target_id += 1
            target = app.opponent.list_coordinates[target_id]
        target_type = "Basic Ammo"
    ### END user action

    if target_type == "Basic Ammo":
      targets = [target]
    elif target_type == "Heavy Ammo":
      x_target, y_target = target
      targets = []
      for y in range(y_target-1, y_target+2):
        for x in range(x_target-1, x_target+2):
          if (0 < x < get_cfg("size")[0]) and (0 < y < get_cfg("size")[1]):
            targets += [(x, y)]

    for target in targets:
      app.player.stats["shots"] += 1
      app.player.list_shots.append(target)
      if target in app.opponent.list_coordinates:
        # if target hit a ship
        app.player.stats["hits"] += 1

        for boat in app.opponent.boats:
          if target in boat.list_coordinates:
            # select boat located on target
            break
        if boat.damages[boat.list_coordinates.index(target)] != 0:
          # if tile haven't already been destroyed
          boat.hit( app.opponent, app.opponent.board_player, boat.list_coordinates.index(target) )
          app.player.board_opponent.draw_hit(boat.list_coordinates[boat.list_coordinates.index(target)])
          app.player.board_opponent.history.append(["hit", boat.list_coordinates[boat.list_coordinates.index(target)]])

          app.player.board_player.status_var.set("HIT!")
          if boat.hp == 0:
            # if boat is fully damaged
            app.player.board_player.status_var.set("SUNK!")
            app.player.stats["sunk"] += 1
            app.opponent.board_player.draw_drown(boat)
            app.opponent.board_player.history.append(["drown", boat])

            app.player.board_opponent.draw_boat(boat)
            app.player.board_opponent.history.append(["boat", boat])

            app.player.board_opponent.draw_drown(boat)
            app.player.board_opponent.history.append(["drown", boat])
      else:
        # if target doesn't hit a ship
        app.player.board_player.status_var.set("MISS!")
        app.player.stats["miss"] += 1
        app.player.board_opponent.draw_miss(target)
        app.player.board_opponent.history.append(["miss", target])

        app.opponent.board_player.draw_miss(target)
        app.opponent.board_player.history.append(["miss", target])

    if nbr_players == 2 or (nbr_players == 1 and current_player == 1): # if player's turn
      update_window(window)
      popup_block(window, f"Battleships - Player {current_player}", app.player.board_player.status_var.get())

      app.gen_boards()
      app.player.board_opponent.clear_highlight()
      if app.net:
        if app.is_host:
          hide_win(p2, p1)
        else:
          hide_win(p1, p2)
      else:
        hide_win(app.player, app.opponent)

    current_player = int(not(current_player-1))+1

  end_game(app)

def end_game(app: ApplicationClass):
  "display post-game stats"

  if app.net:
    if app.is_host:
      app.connection.close()
      app.server.close()
    else:
      app.connection.close()
      os.remove('battleships.save.tmp')

  app.win.destroy()

  p1, p2 = app.players

  end_time = time.perf_counter() - app.start_time
  print("GAME IS FINISHED!")
  print(f"THE GAME LASTED {str(round(end_time, 2))} SECONDS.")
  if p1.hp == 0 and p2.hp != 0:
    if app.nbr_players == 2:
      print("PLAYER 2 WINS!")
    else:
      print("AI WINS!")
  elif p1.hp != 0 and p2.hp == 0:
    print("PLAYER 1 WINS!")
  elif p1.hp == 0 and p2.hp == 0:
    print("IT'S A DRAW!")

  print(f"STATS : ")
  print(f"  Player 1 : ")
  print(f"    undamaged boats : {p1.hp:03}")
  print(f"    shots fired     : {p1.stats['shots']:03}")
  print(f"    missed shots    : {p1.stats['miss']:03}")
  print(f"    damages done    : {p1.stats['hits']:03}")
  print(f"    boats sunk      : {p1.stats['sunk']:03}")
  print()

  if app.nbr_players == 2: print(f"  Player 2 : ")
  else: print(f"  AI : ")
  print(f"    undamaged boats : {p2.hp:03}")
  print(f"    shots fired     : {p2.stats['shots']:03}")
  print(f"    missed shots    : {p2.stats['miss']:03}")
  print(f"    damages done    : {p2.stats['hits']:03}")
  print(f"    boats sunk      : {p2.stats['sunk']:03}")

  os.system("pause")

def main_menu():
  "display the game's main menu"
  while True:
    exec(menu_generator(
      "Battleships",
      ["Play", "Settings", "Exit"],
      ["play()", "Config()", "raise SystemExit"], hidden={
        "your choice":"""print("Tu te crois malin ? hmm... Tu me fais presque de la peine.");time.sleep(2)""",
        0:"""print("Te crois-tu capable de faire bugger ce menu ? HA n'essaye même pas !");time.sleep(2)""",
        123:"""print("Soleil !");time.sleep(2)""",
        666:"""print("SATAN! Je t'ai fais quoi pour que tu me fasse ça !?".upper());time.sleep(2)""",
        999:"""print("Me dit pas que t'as fait toutes les combinaisons pour arriver jusqu'ici !?");time.sleep(2)"""
      })
    )

def play():
  "pre-game selector"
  net, nbr_players = menu_generator("Number of players :", ["Solo", "Local", "Wireless"], [(0, 1), (0, 2), (1, 2)])
  game(net, nbr_players)

def rules():
  "display game's rules"
  os.system("cls")
  print("""\
This game is a single and multiplayer game.

Your goal is to sink all of your opponent's boats.

To do so, you have to fire at your opponent's fleet.
You can aim by entering the grid's coordinates. (e.g. : A1 or J10)
After entering a valid target (a square you haven't already shot at and
that is in the grid), you'll know if you hit a boat or miss your shot.

The winner is the one that sunk all of his opponent's fleet.
""")
  os.system("pause")
  return

def get_cfg(param=None, recovery=False):
  "get configuration from save data"
  filename = "battleships.save.tmp" if os.path.exists("battleships.save.tmp") else "battleships.save"
  try:
    with open(filename, mode="r") as f:
      size = eval(f.readline().rstrip("\n")), eval(f.readline().rstrip("\n"))

      boatnbr = eval(f.readline().rstrip("\n"))

      caps = []
      for i in range(boatnbr):
        caps.append(eval(f.readline().rstrip("\n")))

      ammo = {"Basic Ammo": -1}
      for i in ["Heavy Ammo"]:
        ammo[i] = eval(f.readline().rstrip("\n"))

    with open("battleships.save", mode='r') as f:
      for i in range(len(size)+boatnbr+len(ammo)):
        f.readline()
      colors = {}
      for i in ['background', 'boat', 'grid', 'hit', 'miss', 'highlight']:
        colors[i] = f.readline().rstrip("\n")

    assert isinstance(size, tuple)
    for x in size:
      assert isinstance(x, int)

    assert isinstance(boatnbr, int)
    assert boatnbr == len(caps)

    assert isinstance(caps, list)
    for x in caps:
      assert isinstance(x, int)

    assert isinstance(ammo, dict)
    for x in ammo:
      assert isinstance(ammo[x],int)

    assert isinstance(colors, dict)
    for x in colors:
      assert isinstance(colors[x], str)

    if param == None:
      return [size, boatnbr, caps, ammo, colors]
    else:
      return eval(param)
  except Exception as e:
    if not(recovery):
      if e == AssertionError:
        msg = "An error occurred while saving the save file.\nA recovery protocol will be initiated.\nError: "+str(sys.exc_info()[1])
      else:
        msg = "An error occurred while reading the save file.\nA recovery protocol will be initiated.\nError: "+str(sys.exc_info()[1])
      win = tk.Tk()
      user = tk.messagebox.askokcancel("Configuration Error", msg)
      if user:
        Config(True)
        get_cfg(recovery=True)
        tk.messagebox.showinfo("Configuration Error", "The recovery protocol was successful !")
        win.destroy()
      else:
        raise SystemExit
    else:
      tk.messagebox.showerror("Configuration Error", "The recovery protocol was unsuccessful.\nTry retrieving the base configuration file.")
      raise SystemExit

if __name__ == '__main__':
  get_cfg()
  main_menu()
