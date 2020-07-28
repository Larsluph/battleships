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
import xml.etree.ElementTree as et
from typing import Iterable, Union

import numpy as np
from larsmod.utilities import menu_generator, strfill


class Board:
    """board object"""

    def __init__(self, colors=None):
        self.size = get_cfg("size")  # get the size of the board
        # store the length of a tile
        self.scale = (500/self.size[0], 500/self.size[1])
        # stores board's colors in a dict
        self.color = get_cfg('colors') if colors == None else colors
        self.width = 5

        self.map = np.zeros((self.size[0]+1, self.size[1]+1), dtype=np.int8)

        # placeholder for the highlight rectangle on the canvas
        self.rect_highlight = None
        # placeholder (for InputCoords only)
        self.last_boat = None
        # stores last shot's status ('hit' / 'sunk' / 'miss')
        self.status_var = tk.StringVar(value='{dmg_status}')
        # stores the highlighted tile's coordinates
        self.highlighted = (None, None)
        # font to use when drawing columns / rows index
        self.grid_font = ("Helvetica", 18, "bold")

    def generate(self, win: tk.Tk, player: int):
        """generate label and canvas"""
        # set the board's title
        if player == 1:
            self.txt = get_str("player_playboard")
        elif player == 2:
            self.txt = get_str("opponent_playboard")

        # create board related widgets
        if player:
            self.txt = tk.Label(win, text=self.txt)

        self.board = tk.Canvas(win,
                               height=(self.size[0] + 1)*self.scale[1],
                               width=(self.size[1] + 1)*self.scale[0],
                               bg=self.color["background"])

    def get_tile_coords(self, coordinates: tuple):
        """return (x, y) from the canvas' coordinates or (None, None) if it isn't a valid tile"""
        errors = []
        # if x_target isn't valid
        if not(1 <= (target_x := coordinates[0] // self.scale[0]) <= self.size[0]):
            errors.append("x OOB")

        # if y_target isn't valid
        if not(1 <= (target_y := coordinates[1] // self.scale[1]) <= self.size[1]):
            errors.append("y OOB")

        if not(errors):
            return (round(target_x), round(target_y))
        else:
            return (None, None)

    def draw_grid(self):
        """draw the canvas' grid"""
        self.board.create_line(self.scale[0], self.width,
                               (self.size[0]+1)*self.scale[0], self.width,
                               width=self.width, fill=self.color["grid"])

        self.board.create_line(self.width, self.scale[1],
                               self.width, (self.size[1] + 1)*self.scale[1],
                               width=self.width, fill=self.color["grid"])

        # draw x lines
        i = self.scale[0]
        while i <= (self.size[0]+1)*self.scale[0]:
            self.board.create_line(0, i,
                                   (self.size[0] + 1)*self.scale[0], i,
                                   width=self.width, fill=self.color["grid"])
            i += self.scale[0]

        # draw y lines
        i = self.scale[1]
        while i <= (self.size[1]+1)*self.scale[1]:
            self.board.create_line(i, 0,
                                   i, (self.size[1] + 1)*self.scale[1],
                                   width=self.width, fill=self.color["grid"])
            i += self.scale[1]

        for x in range(self.size[0]):
            self.board.create_text((self.scale[0]*x + self.scale[0]*1.5, self.scale[1]/2),
                                   text=str(x + 1), font=self.grid_font)
            self.map[x, 0] = x
        else:
            self.map[x+1, 0] = x+1

        letter = list(string.ascii_uppercase)
        for y in range(self.size[1]):
            self.board.create_text((self.scale[0]/2, self.scale[1]*y + self.scale[1]*1.5),
                                   text=letter[y], font=self.grid_font)
            self.map[0, y] = y
        else:
            self.map[0, y+1] = y+1

    def draw_boat(self, boat: "Boat"):
        """draw a boat on the canvas"""
        cap = boat.capacity
        x, y, rot = boat.base_coordinates
        if not(rot):
            # if boat's rotation is horizontal
            self.last_boat = self.board.create_oval(
                x*self.scale[0],
                y*self.scale[1],
                x*self.scale[0] + cap*self.scale[0],
                y*self.scale[1] + self.scale[1],
                outline=self.color["boat"], fill=self.color["boat"], width=1)
        else:
            # if boat's rotation is vertical
            self.last_boat = self.board.create_oval(
                x*self.scale[0],
                y*self.scale[1],
                x*self.scale[0] + self.scale[0],
                y*self.scale[1] + cap*self.scale[1],
                outline=self.color["boat"], fill=self.color["boat"], width=1)

        for coords in boat.list_coordinates:
            self.map[coords[0], coords[1]] = 1

    def draw_hit(self, coordinates: tuple):
        """draw a hit on the canvas"""
        self.board.create_line(
            coordinates[0]*self.scale[0], (coordinates[1]+1)*self.scale[1],
            (coordinates[0]+1)*self.scale[0], coordinates[1]*self.scale[1],
            width=self.width, fill=self.color["hit"]
        )
        self.map[coordinates[0], coordinates[1]] = 2

    def draw_drown(self, boat: "Boat"):
        """draw a drown boat"""
        cap = boat.capacity
        x, y, rot = boat.base_coordinates
        if not(rot):
            # if boat's rotation is horizontal
            for i in range(cap):
                self.board.create_line(
                    (x+i) * self.scale[0], y * self.scale[1],
                    (x+i+1) * self.scale[0], (y+1) * self.scale[1],
                    width=self.width, fill=self.color["hit"])
                self.board.create_line(
                    (x+i) * self.scale[0], (y+1) * self.scale[1],
                    (x+i+1) * self.scale[0], y * self.scale[1],
                    width=self.width, fill=self.color["hit"])
                self.map[x+i, y] = 3
        else:
            # if boat's rotation is vertical
            for i in range(cap):
                self.board.create_line(
                    x * self.scale[0], (y+i) * self.scale[1],
                    (x+1) * self.scale[0], (y+i+1) * self.scale[1],
                    width=self.width, fill=self.color["hit"])
                self.board.create_line(
                    (x+1) * self.scale[0], (y+i) * self.scale[1],
                    x * self.scale[0], (y+i+1) * self.scale[1],
                    width=self.width, fill=self.color["hit"])
                self.map[x, y+i] = 3

    def draw_miss(self, coordinates: tuple):
        """draw a missed shot"""
        self.board.create_line(
            (coordinates[0]+1)*self.scale[0], (coordinates[1]+1)*self.scale[1],
            coordinates[0]*self.scale[0], coordinates[1]*self.scale[1],
            width=self.width, fill=self.color["miss"]
        )
        self.board.create_line(
            (coordinates[0])*self.scale[0], (coordinates[1]+1)*self.scale[1],
            (coordinates[0]+1)*self.scale[0], coordinates[1]*self.scale[1],
            width=self.width, fill=self.color["miss"]
        )
        self.map[coordinates[0], coordinates[1]] = -1

    def highlight_tile(self, coordinates: tuple, coordinates_2: tuple = None, target: tuple = None):
        """highlight a tile on the board"""
        self.clear_highlight()

        if coordinates != (None, None):
            if coordinates[0] < 1:
                coordinates = (1, coordinates[1])
            elif coordinates[0] > self.size[0]:
                coordinates = (self.size[0], coordinates[1])

            if coordinates[1] < 1:
                coordinates = (coordinates[0], 1)
            elif coordinates[1] > self.size[1]:
                coordinates = (coordinates[0], self.size[1])

            if coordinates_2 == None:
                self.rect_highlight = self.board.create_rectangle(
                    coordinates[0]*self.scale[0], coordinates[1]*self.scale[1],
                    (coordinates[0]+1) *
                    self.scale[0], (coordinates[1]+1)*self.scale[1],
                    width=self.width, outline=self.color["highlight"]
                )
                self.highlighted = coordinates
            else:
                self.rect_highlight = self.board.create_rectangle(
                    coordinates[0]*self.scale[0], coordinates[1]*self.scale[1],
                    (coordinates_2[0]+1) *
                    self.scale[0], (coordinates_2[1]+1)*self.scale[1],
                    width=self.width, outline=self.color["highlight"]
                )
            if target == None:
                self.highlighted = coordinates
            else:
                self.highlighted = target

    def clear_highlight(self):
        """clear the highlighted tile"""
        self.highlighted = (None, None)
        self.board.delete(self.rect_highlight)


class Boat:
    """Boat object"""

    def __init__(self, capacity: int, coordinates: tuple):
        self.capacity = capacity
        self.base_coordinates = coordinates
        self.list_coordinates = []
        self.hp = self.capacity
        self.damages = list()
        for _ in range(self.capacity):
            self.damages.append(1)

        for x in range(self.capacity):
            if self.base_coordinates[2] == 0:
                self.list_coordinates.append(
                    (self.base_coordinates[0]+x, self.base_coordinates[1]))
            else:
                self.list_coordinates.append(
                    (self.base_coordinates[0], self.base_coordinates[1]+x))

    def hit(self, player: "Player", board: "Board", damaged_tile: int):
        """hit a boat"""
        self.damages[damaged_tile] = 0
        self.hp -= 1
        player.hp -= 1
        board.draw_hit(self.list_coordinates[damaged_tile])


class Player:
    """Player object"""

    def __init__(self, id: int, boatnbr: int):
        self.id = id
        self.boatnbr = boatnbr
        self.hp = 0
        self.boats = []
        self.list_coordinates = [None]
        self.list_shots = []
        self.last_status = get_str("miss").lower()
        self.ammo = get_cfg("ammo")
        self.stats = {
            "shots": 0,
            "ammo used": {
                get_str("ammo", ammo_type=get_str("ammo_type/basic")): 0,
                get_str("ammo", ammo_type=get_str("ammo_type/heavy")): 0,
                get_str("ammo", ammo_type=get_str("ammo_type/sonar")): 0,
            },
            "miss": 0,
            "hits": 0,
            "sunk": 0
        }

    def create_boards(self):
        """generate boards"""
        self.board_player = Board()
        self.board_opponent = Board()

        return


class AI(Player):
    target_id = 0  # threat lvl of AI for human-like strength
    _strength = 0
    base_hit = (None, None)
    i = 0

    @property
    def ai_strength(self):
        return self._strength

    @ai_strength.setter
    def ai_strength(self, lvl):
        self._strength = lvl

    def ai_turn(self, app):
        if self._strength == 1:
            return self.ai_easy(app)

        elif self._strength == 2:
            return self.ai_human(app)

        elif self._strength == 3:
            return self.ai_snipe(app)

        elif self._strength == 4:
            return self.ai_godlike(app)

    def ai_easy(self, app):
        while (target := (random.randint(1, self.board_opponent.size[0]), random.randint(1, self.board_opponent.size[1]))) in self.list_shots:
            pass
        return target, get_str("ammo", ammo_type=get_str("ammo_type/basic"))

    def ai_human(self, app):
        # if boat not found or last sunk
        if self.target_id == 0 or app.player.last_status == get_str("sunk").lower():
            # random shot
            while (target := (random.randint(1, self.board_opponent.size[0]), random.randint(1, self.board_opponent.size[1]))) in self.list_shots:
                pass
            if target in app.opponent.list_coordinates:  # if boat is found
                self.target_id = 1
                self.base_hit = target  # save coords for future shots
                # all possible shots around base_target
                self.check = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            else:
                self.target_id = 0
            return target, get_str("ammo", ammo_type=get_str("ammo_type/basic"))

        if self.target_id == 1:  # if boat just found
            temp = self.check.pop(random.randint(0, len(self.check)-1))
            target = (self.base_hit[0] + temp[0], self.base_hit[1] + temp[1])

            while not(1 <= target[0] <= self.board_opponent.size[0] and 1 <= target[1] <= self.board_opponent.size[1]) or target in self.list_shots:
                temp = self.check.pop(random.randint(0, len(self.check)-1))
                target = (self.base_hit[0] + temp[0],
                          self.base_hit[1] + temp[1])
                if len(self.check) == 0:
                    self.target_id = 0
                    while (target := (random.randint(1, self.board_opponent.size[0]), random.randint(1, self.board_opponent.size[1]))) in self.list_shots:
                        pass
                    break

            self.target_id = 2
            return target, get_str("ammo", ammo_type=get_str("ammo_type/basic"))

        if self.target_id == 2:  # if boat found but rot not found
            if app.player.last_status == get_str("hit").lower():
                self.check = [(-1, 0), (0, 1), (1, 0), (0, -1)]
                self.target_id = 3
                self.i = round((random.randint(0, 1)-.5) * 2)  # random -1 or 1
            else:
                temp = self.check.pop(random.randint(0, len(self.check)-1))
                target = (self.base_hit[0] + temp[0],
                          self.base_hit[1] + temp[1])
                while (target := (self.base_hit[0] + temp[0], self.base_hit[1] + temp[1])) in self.list_shots or not(1 <= target[0] <= self.board_opponent.size[0] and 1 <= target[1] <= self.board_opponent.size[1]):
                    temp = self.check.pop(random.randint(0, len(self.check)-1))
                    target = (self.base_hit[0] + temp[0],
                              self.base_hit[1] + temp[1])
                    if len(self.check) == 0:
                        self.target_id = 0
                        while (target := (random.randint(1, self.board_opponent.size[0]), random.randint(1, self.board_opponent.size[1]))) in self.list_shots:
                            pass
                        break
                return target, get_str("ammo", ammo_type=get_str("ammo_type/basic"))

        if self.target_id == 3:  # if boat found and rot found
            for boat in app.opponent.boats:
                if self.base_hit in boat.list_coordinates:
                    # select boat located on target
                    break
            rot = boat.base_coordinates[2]
            if rot:
                target = (self.base_hit[0], self.base_hit[1]+self.i)
                while target in self.list_shots or not(1 <= self.base_hit[1]+self.i <= self.board_opponent.size[1]):
                    if self.i < 0:
                        self.i -= 1
                    else:
                        self.i += 1
                    if not(1 <= self.base_hit[1]+self.i <= self.board_opponent.size[1]) or app.player.last_status == get_str("miss").lower():
                        self.i = round(self.i / -abs(self.i))
                    target = (self.base_hit[0], self.base_hit[1]+self.i)
                return (self.base_hit[0], self.base_hit[1]+self.i), get_str("ammo", ammo_type=get_str("ammo_type/basic"))

            else:
                target = (self.base_hit[0]+self.i, self.base_hit[1])
                while target in self.list_shots or not(1 <= self.base_hit[0]+self.i <= self.board_opponent.size[0]):
                    if self.i < 0:
                        self.i -= 1
                    else:
                        self.i += 1
                    if not(1 <= self.base_hit[0]+self.i <= self.board_opponent.size[0]) or app.player.last_status == get_str("miss").lower():
                        self.i = round(self.i / -abs(self.i))
                    target = (self.base_hit[0]+self.i, self.base_hit[1])
                return (self.base_hit[0]+self.i, self.base_hit[1]), get_str("ammo", ammo_type=get_str("ammo_type/basic"))

    def ai_snipe(self, app):
        if app.opponent.list_coordinates[self.target_id] == None:
            success_chance = 1/10  # % chance to hit the player
            if random.random() <= success_chance:
                self.target_id += 1
                target = app.opponent.list_coordinates[self.target_id]
                while target in self.list_shots or target == None:
                    self.target_id += 1
                    target = app.opponent.list_coordinates[self.target_id]
            else:
                while (target := (random.randint(1, self.board_opponent.size[0]), random.randint(1, self.board_opponent.size[1]))) in self.list_shots or target == None:
                    pass
        else:
            self.target_id += 1
            target = app.opponent.list_coordinates[self.target_id]
            while target in self.list_shots or target == None:
                self.target_id += 1
                target = app.opponent.list_coordinates[self.target_id]
        return target, get_str("ammo", ammo_type=get_str("ammo_type/basic"))

    def ai_godlike(self, app):
        if app.opponent.list_coordinates[self.target_id] == None:
            success_chance = 1/3  # % chance to hit the player
            if random.random() <= success_chance:
                self.target_id += 1
                target = app.opponent.list_coordinates[self.target_id]
                while target in self.list_shots or target == None:
                    self.target_id += 1
                    target = app.opponent.list_coordinates[self.target_id]
            else:
                while (target := (random.randint(1, self.board_opponent.size[0]), random.randint(1, self.board_opponent.size[1]))) in self.list_shots or target == None:
                    pass
        else:
            self.target_id += 1
            target = app.opponent.list_coordinates[self.target_id]
            while target in self.list_shots or target == None:
                self.target_id += 1
                target = app.opponent.list_coordinates[self.target_id]
        return target, get_str("ammo", ammo_type=get_str("ammo_type/basic"))


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

        self.cancelled = False
        self.win = tk.Tk()
        self.win.title(get_str("game_title"))
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.close)

        self.highlight_range = (0, 0, 0, 0)

    def update_window(self):
        "update main window"
        try:
            self.win.update()
            self.win.update_idletasks()
        except:
            self.cancelled = True
            return

    def close(self):
        """close main window and exit game"""
        self.cancelled = True
        self.win.destroy()
        print(get_str("error_exit"))
        time.sleep(2)

    def set_player_turn(self, player: "Player", opponent: "Player"):
        "set current player's turn"
        self.player = player
        self.opponent = opponent

    def callback_highlight(self, event: "tkinter event"):
        if self.net:
            if self.is_host:
                show_win(self.p1, self.p2)
            else:
                show_win(self.p2, self.p1)
        else:
            show_win(self.player, self.opponent)
        self.update_window()
        highlight_coords = self.player.board_opponent.get_tile_coords(
            (event.x, event.y))
        if highlight_coords != (None, None):
            if self.highlight_range == (0, 0, 0, 0):
                self.player.board_opponent.highlight_tile(
                    (highlight_coords[0], highlight_coords[1]))
            else:
                self.player.board_opponent.highlight_tile((highlight_coords[0]-self.highlight_range[0], highlight_coords[1]-self.highlight_range[1]), (
                    highlight_coords[0]+self.highlight_range[2], highlight_coords[1]+self.highlight_range[3]), highlight_coords)


class InputCoords:
    """Boats window selector"""

    def __init__(self, capacity: Iterable, player_id: int):
        self.player_id = player_id
        self.win = tk.Tk()
        self.capacity = capacity
        self.selected_coords = (None, None)
        self.data = list()
        self.list_coordinates = list()
        self.board_obj = Board()
        self.highlight_range = (self.capacity[len(self.data)] - 1, 0)
        self.boatnbr = get_cfg("boatnbr")

        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.close)

        self.board_obj.generate(self.win, 0)
        self.board_obj.draw_grid()
        self.board_obj.board.grid(row=1, column=0)

        self.win.bind("<Return>", self.callback)
        self.win.bind("<space>", self.callback)
        # left click
        self.board_obj.board.bind("<Button-1>", self.select_boat)
        # right click
        self.board_obj.board.bind("<Button-3>", self.rotate_boat)

        tk.Label(self.win, text=get_str(
            "boat_input_intro")).grid(row=0, column=0)

        self.rotation = 0  # 0 == Horizontal || 1 == Vertical

        tk.Button(self.win, text=get_str("confirm"), command=self.callback).grid(
            row=2, column=0, columnspan=2)

        self.win.focus_set()
        self.win.after(250, self.wait_user)
        self.win.mainloop()

    def set_win_title(self):
        "update the window title"
        self.win.title(
            get_str("title_input", player_nbr=self.player_id, boat_id=len(self.data)+1))

    def wait_user(self):
        "wait for the user to select all of the boats"
        try:
            while self.boatnbr > len(self.data):
                self.win.update()
                self.win.update_idletasks()
        except:
            master = tk.Tk()
            tk.messagebox.showerror(parent=master, message=get_str(
                "error_exit"))
            master.destroy()
            return
        else:
            self.win.destroy()

    def select_boat(self, tk_evt=None):
        "select a boat on the board"
        if tk_evt == None:
            return

        self.selected_coords = self.board_obj.get_tile_coords(
            (tk_evt.x, tk_evt.y))
        self.highlight_selection()

    def rotate_boat(self, *evt):
        "rotate the selection"
        self.rotation = not(self.rotation)
        self.highlight_selection()

    def highlight_selection(self):
        if self.selected_coords != (None, None):
            if not(self.rotation):  # if boat horizontal
                self.highlight_range = (self.capacity[len(self.data)]-1, 0)
            elif self.rotation:  # if boat vertical
                self.highlight_range = (0, self.capacity[len(self.data)]-1)

            self.board_obj.highlight_tile(
                self.selected_coords,
                (self.selected_coords[0] + self.highlight_range[0],
                 self.selected_coords[1] + self.highlight_range[1])
            )
        else:
            self.board_obj.clear_highlight()

    def callback(self, *args):
        "check if a boat is valid before saving it"
        errors = []

        size = self.board_obj.size
        boat_obj = Boat(
            self.capacity[len(self.data)], (*self.selected_coords, self.rotation))

        if not(size[0]+1 - self.capacity[len(self.data)] >= self.selected_coords[0]) and not(self.rotation):
            errors.append("x OOB")

        if not(size[1]+1 - self.capacity[len(self.data)] >= self.selected_coords[1]) and self.rotation:
            errors.append("y OOB")

        for x in range(len(boat_obj.list_coordinates)):
            if boat_obj.list_coordinates[x] in self.list_coordinates:
                errors.append("boat conflict")
                break

        if errors == []:
            self.board_obj.draw_boat(boat_obj)
            self.data.append(boat_obj)
            self.list_coordinates += boat_obj.list_coordinates
            if len(self.data) < self.boatnbr:
                self.set_win_title()
                # refresh highlight_range
                self.highlight_selection()
        else:
            if "boat conflict" in errors:
                tk.messagebox.showwarning(
                    get_str("warning"), get_str("error_boat_over"))
            else:
                tk.messagebox.showwarning(
                    get_str("warning"), get_str("error_boat_fit"))

    def close(self):
        """close main window and exit game"""
        self.win.destroy()
        self.data = list()
        print(get_str("error_exit"))
        time.sleep(1)


class InputTarget:
    """Target selector addons on main window"""

    def __init__(self, app: ApplicationClass):
        app.highlight_range = (0, 0, 0, 0)
        self.app = app
        self.win = app.win
        self.player = app.player
        self.target_coordinates = (None, None)
        self.win.bind("<Return>", self.callback)
        self.win.bind("<space>", self.callback)
        self.loop = True
        confirm_button = tk.Button(self.win, text=get_str("fire"), command=self.callback,
                                   height=2, width=26, relief='groove', bd=4, padx=5, pady=5, justify='center')
        confirm_button.grid(row=10, column=1, columnspan=2)

        target_type_frame = tk.LabelFrame(self.win, text=get_str("frame_target"), height=(
            self.player.board_player.size[0]+1)*self.player.board_player.scale[1], width=125, padx=4, pady=4, relief='ridge', bd=3)
        target_type_frame.grid_propagate(0)
        target_type_frame.grid(row=2, column=3, rowspan=4)

        vals = [
            get_str("ammo_type/basic"),
            get_str("ammo_type/heavy"),
            get_str("ammo_type/sonar")
        ]
        self.var_target_type = tk.StringVar()
        self.var_target_type.set(
            get_str("ammo", ammo_type=get_str("ammo_type/basic")))
        for i in range(len(vals)):
            tk.Radiobutton(target_type_frame, indicatoron=0, padx=2, pady=2, variable=self.var_target_type, text=get_str(
                "ammo", ammo_type=vals[i]), value=get_str("ammo", ammo_type=vals[i]), command=self.edit_highlight_range).grid(row=i, column=0)
            if self.player.ammo[f'{get_str("ammo", ammo_type=vals[i])}'] > -1:
                tk.Label(target_type_frame, text=strfill(
                    f"{self.player.ammo[get_str('ammo', ammo_type=vals[i])]} left", 7, before=True)).grid(row=i, column=1)
        while self.loop:
            if app.cancelled:
                return
            else:
                app.update_window()
        else:
            self.win.unbind("<Return>")
            self.win.unbind("<space>")
            confirm_button.destroy()
            target_type_frame.destroy()

        return

    def callback(self, event: "tkinter event" = None):
        self.target_coordinates = self.player.board_opponent.highlighted
        if self.target_coordinates == (None, None):
            tk.messagebox.showerror(message=get_str("invalid_target"))
        elif self.player.ammo[self.var_target_type.get()] == 0:
            tk.messagebox.showerror(message=get_str("no_ammo_left"))
        elif self.player.ammo[self.var_target_type.get()] < 0:
            self.loop = False
        else:
            self.player.ammo[self.var_target_type.get()] -= 1
            self.loop = False

    def edit_highlight_range(self, event: 'tkinter event' = None):
        bullet = self.var_target_type.get()
        if bullet == get_str("ammo", ammo_type=get_str("ammo_type/basic")):
            self.app.highlight_range = (0, 0, 0, 0)
            self.app.player.board_opponent.highlight_tile(
                (self.player.board_opponent.highlighted[0], self.player.board_opponent.highlighted[1]))
        elif bullet == get_str("ammo", ammo_type=get_str("ammo_type/heavy")):
            self.app.highlight_range = (1, 1, 1, 1)
        elif bullet == get_str("ammo", ammo_type=get_str("ammo_type/sonar")):
            self.app.highlight_range = (0, 0, get_cfg(
                "probe_range")-1, get_cfg("probe_range")-1)

        if self.app.highlight_range != (0, 0, 0, 0) and self.player.board_opponent.highlighted != (None, None):
            self.app.player.board_opponent.highlight_tile(
                (self.player.board_opponent.highlighted[0]-self.app.highlight_range[0],
                 self.player.board_opponent.highlighted[1]-self.app.highlight_range[1]),
                (self.player.board_opponent.highlighted[0]+self.app.highlight_range[2],
                 self.player.board_opponent.highlighted[1]+self.app.highlight_range[3]),
                (self.player.board_opponent.highlighted[0],
                 self.player.board_opponent.highlighted[1])
            )


class Config:
    """Configuration window"""

    def __init__(self, force_restore: bool = False):
        self.cfg_win = tk.Tk()
        if force_restore:
            self.restore_cfg()
            return
        self.cfg_win.geometry('600x565+650+100')
        self.cfg_win.resizable(False, False)
        self.cfg_win.wm_protocol("WM_DELETE_WINDOW", self.close)

        size, boatnbr, caps, ammo, colors = get_cfg()

        monospaced_font = tk.font.nametofont("TkDefaultFont").copy()
        monospaced_font.config(family="Consolas")

        ####################
        self.boats_frame = tk.LabelFrame(
            self.cfg_win, text=get_str("frame_cfg_boat"), padx=10, pady=10)
        self.boats_frame.place(x=10, y=7)

        tk.Label(self.boats_frame, text=get_str(
            "cfg_nbrboats")).grid(row=1, column=1)

        self.boatnbr_scale = tk.Scale(
            self.boats_frame, from_=1, to=min(size), orient="horizontal")
        self.boatnbr_scale.set(boatnbr)
        self.boatnbr_scale.grid(row=1, column=2)

        self.caps_frame = tk.Frame(
            self.boats_frame, padx=4, pady=4, relief='ridge', bd=2)
        self.caps_frame.grid(row=2, column=1, columnspan=2)

        self.caps = []
        for i in range(len(caps)):
            lbl = tk.Label(self.caps_frame, text=get_str("cfg_boat_cap", i=i))
            lbl.grid(row=i, column=0)
            cap = tk.Scale(self.caps_frame, from_=2,
                           to=min(size), orient="horizontal")
            cap.set(caps[i])
            cap.grid(row=i, column=1)
            self.caps.append([lbl, cap])
        ####################
        self.missiles_frame = tk.LabelFrame(
            self.cfg_win, text=get_str("cfg_ammo"), padx=10, pady=10)
        self.missiles_frame.place(x=338, y=7)

        tk.Label(self.missiles_frame, text=strfill(get_str(
            "ammo", ammo_type=get_str("ammo_type/basic")), 15)).grid(row=0, column=0)
        basic_shot = tk.StringVar()
        basic_shot.set(u"\u221E")
        tk.Entry(self.missiles_frame, textvariable=basic_shot, state='disabled',
                 width=3, font=monospaced_font).grid(row=0, column=1)

        self.missiles = {}
        self.missiles_list = [get_str("ammo", ammo_type=get_str(
            "ammo_type/heavy")), get_str("ammo", ammo_type=get_str("ammo_type/sonar"))]
        for i in range(len(self.missiles_list)):
            lbl = tk.Label(self.missiles_frame, text=strfill(
                self.missiles_list[i], 15))
            lbl.grid(row=1+i, column=0)
            shot = tk.IntVar()
            shot.set(ammo[self.missiles_list[i]])
            entry = tk.Entry(self.missiles_frame,
                             textvariable=shot, width=3, font=monospaced_font)
            entry.grid(row=1+i, column=1)

            self.missiles[self.missiles_list[i]] = shot

        tk.Label(self.missiles_frame, text=get_str(
            "probe_range")).grid(row=2+i, column=0)
        self.probe_range = tk.Scale(
            self.missiles_frame, from_=1, to=min(size), orient="horizontal")
        self.probe_range.set(get_cfg("probe_range"))
        self.probe_range.grid(row=2+i, column=1)

        ####################
        self.color_frame = tk.LabelFrame(
            self.cfg_win, text=get_str("frame_cfg_color"), padx=10, pady=10)
        self.color_frame.place(x=338, y=160)

        self.presets = [get_str("light_mode"), get_str(
            "night_mode"), get_str("user_color")]
        self.selected_preset = tk.StringVar(self.color_frame)
        self.selected_preset.set(self.presets[-1])
        tk.OptionMenu(self.color_frame, self.selected_preset, *self.presets,
                      command=self.change_preset).grid(row=0, column=0, columnspan=3)

        self.colors = []
        for i in range(len(colors)):
            lbl = tk.Label(
                self.color_frame, text=f"{strfill(list(colors.keys())[i], 11)}:", font=monospaced_font)
            lbl.grid(row=1+i, column=1, sticky='e')
            color = tk.Entry(self.color_frame, width=8, font=monospaced_font)
            color.insert(0, list(colors.values())[i])
            color.grid(row=1+i, column=2)

            self.colors.append([lbl, color])

        button = tk.Button(self.color_frame, text=get_str(
            "color_picker_util"), command=self.color_selector)
        button.grid(row=2+len(colors), column=1, columnspan=2)
        self.color_lbl = tk.Entry(self.color_frame, width=8)
        self.color_lbl.grid(row=3+len(colors), column=1, columnspan=2)

        tk.Button(self.color_frame, text=get_str("preview"), command=self.preview_board).grid(
            row=4+len(colors), column=1, columnspan=2)
        ####################
        self.langs = {
            "English (United Kingdom)": "engb",
            "Fran"+u"\u00E7"+"ais (France)": "frfr"
        }
        choices = list(self.langs.keys())
        self.lang = tk.StringVar(self.cfg_win)
        self.lang.set(list(self.langs.keys())[0])
        selected_lang = get_cfg("lang")
        for lang in list(self.langs.items()):
            if selected_lang in lang:
                self.lang.set(lang[0])
        tk.Label(self.cfg_win, text=get_str("lang_select")).place(x=338, y=455)
        tk.OptionMenu(self.cfg_win, self.lang, *choices).place(x=338, y=480)
        ####################
        tk.Button(self.cfg_win, text=get_str("confirm"),
                  command=self.save_cfg).place(x=230, y=530)
        tk.Button(self.cfg_win, text=get_str("reset"),
                  command=self.restore_cfg).place(x=325, y=530)
        ####################
        self.boatnbr_scale.config(command=self.caps_gen)
        self.boatnbr_scale.focus_set()
        self.cfg_win.mainloop()
        return

    def caps_gen(self, boatnbr: int):
        """gen caps lbls/scales in config window"""
        self.caps_frame.destroy()
        self.caps_frame = tk.Frame(
            self.boats_frame, padx=4, pady=4, relief='ridge', bd=3)
        self.caps_frame.grid(row=2, column=1, columnspan=2)

        boatnbr = int(boatnbr)
        self.caps = []

        for i in range(boatnbr):
            lbl = tk.Label(self.caps_frame, text=get_str("cfg_boat_cap", i=i))
            lbl.grid(row=i, column=0)
            cap = tk.Scale(self.caps_frame, from_=2,
                           to=10, orient="horizontal")
            cap.grid(row=i, column=1)
            self.caps.append([lbl, cap])

    def change_preset(self, event=None):
        if self.selected_preset.get() == self.presets[0]:
            for i in range(len(self.colors)):
                self.colors[i][1].delete(0, tk.END)
                self.colors[i][1].insert(
                    0, ["#61c5ff", "#808080", "#000000", "#ff0000", "#0c00ed", "#fdb100"][i])
        elif self.selected_preset.get() == self.presets[1]:
            for i in range(len(self.colors)):
                self.colors[i][1].delete(0, tk.END)
                self.colors[i][1].insert(
                    0, ['#4d4d4d', '#663300', '#000000', '#b30000', '#000085', '#006000'][i])
        else:
            pass

    def color_selector(self, event=None):
        _, hexa = tk.colorchooser.askcolor()
        if hexa != None:
            self.color_lbl.delete(0, tk.END)
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
                self.colors[i][1].delete(0, tk.END)
                self.colors[i][1].insert(0, get_str("invalid"))
                return
            else:
                colors[color_name[i]] = color

        preview = tk.Toplevel(self.cfg_win)
        preview.grab_set()

        sample = Board(colors=colors)
        sample.generate(preview, 1)

        boat1 = Boat(2, (5, 5, 0))
        boat2 = Boat(3, (4, 2, 1))
        sample.draw_boat(boat1)
        sample.draw_boat(boat2)
        sample.draw_drown(boat1)
        sample.draw_miss((4, 5))
        sample.draw_grid()

        sample.txt.pack()
        sample.board.pack()

        preview.mainloop()

    def save_cfg(self):
        """save all configurations in a local file"""
        lang = self.langs[self.lang.get()]
        size = get_cfg("size")
        boatnbr = self.boatnbr_scale.get()
        caps = [cap.get() for lbl, cap in self.caps]
        ammo = [self.missiles[x].get() for x in self.missiles_list]
        probe_range = self.probe_range.get()
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
            assert isinstance(x, int)

        assert isinstance(probe_range, int)

        assert isinstance(colors, list)
        for x in colors:
            assert isinstance(x, str)

        with open("battleships.save", mode="w") as f:
            f.write(f"{lang}\n")

            for x in size:
                f.write(f"{x}\n")

            f.write(f"{boatnbr}\n")

            for x in caps:
                f.write(f"{x}\n")

            for x in ammo:
                f.write(f"{x}\n")

            f.write(f"{probe_range}\n")

            for i in range(len(colors)):
                f.write(f"{colors[i]}\n")
        self.cfg_win.destroy()

    def restore_cfg(self):
        """restore default configuration to a file"""
        lang = "engb"
        size = (10, 10)
        boatnbr = 5
        caps = [2, 3, 3, 4, 5]
        ammo = [0, 0]
        probe_range = 4
        colors = {
            "background": "#61c5ff",
            "boat": "#808080",
            "grid": "#000000",
            "hit": "#ff0000",
            "miss": "#0c00ed",
            "highlight": "#fdb100"
        }

        with open("battleships.save", mode="w") as f:
            f.write(f"{lang}\n")

            for x in size:
                f.write(f"{x}\n")

            f.write(f"{boatnbr}\n")

            for x in caps:
                f.write(f"{x}\n")

            for x in ammo:
                f.write(f"{x}\n")

            f.write(f"{probe_range}\n")

            for i in colors:
                f.write(f"{colors[i]}\n")

        self.cfg_win.destroy()

    def close(self):
        """window close protocol callback"""
        user = tk.messagebox.askyesnocancel(get_str("save"), get_str(
            "save_ask"), default='yes', icon='question')
        if user == True:
            self.save_cfg()
        elif user == False:
            self.cfg_win.destroy()
        else:
            pass


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


def popup_block(master: tk.Tk, title, msg):
    "show a blocking popup on top of {master}"
    block = tk.Toplevel(master)
    block.grab_set()
    block.focus_set()
    block.title(str(title))
    block.bind('<Return>', lambda x: block.destroy())
    block.bind('<space>', lambda x: block.destroy())

    tk.Label(block, text=str(msg)).pack()
    but = tk.Button(block, text=get_str("ok"), command=block.destroy)
    but.pack()

    master.wait_window(block)


def get_str(str_id, **data):
    "fetch string data from xml lang file"
    try:
        filename = "battleships.save.tmp" if os.path.exists(
            "battleships.save.tmp") else "battleships.save"
        with open(filename, mode="r") as f:
            lang = f.readline().rstrip("\n")
    except:
        lang = "engb"
    tree = et.parse(f"locales\\{lang}.xml")
    val = tree.find(str_id)
    if val == None:
        return
    val = val.text.replace("\\n", "\n")
    try:
        val = eval("f"+repr(val), data)
    except:
        pass
    return val


def init_game(net: bool, nbr_players: int):
    "game prerequirements"
    os.system('cls')

    if net:
        is_host = menu_generator(get_str("ask_host"), [
                                 get_str("host"), get_str("join")], [1, 0])

        if is_host:
            ip = ('', 50001)

            server = socket.socket()
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                server.bind(ip)
                print(get_str("server_binded"))
                server.listen(1)
                connection, _ = server.accept()
            except:
                print(get_str("server_error")+str(sys.exc_info()[1]))
                os.system("pause")
                main_menu()
            else:
                print(get_str("connected"))
                with open("battleships.save", mode='rb') as f:
                    connection.send(f.read(1024))
                connection.recv(1024)
                print(get_str("cfg_sync_complete"))
        else:
            ip = (input(get_str("ip_input")), 50001)
            connection = socket.socket()
            print(get_str("connecting"))
            try:
                connection.connect(ip)
            except:
                print(get_str("client_error") + str(sys.exc_info()[1]))
                os.system("pause")
                main_menu()
            else:
                print(get_str("connected"))
                with open("battleships.save.tmp", mode='wb') as f:
                    f.write(connection.recv(1024))
                connection.send(b'200')
                print(get_str("cfg_sync_complete"))

    size, boatnbr, caps = get_cfg()[:3]
    p1 = Player(1, boatnbr)
    if nbr_players == 2:
        p2 = Player(2, boatnbr)
    else:
        p2 = AI(2, boatnbr)
        while not(p2.ai_strength):
            p2.ai_strength = menu_generator(
                get_str("select_ai"), eval(get_str("ai_name")), [1, 2, 3, 4])

    for p in [p1, p2]:
        if net and p.id == 2:
            print(get_str("waiting"))

        if nbr_players == 2 or (nbr_players == 1 and p.id == 1):  # if human's turn
            if net:  # if wireless
                if p.id == 1:  # first enter data
                    user_input = InputCoords(caps, p.id)
                    p.boats = user_input.data
                    if p.boats == []:
                        return  # if force stop then return to main_menu
                    boat_list = [(boat.capacity, boat.base_coordinates)
                                 for boat in p.boats]
                    boat_list = list(map(str, boat_list))
                    connection.send(
                        strfill(" / ".join(boat_list), 512).encode())
                else:  # then receive opponent's
                    boat_list = connection.recv(512).decode().split(" / ")
                    boats_coords = list(map(eval, boat_list))
                    p.boats = [Boat(*coord) for coord in boats_coords]
            else:
                user_input = InputCoords(caps, p.id)
                p.boats = user_input.data
                if p.boats == []:
                    return  # if force stop then return to main_menu

            for boat in p.boats:
                p.list_coordinates += boat.list_coordinates + [None]
                p.hp += boat.capacity
        else:  # if AI's turn
            i = 0
            while i < boatnbr:
                rot = random.randint(0, 1)
                if not(rot):
                    boat = (caps[i], (random.randint(1, size[0]+1-caps[i]),
                                      random.randint(1, size[1]), rot))
                else:
                    boat = (caps[i], (random.randint(1, size[0]),
                                      random.randint(1, size[1]+1-caps[i]), rot))

                boat_obj = Boat(*boat)

                restart = False
                for x in range(len(boat_obj.list_coordinates)):
                    if boat_obj.list_coordinates[x] in p.list_coordinates:
                        restart = True
                        break
                if restart:
                    continue

                p.boats.append(boat_obj)
                p.list_coordinates += boat_obj.list_coordinates + [None]
                p.hp += boat_obj.capacity
                i += 1
            del p.list_coordinates[-1]

    if net and not(is_host):
        p1, p2 = p2, p1  # switch vars to match players' id on both computer

    ########## game initiated ##########

    if net:
        if is_host:
            app = ApplicationClass(
                [p1, p2], nbr_players, net, is_host, server, connection)
        else:
            app = ApplicationClass(
                [p1, p2], nbr_players, net, None, None, connection)
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
    app.update_window()
    app.win.focus_set()
    print(get_str("game_start"))

    return (p1, p2, app)
############################################################################################


def game(net: bool, nbr_players: int):
    rules()
    init = init_game(net, nbr_players)
    if init == None:
        del init
        return
    else:
        p1, p2, app = init
        del init

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
        app.connection.setblocking(0)

    while p1.hp != 0 and p2.hp != 0:
        if app.cancelled:
            return

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
        app.set_player_turn(eval(f"p{current_player}"), eval(
            f"p{int(not(current_player-1))+1}"))
        app.win.title(get_str("title_current_player", game_title=get_str(
            "game_title"), current_player=current_player))

        # if player's turn
        if nbr_players == 2 or (nbr_players == 1 and current_player == 1):
            msg = get_str("popup_current_player",
                          current_player=current_player)
            if not(app.net):
                msg += get_str("popup_current_player_add")
            popup_block(app.win, get_str("title_current_player", game_title=get_str(
                "game_title"), current_player=current_player), msg)
            show_win(player, opponent)
            app.update_window()

        # user action
        # if player's turn
        if nbr_players == 2 or (nbr_players == 1 and current_player == 1):
            if app.net:
                if (app.is_host and current_player == 1) or (not(app.is_host) and current_player == 2):
                    while (target := InputTarget(app)).target_coordinates in app.player.list_shots:
                        tk.messagebox.showerror(get_str("title_current_player", game_title=get_str(
                            "game_title"), current_player=current_player), get_str("error_already_shot"))
                    else:
                        if app.cancelled:
                            return
                    target_type = target.var_target_type.get()
                    target = target.target_coordinates
                    app.connection.send(repr((target, target_type)).encode())
                else:
                    # waiting for the opponent
                    try:
                        target, target_type = eval(
                            app.connection.recv(1024).decode())
                    except BlockingIOError:
                        app.update_window()
                    except:
                        popup_block(app.win, get_str(
                            "crashed"), sys.exc_info()[1])
                        raise SystemExit
            else:
                while (target := InputTarget(app)).target_coordinates in app.player.list_shots:
                    tk.messagebox.showerror(get_str("title_current_player", game_title=get_str(
                        "game_title"), current_player=current_player), get_str("error_already_shot"))
                else:
                    if app.cancelled:
                        return
                target_type = target.var_target_type.get()
                target = target.target_coordinates
        # END user action

        # AI action
        elif nbr_players == 1 and current_player == 2:  # elif AI's turn
            target, target_type = p2.ai_turn(app)
        # END AI action

        if target_type == get_str("ammo", ammo_type=get_str("ammo_type/basic")):
            app.player.stats["ammo used"][get_str(
                "ammo", ammo_type=get_str("ammo_type/basic"))] += 1
            targets = [target]
        elif target_type == get_str("ammo", ammo_type=get_str("ammo_type/heavy")):
            app.player.stats["ammo used"][get_str(
                "ammo", ammo_type=get_str("ammo_type/heavy"))] += 1
            x_target, y_target = target
            targets = []
            for y in range(y_target-1, y_target+2):
                for x in range(x_target-1, x_target+2):
                    if (1 <= x <= p1.board_opponent.size[0]) and (1 <= y <= p1.board_opponent.size[1]):
                        targets += [(x, y)]
        elif target_type == get_str("ammo", ammo_type=get_str("ammo_type/sonar")):
            app.player.stats["ammo used"][get_str(
                "ammo", ammo_type=get_str("ammo_type/sonar"))] += 1
            x_target, y_target = target
            probe_result = 0
            targets = []
            for y in range(y_target, y_target+get_cfg("probe_range")+1):
                for x in range(x_target, x_target+get_cfg("probe_range")+1):
                    if (1 <= x <= p1.board_opponent.size[0]) and (1 <= y <= p1.board_opponent.size[1]):
                        targets += [(x, y)]
            for boat in app.opponent.boats:
                for target in targets:
                    if target in boat.list_coordinates:
                        probe_result += 1
                        break
            targets = []

        target_count = {
            get_str("miss"): 0,
            get_str("hit"): 0,
            get_str("sunk"): 0
        }
        app.player.stats["shots"] += 1
        for target in targets:
            if not(target in app.player.list_shots):
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
                        boat.hit(app.opponent, app.opponent.board_player,
                                 boat.list_coordinates.index(target))
                        app.player.board_opponent.draw_hit(
                            boat.list_coordinates[boat.list_coordinates.index(target)])

                        target_count[get_str("hit")] += 1
                        app.player.board_player.status_var.set(
                            get_str("hit") + " !")
                        if boat.hp == 0:
                            # if boat is fully damaged
                            target_count[get_str("sunk")] += 1
                            app.player.board_player.status_var.set(
                                get_str("sunk") + " !")
                            app.player.stats["sunk"] += 1
                            app.opponent.board_player.draw_drown(boat)
                            app.player.board_opponent.draw_boat(boat)
                            app.player.board_opponent.draw_drown(boat)
                else:
                    # if target doesn't hit a ship
                    target_count[get_str("miss")] += 1
                    app.player.board_player.status_var.set(
                        get_str("miss") + " !")
                    app.player.stats["miss"] += 1
                    app.player.board_opponent.draw_miss(target)
                    app.opponent.board_player.draw_miss(target)

        # if player's turn
        if nbr_players == 2 or (nbr_players == 1 and current_player == 1):
            app.update_window()

            if target_type == get_str("ammo", ammo_type=get_str("ammo_type/sonar")):
                popup_block(app.win, get_str("title_current_player", game_title=get_str(
                    "game_title"), current_player=current_player), get_str("sonar_warn", probe_result=probe_result))
                app.player.last_status = "scan"

            elif len(targets) > 1:
                checksum = [str(target_count[x])+"x "+x.upper()+" !" for x in [get_str(
                    "miss"), get_str("hit"), get_str("sunk")] if target_count[x] != 0]
                popup_block(app.win, get_str("title_current_player", game_title=get_str(
                    "game_title"), current_player=current_player), "\n".join(checksum))
                app.player.last_status = checksum[-1].split(" ")[
                    1].lower().strip()

            else:
                popup_block(app.win, get_str("title_current_player", game_title=get_str(
                    "game_title"), current_player=current_player), app.player.board_player.status_var.get().upper())
                app.player.last_status = app.player.board_player.status_var.get().lower()[
                    :-2]

            app.player.board_opponent.clear_highlight()
            if app.net:
                if app.is_host:
                    hide_win(p2, p1)
                else:
                    hide_win(p1, p2)
            else:
                hide_win(app.player, app.opponent)
        if len(targets) > 1:
            checksum = [str(target_count[x])+"x "+x.upper()+" !" for x in [get_str(
                "miss"), get_str("hit"), get_str("sunk")] if target_count[x] != 0]
            app.player.last_status = checksum[-1].split(" ")[1].lower().strip()
        else:
            app.player.last_status = app.player.board_player.status_var.get().lower()[
                :-2]

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
    print(get_str("game_finished"))
    print(get_str("game_duration", end_time=end_time))
    if p1.hp == 0 and p2.hp != 0:
        if app.nbr_players == 2:
            print(get_str("victory/player", id=2))
        else:
            print(get_str("victory/ai"))
    elif p1.hp != 0 and p2.hp == 0:
        print(get_str("victory/player", id=1))
    else:
        print(get_str("victory/draw"))

    print(get_str("stats_recap/header"))
    for p in app.players:
        if p.id == 2 and app.nbr_players == 1:
            print(get_str("stats_recap/ai"))
        else:
            print(get_str("stats_recap/player", p=p))
        print(get_str("stats_recap/content", p=p))
        print()

    os.system("pause")


def main_menu():
    "display the game's main menu"
    while True:
        exec(menu_generator(
            get_str("game_title"),
            [get_str("play"), get_str("settings"), get_str("exit_game")],
            ["play()", "Config()", "raise SystemExit"]
        ))


def play():
    "pre-game selector"
    net, nbr_players = menu_generator(
        get_str("game_modes"),
        [get_str("solo"), get_str("local"), get_str("wireless")],
        [(0, 1), (0, 2), (1, 2)]
    )
    game(net, nbr_players)


def rules():
    "display game's rules"
    os.system("cls")
    print(get_str("rules"))
    os.system("pause")
    return


def get_cfg(param=None, recovery=False):
    "get configuration from save data"
    filename = "battleships.save.tmp" if os.path.exists(
        "battleships.save.tmp") else "battleships.save"
    try:
        with open(filename, mode="r") as f:
            lang = f.readline().rstrip("\n")

            size = eval(f.readline().rstrip("\n")), eval(
                f.readline().rstrip("\n"))

            boatnbr = eval(f.readline().rstrip("\n"))

            caps = []
            for i in range(boatnbr):
                caps.append(eval(f.readline().rstrip("\n")))

            ammo = {get_str("ammo", ammo_type=get_str("ammo_type/basic")): -1}
            for i in [get_str("ammo", ammo_type=get_str("ammo_type/heavy")), get_str("ammo", ammo_type=get_str("ammo_type/sonar"))]:
                ammo[i] = eval(f.readline().rstrip("\n"))

            probe_range = eval(f.readline().rstrip("\n"))

        with open("battleships.save", mode='r') as f:
            for i in range(len(size)+boatnbr+len(ammo)+2):
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
            assert isinstance(ammo[x], int)

        assert isinstance(probe_range, int)

        assert isinstance(colors, dict)
        for x in colors:
            assert isinstance(colors[x], str)

        if param == None:
            [lang]
            return [size, boatnbr, caps, ammo, colors]
        else:
            return eval(param)
    except Exception as e:
        if not(recovery):
            if type(e) == AssertionError:
                msg = get_str("cfg_error_save")+str(sys.exc_info()[1])
            elif type(e) == FileNotFoundError:
                msg = get_str("cfg_error_not_found")+str(sys.exc_info()[1])
            else:
                msg = get_str("cfg_error_read")+str(sys.exc_info()[1])
            win = tk.Tk()
            user = tk.messagebox.askokcancel(get_str("cfg_error_title"), msg)
            if user:
                Config(force_restore=True)
                get_cfg(recovery=True)
                tk.messagebox.showinfo(
                    get_str("cfg_error_title"), get_str("cfg_recovery_successful"))
                win.destroy()
            else:
                raise SystemExit
        else:
            tk.messagebox.showerror(
                get_str("cfg_error_title"), get_str("cfg_recovery_unsuccessful"))
            raise SystemExit


if __name__ == '__main__':
    get_cfg()
    main_menu()
