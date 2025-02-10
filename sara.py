'''
Made By @Buck3ts41
'''


import pyMeow as pm
from offsets import *
import time
import math
from pynput.mouse import Controller
from random import uniform
import win32api
import win32con

mouse = Controller()

class Colors:
    purple = pm.get_color("purple")
    black = pm.get_color("black")
    cyan = pm.get_color("cyan")
    white = pm.get_color("white")
    grey = pm.fade_color(pm.get_color("#242625"), 0.7)
    red = pm.get_color("red")
    green = pm.get_color("#70ff00")
    blue = pm.get_color("blue")

class Entity:
    def __init__(self, ptr, pawn_ptr, proc):
        self.ptr = ptr
        self.pawn_ptr = pawn_ptr
        self.proc = proc
        self.pos2d = None
        self.head_pos2d = None
      

    @property
    def name(self):
        return pm.r_string(self.proc, self.ptr + m_iszPlayerName)

    @property
    def health(self):
        return pm.r_int(self.proc, self.pawn_ptr + m_iHealth)

    @property
    def armor(self):
        return pm.r_int(self.proc, self.pawn_ptr + m_ArmorValue)

    @property
    def team(self):
        return pm.r_int(self.proc, self.pawn_ptr + m_iTeamNum)

    @property
    def pos(self):
        return pm.r_vec3(self.proc, self.pawn_ptr + m_vOldOrigin)
        
    @property
    def pos(self):
        return pm.r_vec3(self.proc, self.pawn_ptr + m_vOldOrigin)

    @property
    def dormant(self):
        return pm.r_bool(self.proc, self.pawn_ptr + m_bDormant)

    def bone_pos(self, bone):
        game_scene = pm.r_int64(self.proc, self.pawn_ptr + m_pGameSceneNode)
        bone_array_ptr = pm.r_int64(self.proc, game_scene + m_pBoneArray)
        return pm.r_vec3(self.proc, bone_array_ptr + bone * 32)
    def get_shots_fired(self, local_player):
        return pm.r_int(self.proc, local_player + m_iShotsFired)
    
    def get_aim_punch(self, local_player):
        return pm.r_vec2(self.proc, local_player + m_aimPunchAngle)
    
    def is_shooting(self):
        return win32api.GetKeyState(0x01) < 0
    
    def wts(self, view_matrix):
        try:
            self.pos2d = pm.world_to_screen(view_matrix, self.pos, 1)
            self.head_pos2d = pm.world_to_screen(view_matrix, self.bone_pos(6), 1)
        except:
            return False
        return True

class CS2Esp:
    def __init__(self):
        self.proc = pm.open_process("cs2.exe")
        self.mod = pm.get_module(self.proc, "client.dll")["base"]
        
        self.current_tab = "Visual"
        self.entities = []
        self.local_player = None  
        self.old_punch = {"x": 0, "y": 0}
        self.rcs_bullet = 0
        self.rcs_scale = {"x": 2.0, "y": 2.0}
        self.rcs_config = {
            'intensity': 1.0,
            'recovery_time': 0.3,
            'max_shots': 30,
            'vertical_scale': 1.0,
            'horizontal_scale': 0.0,
            'smoothing': 1.0,
        }
        
    menu_position = {"x": 500, "y": 500}  
    is_dragging = False 
    drag_offset = {"x": 0, "y": 0}  
    
    from offsets import BONE_CONNECTIONS, BONE_POSITIONS, Weapons, Grenades, Npc
    show_menu = False
    snapline = False
    box = False
    info = False
    name = False
    shadow = False
    draw_reticle = False
    health = False
    triggerbot_active = False
    skeleton = False
    deathmatch = False
    rcsenable = False
    noteam = False
    spectatorlist = False
    corner = False
    
    
    def it_entities(self):
        ent_list = pm.r_int64(self.proc, self.mod + dwEntityList)
        local = pm.r_int64(self.proc, self.mod + dwLocalPlayerController)
        
        for i in range(1, 65):
            try:
                entry_ptr = pm.r_int64(self.proc, ent_list + (8 * (i & 0x7FFF) >> 9) + 16)
                controller_ptr = pm.r_int64(self.proc, entry_ptr + 120 * (i & 0x1FF))
                if controller_ptr == local:
                    continue

                controller_pawn_ptr = pm.r_int64(self.proc, controller_ptr + m_hPlayerPawn)
                list_entry_ptr = pm.r_int64(self.proc, ent_list + 0x8 * ((controller_pawn_ptr & 0x7FFF) >> 9) + 16)
                pawn_ptr = pm.r_int64(self.proc, list_entry_ptr + 120 * (controller_pawn_ptr & 0x1FF))
            except:
                continue

            entity = Entity(controller_ptr, pawn_ptr, self.proc)
            
            
            if controller_ptr == local:
                self.local_player = entity  
            
            yield entity

    def run(self):
        pm.overlay_init("Counter-Strike 2", fps=144)
        
        player = pm.r_uint64(self.proc, self.mod + dwLocalPlayerPawn)
        playerTeam = pm.r_int(self.proc,player + m_iTeamNum)
        
        while pm.overlay_loop():
            view_matrix = pm.r_floats(self.proc, self.mod + dwViewMatrix, 16)
            
            if pm.key_pressed(0x2D):
                self.show_menu = not self.show_menu
                pm.toggle_mouse()
                time.sleep(0.2)

            if self.show_menu:
                self.menushow()

            if self.triggerbot_active:
                self.trigger()
            
            if self.rcsenable:   
                self.rcs()
                time.sleep(0.001)
            
            if self.noteam == False:
                for ent in self.it_entities():
                    if ent.wts(view_matrix) and ent.health > 0 and not ent.dormant and ent.team:
                        color = Colors.cyan if ent.team != 2 else Colors.purple
                        head = ent.pos2d["y"] - ent.head_pos2d["y"]
                        width = head / 2
                        center = width / 2 
                        
                        if self.skeleton:
                        
                            skeleton_color = pm.get_color('yellow')
                            for bone_start, bone_end in self.BONE_CONNECTIONS:
                                start_pos = ent.bone_pos(bone_start)
                                end_pos = ent.bone_pos(bone_end)

                                try:
                                    start_pos_screen = pm.world_to_screen(view_matrix, start_pos, 1)
                                    end_pos_screen = pm.world_to_screen(view_matrix, end_pos, 1)
                                except Exception as e:
                                    continue

                                if start_pos_screen and end_pos_screen:
                                    start_x, start_y = start_pos_screen["x"], start_pos_screen["y"]
                                    end_x, end_y = end_pos_screen["x"], end_pos_screen["y"]

                                    pm.draw_line(start_x, start_y, end_x, end_y, skeleton_color)
                        
                        if self.snapline:
                            pm.draw_line(
                                pm.get_screen_width() / 2,
                                1,
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2,
                                Colors.black,
                                3
                            )
                            pm.draw_line(
                                pm.get_screen_width() / 2,
                                1,
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2,
                                Colors.white,
                            )

                        
                        if self.shadow:
                            pm.draw_rectangle(
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2,
                                width,
                                head + center / 2,
                                Colors.grey,
                            )

                        if self.box:
                            pm.draw_rectangle_lines(
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2,
                                width,
                                head + center / 2,
                                color,
                                1.2,
                            )
                        
                        if self.corner:
                            corner_length = 10  
                            thickness = 2       

                            pm.draw_line(
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2,
                                ent.head_pos2d["x"] - center + corner_length,
                                ent.head_pos2d["y"] - center / 2,
                                color,
                                thickness
                            )
                            pm.draw_line(
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2,
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2 + corner_length,
                                color,
                                thickness
                            )

                            
                            pm.draw_line(
                                ent.head_pos2d["x"] - center + width,
                                ent.head_pos2d["y"] - center / 2,
                                ent.head_pos2d["x"] - center + width - corner_length,
                                ent.head_pos2d["y"] - center / 2,
                                color,
                                thickness
                            )
                            pm.draw_line(
                                ent.head_pos2d["x"] - center + width,
                                ent.head_pos2d["y"] - center / 2,
                                ent.head_pos2d["x"] - center + width,
                                ent.head_pos2d["y"] - center / 2 + corner_length,
                                color,
                                thickness
                            )

                            
                            pm.draw_line(
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2,
                                ent.head_pos2d["x"] - center + corner_length,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2,
                                color,
                                thickness
                            )
                            pm.draw_line(
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2,
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2 - corner_length,
                                color,
                                thickness
                            )

                            
                            pm.draw_line(
                                ent.head_pos2d["x"] - center + width,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2,
                                ent.head_pos2d["x"] - center + width - corner_length,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2,
                                color,
                                thickness
                            )
                            pm.draw_line(
                                ent.head_pos2d["x"] - center + width,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2,
                                ent.head_pos2d["x"] - center + width,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2 - corner_length,
                                color,
                                thickness
                            )
                        
                        bar_thickness = 3  
                        bar_length = head  
                        bar_offset = 5  

                        if self.health and ent.health > 0:
                            health_percentage = ent.health / 100

                            health_bar_height = bar_length * health_percentage
                            health_bar_y = ent.head_pos2d["y"] - center / 2 + (bar_length - health_bar_height)

                            pm.draw_rectangle(
                                ent.head_pos2d["x"] - center - bar_offset - bar_thickness,
                                health_bar_y,
                                bar_thickness,
                                health_bar_height,
                                Colors.green
                            )
                        
                        if self.name:
                            txt = f"{ent.name}"
                            font_size = 12  
                            name_y = ent.head_pos2d["y"] - center / 2 - 15  
                            pm.draw_text(
                                txt,
                                ent.head_pos2d["x"] - pm.measure_text(txt, font_size) // 2,  
                                name_y,
                                font_size,
                                Colors.white,
                            )

                        if self.info:
                            txt = f"h:{ent.health}% a:{ent.armor}%"
                            pm.draw_text(
                                txt,
                                ent.head_pos2d["x"] - pm.measure_text(txt, 12) // 2,
                                ent.pos2d["y"],
                                15,
                                Colors.white,
                            )
                        
                        
            else:
                playerTeam = pm.r_int(self.proc,player + m_iTeamNum)
                for ent in self.it_entities():
                    if ent.wts(view_matrix) and ent.health > 0 and not ent.dormant and ent.team != playerTeam:
                        color = Colors.cyan if ent.team != 2 else Colors.purple
                        head = ent.pos2d["y"] - ent.head_pos2d["y"]
                        width = head / 2
                        center = width / 2
                        
                        if self.skeleton:
                        
                            skeleton_color = pm.get_color('yellow')
                            for bone_start, bone_end in self.BONE_CONNECTIONS:
                                start_pos = ent.bone_pos(bone_start)
                                end_pos = ent.bone_pos(bone_end)

                                try:
                                    start_pos_screen = pm.world_to_screen(view_matrix, start_pos, 1)
                                    end_pos_screen = pm.world_to_screen(view_matrix, end_pos, 1)
                                except Exception as e:
                                    continue

                                if start_pos_screen and end_pos_screen:
                                    start_x, start_y = start_pos_screen["x"], start_pos_screen["y"]
                                    end_x, end_y = end_pos_screen["x"], end_pos_screen["y"]

                                    pm.draw_line(start_x, start_y, end_x, end_y, skeleton_color)
                        
                        if self.snapline:
                            pm.draw_line(
                                pm.get_screen_width() / 2,
                                1,
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2,
                                Colors.black,
                                3
                            )
                            pm.draw_line(
                                pm.get_screen_width() / 2,
                                1,
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2,
                                Colors.white,
                            )

                        
                        if self.shadow:
                            pm.draw_rectangle(
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2,
                                width,
                                head + center / 2,
                                Colors.grey,
                            )

                        if self.box:
                            pm.draw_rectangle_lines(
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2,
                                width,
                                head + center / 2,
                                color,
                                1.2,
                            )

                        if self.corner:
                            corner_length = 10  
                            thickness = 2       

                            pm.draw_line(
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2,
                                ent.head_pos2d["x"] - center + corner_length,
                                ent.head_pos2d["y"] - center / 2,
                                color,
                                thickness
                            )
                            pm.draw_line(
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2,
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2 + corner_length,
                                color,
                                thickness
                            )

                            
                            pm.draw_line(
                                ent.head_pos2d["x"] - center + width,
                                ent.head_pos2d["y"] - center / 2,
                                ent.head_pos2d["x"] - center + width - corner_length,
                                ent.head_pos2d["y"] - center / 2,
                                color,
                                thickness
                            )
                            pm.draw_line(
                                ent.head_pos2d["x"] - center + width,
                                ent.head_pos2d["y"] - center / 2,
                                ent.head_pos2d["x"] - center + width,
                                ent.head_pos2d["y"] - center / 2 + corner_length,
                                color,
                                thickness
                            )

                            
                            pm.draw_line(
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2,
                                ent.head_pos2d["x"] - center + corner_length,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2,
                                color,
                                thickness
                            )
                            pm.draw_line(
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2,
                                ent.head_pos2d["x"] - center,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2 - corner_length,
                                color,
                                thickness
                            )

                            
                            pm.draw_line(
                                ent.head_pos2d["x"] - center + width,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2,
                                ent.head_pos2d["x"] - center + width - corner_length,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2,
                                color,
                                thickness
                            )
                            pm.draw_line(
                                ent.head_pos2d["x"] - center + width,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2,
                                ent.head_pos2d["x"] - center + width,
                                ent.head_pos2d["y"] - center / 2 + head + center / 2 - corner_length,
                                color,
                                thickness
                            )
                        
                        bar_thickness = 3  
                        bar_length = head  
                        bar_offset = 5 
                        
                        if self.health and ent.health > 0:
                            health_percentage = ent.health / 100

                            health_bar_height = bar_length * health_percentage
                            health_bar_y = ent.head_pos2d["y"] - center / 2 + (bar_length - health_bar_height)

                            pm.draw_rectangle(
                                ent.head_pos2d["x"] - center - bar_offset - bar_thickness,
                                health_bar_y,
                                bar_thickness,
                                health_bar_height,
                                Colors.green
                            )
                        
                        if self.name:
                            txt = f"{ent.name}"
                            font_size = 12  
                            name_y = ent.head_pos2d["y"] - center / 2 - 15  
                            pm.draw_text(
                                txt,
                                ent.head_pos2d["x"] - pm.measure_text(txt, font_size) // 2,  
                                name_y,
                                font_size,
                                Colors.white,
                            )
      
                        if self.info:
                            txt = f"h:{ent.health}% a:{ent.armor}%"
                            pm.draw_text(
                                txt,
                                ent.head_pos2d["x"] - pm.measure_text(txt, 12) // 2,
                                ent.pos2d["y"],
                                15,
                                Colors.white,
                            )
                            
                
            pm.end_drawing()

    def menushow(self):
        menu_width, menu_height = 400, 300
        menu_x, menu_y = self.menu_position["x"], self.menu_position["y"]

        pm.draw_rectangle(0, 0, pm.get_screen_width(), pm.get_screen_height(), pm.fade_color(Colors.black, 0.7))
 
        mouse_x, mouse_y = pm.mouse_position()
        if pm.mouse_down("left"):
            if not self.is_dragging:
                
                if menu_x <= mouse_x <= menu_x + menu_width and menu_y <= mouse_y <= menu_y + 30:
                    self.is_dragging = True
                    self.drag_offset["x"] = mouse_x - menu_x
                    self.drag_offset["y"] = mouse_y - menu_y
        elif self.is_dragging:
            
            self.is_dragging = False
        
        if self.is_dragging:
            self.menu_position["x"] = mouse_x - self.drag_offset["x"]
            self.menu_position["y"] = mouse_y - self.drag_offset["y"]

        pm.gui_window_box(posX=menu_x, posY=menu_y, width=menu_width, height=menu_height, title="Sara ESP")

        if pm.gui_button(menu_x + 10, menu_y + 20, 80, 30, "Visual"):
            self.current_tab = "Visual"
        if pm.gui_button(menu_x + 100, menu_y + 20, 80, 30, "Aim"):
            self.current_tab = "Aim"
        if pm.gui_button(menu_x + 190, menu_y + 20, 80, 30, "Misc"):  
            self.current_tab = "Misc"
        
        if self.current_tab == "Visual":
            self.box = pm.gui_check_box(posX=menu_x + 20, posY=menu_y + 60, width=20, height=20, text="Box", checked=self.box)
            self.corner = pm.gui_check_box(posX=menu_x + 20, posY=menu_y + 90, width=20, height=20, text="Corner Box", checked=self.corner)
            self.skeleton = pm.gui_check_box(posX=menu_x + 20, posY=menu_y + 120, width=20, height=20, text="Skeleton", checked=self.skeleton)
            self.shadow = pm.gui_check_box(posX=menu_x + 20, posY=menu_y + 150, width=20, height=20, text="Shadow", checked=self.shadow)
            
            self.snapline = pm.gui_check_box(posX=menu_x + 200, posY=menu_y + 60, width=20, height=20, text="Line", checked=self.snapline)
            self.name = pm.gui_check_box(posX=menu_x + 200, posY=menu_y + 90, width=20, height=20, text="Name", checked=self.name)
            self.info = pm.gui_check_box(posX=menu_x + 200, posY=menu_y +120, width=20, height=20, text="Info", checked=self.info)
            self.health = pm.gui_check_box(posX=menu_x + 200, posY=menu_y + 150, width=20, height=20, text="Health", checked=self.health)
            self.noteam = pm.gui_check_box(posX=menu_x + 200, posY=menu_y + 180, width=20, height=20, text="Ignore Team", checked=self.noteam)

        elif self.current_tab == "Aim":
            self.rcsenable = pm.gui_check_box(posX=menu_x + 20, posY=menu_y + 60, width=20, height=20, text="Recoil Control", checked=self.rcsenable)
            self.triggerbot_active = pm.gui_check_box(posX=menu_x + 20, posY=menu_y + 90, width=20, height=20, text="Triggerbot", checked=self.triggerbot_active)
            self.deathmatch = pm.gui_check_box(posX=menu_x + 20, posY=menu_y + 120, width=20, height=20, text="Deathmatch", checked=self.deathmatch)
        
        elif self.current_tab == "Misc":  
            self.spectatorlist = pm.gui_check_box(posX=menu_x + 20, posY=menu_y + 60, width=20, height=20, text="Show Spectator List", checked=self.spectatorlist)
           
            
    def Shoot(self):
        time.sleep(uniform(0.01, 0.03))
        pm.mouse_down(button='left')
        time.sleep(uniform(0.01, 0.05))
        pm.mouse_up(button='left')
        
    def trigger(self):
        player = pm.r_uint64(self.proc, self.mod + dwLocalPlayerPawn)
        entityId = pm.r_int(self.proc, player + m_iIDEntIndex)
        if entityId > 0:
            entList = pm.r_uint64(self.proc, self.mod + dwEntityList)
            entEntry = pm.r_uint64(self.proc,entList + 0x8 * (entityId >> 9) + 0x10)
            entity = pm.r_uint64(self.proc,entEntry + 120 * (entityId & 0x1FF))
            entityTeam = pm.r_int(self.proc,entity + m_iTeamNum)
            playerTeam = pm.r_int(self.proc,player + m_iTeamNum)
            entityHp = pm.r_int(self.proc,entity + m_iHealth)

            if self.deathmatch:
                if entityHp > 0:
                    self.Shoot()
            
            if (entityTeam != playerTeam) and entityHp > 0 and self.deathmatch == False:
                self.Shoot()
    
    def is_shooting(self):
        return win32api.GetKeyState(0x01) < 0   
          
    def rcs(self):
        player = pm.r_int64(self.proc, self.mod + dwLocalPlayerPawn)
        
        def get_shots_fired(local_player):
            return pm.r_int(self.proc, local_player + m_iShotsFired)
    
        def get_aim_punch(local_player):
            return pm.r_vec2(self.proc, local_player + m_aimPunchAngle)
    
        if not player:
            return
            
        shots_fired = get_shots_fired(player)
        if shots_fired <= self.rcs_bullet:
            self.old_punch = {"x": 0, "y": 0}
            return
            
        aim_punch = get_aim_punch(player)
            
        sensitivity = 3.0
        delta = {
            "x": (aim_punch["x"] - self.old_punch["x"]) * 2.0,
            "y": (aim_punch["y"] - self.old_punch["y"]) * 2.0
        }
            
        mouse_x = int(delta["y"] / (sensitivity * 0.11) * self.rcs_scale["x"] * self.rcs_config['intensity'])
        mouse_y = int(delta["x"] / (sensitivity * 0.11) * self.rcs_scale["y"] * self.rcs_config['intensity'])
            
        if self.is_shooting():
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, mouse_x, -mouse_y, 0, 0)
            
        self.old_punch = aim_punch
    
    def get_weapon_type(item_identifier):
        it = Weapons.get(item_identifier)
        if it is not None:
            return it
        return "<unknown>"

    def get_projectile_type(item_identifier):
        it = Grenades.get(item_identifier)
        if it is not None:
            return it
        return "<unknown>"

    def get_entity_type(item_identifier):
        it = Npc.get(item_identifier)
        if it is not None:
            return it
        return "<unknown>"
            
    
                
