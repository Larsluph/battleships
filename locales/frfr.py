#!/usr/bin/env python3
#-*- coding: utf-8 -*-

rules = "Ce jeu se joue à 1 ou 2 joueurs.\n\nVotre but est de couler tout les bateaux de votre adversaire.\n\nPour cela, vous devez tirer sur la flotte adverse.\nVous pouvez viser en tirant sur une case de la grille.\nAprès avoir selectionné une cible valide (une case où vous\nn'avez pas encore tiré et qui est sur la grille), vous\nsaurez si votre tir a touché un bateau.\n\nLe gagnant est celui qui coule toute la flotte adverse."
cfg_error_title = "Erreur dans la configuration"
cfg_error_save = "Une erreur est survenue en enregistrant le fichier de sauvegarde.\nUn protocol de récupération va être initié.\nErreur: "
cfg_error_not_found = "Aucun fichier de sauvegarde n'a été trouvé.\nUn nouveau va être créé.\nErreur: "
cfg_error_read = "Une erreur est survenue en lisant le fichier de sauvegarde.\nUn protocol de récupération va être initié.\nErreur: "
cfg_recovery_successful = "Le protocol de récupération a réussi !"
cfg_recovery_unsuccessful = "Le protocol de récupération a échoué.\nEssayez de réinstaller le fichier de configuration de base."
game_modes = "Modes de jeux :"
solo = "Solo"
local = "Multijoueur Local"
wireless = "Multijoueur Sans-fil"
game_title = "Bataille Navale"
play = "Jouer"
settings = "Paramètres"
exit_game = "Quitter"
ask_host = "Que voulez-vous faire ?"
host = "Héberger"
join = "Rejoindre"
server_binded = "Serveur lié\nEn attente d'une connection..."
server_error = "Impossible de créer le serveur. Réessayez ultérieurement.\n Erreur: "
ip_input = "Entrer l'ip de connexion : "
connecting = "Connexion en cours..."
client_error = "Impossible de se connecter. Réessayez ultérieurement.\n Erreur: "
connected = "Connecté!\nSynchronisation des paramètres de jeu..."
cfg_sync_complete = "Paramètres de jeu synchronisés !"
select_ai = "Selectionnez la difficulté de l'ordinateur"
ai_name = ["Facile", "Normal", "Difficile", "Extrême"]
waiting = "En attente de l'adversaire..."
player_turn = game_title + " - Joueur {p.id}"
error_boat_over = "Ce bateau est sur un autre.\nUn bateau peut uniquement être placé sur l'eau"
game_start = "Démarrage de la partie..."
title_current_player = game_title + " - Joueur {current_player}"
popup_current_player = "Au tour du joueur {current_player}"
popup_current_player_add = "\nLe plateau du joueur sera affiché une fois cette fenêtre fermée."
error_already_shot = "Vous avez déjà tiré ici !"
crashed = "Le jeu a planté !"
sonar_warn = "{probe_result} bateaux sont situés dans la zone"
player_playboard = "Votre plateau de jeu"
opponent_playboard = "La plateau de votre adversaire"
error_exit = "Action annulée par l'utilisateur. Retour au menu principal..."
place_boat = "Joueur {player_nbr} - Bateau n°{boat_id}"
boat_capacity = "Capacité du bateau :"
x_boat = "Entrez la position x du bateau :"
y_boat = "Entrez la position y du bateau :"
rot_boat = "Choississez la rotation du bateau :"
horizontal = "Horizontal"
vertical = "Vertical"
confirm = "Confirmer !"
reset = "Réinitialiser"
warning = "Avertissement"
error_boat_fit = "Le bateau doit rentrer sur la grille !"
fire = "Tirer !"
frame_target = "Selection des munitions"
invalid_target = "Cible invalide.\nImpossible de tirer."
no_ammo_left = "Vous n'avez plus de ce type de munitions.\nImpossible de tirer."
frame_cfg_boat = "Configuration des bateaux"
cfg_nbrboats = "Entrez le nombre de bateaux\npar équipes :"
cfg_boat_cap = "Capacité du bateau {i+1} :"
cfg_ammo = "Configuration des munitions"
frame_cfg_color = "Configuration des couleurs"
light_mode = "Mode Clair"
night_mode = "Mode Sombre"
user_color = "Utilisateur"
color_picker_util = "Outil de selection des couleurs"
preview = "Aperçu de la grille"
invalid = "Invalide"
save = "Enregistrer"
save_ask = "Voulez-vous enregistrer les modifications ?"
ok = "Ok"
miss = "raté"
hit = "touché"
sunk = "coulé"
probe_range = "Portée du sonar"
ammo = "Munitions {ammo_type}"
basic = "Normales"
heavy = "Lourdes"
sonar = "Sonar"
stats_recap = {
  "header": "Statistiques : ",
  "player": "  Joueur {p.id} : ",
  "ai": "  Ordinateur : ",
  "content": [
    "    Cases non détruites  : {p.hp:03}",
    "    Coups tirés          : {p.stats['shots']:03}",
    "    Munitions Utilisées",
    "      Munitions Normales   : {p.stats['ammo used']['"+ str(eval("f"+repr(ammo), {"ammo_type": basic})) +"']:03}",
    "      Munitions Lourdes    : {p.stats['ammo used']['"+ str(eval("f"+repr(ammo), {"ammo_type": heavy})) +"']:03}",
    "      Munitions Sonar      : {p.stats['ammo used']['"+ str(eval("f"+repr(ammo), {"ammo_type": sonar})) +"']:03}",
    "    Tirs manqués         : {p.stats['miss']:03}",
    "    Dégâts causés        : {p.stats['hits']:03}",
    "    Bateaux coulés       : {p.stats['sunk']:03}"
  ]
}
game_finished = "Partie terminée!"
game_duration = "La partie a duré {str(round(end_time, 2))} secondes."
victory = {
  "player": "Le joueur {id} a gagné!",
  "ai": "L'ordinateur a gagné!",
  "draw": "Egalité!"
}
lang_select = "Choississez la langue du jeu :"
restart_needed_title = "Redémarrage nécessaire"
restart_needed_txt = "Assurez vous de fermer et rouvrir le jeu pour que tous les changements prennent effet."
