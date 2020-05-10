#!/usr/bin/env python3
#-*- coding: utf-8 -*-

rules = "This game is a single and multiplayer game.\n\nYour goal is to sink all of your opponent's boats.\n\nTo do so, you have to fire at your opponent's fleet.\nYou can aim by clicking on a grid's tile.\nAfter selecting a valid target (a square you haven't already shot at and\nthat is in the grid), you'll know if you hit a boat or miss your shot.\n\nThe winner is the one that sunk all of his opponent's fleet."
cfg_error_title = "Configuration Error"
cfg_error_save = "An error occurred while saving the save file.\nA recovery protocol will be initiated.\nError: "
cfg_error_not_found = "No save file were found.\nA new one will be created.\nError: "
cfg_error_read = "An error occurred while reading the save file.\nA recovery protocol will be initiated.\nError: "
cfg_recovery_successful = "The recovery protocol was successful !"
cfg_recovery_unsuccessful = "The recovery protocol was unsuccessful.\nTry retrieving the base configuration file."
game_modes = "Game modes :"
solo = "Solo"
local = "Local"
wireless = "Wireless"
game_title = "Battleships"
play = "Play"
settings = "Settings"
exit_game = "Exit"
ask_host = "What do you want to do ?"
host = "Host"
join = "Join"
server_binded = "Server binded\nWaiting for a connection..."
server_error = "Can't create server. Try again later.\n Error: "
ip_input = "Enter ip to connect : "
connecting = "Connecting..."
client_error = "Can't connect. Try again later.\n Error: "
connected = "Connected!\nSyncronizing game configuration..."
cfg_sync_complete = "Game configuration syncronized!"
select_ai = "Select the AI's difficulty"
ai_name = ["Dumbass", "Kinda Human", "Basic Sniper", "Godlike Sniper"]
waiting = "Waiting for the opponent..."
player_turn = game_title + " - Player {p.id}"
error_boat_over = "This boat is on another one\nYou can only place a boat in the water"
game_start = "Starting game..."
title_current_player = game_title + " - Player {current_player}"
popup_current_player = "Player {current_player}'s turn"
popup_current_player_add = "\nThe player's board will be displayed when this window will be closed."
error_already_shot = "You already shot at that point !"
crashed = "Game crashed!"
sonar_warn = "{probe_result} boats are located in the highlighted area"
player_playboard = "Your Playboard"
opponent_playboard = "Enemy's Playboard"
error_exit = "Action cancelled by user. Exiting to main menu..."
place_boat = "Player {player_nbr} - Place Boat {boat_id}"
boat_capacity = "boat's capacity :"
x_boat = "Enter the x position of the boat :"
y_boat = "Enter the y position of the boat :"
rot_boat = "Choose the boat's rotation :"
horizontal = "Horizontal"
vertical = "Vertical"
confirm = "Confirm!"
reset = "Reset"
warning = "Warning"
error_boat_fit = "The boat must fit in the grid!"
fire = "Fire !"
frame_target = "Ammo Selection"
invalid_target = "Target is invalid.\nUnable to fire."
no_ammo_left = "You don't have any more ammo of this type.\nUnable to fire."
frame_cfg_boat = "Boats Configuration"
cfg_nbrboats = "Enter number of boats per team :"
cfg_boat_cap = "Boat {i+1}'s capacity :"
cfg_ammo = "Ammo Configuration"
frame_cfg_color = "Colors Configuration"
light_mode = "Light Mode"
night_mode = "Night Mode"
user_color = "User Defined"
color_picker_util = "Color picker utility"
preview = "Preview Board"
invalid = "Invalid"
save = "Save"
save_ask = "Do you want to save changes ?"
ok = "Ok"
miss = "miss"
hit = "hit"
sunk = "sunk"
probe_range = "Sonar's range"
ammo = "{ammo_type} Ammo"
basic = "Basic"
heavy = "Heavy"
sonar = "Sonar"
stats_recap = {
  "header": "STATS : ",
  "player": "  Player {p.id} : ",
  "ai": "  AI : ",
  "content": [
    "    Undamaged boats : {p.hp:03}",
    "    Shots fired     : {p.stats['shots']:03}",
    "    Ammo used",
    "      Basic Ammo      : {p.stats['ammo used']['"+ str(eval("f"+repr(ammo), {"ammo_type": basic})) +"']:03}",
    "      Heavy Ammo      : {p.stats['ammo used']['"+ str(eval("f"+repr(ammo), {"ammo_type": heavy})) +"']:03}",
    "      Sonar Ammo      : {p.stats['ammo used']['"+ str(eval("f"+repr(ammo), {"ammo_type": sonar})) +"']:03}",
    "    Missed shots    : {p.stats['miss']:03}",
    "    Damages done    : {p.stats['hits']:03}",
    "    Boats sunk      : {p.stats['sunk']:03}"
  ]
}
game_finished = "Game over!"
game_duration = "The game lasted {str(round(end_time, 2))} seconds."
victory = {
  "player": "Player {id} wins!",
  "ai": "AI wins!",
  "draw": "It's a draw!"
}
lang_select = "Choose the game's language :"
restart_needed_title = "Restart needed"
restart_needed_txt = "Please make sure to close and reopen the game for all changes to take effect."
