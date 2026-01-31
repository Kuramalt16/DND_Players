import math

import Functions as F, Variables as V, Settings as S

import pygame as pg

def Select_condition(screen, clock):
    running = True
    text_size = 30
    pressed = -1
    button_dict = {}

    # for y in range(0, int(len(list(V.Conditions.keys()))/4)):
    #     for x in range(0, 4):
    #         button_dict[(x, y)] = [list(V.Conditions.keys())[x * (y+1)], "background", "background", "rect-place-holder", "black"]

    conditions = V.Conditions.copy()
    extra_conditions = {
        "Exhaustion lv1": {"Description": ""},
        "Exhaustion lv2": {"Description": ""},
        "Exhaustion lv3": {"Description": ""},
        "Exhaustion lv4": {"Description": ""},
        "Exhaustion lv5": {"Description": ""},
        "Exhaustion lv6": {"Description": ""}
                        }
    conditions.update(extra_conditions)
    del conditions["Exhaustion"]

    for i, (key, value) in enumerate(conditions.items()):
        color = "black"

        x = i % 4  # x cycles every 4 entries (0, 1, 2, 3)
        y = i // 4  # y increments by 1 after every 4 entries
        if key in ["Frightened", "Petrified", "Stunned"]:
            color = "White"
        button_dict[(x, y)] = [key, key, "Conditions", "rect-place-holder", color]


    while running:
        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.15
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Back")
        x_pos = []
        y_pos = []
        start_x = S.SCREEN_WIDTH * 0.01
        start_y = S.SCREEN_HEIGHT * 0.01
        step_y = 0
        for y in range(0, int(len(button_dict) / 4) + 1):  # Loop through y (rows)
            y_pos.append(start_y + step_y)
            step_y += button_height * 1.1  # Increment y step

            step_x = 0  # Reset x step at the start of each row
            for x in range(0, 4):  # Loop through x (columns)
                x_pos.append(start_x + step_x)  # Calculate the x position
                step_x += button_width * 1.25  # Increment x step


        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)

        for event in pg.event.get():
            keys = pg.key.get_pressed()
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(mouse_pos):
                        pressed = "Back"
                        if not V.CARRY_TOO_MUCH:
                            V.Condition = ""
                            S.Background_image = "background"
                            S.Standart_color = "black"
                        for key, value in button_dict.items():
                            if value[3] == buttons[i]:
                                pressed = value[0]
                        pg.draw.rect(screen, "black", buttons[i], width=3)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed != "Back":
                        V.Condition = pressed

                        on_condition_change()

                    return

        pg.display.flip()
        clock.tick(60)

def display_condition_effects_actions(screen):
    if V.Condition in ["Charmed", "Frightened"]:
        if V.Condition == "Charmed":
            F.display_text(screen, "Can not target or harm the charmer in any way", 10, (S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.87), case="C", color="red")
        else:
            F.display_text(screen, "Roll attack rolls with disadvantage if source of fear is in sight", 10, (S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.87), case="C", color="red")
def on_condition_change():
    if V.Condition != "":
        S.Background_image = "Conditions/" + V.Condition
    else:
        S.Background_image = "background"
    text_color_change()

    if V.Condition == 'Exhaustion lv4' and V.char_max_hp_tracker == "":
        V.char_max_hp_tracker = V.character_dict[V.char_name]["Health"][1]
        V.character_dict[V.char_name]["Health"][1] = math.floor(V.character_dict[V.char_name]["Health"][1] / 2)
        if V.character_dict[V.char_name]["Health"][0] > V.character_dict[V.char_name]["Health"][1]:
            V.character_dict[V.char_name]["Health"][0] = V.character_dict[V.char_name]["Health"][1]

    elif V.Condition == "Exhaustion lv3" and V.char_max_hp_tracker != "":
        V.character_dict[V.char_name]["Health"][1] = V.char_max_hp_tracker
        V.char_max_hp_tracker = ""

def skill_conditions(screen):
    if V.Condition in ["Blinded", "Deafened"]:
        if V.Condition == "Blinded":
            extra_text = "Sight"
        else:
            extra_text = "Hearing"
        F.display_text(screen, "Fail all checks that require " + extra_text, 20, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.8), case="C")
    elif V.Condition in ["Frightened"]:
        F.display_text(screen, "If source of fear is in line of sight Ability checks have disadvantage", 20, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.8), case="C")
    elif V.Condition in ["Charmed"]:
        F.display_text(screen, "if interacting socialy with charmer roll with advantage", 20, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.8), case="C")

def text_color_change():
    """Cant use RED, Purple, Orange, silver"""
    if V.Condition in ["Charmed", "Blinded", "Deafened"]: # GOOD
        S.Standart_color = "Brown"
    elif V.Condition in ["Frightened", "Petrified", "Poisoned", "Stunned", "Exhaustion lv4", "Exhaustion lv5", "Exhaustion lv1", "Exhaustion lv6"]: # GOOD
        S.Standart_color = "White"
    elif V.Condition in ["Grappled", "Incapacitated", "Invisible", "Paralyzed", "Prone", "Restrained", "Unconscious", "Exhaustion lv2", "Exhaustion lv3"]: # GOOD
        S.Standart_color = "black"
    else:
        S.Standart_color = "black"


def exhaustion_condition_decreese():
    if "Exhaustion" in V.Condition:
        exhaustion_lv = V.Condition.replace("Exhaustion lv", "")
        exhaustion_lv = str(int(exhaustion_lv) - 1)
        if exhaustion_lv == "0":
            V.Condition = ""
        else:
            V.Condition = "Exhaustion lv" + exhaustion_lv
    on_condition_change()


def display_char_speed_conditions_applied(screen, character, pos):
    speed = int(character["Speed"])
    if V.Condition != "" and V.Condition in ["Exhaustion lv2", "Exhaustion lv3", "Exhaustion lv4", "Exhaustion lv5", "Exhaustion lv6", "Restrained", "Grappled", "Unconscious", "Stunned", "Petrified", "Paralyzed", "Encumbrance", "Over Encumbered", "Heavily Encumbered"]:
        if V.Condition in ["Exhaustion lv5", "Exhaustion lv6", "Restrained", "Grappled", "Unconscious", "Stunned", "Petrified", "Paralyzed", "Over Encumbered"]:
            """If exhaustion level 5 or 6 or Restrained, Grappled"""
            speed = 0
        elif V.Condition in ["Encumbrance"]:
            speed = speed - 10
        elif V.Condition in ["Heavily Encumbered"]:
            speed = speed - 20
        else:
            """If condition is above exhaustion level 2 but bellow level 5"""
            speed = math.floor(speed/2)
    if V.EQUIPED_CHAR_ITEMS != {} and V.EQUIPED_CHAR_ITEMS.get("Armour") != '' and V.EQUIPED_CHAR_ITEMS.get("Armour") != None:
        if V.EQUIPED_CHAR_ITEMS.get("Armour") in ["Splint", "Plate"] and int(character["Ability_Scores"].split(",")[0]) < 15:
            speed -= 10
        elif V.EQUIPED_CHAR_ITEMS.get("Armour") in ["Chain mail"] and int(character["Ability_Scores"].split(",")[0]) < 13:
            speed -= 10
    if speed < 0:
        speed = 0


    F.display_text(screen, "Speed: " + str(speed), 20, pos)

def saving_throw_conditions(dtwenty, pressed):
    if V.Condition in ["Unconscious", "Stunned", "Petrified", "Paralyzed"] and pressed[0].split(":")[0] in ["STR","DEX"]:
        """imidiately fail STR and DEX rolls if stunned or unconcious"""
        return 1
    return dtwenty

def display_resistances(screen, character, r, y):
    if character["Resistance"] == None:
        character["Resistance"] = ""
    if V.Condition in ["Petrified"]:
        F.display_text(screen, character["Resistance"] + " All Damage Types", 20, (r.x + r.w, y), color="Dark red")
    elif V.Condition in ["Invisible"]:
        F.display_text(screen, character["Resistance"] + " Disadvantage All Attack rolls", 20, (r.x + r.w, y), color="Dark red")
    elif V.Condition in ["Prone"]:
        F.display_text(screen, character["Resistance"] + " Disadvantage ranged Attack rolls", 20, (r.x + r.w, y), color="Dark red")
    elif V.Special_Flags.get("Rage") != None:
        F.display_text(screen, character["Resistance"] + " Bludgeoning, Piercing, Slashing", 20, (r.x + r.w, y), color="Dark red")
    else:
        F.display_text(screen, character["Resistance"], 20, (r.x + r.w, y), color="Dark red")