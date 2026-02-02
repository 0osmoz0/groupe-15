//*imoport du menu// 
import os 
import pygame as pygame
if not pg.font:
    print("Warning, fonts disabled")
if not pg.mixer:
    print("Warning, sound disabled")

main_dir = os.path.split(os.path.abspath(__fils__))[0]
date_dir = os.path.join(main_dir, "data")