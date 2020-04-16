#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import custom_module
import os
import random
import string
import sys
import time
import tkinter as tk
import tkinter.messagebox


class Board:
  def __init__(self, scale, is_dark=False):
    self.scale = scale
    self.is_dark = is_dark

    self.size = get_cfg("size")
    self.history = list()
    self.status_var = tk.StringVar(value='{dmg_status}')
    self.highlighted = (None, None)

    if self.is_dark:
      self.color = {
        "board"    : "#4d4d4d",
        "boat"     : "#663300",
        "line"     : "#000000",
        "hit"      : "#b30000",
        "miss"     : "#000085",
        "highlight": "#006000"
      }
    else:
      self.color = {
        "board"    : "#61c5ff",
        "boat"     : "#808080",
        "line"     : "#000000",
        "hit"      : "#ff0000",
        "miss"     : "#0c00ed",
        "highlight": "#fdb100"
      }

  def generate(self, win, player):
    if player == 1:
      self.txt = "Your Playboard"
    else:
      self.txt = "Enemy's Playboard"

    self.txt = tk.Label(win, text=self.txt)
    self.board = tk.Canvas(win, height=(self.size[0]+1)*self.scale[1], width=(self.size[1]+1)*self.scale[0], bg=self.color["board"])

    return

  def get_tile_coords(self, coordinates):
    errors = []
    if not(1 <= (target_x := coordinates[0] // self.scale[0]) <= self.size[0]): # if x_target isn't in the grid
      errors.append("x OOB")

    if not(1 <= (target_y := coordinates[1] // self.scale[1]) <= self.size[1]): # if y_target isn't in the grid
      errors.append("y OOB")

    if not(errors):
      return (target_x, target_y)
    else:
      return (None, None)

  def draw_grid(self):
    self.board.create_line(self.scale[0], 3, (self.size[0]+1)*self.scale[0], 3, width=3, fill=self.color["line"])
    self.board.create_line(3, self.scale[1], 3, (self.size[1]+1)*self.scale[1], width=3, fill=self.color["line"])

    i=self.scale[0]
    while i <= (self.size[0]+1)*self.scale[0]:
      self.board.create_line(0, i, (self.size[0]+1)*self.scale[0], i, width=3, fill=self.color["line"]) # draw x lines
      i+=self.scale[0]

    i=self.scale[1]
    while i <= (self.size[1]+1)*self.scale[1]:
      self.board.create_line(i, 0, i, (self.size[1]+1)*self.scale[1], width=3, fill=self.color["line"]) # draw y lines
      i+=self.scale[1]

    bold_font = ("Helvetica", 18, "bold")
    for x in range(self.size[0]):
      self.board.create_text( ( (self.scale[0]*x)+(self.scale[0]*1.5), self.scale[1]/2 ) , text=str(x+1), font=bold_font)

    for y in range(self.size[1]):
      self.board.create_text( ( self.scale[0]/2, (self.scale[1]*y)+(self.scale[1]*1.5) ) , text=letter[y], font=bold_font)

  def draw_boat(self, boat):
    if boat.base_coordinates[2] == 0:
      self.board.create_oval(
        boat.base_coordinates[0]*self.scale[0], boat.base_coordinates[1]*self.scale[1],
        (boat.base_coordinates[0]*self.scale[0])+(boat.capacity*self.scale[0]), (boat.base_coordinates[1]*self.scale[1])+self.scale[1],
        outline=self.color["boat"], fill=self.color["boat"], width=1)
    else:
      self.board.create_oval(
        boat.base_coordinates[0]*self.scale[0], boat.base_coordinates[1]*self.scale[1],
        (boat.base_coordinates[0]*self.scale[0])+self.scale[0], (boat.base_coordinates[1]*self.scale[1])+(boat.capacity*self.scale[1]),
        outline=self.color["boat"], fill=self.color["boat"], width=1)

  def draw_hit(self, coordinates):
    self.board.create_line(
      coordinates[0]*self.scale[0], (coordinates[1]+1)*self.scale[1],
      (coordinates[0]+1)*self.scale[0], coordinates[1]*self.scale[1],
      width=3, fill=self.color["hit"])

  def draw_drown(self, boat):
    if not(boat.base_coordinates[2]):
      for x in range(boat.capacity):
        self.board.create_line(
          (boat.base_coordinates[0]+x)*self.scale[0], (boat.base_coordinates[1])*self.scale[1],
          (boat.base_coordinates[0]+x+1)*self.scale[0], (boat.base_coordinates[1]+1)*self.scale[1],
          width=3, fill=self.color["hit"])
        self.board.create_line(
          (boat.base_coordinates[0]+x)*self.scale[0], (boat.base_coordinates[1]+1)*self.scale[1],
          (boat.base_coordinates[0]+x+1)*self.scale[0], (boat.base_coordinates[1])*self.scale[1],
          width=3, fill=self.color["hit"])
    else:
      for x in range(boat.capacity):
        self.board.create_line(
          (boat.base_coordinates[0])*self.scale[0], (boat.base_coordinates[1]+x)*self.scale[1],
          (boat.base_coordinates[0]+1)*self.scale[0], (boat.base_coordinates[1]+x+1)*self.scale[1],
          width=3, fill=self.color["hit"])
        self.board.create_line(
          (boat.base_coordinates[0]+1)*self.scale[0], (boat.base_coordinates[1]+x)*self.scale[1],
          (boat.base_coordinates[0])*self.scale[0], (boat.base_coordinates[1]+x+1)*self.scale[1],
          width=3, fill=self.color["hit"])

  def draw_miss(self, coordinates):
    self.board.create_line(
      (coordinates[0]+1)*self.scale[0], (coordinates[1]+1)*self.scale[1],
      coordinates[0]*self.scale[0], coordinates[1]*self.scale[1],
      width=3, fill=self.color["miss"])
    self.board.create_line(
      (coordinates[0])*self.scale[0], (coordinates[1]+1)*self.scale[1],
      (coordinates[0]+1)*self.scale[0], coordinates[1]*self.scale[1],
      width=3, fill=self.color["miss"])

  def highlight_tile(self, coordinates):
    if coordinates == (None, None):
      self.clear_highlight()
    else:
      self.board.create_rectangle(
        coordinates[0]*self.scale[0], coordinates[1]*self.scale[1],
        (coordinates[0]+1)*self.scale[0], (coordinates[1]+1)*self.scale[1],
        width=3, outline=self.color["highlight"])

      self.highlighted = coordinates

  def clear_highlight(self):
    self.highlighted = (None, None)


class Boat:
  def __init__(self, properties):
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

  def hit(self, player, board, damaged_tile):
    self.damages[damaged_tile] = 0
    self.hp -= 1
    player.hp -= 1

    board.draw_hit(self.list_coordinates[damaged_tile])
    board.history.append(["hit", self.list_coordinates[damaged_tile]])


class Player:
  def __init__(self, id, boatnbr):
    self.id = id
    self.boatnbr = boatnbr
    self.hp = 0
    self.boats = []
    self.list_coordinates = [None]
    self.list_shots = []
    self.stats = {
      "shots": 0,
      "miss": 0,
      "hits": 0,
      "sunk": 0
    }

  def create_boards(self):
    scale = (500/get_cfg("size")[0], 500/get_cfg("size")[1])
    self.board_player = Board(scale, get_cfg("is_dark"))
    self.board_opponent = Board(scale, get_cfg("is_dark"))

    return


class ApplicationClass:
  def __init__(self, players, nbr_players):
    self.p1, self.p2 = players
    self.players = players
    self.nbr_players = nbr_players

    self.win = tk.Tk()
    self.win.title(f"Python Battleships")
    self.win.resizable(False, False)
    self.win.protocol("WM_DELETE_WINDOW", self.close)

  def close(self):
    try:
      self.win.destroy()
    except:
      pass
    print('Action cancelled by user. Exiting...')
    time.sleep(2)
    raise SystemExit

  def set_player_turn(self, player, opponent):
    "set current player's turn"
    self.player = player
    self.opponent = opponent

  def gen_boards(self):
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

  def callback_highlight(self, event):
    self.gen_boards()
    show_win(self.player, self.opponent)
    self.player.board_opponent.highlight_tile(self.player.board_opponent.get_tile_coords((event.x, event.y)))


class InputCoords:
  def __init__(self, capacity, player_nbr, boat_id):
    self.win = tk.Tk()
    self.win.title(f"Player {player_nbr} - Place Boat {boat_id}")
    self.win.resizable(False, False)
    self.win.protocol("WM_DELETE_WINDOW", self.close)
    self.win.bind("<Return>", self.callback)

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

    tk.Button(self.win, text="Validate!", command=self.callback).grid(row=5, column=1, columnspan=2)

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
    try:
      self.win.destroy()
    except:
      pass
    print('Action cancelled by user. Exiting...')
    time.sleep(2)
    raise SystemExit


class InputTarget:
  def __init__(self, win, player, opponent):
    self.win = win
    self.player = player
    self.opponent = opponent
    self.target = (None, None)
    self.loop = True
    confirm_button = tk.Button(self.win, text='Fire !', command=self.callback, height=2, width=26, relief='groove', bd=4, padx=5, pady=5, justify='center')
    confirm_button.grid(row=10, column=1, columnspan=2)

    while self.loop:
      update_window(self.win)
    else:
      confirm_button.destroy()

    return

  def callback(self, event=None):
    self.target = self.player.board_opponent.highlighted
    if self.target == (None, None):
      tk.messagebox.showerror(message="Target is invalid.\nCan't fire right now.")
    else:
      self.loop = False


class Config:
  def __init__(self):
    self.cfg_win = tk.Tk()
    self.cfg_win.geometry('750x565+650+100')
    self.cfg_win.resizable(False, False)
    self.cfg_win.wm_protocol("WM_DELETE_WINDOW", self.close)

    size, boatnbr, caps, is_dark = get_cfg()

    self.boats_frame = tk.LabelFrame(self.cfg_win, text="boats", padx=10, pady=10)
    self.boats_frame.place(x=10, y=7)

    tk.Label(self.boats_frame, text="Enter number of boats per team :").grid(row=1, column=1)

    self.boatnbr_scale = tk.Scale(self.boats_frame, from_=1, to=min(size), orient="horizontal")
    self.boatnbr_scale.set(boatnbr)
    self.boatnbr_scale.grid(row=1, column=2)

    self.caps_frame = tk.Frame(self.boats_frame, padx=4, pady=4, relief='ridge', bd=2)
    self.caps_frame.grid(row=2, column=1, columnspan=2)

    self.caps = []
    for i in range(int(boatnbr)):
      lbl = tk.Label(self.caps_frame, text=f"boat{i+1}'s capacity")
      lbl.grid(row=i, column=0, sticky='n')
      cap = tk.Scale(self.caps_frame, from_=2, to=min(size), orient="horizontal")
      cap.set(caps[i])
      cap.grid(row=i, column=1, sticky='n')
      self.caps.append([lbl, cap])

    self.dark_mode = tk.BooleanVar()
    self.dark_mode.set(is_dark)
    dark_tickbox = tk.Checkbutton(self.cfg_win, text="Dark Mode", variable=self.dark_mode)
    dark_tickbox.place(x=400, y=7)

    tk.Button(self.cfg_win, text="Confirm", command=self.save_cfg).place(x=300, y=530)
    tk.Button(self.cfg_win, text="Reset", command=self.restore_cfg).place(x=400, y=530)

    self.boatnbr_scale.config(command=self.caps_gen)
    self.boatnbr_scale.focus_set()
    self.cfg_win.mainloop()
    return

  def caps_gen(self, boatnbr):
    self.caps_frame.destroy()
    self.caps_frame = tk.Frame(self.boats_frame, padx=4, pady=4, relief='ridge', bd=3)
    self.caps_frame.grid(row=2, column=1, columnspan=2)

    boatnbr = int(boatnbr)
    self.caps = []

    for i in range(boatnbr):
      lbl = tk.Label(self.caps_frame, text=f"boat{i+1}'s capacity")
      lbl.grid(row=i, column=0, sticky='n')
      cap = tk.Scale(self.caps_frame, from_=2, to=10, orient="horizontal")
      cap.grid(row=i, column=1, sticky='n')
      self.caps.append([lbl, cap])

  def save_cfg(self):
    size = get_cfg("size")
    boatnbr = int(self.boatnbr_scale.get())
    caps = [ int(cap.get()) for lbl, cap in self.caps]
    dark_mode = self.dark_mode.get()

    assert isinstance(size,tuple)
    assert boatnbr == len(caps)
    assert isinstance(dark_mode,bool)

    with open("battleships.save", mode="w") as f:
      f.write(f"{size[0]}\n")
      f.write(f"{size[1]}\n")
      f.write(f"{boatnbr}\n")
      for i in range(len(caps)):
        f.write(f"{caps[i]}\n")
      f.write(f"{dark_mode}\n")

    self.cfg_win.destroy()

  def restore_cfg(self):
    size = (10, 10)
    boatnbr = 5
    caps = [2, 3, 3, 4, 5]
    dark_mode = True

    assert isinstance(size,tuple)
    assert boatnbr == len(caps)
    assert isinstance(dark_mode,bool)

    with open("battleships.save", mode="w") as f:
      f.write(f"{size[0]}\n")
      f.write(f"{size[1]}\n")
      f.write(f"{boatnbr}\n")
      for i in range(boatnbr):
        f.write(f"{caps[i]}\n")
      f.write(f"{dark_mode}\n")

    self.cfg_win.destroy()

  def close(self):
    user = tk.messagebox.askyesnocancel("Save", "Do you want to save changes ?", default='yes', icon='question')
    if user == True:
      self.save_cfg()
    elif user == False:
      self.cfg_win.destroy()
    else:
      pass
############################################################################################
def grid_set(p1, p2):
  p1.board_player.txt.grid(row=1, column=1)
  p1.board_player.board.grid(row=2, column=1)

  p1.board_opponent.txt.grid(row=1, column=2)
  p1.board_opponent.board.grid(row=2, column=2)

  p2.board_player.txt.grid(row=4, column=1)
  p2.board_player.board.grid(row=5, column=1)

  p2.board_opponent.txt.grid(row=4, column=2)
  p2.board_opponent.board.grid(row=5, column=2)

def show_win(player, opponent):
  opponent.board_player.txt.grid_remove()
  opponent.board_player.board.grid_remove()

  opponent.board_opponent.txt.grid_remove()
  opponent.board_opponent.board.grid_remove()

  player.board_player.txt.grid()
  player.board_player.board.grid()

  player.board_opponent.txt.grid()
  player.board_opponent.board.grid()

def hide_win(player, opponent):
  player.board_player.txt.grid_remove()
  player.board_player.board.grid_remove()
  player.board_opponent.txt.grid_remove()
  player.board_opponent.board.grid_remove()

  opponent.board_player.txt.grid_remove()
  opponent.board_player.board.grid_remove()
  opponent.board_opponent.txt.grid_remove()
  opponent.board_opponent.board.grid_remove()

def update_window(win):
  "update TKinter window"
  win.update()
  win.update_idletasks()
############################################################################################
def init_game(nbr_players):
  os.system('cls')

  size, boatnbr, caps, is_dark = get_cfg()
  p1 = Player(1, boatnbr)
  p2 = Player(2, boatnbr)

  for p in [p1, p2]:
    i = 0
    while i < boatnbr:
      if nbr_players == 2 or (nbr_players == 1 and p.id == 1):
        boat = InputCoords(caps[i], p.id, i+1).data
      else:
        rot = random.randint(0, 1)
        if not(rot):
          boat = (caps[i], (random.randint(1, 11-caps[i]), random.randint(1, 10), rot))
        else:
          boat = (caps[i], (random.randint(1, 10), random.randint(1, 11-caps[i]), rot))

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

  ########## game initiated ##########

  app = ApplicationClass([p1, p2],nbr_players)

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

  return (p1, p2, app)
############################################################################################
def game(nbr_players):
  rules()
  if nbr_players == 1:
    ai_strength = 0
    target_id = 0
    while ai_strength == 0:
      ai_strength = custom_module.utilities.menu_generator(
        "Select the AI's difficulty",
        ["Easy", "Normal (in development)", "Hardcore"],
        [1, 0, 3]
      )
  p1, p2, app = init_game(nbr_players)
  window = app.win

  if False:
    print(p1.list_coordinates)
    print(p2.list_coordinates)

  app.start_time = time.perf_counter()
  current_player = random.randint(1, 2)
  while p1.hp != 0 and p2.hp != 0:
    player = eval(f"p{current_player}")
    opponent = eval(f"p{int(not(current_player-1))+1}")
    app.set_player_turn(player, opponent)
    window.title(f"Battleships - Player {current_player}")

    if nbr_players == 2 or (nbr_players == 1 and current_player == 1): # if player's turn
      tk.messagebox.showwarning(f"Battleships - Player {current_player}", f"Player {current_player}'s turn\nThe player's board will be displayed when this window will be closed")
      show_win(player,opponent)

    ### user action
    if nbr_players == 2 or (nbr_players == 1 and current_player == 1): # if player's turn
      while (target := InputTarget(window, player, opponent).target) in player.list_shots:
        tk.messagebox.showerror(f"Battleships - Player {current_player}", "you already shot at that point")

    ### AI action
    elif nbr_players == 1 and current_player == 2: # elif AI's turn
      # Easy
      if ai_strength == 1:
        while (target := (random.randint(1, get_cfg("size")[0]), random.randint(1, get_cfg("size")[1]))) in player.list_shots:
          pass

      # Normal
      elif ai_strength == 2:
        pass

      # Hardcore
      elif ai_strength == 3:
        if opponent.list_coordinates[target_id] == None:
          success_chances = 20 # % chance to hit the player
          if random.randint(1, 100) <= success_chances:
            target_id += 1
            target = opponent.list_coordinates[target_id]
            while target in player.list_shots or target == None:
              target_id += 1
              target = opponent.list_coordinates[target_id]
          else:
            while ( target := (random.randint(1, get_cfg("size")[0]), random.randint(1, get_cfg("size")[1])) ) in player.list_shots or target == None:
              pass
        else:
          target_id += 1
          target = opponent.list_coordinates[target_id]
          while target in player.list_shots or target == None:
            target_id += 1
            target = opponent.list_coordinates[target_id]

    player.stats["shots"] += 1
    player.list_shots.append(target)
    if target in opponent.list_coordinates:
      player.stats["hits"] += 1

      for boat in opponent.boats:
        if target in boat.list_coordinates:
          break
      if boat.damages[boat.list_coordinates.index(target)] != 0:
        boat.hit( opponent, opponent.board_player, boat.list_coordinates.index(target) )
        player.board_opponent.draw_hit(boat.list_coordinates[boat.list_coordinates.index(target)])
        player.board_opponent.history.append(["hit", boat.list_coordinates[boat.list_coordinates.index(target)]])

        player.board_player.status_var.set("HIT!")
        if boat.hp == 0:
          player.board_player.status_var.set("SUNK!")
          player.stats["sunk"] += 1
          opponent.board_player.draw_drown(boat)
          opponent.board_player.history.append(["drown", boat])

          player.board_opponent.draw_boat(boat)
          player.board_opponent.history.append(["boat", boat])

          player.board_opponent.draw_drown(boat)
          player.board_opponent.history.append(["drown", boat])
    else:
      player.board_player.status_var.set("MISS!")
      player.stats["miss"] += 1
      player.board_opponent.draw_miss(target)
      player.board_opponent.history.append(["miss", target])

      opponent.board_player.draw_miss(target)
      opponent.board_player.history.append(["miss", target])
    ### END user action

    if nbr_players == 2 or (nbr_players == 1 and current_player == 1): # if player's turn
      update_window(window)
      tk.messagebox.showinfo(f"Battleships - Player {current_player}", player.board_player.status_var.get())

      app.gen_boards()
      player.board_opponent.clear_highlight()
      hide_win(player, opponent)

    current_player = int(not(current_player-1))+1

  end_game(app)

def end_game(app):
  "display post-game stats"

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
  print(f"    shots done   : {p1.stats['shots']:03}")
  print(f"    missed shots : {p1.stats['miss']:03}")
  print(f"    damages done : {p1.stats['hits']:03}")
  print(f"    boats sunk   : {p1.stats['sunk']:03}")
  print()

  if app.nbr_players == 2:
    print(f"  Player 2 : ")
  else:
    print(f"  AI : ")
  print(f"    shots done   : {p2.stats['shots']:03}")
  print(f"    missed shots : {p2.stats['miss']:03}")
  print(f"    damages done : {p2.stats['hits']:03}")
  print(f"    boats sunk   : {p2.stats['sunk']:03}")

  os.system("pause")

def main_menu():
  "display the game's main menu"
  while True:
    exec(custom_module.utilities.menu_generator(
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
  "player nbr selector"
  nbr_players = custom_module.utilities.menu_generator(
    "Number of players :",
    ["1", "2"],
    [1, 2]
  )
  game(nbr_players)

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

def get_cfg(param=None):
  "get configuration from save data"
  try:
    with open("battleships.save", mode="r") as f:
      size = eval(f.readline().rstrip("\n")), eval(f.readline().rstrip("\n"))
      boatnbr = eval(f.readline().rstrip("\n"))
      caps = []
      for i in range(boatnbr):
        caps.append(eval(f.readline().rstrip("\n")))
      is_dark = eval(f.readline().rstrip("\n"))

      f.seek(0)
      assert len(f.readlines()) == 4 + boatnbr

    assert isinstance(size,tuple)
    assert boatnbr == len(caps)
    assert isinstance(is_dark,bool)

    if param == None:
      return [size, boatnbr, caps, is_dark]
    else:
      return eval(param)
  except:
    tk.messagebox.showerror("Configuration Error", "An error occured with the configuration file\nPlease consider retrieving the base configuration file\nError: "+str(sys.exc_info()[0]))
    raise SystemExit

letter = list(string.ascii_uppercase)

start_time = 0.0
end_time = 0.0

if __name__ == '__main__':
  get_cfg()
  main_menu()
