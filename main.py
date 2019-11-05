#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import custom_module
import os
import string
import random
import time
import tkinter as tk

import win_manager

class Board:
    def __init__(self,size,scale):
        self.size = size
        self.scale = scale
        self.status_var = tk.StringVar(value='{dmg_status}')

    def generate(self,window,player):
        if player == 1:
            self.txt = "Your Playboard"
        else:
            self.txt = "Enemy's Playboard"

        self.txt = tk.Label(window, text=self.txt)
        self.board = tk.Canvas(window, height=(self.size[0]+1)*self.scale[1], width=(self.size[1]+1)*self.scale[0], bg='#61c5ff')
    
    def draw_grid(self):
        self.board.create_line(self.scale[0], 3, (self.size[0]+1)*self.scale[0], 3, width=3, fill='black')
        self.board.create_line(3, self.scale[1], 3, (self.size[1]+1)*self.scale[1], width=3, fill='black')

        i=self.scale[0]
        while i <= (self.size[0]+1)*self.scale[0]:
            self.board.create_line(0,i,(self.size[0]+1)*self.scale[0],i,width=3,fill='black') # draw x lines
            i+=self.scale[0]

        i=self.scale[1]
        while i <= (self.size[1]+1)*self.scale[1]:
            self.board.create_line(i,0,i,(self.size[1]+1)*self.scale[1],width=3,fill='black') # draw y lines
            i+=self.scale[1]

        bold_font = ("Helvetica", 18, "bold")
        for x in range(self.size[0]):
            self.board.create_text( ( (self.scale[0]*x)+(self.scale[0]*1.5), self.scale[1]/2 ) , text=str(x+1) ,font=bold_font)
        
        for y in range(self.size[1]):
            self.board.create_text( ( self.scale[0]/2, (self.scale[1]*y)+(self.scale[1]*1.5) ) , text=letter[y] ,font=bold_font)

    def draw_boat(self,boat):
        boat_color = "#808080"
        if boat.base_coordinates[2] == 0:
            self.board.create_oval(
                boat.base_coordinates[0]*self.scale[0], boat.base_coordinates[1]*self.scale[1],
                (boat.base_coordinates[0]*self.scale[0])+(boat.capacity*self.scale[0]), (boat.base_coordinates[1]*self.scale[1])+self.scale[1],
                outline=boat_color,fill=boat_color,width=1)
        else:
            self.board.create_oval(
                boat.base_coordinates[0]*self.scale[0], boat.base_coordinates[1]*self.scale[1],
                (boat.base_coordinates[0]*self.scale[0])+self.scale[0], (boat.base_coordinates[1]*self.scale[1])+(boat.capacity*self.scale[1]),
                outline=boat_color,fill=boat_color,width=1)
    
    def draw_hit(self,coordinates):
        self.board.create_line(
            coordinates[0]*self.scale[0],(coordinates[1]+1)*self.scale[1],
            (coordinates[0]+1)*self.scale[0],coordinates[1]*self.scale[1],
            width=3,fill='#ff0000')
    
    def draw_drown(self,boat):
        if not(boat.base_coordinates[2]):
            for x in range(boat.capacity):
                self.board.create_line(
                    (boat.base_coordinates[0]+x)*self.scale[0], (boat.base_coordinates[1])*self.scale[1],
                    (boat.base_coordinates[0]+x+1)*self.scale[0], (boat.base_coordinates[1]+1)*self.scale[1],
                    width=3,fill='#ff0000')
                self.board.create_line(
                    (boat.base_coordinates[0]+x)*self.scale[0], (boat.base_coordinates[1]+1)*self.scale[1],
                    (boat.base_coordinates[0]+x+1)*self.scale[0], (boat.base_coordinates[1])*self.scale[1],
                    width=3,fill='#ff0000')
        else:
            for x in range(boat.capacity):
                self.board.create_line(
                    (boat.base_coordinates[0])*self.scale[0], (boat.base_coordinates[1]+x)*self.scale[1],
                    (boat.base_coordinates[0]+1)*self.scale[0], (boat.base_coordinates[1]+x+1)*self.scale[1],
                    width=3,fill='#ff0000')
                self.board.create_line(
                    (boat.base_coordinates[0]+1)*self.scale[0], (boat.base_coordinates[1]+x)*self.scale[1],
                    (boat.base_coordinates[0])*self.scale[0], (boat.base_coordinates[1]+x+1)*self.scale[1],
                    width=3,fill='#ff0000')
    
    def draw_miss(self,coordinates):
        self.board.create_line(
            (coordinates[0]+1)*self.scale[0],(coordinates[1]+1)*self.scale[1],
            coordinates[0]*self.scale[0],coordinates[1]*self.scale[1],
            width=3,fill='#0c00ed')
        self.board.create_line(
            (coordinates[0])*self.scale[0],(coordinates[1]+1)*self.scale[1],
            (coordinates[0]+1)*self.scale[0],coordinates[1]*self.scale[1],
            width=3,fill='#0c00ed')
    
class Boat:
    def __init__(self,properties):
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
    
    def hit(self,player,board,damaged_tile):
        self.damages[damaged_tile] = 0
        self.hp -= 1
        player.hp -= 1

        board.draw_hit(self.list_coordinates[damaged_tile])

class Player:
    def __init__(self,id,boatnbr):
        self.id = id
        self.boatnbr = boatnbr
        self.hp = 0
        self.boats = []
        self.list_coordinates = [None]
        self.list_shots = []
        self.stats = {
            "shots":0,
            "miss":0,
            "hits":0,
            "sunk":0
            }
            
    def create_boards(self,size):
        scale = (500/size[0],500/size[1])
        self.board_player = Board(size,scale)
        self.board_opponent = Board(size,scale)
############################################################################################
def show_win(player,opponent):
    opponent.board_player.txt.grid_remove()
    opponent.board_player.board.grid_remove()

    opponent.board_opponent.txt.grid_remove()
    opponent.board_opponent.board.grid_remove()

    player.board_player.txt.grid()
    player.board_player.board.grid()

    player.board_opponent.txt.grid()
    player.board_opponent.board.grid()

def hide_win(player,opponent):
    player.board_player.txt.grid_remove()
    player.board_player.board.grid_remove()
    player.board_opponent.txt.grid_remove()
    player.board_opponent.board.grid_remove()

    opponent.board_player.txt.grid_remove()
    opponent.board_player.board.grid_remove()
    opponent.board_opponent.txt.grid_remove()
    opponent.board_opponent.board.grid_remove()
############################################################################################
def init_game(nbr_players):
    os.system('cls')

    p1 = Player(1,boatnbr)
    p2 = Player(2,boatnbr)

    for p in ["p1","p2"]:
        i=0
        while i < boatnbr:
            if nbr_players == 2 or (nbr_players == 1 and p == "p1"):
                boat = win_manager.input_coords(caps[i],p[1],i+1)
            else:
                rot = random.randint(0,1)
                if not(rot):
                    boat = (caps[i],(random.randint(1,11-caps[i]),random.randint(1,10),rot))
                else:
                    boat = (caps[i],(random.randint(1,10),random.randint(1,11-caps[i]),rot))
            
            boat_obj = Boat(boat)

            restart = False
            for x in range(len(boat_obj.list_coordinates)):
                if boat_obj.list_coordinates[x] in eval(p).list_coordinates:
                    if nbr_players == 2 or (nbr_players == 1 and p == "p1"):
                        win = tk.Tk()
                        tk.Label(win,text="this boat is on another one").pack()
                        tk.Label(win,text="you can only place a boat in the water").pack()
                        ok=tk.Button(win,text="OK",command=win.destroy)
                        ok.pack()
                        ok.focus_force()
                        win.bind("<Return>",win.destroy)
                        win.mainloop()
                    else:
                        pass
                    restart = True
                    break
            if restart:
                continue
            
            eval(p).boats.append(boat_obj)
            eval(p).list_coordinates += boat_obj.list_coordinates + [None]
            eval(p).hp += boat[0]
            i += 1
        del eval(p).list_coordinates[len(eval(p).list_coordinates)-1]

    ########## game started ##########

    window = win_manager.create_mainwindow()

    for p in ["p1","p2"]:
        eval(p).create_boards(size)

        eval(p).board_player.generate(window,1)
        eval(p).board_opponent.generate(window,2)

        for boat in eval(p).boats:
            eval(p).board_player.draw_boat(boat)

        eval(p).board_player.draw_grid()
        eval(p).board_opponent.draw_grid()

    p1.board_player.txt.grid(row=1,column=1)
    p1.board_player.board.grid(row=2,column=1)

    p1.board_opponent.txt.grid(row=1,column=2)
    p1.board_opponent.board.grid(row=2,column=2)

    p2.board_player.txt.grid(row=4,column=1)
    p2.board_player.board.grid(row=5,column=1)

    p2.board_opponent.txt.grid(row=4,column=2)
    p2.board_opponent.board.grid(row=5,column=2)

    show_win(p1,p2)
    hide_win(p1,p2)
    window.update()
    window.focus_force()
    
    return (p1,p2,window)
############################################################################################
def game(nbr_players):
    rules()
    if nbr_players == 1:
        ai_strength = 0
        while ai_strength == 0:
            ai_strength = custom_module.utilities.menu_generator(
                "Select the AI's difficulty",
                ["Easy","Normal (in development)","Hardcore"],
                [1,0,3]
            )
        target_id = 0
    p1,p2,window = init_game(nbr_players)

    # print(p1.list_coordinates)
    # print(p2.list_coordinates)

    start_time = time.perf_counter()
    current_player = random.randint(1,2)
    while p1.hp != 0 and p2.hp != 0:
        player = "p"+str(current_player)
        opponent = "p"+str(int(not(current_player-1))+1)
        window.title(f"Python Battleships - Player {player[1]}")

        if nbr_players == 2 or (nbr_players == 1 and current_player == 1): # if player's turn
            win_manager.popup(window,f"Player {player[1]}'s turn","The player's board will be displayed when this window will be closed")
            show_win(eval(player),eval(opponent))

        ### user action
        if nbr_players == 2 or (nbr_players == 1 and current_player == 1): # if player's turn
            target = win_manager.input_target(window,player[1])
            while target in eval(player).list_shots:
                win_manager.popup(window, f"you already shot at that point")
                target = win_manager.input_target(window,player[1])
        
        ### AI action
        elif nbr_players == 1 and current_player == 2: # elif AI's turn
            # Easy
            if ai_strength == 1:
                target = (random.randint(1,size[0]),random.randint(1,size[1]))
                while target in eval(player).list_shots:
                    target = (random.randint(1,size[0]),random.randint(1,size[1]))

            # Normal
            elif ai_strength == 2:
                pass

            # Hardcore
            elif ai_strength == 3:
                if eval(opponent).list_coordinates[target_id] == None:
                    success_chances = 20 # % chance to hit the player
                    if random.randint(1,100) <= success_chances:
                        target_id += 1
                        target = eval(opponent).list_coordinates[target_id]
                        while target in eval(player).list_shots or target == None:
                            target_id += 1
                            target = eval(opponent).list_coordinates[target_id]
                    else:
                        target = (random.randint(1,size[0]),random.randint(1,size[1]))
                        while target in eval(player).list_shots or target == None:
                            target = (random.randint(1,size[0]),random.randint(1,size[1]))
                else:
                    target_id += 1
                    target = eval(opponent).list_coordinates[target_id]
                    while target in eval(player).list_shots or target == None:
                        target_id += 1
                        target = eval(opponent).list_coordinates[target_id]

        eval(player).stats["shots"] += 1
        eval(player).list_shots.append(target)
        if target in eval(opponent).list_coordinates:
            eval(player).stats["hits"] += 1
            
            for boat in eval(opponent).boats:
                if target in boat.list_coordinates:
                    break
            if boat.damages[boat.list_coordinates.index(target)] != 0:
                boat.hit( eval(opponent), eval(opponent).board_player, boat.list_coordinates.index(target) )
                eval(player).board_opponent.draw_hit(boat.list_coordinates[boat.list_coordinates.index(target)])
                eval(player).board_player.status_var.set("HIT!")
                if boat.hp == 0:
                    eval(player).board_player.status_var.set("SUNK!")
                    eval(player).stats["sunk"] += 1
                    eval(opponent).board_player.draw_drown(boat)
                    eval(player).board_opponent.draw_boat(boat)
                    eval(player).board_opponent.draw_drown(boat)
        else:
            eval(player).board_player.status_var.set("MISS!")
            eval(player).stats["miss"] += 1
            eval(player).board_opponent.draw_miss(target)
            eval(opponent).board_player.draw_miss(target)
        ### END user action

        if nbr_players == 2 or (nbr_players == 1 and current_player == 1): # if player's turn
            window.update()
            win_manager.popup(window,eval(player).board_player.status_var.get())

            hide_win(eval(player),eval(opponent))

        current_player = int(not(current_player-1))+1

    window.destroy()

    end_time = time.perf_counter() - start_time
    print("GAME IS FINISHED!")
    print(f"THE GAME LASTS {str(int(end_time))} SECONDS.")
    if p1.hp == 0 and p2.hp != 0:
        if nbr_players == 2:
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
    if nbr_players == 2:
        print(f"  Player 2 : ")
    else:
        print(f"  AI : ")
    print(f"    shots done   : {p2.stats['shots']:03}")
    print(f"    missed shots : {p2.stats['miss']:03}")
    print(f"    damages done : {p2.stats['hits']:03}")
    print(f"    boats sunk   : {p2.stats['sunk']:03}")

    os.system("pause")
    
def main_menu():
    while True:
        exec(custom_module.utilities.menu_generator(
            "Battleships",
            ["Play", "Exit"],
            ["play()","raise SystemExit"],hidden={
                "your choice":"""print("Tu te crois malin ? hmm... Tu me fais presque de la peine.");time.sleep(2)""",
                0:"""print("Te crois-tu capable de faire bugger ce menu ? HA n'essaye même pas !");time.sleep(2)""",
                123:"""print("Soleil !");time.sleep(2)""",
                666:"""print("SATAN! Je t'ai fais quoi pour que tu me fasse ça !?".upper());time.sleep(2)""",
                999:"""print("Me dit pas que t'as fait toutes les combinaisons pour arriver jusqu'ici !?");time.sleep(2)"""
            })
        )

def play():
    nbr_players = custom_module.utilities.menu_generator(
        "Number of players :",
        ["1","2"],
        [1,2]
    )
    game(nbr_players)

def rules():
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
    return 1

letter = list(string.ascii_uppercase)

with open("battleships.config",mode="r") as f:
    lines = f.readlines()

shift = 5
boatnbr_line = 17
caps_line = 18
"""removed feature
try:
    size = eval(lines[size_line][:len(lines[size_line])-1])
    if size == None:
        size = eval(lines[size_line-shift][:len(lines[size_line-shift])-1])
except:
    print("Configuration file error line 20. Please make sure you only changed the custom values.")
    os.system("pause")
    raise SystemExit
"""
size = (10,10)

try:
    boatnbr = eval(lines[boatnbr_line][:len(lines[boatnbr_line])-1])
    if boatnbr == None:
        boatnbr = int(lines[boatnbr_line-shift][:len(lines[boatnbr_line-shift])-1])
except:
    print("Configuration file error line 21. Please make sure you only changed the custom values.")
    os.system("pause")
    raise SystemExit

try:
    caps = eval(lines[caps_line][:len(lines[caps_line])-1])
    if caps == None:
        caps = eval(lines[caps_line-shift][:len(lines[caps_line-shift])-1])

    for x in caps:
        if x > size[0] or x > size[1]:
            print("Configuration file error line 22. Some boats are larger than the grid.")
            os.system("pause")
            raise SystemExit
        elif x < 1:
            print("Configuration file error line 22. A boat's capacity have to be higher than 1.")
            os.system("pause")
            raise SystemExit

except:
    print("Configuration file error line 22. Please make sure you only changed the custom values.")
    os.system("pause")
    raise SystemExit

if len(caps) >= boatnbr:
    caps = caps[:boatnbr]
else:
    print("Configuration file error line 22. The number of boats isn't corresponding to the list's length")
    os.system("pause")
    raise SystemExit

start_time = 0.0
end_time = 0.0

if __name__ == '__main__':
    main_menu()
