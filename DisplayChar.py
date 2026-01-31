import math, json, threading, time
import os.path
import pygame as pg, Settings as S, Variables as V, Functions as F, random, Actions as A, conditions as C, Skills as sk, Special_Needs as special, Items as I, Spells as Sp

import operator


def selected_char_display(selected, screen, clock):
    character = V.character_dict[selected]
    character["Name"] = selected
    add_hp_after_ShortRest(screen, character, clock)
    special.handle_special_flag_needs(screen, clock, character)
    running = True
    selected_entry = -1
    txt_dict = {"Heal": ["", 0]}
    timer = 10
    text_size = 30
    pressed = -1
    button_dict = {
        (3, 0): ["Update Hp", "background", "background", "rect-place-holder", "black"],
        (0, 1): ["Spells", "background", "background", "rect-place-holder", "black"],
        (1, 1): ["Skills", "background", "background", "rect-place-holder", "black"],
        (2, 0): ["Level Up", "background", "background", "rect-place-holder", "dark gray"],
        (2, 1): ["Actions", "background", "background", "rect-place-holder", "black"],
        (1, 0): ["Conditions", "background", "background", "rect-place-holder", "black"],
    }
    got_damaged = -1
    while running:
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        # displayed_slots = F.display_spell_slots(selected, screen)
        x = S.SCREEN_WIDTH * 0.4
        y = S.SCREEN_HEIGHT * 0.5
        w = S.SCREEN_WIDTH * 0.25
        h = S.SCREEN_HEIGHT * 0.04
        button_width = S.SCREEN_WIDTH / 5
        button_height = S.SCREEN_HEIGHT / 20
        enter_hp = F.add_entry_to_list((x + S.SCREEN_WIDTH * 0.3, S.SCREEN_HEIGHT * 0.44, w, h), "hp", screen, "", 20, (x - S.SCREEN_WIDTH * 0.2, y))

        display_char(character, screen)

        buttons = F.display_back_button(screen, "Back")
        x_pos = [S.SCREEN_WIDTH * 0.02, S.SCREEN_WIDTH * 0.27, S.SCREEN_WIDTH * 0.52, S.SCREEN_WIDTH * 0.77]
        y_pos = [S.SCREEN_HEIGHT * 0.8, S.SCREEN_HEIGHT * 0.9]

        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)
        if got_damaged != -1:
            # display_reactions(screen)
            got_damaged -= 1

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
                        for key, value in button_dict.items():
                            if value[3] == buttons[i]:
                                pressed = value[0]
                        # pressed = i
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                if enter_hp.collidepoint(mouse_pos):
                    selected_entry = 0

            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == "Back":
                        """Back button pressed"""
                        running = False
                    elif pressed == "Update Hp":
                        txt_dict, selected_entry, got_damaged = update_char_hp_based_on_entry(character, txt_dict, selected_entry, screen, clock)
                    elif pressed == "Spells":
                        if V.Condition not in ["Incapacitated", "Unconscious", "Stunned", "Petrified", "Paralyzed", "Over Encumbered"]:
                            Sp.display_char_spells(screen, clock)
                    elif pressed == "Skills":
                        sk.display_char_skills(character, screen, clock)
                    elif pressed == "Level Up":
                        F.print_debug("Levelup", debug="WARNING")
                    elif pressed == "Actions":
                        if V.Condition not in ["Incapacitated", "Unconscious", "Stunned", "Petrified", "Paralyzed", "Over Encumbered"]:
                            A.Initialize_actions(screen, clock)
                            if V.Condition == 'Exhaustion lv6':
                                return
                    elif pressed == "Conditions":
                        C.Select_condition(screen, clock)
                        if V.Condition == 'Exhaustion lv6':
                            return
                    pressed = -1

            elif event.type == pg.TEXTINPUT and selected_entry != -1:
                property = list(txt_dict.keys())[selected_entry]
                txt_dict[property][0] += event.text

            # elif event.type == pg.KEYDOWN:
            if keys[pg.K_BACKSPACE] and selected_entry != -1 and not keys[pg.K_LCTRL]:
                property = list(txt_dict.keys())[selected_entry]
                txt_dict[property][0] = txt_dict[property][0][:-1]
            elif keys[pg.K_BACKSPACE] and selected_entry != -1 and keys[pg.K_LCTRL]:
                property = list(txt_dict.keys())[selected_entry]
                text_list = txt_dict[property][0].split(", ")[:-1]
                txt_dict[property][0] = ""
                for text in text_list:
                    txt_dict[property][0] += text + ", "
                txt_dict[property][0] = txt_dict[property][0][:-2]
            elif keys[pg.K_RETURN] or keys[pg.K_KP_ENTER]:
                txt_dict, selected_entry, got_damaged = update_char_hp_based_on_entry(character, txt_dict, selected_entry, screen, clock)

        F.update_text(txt_dict, [enter_hp], screen)

        if selected_entry != -1:
            F.flash_marker(selected_entry, [enter_hp], screen, timer, txt_dict)

        pg.display.flip()
        clock.tick(60)
        timer = F.reset_timer(timer)


def add_hp_after_ShortRest(screen, character, clock):
    if ("hp", True) in V.short_rest:
        running = True
        pressed = -1
        hp_to_add = 0
        while running:
            x = S.SCREEN_WIDTH / (10)
            y = S.SCREEN_HEIGHT * 0.1
            w = S.SCREEN_WIDTH * 0.1
            h = S.SCREEN_HEIGHT * 0.1
            r = pg.Rect(0, y, 0, 0)
            F.add_image_to_screen(screen, "ShortRest", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Conditions")
            pg.draw.rect(screen, "red", (S.SCREEN_WIDTH * 0.1, S.SCREEN_HEIGHT * 0.05, S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.03))
            remainder = V.character_dict[V.char_name]["Health"][0] / V.character_dict[V.char_name]["Health"][1]
            pg.draw.rect(screen, "green", (S.SCREEN_WIDTH * 0.1, S.SCREEN_HEIGHT * 0.05, S.SCREEN_WIDTH * 0.8 * remainder, S.SCREEN_HEIGHT * 0.03))
            pg.draw.rect(screen, "white", (S.SCREEN_WIDTH * 0.1, S.SCREEN_HEIGHT * 0.05, S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.03), width=1)


            buttons = F.display_back_button(screen, "Back")
            for d in range(1, len(V.BASE_HIT_DICE) +1):
                r = pg.Rect(x + r.x, r.y, w, h)
                di = V.BASE_HIT_DICE[d - 1]
                folder_path =S.local_path + "\\images\\Background\\Roling_Dice\\" + di
                image = pg.image.load(folder_path + ".png")
                image = pg.transform.scale(image, (w, r.h))
                screen.blit(image, (r.x, r.y))
                buttons.append(r)
                if r.x + r.w > S.SCREEN_WIDTH - x:
                    r.x = 0
                    r.y += y + h * 0.5
            for event in pg.event.get():
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
                            pressed = i
                            pg.draw.rect(screen, "black", buttons[i], width=3)
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    mouse_pos = pg.mouse.get_pos()
                    if pressed != -1 and buttons[pressed].collidepoint(mouse_pos):
                        if pressed == 0:
                            running = False
                            if ("hp", True) in V.short_rest:
                                a = V.short_rest.index(("hp", True))
                                V.short_rest.pop(a)
                        else:
                            dice = V.BASE_HIT_DICE.pop()
                            buttons.pop()
                            dtwenty = random.randint(1, int(dice))
                            F.Roll_3d_dice(screen, clock, "D" + str(dice), str(dtwenty),(S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.5))
                            F.add_to_roll_history(dtwenty, str(dtwenty + int(V.score_modifiers["CON"])), "Hit Die")

                            character["Health"] = [int(character["Health"][0]) + int(dtwenty + V.score_modifiers["CON"]), character["Health"][1]]
                            if int(character["Health"][0]) > int(character["Health"][1]):
                                character["Health"] = [character["Health"][1], character["Health"][1]]

            pg.display.flip()
            clock.tick(60)


def display_char(character, screen):
    V.SPEED_OFFSET = 0
    char_name = character["Name"]
    race = character["Race"]
    char_class = character["Class"]
    sub_class = ""
    if character.get("SubClass") != None:
        sub_class = character["SubClass"]
    languages = character["Languages"]
    size = character["Size"]
    if V.SECRETS.get(character["Name"]) != None:
        if V.SECRETS[character["Name"]]["Name"] == 1:
            char_name = "UNKNOWN"
        if V.SECRETS[character["Name"]]["Race"]:
            race = "UNKNOWN"
            size = "UNKNOWN"
            languages = "UNKNOWN"
        if V.SECRETS[character["Name"]]["Class"]:
            char_class = "UNKNOWN, UNKNOWN"
            if sub_class != "":
                sub_class = "UNKNOWN,UNKNOWN"
    rect = F.add_image_to_screen(screen, char_name, (S.SCREEN_WIDTH * 0.7, S.SCREEN_HEIGHT * 0.02, S.SCREEN_WIDTH * 0.25, S.SCREEN_HEIGHT * 0.4), "Player")
    if rect == None:
        rect = F.add_image_to_screen(screen, V.character_dict[V.char_name]["Race"], (S.SCREEN_WIDTH * 0.7, S.SCREEN_HEIGHT * 0.02, S.SCREEN_WIDTH * 0.25, S.SCREEN_HEIGHT * 0.4), "Race")
    # health_bar_rect = pg.Rect(rect.x, rect.y + rect.h + S.SCREEN_HEIGHT * 0.02, rect.w, S.SCREEN_HEIGHT / 50)

    remainder = round(((character["Health"][0] / character["Health"][1]) - 1) * -1, 3)
    health_bar_x = rect.x
    health_bar_w = rect.w
    health_bar_y = rect.y + rect.h
    health_bar_h = 0
    health_bar_h_final = rect.h
    pg.draw.rect(screen, "red", pg.Rect(health_bar_x, health_bar_y - (health_bar_h_final * remainder), health_bar_w, health_bar_h + (health_bar_h_final * remainder)))

    if remainder == 1:
        F.display_text(screen, "DEAD", 30, (rect.x + rect.w / 2, rect.y + rect.h / 2), case="C")



    F.display_text(screen, "Name: " + char_name, 20, (20, 20))

    r = F.display_text(screen, "Race: " + race, 20, (20, 60))
    F.display_text(screen, "Size: " + size, 20, (10 + r.x + r.w, 60))

    if len(char_class.split(", ")) == 2:
        F.display_text(screen, "Class: " + char_class.split(", ")[0] + "|" + char_class.split(", ")[1], 20, (20, 100))
    else:
        F.display_text(screen, "Class: " + char_class.split(", ")[0], 20, (20, 100))
    if character.get("SubClass") != None and character["SubClass"] != "":
        if "," in character["SubClass"]:
            F.display_text(screen, "Sub-Class: " + sub_class.split(",")[0] + "|" + sub_class.split(",")[1], 20, (20, 140))
        else:
            F.display_text(screen, "Sub-Class: " + sub_class, 20, (20, 140))
    # F.display_text(screen, "Experience: " + character["Experience"], 20, (20, 140))
    if len(character["Level"]) == 1:
        F.display_text(screen, "Level: " + str(character["Level"][0]), 20, (20, 180))
    else:
        F.display_text(screen, "Level: " + str(character["Level"][0]) + "|" + str(character["Level"][2]), 20, (20, 180))

    r = F.display_text(screen, "HP: " + str(character["Health"]), 20, (20, 220), color="red")
    if character.get("Temp_hp") != None:
        F.display_text(screen, "Temp HP: " + str(character["Temp_hp"]), 20, (r.x + r.w, 220), color="red")

    r = F.display_text(screen, "Str: " + character["Ability_Scores"].split(",")[0] + " |", 20, (20, 260))
    r = F.display_text(screen, "Dex: " + character["Ability_Scores"].split(",")[1] + " |", 20, (r.x + r.w, 260))
    r = F.display_text(screen, "Con: " + character["Ability_Scores"].split(",")[2] + " |", 20, (r.x + r.w, 260))
    r = F.display_text(screen, "Int: " + character["Ability_Scores"].split(",")[3] + " |", 20, (r.x + r.w, 260))
    r = F.display_text(screen, "Wis: " + character["Ability_Scores"].split(",")[4] + " |", 20, (r.x + r.w, 260))
    F.display_text(screen, "Cha: " + character["Ability_Scores"].split(",")[5], 20, (r.x + r.w, 260))

    F.display_text(screen, "Gold: " + str(character["Gold"] + " Gp"), 20, (20, 300))

    F.display_text(screen, "Background: " + character["Background"], 20, (20, 340))

    F.display_text(screen, "Alignment: " + character["Alignment"], 20, (20, 380))

    special.handle_unarmored_defense(character)
    I.handle_armor_effects(character)

    char_AC = character["AC"]
    if V.spell_effects.get("Char") != None and V.spell_effects["Char"].get("AC") != None:
        char_AC = str(V.spell_effects["Char"]["AC"])
    F.display_text(screen, "Armor Class: " + str(char_AC), 20, (S.SCREEN_WIDTH * 0.7, S.SCREEN_HEIGHT * 0.50), color="red")


    F.display_text(screen, "Spell Save DC: " + str(V.Spell_save_DC), 20, (S.SCREEN_WIDTH * 0.7, S.SCREEN_HEIGHT * 0.54), color="purple")

    special.handle_fast_movement(character)

    C.display_char_speed_conditions_applied(screen, character, (20, 420))

    r = F.display_text(screen, "Immunities: ", 20, (20, 460))

    if "Disease" not in character["Immunity"] and "Divine Health" in character["Code"]:
        immunities = character["Immunity"].split(" ")
        immunities.append("Disease")
        character["Immunity"] = " ".join(immunities)
    if V.Condition in ["Petrified"]:
        F.display_text(screen, character["Immunity"] + " Poison Disease", 20, (r.x + r.w, 460), color="Green")
    else:
        F.display_text(screen, character["Immunity"], 20, (r.x + r.w, 460), color="Green")

    r = F.display_text(screen, "Resistances: ", 20, (20, 500))

    C.display_resistances(screen, character, r, 500)


    r = F.display_text(screen, "Vulnerabilities: ", 20, (20, 540))
    if V.Condition in ["Prone"]:
        F.display_text(screen, character["Vulnerabilities"] + " Advantage for Close range attack rolls", 20, (r.x + r.w, 540), color="Purple")
    elif V.Condition in ["Stunned", "Restrained", "Petrified", "Blinded", "Heavily Encumbered"]:
        F.display_text(screen, character["Vulnerabilities"] + " Advantage for All Attack rolls", 20, (r.x + r.w, 540), color="Purple")
    elif V.Condition in ["Unconscious", "Paralyzed", "Over Encumbered"]:
        F.display_text(screen, character["Vulnerabilities"] + " Advantage for All Attack rolls Critical damage for close range attacks", 20, (r.x + r.w, 540), color="Purple")
    else:
        F.display_text(screen, character["Vulnerabilities"], 20, (r.x + r.w, 540), color="Cyan")

    F.display_text(screen, "Languages: " + ", ".join(languages.split(",")), 20, (20, 580))
    F.display_text(screen, "Proficiency Bonus: " + str(V.Proficiecy_bonus), 20, (20, 620), color="Red")
    # F.display_text(screen, "Alchemy: " + character["Alchemy"], 20, (20, 580))




def update_char_hp_based_on_entry(character, txt_dict, selected_entry, screen, clock, temp_hp=True):
    hp = ""
    Got_Damaged = -1
    property = list(txt_dict.keys())[selected_entry]
    text = txt_dict[property][0]
    for char in text:
        if char.isdigit() or char in [".", ",", "-"]:
            hp += char
    if "." in hp:
        suffix = ""
        if "-" in hp:
            suffix = "-"
        hp = hp.split(".")
        try:
            hp = float(hp[0]) + (float(hp[1]) / 10)
        except ValueError:
            hp = 0
        if suffix == "-":
            hp = hp * -1
    elif "," in hp:
        suffix = ""
        if "-" in hp:
            suffix = "-"
        hp = hp.split(",")
        try:
            hp = float(hp[0]) + (float(hp[1]) / 10)
        except ValueError:
            hp = 0
        if suffix == "-":
            hp = hp * -1
    elif hp != "":
        try:
            hp = int(hp)
        except ValueError:
            hp = ""

    if hp != "":
        if "-" in str(hp):
            Got_Damaged = 60
            roll_and_check_concentration_keeping(screen, clock, character, hp)

        if character.get("Temp_hp") != None and "-" in str(hp) and temp_hp:
            character["Temp_hp"] += hp
            hp = 0
            if character["Temp_hp"] < 0:
                hp = character["Temp_hp"]
                del character["Temp_hp"]
        elif character.get("Temp_hp") != None and temp_hp:
            character["Temp_hp"] += hp
            hp = 0
        character["Health"] = [int(character["Health"][0]) + int(hp), int(character["Health"][1])]
        character["Health"][0] = round(character["Health"][0], 2)
        # if character["Health"][0] <= 0:
        #     character["Health"][0] = 0
        if character["Health"][0] > character["Health"][1] + 20 and temp_hp:
            character["Health"][0] = character["Health"][1]
        elif character["Health"][0] > character["Health"][1] and not temp_hp:
            character["Health"][0] = character["Health"][1]
        if character["Health"][0] > character["Health"][1] and temp_hp:
            character["Temp_hp"] = character["Health"][0] - character["Health"][1]
            character["Health"] = [character["Health"][1], character["Health"][1]]


    txt_dict[property][0] = ""
    selected_entry = -1
    return txt_dict, selected_entry, Got_Damaged



def calculate_skills(character):
    ability_score_list = character["Ability_Scores"].split(",")

    V.score_modifiers = {
        "STR": math.floor((int(ability_score_list[0]) - 10) / 2),
        "DEX": math.floor((int(ability_score_list[1]) - 10) / 2),
        "CON": math.floor((int(ability_score_list[2]) - 10) / 2),
        "INT": math.floor((int(ability_score_list[3]) - 10) / 2),
        "WIS": math.floor((int(ability_score_list[4]) - 10) / 2),
        "CHA": math.floor((int(ability_score_list[5]) - 10) / 2)
    }

    if V.character_dict[V.char_name].get("Skills") == None:
        V.character_dict[V.char_name]["Skills"] = "Acrobatics:1,Animal Handling:1,Arcana:1,Athletics:1,Deception:1,History:1,Insight:1,Intimidation:1,Investigation:1,Medicine:1,Nature:1,Perception:1,Performance:1,Persuasion:1,Religion:1,Sleight of Hand:1,Stealth:1,Survival:1"

    for key, [value, mod] in V.Skills.items():
        if V.score_modifiers.get(mod) != None:
            new_value = V.score_modifiers[mod]
            V.Skills[key] = [new_value, mod]


def get_proficiency_Bonus(class_data, character):
    """Gets proficiency bonus from the class json"""
    if character["Level"].count(",") == 0:
        V.Proficiecy_bonus = int(class_data[character["Class"]][character["Level"]]["Proficiency Bonus"][2])
    else:
        levels = character["Level"].split(",")
        class_i = 0
        for char_class in character["Class"].split(", "):
            temp_prof_bonus = int(class_data[char_class][levels[class_i]]["Proficiency Bonus"][2])
            if temp_prof_bonus > V.Proficiecy_bonus:
                V.Proficiecy_bonus = temp_prof_bonus
            class_i += 1



def check_class_features(screen, clock):
    char = V.character_dict[V.char_name]
    calculate_skills(char)
    get_proficiency_Bonus(S.class_data, char)


    if os.path.exists(S.local_path + "/Created_Players/" + V.char_name + "_config.json"):
        """Read level of char in the JSON see if it matches with DB?"""
        data = load_char_data(S.local_path + "/Created_Players/" + V.char_name + "_config.json")
        compare_JSON_DN(data, screen, clock)

    else:

        race_data = get_race_choises(char, screen, clock, data={})
        F.print_debug(race_data, debug="DEBUG")

        # race_data = {'Kobold': {'Size': [['--ADD', 'Char:Size', 'Small']], 'Speed': [['--ADD', 'Char:Speed', '30']], 'Darkvision': [['--ADD', 'Char:Darkvision', '60']], 'Languages': [['--ADD', 'Char:Languages', 'Common', 'Draconic']], 'Code': [['--CODE', 'Feature:Draconic Cry']], 'Skills': [['--ADD', "Char:Skills", 'Medicine']]}}
        # race_data = {'Changeling': {'Size': [['--ADD', 'Char:Size', 'Medium']], 'Speed': [['--ADD', 'Char:Speed', '30']], 'Languages': [['--ADD', 'Char:Languages', 'Common', 'Sylvan', 'Elvish', 'Dwarvish', 'Halfling']], 'Code': [['--CODE', 'Feature:Shapechanger']], 'Skills': [['--ADD', 'Persuasion']], 'Ability Score': [['INT', 'INT', 'INT']]}}


        data = get_player_choises(char, screen, clock, (0, 0), race_data)
        F.print_debug(data, debug="DEBUG")
        if data.get("Feat") != None:
            if data["Feat"][0] == None:
                del data["Feat"]
        # Crocus data = {'Firbolg': {'Size': [['--ADD', 'Char:Size', 'Medium']], 'Speed': [['--ADD', 'Char:Speed', '30']], 'Languages': [['--ADD', 'Char:Languages', 'Common', 'Sylvan']], 'Code': [['--CODE', 'Feature:Firbolg Magic', 'Feature:Hidden Step', 'Feature:Powerful Build', 'Feature:Speech of Beast and Leaf']], 'Ability Score': [['CHA', 'CHA', 'CHA']]}, 'Paladin': {1: {'Hit dice': [['--ADD', 'key', '1d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Armor Proficiencies': [['--ADD', 'PROFICIENCY', 'Light Armor', 'Medium Armor', 'Heavy Armor', 'Shields']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Simple', 'Martial']], 'Saving Throw Proficiencies': [['--ADD', 'PROFICIENCY', 'Saving_WIS', 'Saving_CHA']], 'Code': [['--CODE', 'Feature:Divine Sense', 'Feature:Lay on Hands']], 'Skills': ['Religion', 'Medicine']}, 2: {'Hit dice': [['--ADD', 'key', '2d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Code': [['--CODE', 'Feature:Divine Smite']], 'Primary Ability': [['--ADD', 'key', 'Charisma']], 'Spell Slots': [['--ADD', 'key', '1st:2']], 'Slot Level': [['--ADD', 'key', '1']], 'Fighting Style': ['Defense'], 'Spell': ['Compelled Duel', 'Bless', 'Cure Wounds', 'Detect Evil and Good', 'Detect Poison and Disease', 'Divine Favor', 'Heroism']}, 3: {'Hit dice': [['--ADD', 'key', '3d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Code': [['--CODE', 'Feature:Divine Health']], 'Spell Slots': [['--ADD', 'key', '1st:3']], 'Slot Level': [['--ADD', 'key', '1']], 'Sacred Oath': ['Oath of the Open Sea']}, 4: {'Hit dice': [['--ADD', 'key', '4d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Spell Slots': [['--ADD', 'key', '1st:3']], 'Slot Level': [['--ADD', 'key', '1']], 'Ability Score': ['STR', 'STR']}, 5: {'Hit dice': [['--ADD', 'key', '5d10']], 'Proficiency Bonus': [['--ADD', 'key', '3']], 'Extra Attack': [['--ADD', 'key', '1']], 'Code': [['--CODE', 'Feature:Extra Attack']], 'Spell Slots': [['--ADD', 'key', '1st:4,2nd:2']], 'Slot Level': [['--ADD', 'key', '2']]}}, 'Blood Hunter': {1: {'Hit dice': [['--ADD', 'key', '1d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Armor Proficiencies': [['--ADD', 'PROFICIENCY', 'Light Armor', 'Medium Armor', 'Shields']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Simple', 'Martial']], 'Tool Proficiencies': [['--ADD', 'PROFICIENCY', "Alchemist's supplies"]], 'Saving Throw Proficiencies': [['--ADD', 'PROFICIENCY', 'Saving_DEX', 'Saving_INT']], 'Hemocraft_die': [['--ADD', 'key', '1d4']], 'Blood Curses Known': [['--ADD', 'key', '1']], 'Code': [['--CODE', "Feature:Hunter's Bane", 'Feature:Blood Maledict']], 'Skills': ['Survival', 'Insight', 'Investigation']}, 2: {'Hit dice': [['--ADD', 'key', '2d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Code': [['--CODE', 'Feature:Crimson Rite']], 'Hemocraft_die': [['--ADD', 'key', '1d4']], 'Blood Curses Known': [['--ADD', 'key', '1']], 'Fighting Style': ['Two-Weapon Fighting'], 'Crimson Rites': ['Rite of the Storm']}, 3: {'Hemocraft_die': [['--ADD', 'key', '1d4']], 'Blood Curses Known': [['--ADD', 'key', '1']], 'Hit dice': [['--ADD', 'key', '3d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Blood Hunter Order': ['Order of the Ghostslayer']}, 4: {'Hemocraft_die': [['--ADD', 'key', '1d4']], 'Blood Curses Known': [['--ADD', 'key', '1']], 'Hit dice': [['--ADD', 'key', '4d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Ability Score': ['CON', 'INT']}, 5: {'Hit dice': [['--ADD', 'key', '5d10']], 'Proficiency Bonus': [['--ADD', 'key', '3']], 'Extra Attack': [['--ADD', 'key', '1']], 'Code': [['--CODE', 'Feature:Extra Attack']], 'Hemocraft_die': [['--ADD', 'key', '1d6']], 'Blood Curses Known': [['--ADD', 'key', '1']]}}}
        # Kalabrimbur data = {'Dwarf': {'Ability Score': [['--ADD', 'Char:Ability_Scores', 'CON', 'CON']], 'Size': [['--ADD', 'Char:Size', 'Medium']], 'Speed': [['--ADD', 'Char:Speed', '25']], 'Darkvision': [['--ADD', 'Char:Darkvision', '60']], 'Resistance': [['--ADD', 'Char:Resistance', 'Poison']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Battleaxe', 'Handaxe', 'Light hammer', 'Warhammer']], 'Languages': [['--ADD', 'Char:Languages', 'Common', 'Dwarvish']], 'Second Ability Score': [['--ADD', 'Char:Ability_Scores', 'STR', 'STR']], 'Armor Proficiencies': [['--ADD', 'PROFICIENCY', 'Light Armor', 'Medium Armor']]}, 'Fighter': {1: {'Hit dice': [['--ADD', 'key', '1d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Armor Proficiencies': [['--ADD', 'PROFICIENCY', 'Light Armor', 'Medium Armor', 'Heavy Armor', 'Shields']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Simple', 'Martial']], 'Saving Throw Proficiencies': [['--ADD', 'PROFICIENCY', 'Saving_STR', 'Saving_CON']], 'Second Wind': [['--ADD', 'key', '1d10+1']], 'Code': [['--CODE', 'Feature:Second Wind']], 'Skills': ['Animal Handling', 'History'], 'Fighting Style': ['Dueling']}, 2: {'Hit dice': [['--ADD', 'key', '2d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Action Surge': [['--ADD', 'key', '1']]}, 3: {'Hit dice': [['--ADD', 'key', '3d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Martial Archetype': ['Champion']}, 4: {'Hit dice': [['--ADD', 'key', '4d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Ability Score': ['WIS', 'INT']}, 5: {'Hit dice': [['--ADD', 'key', '5d10']], 'Proficiency Bonus': [['--ADD', 'key', '3']], 'Extra Attack': [['--ADD', 'key', '1']]}}, 'Ranger': {1: {'Hit dice': [['--ADD', 'key', '1d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Armor Proficiencies': [['--ADD', 'PROFICIENCY', 'Light Armor', 'Medium Armor', 'Shields']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Simple', 'Martial']], 'Saving Throw Proficiencies': [['--ADD', 'PROFICIENCY', 'Saving_STR', 'Saving_DEX']], 'Favored Enemy': [['--ADD', 'key', '1']], 'Natural Explorer': [['--ADD', 'key', '1']], 'Code': [['--CODE', 'Feature:Favoured Enemy', 'Feature:Natural Explorer']], 'Skills': ['Nature', 'Insight', 'Survival']}, 2: {'Hit dice': [['--ADD', 'key', '2d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Primary Ability': [['--ADD', 'key', 'Wisdom']], 'Spell Slots': [['--ADD', 'key', '1st:2']], 'Slot Level': [['--ADD', 'key', '1']], 'Spell': ['Goodberry', 'Speak with Animals'], 'Fighting Style': ['Defense']}}}
        # Etheria data = {'Elf': {'Ability Score': [['--ADD', 'Char:Ability_Scores', 'DEX', 'DEX']], 'Size': [['--ADD', 'Char:Size', 'Medium']], 'Speed': [['--ADD', 'Char:Speed', '30']], 'Darkvision': [['--ADD', 'Char:Darkvision', '60']], 'Resistance': [['--ADD', 'Char:Resistance', 'Charmed']], 'Immunity': [['--ADD', 'Char:Immunity', 'Sleep']], 'Skills': [['--ADD_NOW', 'Char:Skills', 'Perception']], 'Languages': [['--ADD', 'Char:Languages', 'Common,Elvish']], 'Second Ability Score': [['--ADD', 'Char:Ability_Scores', 'WIS']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Longsword', 'Shortsword', 'Shortbow', 'Longbow']], 'Fleet of Foot': [['--ADD', 'Char:Speed', '35']], 'Code': [['--CODE', 'Feature:Mask of the Wild']]}, 'Rogue': {1: {'Armor Proficiencies': [['--ADD', 'PROFICIENCY', 'Light Armor']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Simple', 'Hand Crossbow', 'Longsword', 'Rapier', 'Shortsword']], 'Tool Proficiencies': [['--ADD', 'PROFICIENCY', "Thieves' Tools"]], 'Saving Throw Proficiencies': [['--ADD', 'PROFICIENCY', 'Saving_DEX', 'Saving_INT']], 'Sneak Attack': [['--ADD', 'key', '1d6']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Languages': [['--ADD', 'key', "Thieves' Cant"]], 'Code': [['--CODE', 'Feature:Sneak Attack']], 'Skills': ['Acrobatics', 'Stealth', 'Sleight of Hand', 'Persuasion'], 'Expertise': ['Acrobatics', 'Stealth']}, 2: {'Cunning Action': [['--ADD', 'key', 'BONUS:Dash', 'BONUS:Disengage', 'BONUS:Hide']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Sneak Attack': [['--ADD', 'key', '1d6']], 'Code': [['--CODE', 'Bonus:Cunning Action']]}, 3: {'Proficiency Bonus': [['--ADD', 'key', '2']], 'Sneak Attack': [['--ADD', 'key', '2d6']], 'Roguish Archetype': ['Thief']}, 4: {'Proficiency Bonus': [['--ADD', 'key', '2']], 'Sneak Attack': [['--ADD', 'key', '2d6']], 'Ability Score': ['STR', 'CHA']}, 5: {'Uncanny Dodge': [['--ADD', 'key', 'REACT:Half Taken Damage']], 'Proficiency Bonus': [['--ADD', 'key', '3']], 'Sneak Attack': [['--ADD', 'key', '3d6']], 'Code': [['--CODE', 'Reaction:Uncanny Dodge']]}}, 'Warlock': {1: {'Armor Proficiencies': [['--ADD', 'PROFICIENCY', 'Light Armor']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Simple']], 'Saving Throw Proficiencies': [['--ADD', 'PROFICIENCY', 'Saving_WIS', 'Saving_CHA']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Primary Ability': [['--ADD', 'key', 'Charisma']], 'Spell Slots': [['--ADD', 'key', '1st:1']], 'Slot Level': [['--ADD', 'key', '1']], 'Skills': ['Nature', 'Investigation'], 'Cantrip': ['Eldritch Blast', 'Minor Illusion'], 'Spell': ['Hellish Rebuke', 'Unseen Servant'], 'Patron': ['The Celestial']}, 2: {'Magical Cunning': [['--ADD', 'key', 'Once per long rest']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Spell Slots': [['--ADD', 'key', '1st:2']], 'Slot Level': [['--ADD', 'key', '1']], 'Eldritch Invocations': ['Repelling Blast', 'Armor of Shadows'], 'Spell': ['Hex']}}}
        # Conan data = {'Human': {'Ability Score': [['--ADD', 'Char:Ability_Scores', 'STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']], 'Size': [['--ADD', 'Char:Size', 'Medium']], 'Speed': [['--ADD', 'Char:Speed', '30']], 'Languages': [['--ADD', 'Char:Languages', 'Common']]}, 'Druid': {1: {'Hit dice': [['--ADD', 'key', '1d8']], 'Armor Proficiencies': [['--ADD', 'PROFICIENCY', 'Light Armor', 'Medium Armor', 'Shields']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Club', 'Dagger', 'Dart', 'Javelin', 'Mace', 'Quarterstaff', 'Scimitar', 'Sickle', 'Sling', 'Spear']], 'Tool Proficiencies': [['--ADD', 'PROFICIENCY', 'Herbalism kit']], 'Saving Throw Proficiencies': [['--ADD', 'PROFICIENCY', 'Saving_INT', 'Saving_WIS']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Primary Ability': [['--ADD', 'key', 'Wisdom']], 'Spell Slots': [['--ADD', 'key', '1st:2']], 'Slot Level': [['--ADD', 'key', '1']], 'Languages': [['--ADD', 'key', 'Druidic']], 'Skills': ['Animal Handling', 'Nature'], 'Cantrip': ['Druidcraft', 'Guidance'], 'Spell': ['Healing Word', 'Ice Knife', 'Speak with Animals', 'Animal Messenger', 'Enhance Ability', 'Moonbeam', 'Revivify']}, 2: {'Hit dice': [['--ADD', 'key', '2d8']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Wild Shape': [['--ADD', 'key', '2:SR']], 'Spell Slots': [['--ADD', 'key', '1st:3']], 'Slot Level': [['--ADD', 'key', '1']], 'Wild Companion': [['--ADD', 'Spell', 'Find Familiar:Wild Shape']], 'Druid Circle': ['Land']}, 3: {'Hit dice': [['--ADD', 'key', '3d8']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Slot Level': [['--ADD', 'key', '1:2']], 'Spell Slots': [['--ADD', 'key', '1st:4,2nd:2']]}, 4: {'Hit dice': [['--ADD', 'key', '4d8']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Slot Level': [['--ADD', 'key', '1:2']], 'Spell Slots': [['--ADD', 'key', '1st:4,2nd:3']], 'Cantrip': ['Shillelagh'], 'Ability Score': ['INT', 'CON']}, 5: {'Hit dice': [['--ADD', 'key', '5d8']], 'Proficiency Bonus': [['--ADD', 'key', '3']], 'Slot Level': [['--ADD', 'key', '1:2:3']], 'Spell Slots': [['--ADD', 'key', '1st:4,2nd:3,3rd:2']]}}, 'Barbarian': {1: {'Hit dice': [['--ADD', 'key', '1d12']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Armor Proficiencies': [['--ADD', 'PROFICIENCY', 'Light Armor', 'Medium Armor', 'Shields']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Simple', 'Martial']], 'Saving Throw Proficiencies': [['--ADD', 'PROFICIENCY', 'Saving_STR', 'Saving_CON']], 'Rage': [['--ADD', 'key', '2']], 'Rage Damage': [['--ADD', 'key', '2']], 'Languages': [['--ADD', 'key', 'Druidic']], 'Unarmored Defense': [['--ADD', 'key', '{AC:10+DEX MOD+CON MOD}']], 'Skills': ['Athletics', 'Intimidation']}, 2: {'Hit dice': [['--ADD', 'key', '2d12']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Rage': [['--ADD', 'key', '2']], 'Rage Damage': [['--ADD', 'key', '2']], 'Reckless Attack': [['--ADD', 'key', 'Advantage on first attack and more vulnerable on getting hit']], 'Code': [['--CODE', 'Feature:Danger Sense']]}}}
        # Ru`ahala data = {'Kobold': {'Size': [['--ADD', 'Char:Size', 'Small']], 'Speed': [['--ADD', 'Char:Speed', '30']], 'Darkvision': [['--ADD', 'Char:Darkvision', '60']], 'Languages': [['--ADD', 'Char:Languages', 'Common', 'Draconic']]}, 'Barbarian': {1: {'Hit dice': [['--ADD', 'key', '1d12']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Armor Proficiencies': [['--ADD', 'PROFICIENCY', 'Light Armor', 'Medium Armor', 'Shields']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Simple', 'Martial']], 'Saving Throw Proficiencies': [['--ADD', 'PROFICIENCY', 'Saving_STR', 'Saving_CON']], 'Rage': [['--ADD', 'key', '2']], 'Rage Damage': [['--ADD', 'key', '2']], 'Unarmored Defense': [['--ADD', 'key', '{AC:10+DEX MOD+CON MOD}']], 'Code': [['--CODE', 'Feature:Rage', 'Feature:Unarmored Defense']], 'Skills': ['Perception', 'Survival']}, 2: {'Hit dice': [['--ADD', 'key', '2d12']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Rage': [['--ADD', 'key', '2']], 'Rage Damage': [['--ADD', 'key', '2']], 'Reckless Attack': [['--ADD', 'key', 'Advantage on first attack and more vulnerable on getting hit']], 'Code': [['--CODE', 'Feature:Danger Sense', 'Feature:Reckless Attack']]}, 3: {'Hit dice': [['--ADD', 'key', '3d12']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Rage': [['--ADD', 'key', '3']], 'Rage Damage': [['--ADD', 'key', '2']], 'Primal Path': ['Giant'], 'Skills': ['Athletics']}, 4: {'Hit dice': [['--ADD', 'key', '4d12']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Rage': [['--ADD', 'key', '3']], 'Rage Damage': [['--ADD', 'key', '2']], 'Ability Score': ['CON', 'CON']}, 5: {'Hit dice': [['--ADD', 'key', '5d12']], 'Proficiency Bonus': [['--ADD', 'key', '3']], 'Rage': [['--ADD', 'key', '3']], 'Rage Damage': [['--ADD', 'key', '2']], 'Extra Attack': [['--ADD', 'key', '1']], 'Fast Movement': [['--ADD', 'key', '10']], 'Code': [["--CODE", "Feature:Fast Movement"]]}}, 'Fighter': {1: {'Hit dice': [['--ADD', 'key', '1d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Armor Proficiencies': [['--ADD', 'PROFICIENCY', 'Light Armor', 'Medium Armor', 'Heavy Armor', 'Shields']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Simple', 'Martial']], 'Saving Throw Proficiencies': [['--ADD', 'PROFICIENCY', 'Saving_STR', 'Saving_CON']], 'Second Wind': [['--ADD', 'key', '1d10+1']], 'Code': [['--CODE', 'Feature:Second Wind']], 'Skills': ['History', 'Insight'], 'Fighting Style': ['Thrown Weapon Fighting']}, 2: {'Hit dice': [['--ADD', 'key', '2d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Action Surge': [['--ADD', 'key', '1']], 'Code': [['--CODE', 'Feature:Action Surge']]}, 3: {'Hit dice': [['--ADD', 'key', '3d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Martial Archetype': ['Rune Knight']}, 4: {'Hit dice': [['--ADD', 'key', '4d10']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Ability Score': ['STR', 'CON']}, 5: {'Hit dice': [['--ADD', 'key', '5d10']], 'Proficiency Bonus': [['--ADD', 'key', '3']], 'Extra Attack': [['--ADD', 'key', '1']], 'Code': [['--CODE', 'Feature:Extra Attack']]}}}
        # Galandir data = {'Changeling': {'Size': [['--ADD', 'Char:Size', 'Medium']], 'Speed': [['--ADD', 'Char:Speed', '30']], 'Languages': [['--ADD', 'Char:Languages', 'Common', 'Sylvan', 'Elvish', 'Dwarvish', 'Halfling']], 'Code': [['--CODE', 'Feature:Shapechanger']], 'Skills': [['--ADD', 'Persuasion']], 'Ability Score': [['INT', 'INT', 'INT']]}, 'Wizard': {1: {'Hit dice': [['--ADD', 'key', '1d6']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Dagger', 'Dart', 'Sling', 'Quarterstaff', 'Crossbow Light']], 'Saving Throw Proficiencies': [['--ADD', 'PROFICIENCY', 'Saving_INT', 'Saving_WIS']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Primary Ability': [['--ADD', 'key', 'Intelligence']], 'Spell Slots': [['--ADD', 'key', '1st:2']], 'Slot Level': [['--ADD', 'key', '1']], 'Arcane Recovery': [['--ADD', 'key', '1']], 'Skills': ['Arcana', 'History'], 'Cantrip': ['Blade Ward', 'Acid Splash', 'Booming Blade'], 'Spell': ['Absorb Elements', 'Alarm', 'Burning Hands', 'Catapult', 'Cause Fear', 'Charm Person', 'Chromatic Orb', 'Comprehend Languages', 'Color Spray']}, 2: {'Hit dice': [['--ADD', 'key', '2d6']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Spell Slots': [['--ADD', 'key', '1st:3']], 'Slot Level': [['--ADD', 'key', '1']], 'Arcane Recovery': [['--ADD', 'key', '1']], 'Arcane Tradition': ['Necromancy']}, 3: {'Hit dice': [['--ADD', 'key', '3d6']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Spell Slots': [['--ADD', 'key', '1st:4,2nd:2']], 'Slot Level': [['--ADD', 'key', '2']], 'Arcane Recovery': [['--ADD', 'key', '2']]}, 4: {'Hit dice': [['--ADD', 'key', '4d6']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Spell Slots': [['--ADD', 'key', '1st:4,2nd:3']], 'Slot Level': [['--ADD', 'key', '2']], 'Arcane Recovery': [['--ADD', 'key', '2']], 'Ability Score': ['STR', 'STR']}, 5: {'Hit dice': [['--ADD', 'key', '5d6']], 'Proficiency Bonus': [['--ADD', 'key', '3']], 'Spell Slots': [['--ADD', 'key', '1st:4,2nd:3,3rd:2']], 'Slot Level': [['--ADD', 'key', '3']], 'Arcane Recovery': [['--ADD', 'key', '3']]}}, 'Sorcerer': {1: {'Hit dice': [['--ADD', 'key', '1d6']], 'Weapon Proficiencies': [['--ADD', 'PROFICIENCY', 'Dagger', 'Dart', 'Sling', 'Quarterstaff', 'Crossbow Light']], 'Saving Throw Proficiencies': [['--ADD', 'PROFICIENCY', 'Saving_CON', 'Saving_CHA']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Primary Ability': [['--ADD', 'key', 'Charisma']], 'Spell Slots': [['--ADD', 'key', '1st:2']], 'Slot Level': [['--ADD', 'key', '1']], 'Skills': ['Deception', 'Intimidation'], 'Cantrip': ['Chill Touch', 'Blade Ward', 'Acid Splash', 'Booming Blade'], 'Spell': ['Chaos Bolt', 'Absorb Elements'], 'Sorcerous Origin': ['Shadow Magic']}, 2: {'Hit dice': [['--ADD', 'key', '2d6']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Spell Slots': [['--ADD', 'key', '1st:3']], 'Slot Level': [['--ADD', 'key', '1']], 'Sorcery Points': [['--ADD', 'key', '2']], 'Font of Magic': [['--ADD', 'key', '1']]}, 3: {'Hit dice': [['--ADD', 'key', '3d6']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Spell Slots': [['--ADD', 'key', '1st:4,2nd:2']], 'Slot Level': [['--ADD', 'key', '2']], 'Sorcery Points': [['--ADD', 'key', '3']], 'Metamagic': ['Distant Spell', 'Quickened Spell']}, 4: {'Hit dice': [['--ADD', 'key', '4d6']], 'Proficiency Bonus': [['--ADD', 'key', '2']], 'Spell Slots': [['--ADD', 'key', '1st:4,2nd:3']], 'Slot Level': [['--ADD', 'key', '2']], 'Sorcery Points': [['--ADD', 'key', '4']], 'Ability Score': ['CHA', 'WIS']}, 5: {'Hit dice': [['--ADD', 'key', '5d6']], 'Proficiency Bonus': [['--ADD', 'key', '3']], 'Spell Slots': [['--ADD', 'key', '1st:4,2nd:3,3rd:2']], 'Slot Level': [['--ADD', 'key', '3']], 'Sorcery Points': [['--ADD', 'key', '5']], 'Magical Guidance': [['--ADD', 'key', '1']], 'Code': [['--CODE', 'Feature:Magical Guidance']]}}}
        data = reformat_data(data)
        F.create_char_JSON(V.char_name, data)
        load_char_data(S.local_path + "/Created_Players/" + V.char_name + "_config.json")
    calculate_skills(char)

def get_player_choises(char, screen, clock, id, data):
    """current class and level id, tracking the recursion of function"""
    current_level = id[1] + 1
    class_id = id[0]

    """one of two character classes"""
    current_class = char["Class"].split(", ")[class_id]

    """read from main dnd file about classes"""
    current_class_data = S.class_data[current_class]
    current_class_level_data = current_class_data[str(current_level)]
    scroll = 0
    text_scroll = 0
    running = True
    text_size = 30
    pressed = -1
    describtion_button_text = "Description"
    button_dict = {
        0: ["Previous Class", "background", "background", "rect-place-holder", "black"],
        1: [describtion_button_text, "background", "background", "rect-place-holder", "black"]
    }
    class_count = len(char["Class"].split(", "))
    class_level = char["Level"].split(",")[class_id]
    if data.get(current_class) == None:
        data[current_class] = {}
    if data[current_class].get(current_level) == None:
        data[current_class][current_level] = {}

    if int(class_level) == current_level and class_id == class_count - 1:
        button_text = "Finish"
    elif int(class_level) == current_level:
        button_text = "Next Class"
    else:
        button_text = "Next Level"

    selected_dropbox = -1
    dropboxes = {}
    choises = {}
    hold_Value = -1
    hovering_mouse = -1
    # entry_screen2 = screen.copy()
    text_surface = None
    y_scroll = 0
    s = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 3), pg.SRCALPHA).convert_alpha()
    AA = 0
    while running:
        s.fill((0,0,0,0))
        push_y = 2
        entry_screen1 = pg.surface.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.SRCALPHA)
        entry_screen2 = pg.surface.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.SRCALPHA)
        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.05

        start_x = S.SCREEN_WIDTH * 0.07
        start_y = S.SCREEN_HEIGHT * 0.07
        x_pos = []
        y_pos = start_y
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 3), "Background")

        buttons = F.display_back_button(screen, button_text)
        if id != (0, 0):
            if "Level" in button_text:
                prev_text = button_text.replace("Next", "Previous")
            else:
                prev_text = "Previous Level"
            if id[1] == 0:
                prev_text = "Previous Class"

            button_dict[0][0] = prev_text
        else:
            button_dict = {
                1: [describtion_button_text, "background", "background", "rect-place-holder", "black"]
            }
        buttons = buttons + F.display_other_buttons(screen, text_size, ([S.SCREEN_WIDTH * 0.5, S.SCREEN_WIDTH * 0.225], S.SCREEN_HEIGHT * 0.9, S.SCREEN_WIDTH / 4, S.SCREEN_HEIGHT / 20), button_dict)
        for i in range(0, int(class_level)):
            x_pos.insert(i, start_x + i * button_width)
        # for i in range(0, 20):
        #     y_pos.insert(i, start_y + i * button_height)

        F.display_text(s, char["Class"].split(", ")[class_id], text_size, (start_x, y_pos))
        F.display_text(s, "Level: " + str(current_level), text_size, (start_x + button_width, y_pos))
        fill_needed = 0
        or_tracker = ""

        for i in range(0, len(list(current_class_level_data.keys()))):
            key = list(current_class_level_data.keys())[i]
            value = current_class_level_data[key]
            if value == "":
                # print(f"Skipping: {key} cuz its empty")
                continue
            if isinstance(value, list) and "--" in value[0]:
                if "CHOOSE" in value[0]:
                    """--Choose found in class.json, make a choice between certain parameters"""
                    if "OR" not in value[0]:
                        """if its CHOOSE and not CHOOSE_OR"""

                        value = update_choise(value, char, id)
                        fill_needed += int(value[0].split(":")[1])
                    else:
                        """Its CHOOSE_OR used for calculating how much filling is needed before going to next page."""
                        or_tracker += "-" + key + ":" + value[0].split(":")[1]
                        fill_needed = -1

                temp_dropbox, displayed_lower_flag = deal_with_commands_from_JSON(key, value, (s, entry_screen1, entry_screen2),(x_pos[0], y_pos + push_y * button_height), selected_dropbox, choises, scroll, data, id)
                if displayed_lower_flag != 0:
                    push_y += displayed_lower_flag - 1

                if temp_dropbox != None:
                    dropboxes.update(temp_dropbox)
                if "ADD" in value[0]:
                    temp_value = value.copy()
                    for ii in range(2, len(temp_value)):
                        if "_" in temp_value[ii]:
                            temp_value[ii] = temp_value[ii].split("_")[1]
                    value_string = ", ".join(temp_value[2:])
                    F.display_text(s, key + ": " + value_string, int(text_size / 3), (x_pos[0], y_pos + push_y * button_height))
                    if data[current_class][current_level].get(key) == None:
                        data[current_class][current_level][key] = []
                    if value not in data[current_class][current_level][key]:
                        data[current_class][current_level][key].append(value)
                if "CODE" in value[0]:
                    if data[current_class][current_level].get(key) == None:
                        data[current_class][current_level][key] = []
                    if value not in data[current_class][current_level][key]:
                        data[current_class][current_level][key].append(value)
            else:
                """Display text because no functions exist"""
                value_string = ", ".join(value)
                if value_string != "":
                    text_rect = F.display_text(s, key + ": ", int(text_size / 3), (x_pos[0], y_pos + push_y * button_height), color="#AA2200")
                    value_string = value_string.replace("\n\n", " ")
                    value_string = value_string.replace("\n", "")
                    for w in value_string.split(" "):
                        text_rect = F.display_text(s, w + " ", int(text_size / 3), (text_rect.x + text_rect.w, text_rect.y))
                        if text_rect.x + text_rect.w > S.SCREEN_WIDTH * 0.9:
                            text_rect.x = x_pos[0]
                            text_rect.w = 0
                            text_rect.y += button_height
                    y_pos = text_rect.y - push_y * button_height
            y_pos += button_height

        for event in pg.event.get():
            keys = pg.key.get_pressed()
            mouse_pos = pg.mouse.get_pos()
            adjusted_pos = (mouse_pos[0], mouse_pos[1] - y_scroll * 30)
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
                text_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 4), pg.SRCALPHA)
                display_spell_describtion(text_surface, hold_Value, id, describtion_button_text, data)
                s = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 3), pg.SRCALPHA).convert_alpha()

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                hovering_mouse = -1

                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(mouse_pos):
                        # pressed = button_text
                        pressed = i
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                        break
                for key, value in dropboxes.items():
                    if isinstance(value, pg.Rect) and value.collidepoint(adjusted_pos):
                        """When pressing dropboxes closed"""
                        pressed = key
                        pg.draw.rect(s, "black", value, width=3)
                        break
                    elif isinstance(value, dict) and selected_dropbox != -1:
                        """when pressing dropboxes opened"""
                        for name, rect in value.items():
                            if rect.collidepoint(adjusted_pos):
                                """found the rect of the choise"""
                                pressed = key
                                if choises.get(pressed) != None and len(dropboxes.keys()) != 1:
                                    """If the choise was already made and you idiot decided to change your mind. need to set the skill to no longer proficient assuming it was never proficient"""
                                    """because if it was proficient technicly it shouldn't have been part of the list in the first place."""
                                    """ I ALSO NEED TO REMOVE THIS CHOISE FROM EXPERTISE APPARENTLY"""

                                    skill_to_look_for = choises[pressed]
                                    for choise_key, choise_value in choises.items():
                                        if choise_key != pressed and choise_value == skill_to_look_for:
                                            if pressed[0] == "Skills":
                                                """Make sure skills can change expertise, and expertise cant change skills"""
                                                choises[choise_key] = None
                                    if "Skills" == key[0]:
                                        """Means we are dealing with proficiencies and not expertise"""
                                        skills = char["Skills"].split(",")
                                        index = list(V.Skills.keys()).index(choises[pressed])
                                        skills[index] = choises[pressed] + ":1"
                                        char["Skills"] = ",".join(skills)
                                    elif "Expertise" == key[0]:
                                        skills = char["Skills"].split(",")
                                        index = list(V.Skills.keys()).index(choises[pressed])
                                        skills[index] = choises[pressed] + ":" + str(V.Proficiecy_bonus)
                                        char["Skills"] = ",".join(skills)
                                choises[pressed] = name
                                if key[0] == "Cantrip":
                                    V.chosen_cantrips[key[1]] = choises[pressed]
                                elif key[0] == "Spell":
                                    V.chosen_spells[key[1]] = choises[pressed]

                                pg.draw.rect(s, "black", rect, width=3)
                                break

            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if isinstance(pressed, int) and buttons[pressed].collidepoint(mouse_pos):
                        """Buttons"""
                        if pressed == 1 and id == (0, 0):
                            pressed = 2
                        if pressed == 0:
                            """pressed next"""
                            if class_count - 1 == class_id and current_level == int(class_level):
                                """Pressed final NEXT"""
                                for key, value in choises.items():
                                    if data[current_class][current_level].get(key[0]) == None:
                                        data[current_class][current_level][key[0]] = []
                                    if value not in data[current_class][current_level][key[0]]:
                                        if value[1] == "key":
                                            data[current_class][current_level][key[0]].append(value[2])
                                        else:
                                            data[current_class][current_level][key[0]].append(value)
                                return data
                            else:
                                temp_data = None
                                if isinstance(fill_needed, int) and fill_needed == len(choises) and fill_needed != -1:
                                    for key, value in choises.items():
                                        if data[current_class][current_level].get(key[0]) == None:
                                            data[current_class][current_level][key[0]] = []
                                        if value not in data[current_class][current_level][key[0]]:
                                            if value[1] == "key":
                                                data[current_class][current_level][key[0]].append(value[2])
                                            else:
                                                data[current_class][current_level][key[0]].append(value)
                                    if button_text == "Next Level":
                                        or_tracker = ""
                                        temp_data = get_player_choises(char, screen, clock, (class_id, current_level), data)
                                    else:
                                        temp_data = get_player_choises(char, screen, clock, (class_id + 1, 0), data)
                                elif isinstance(or_tracker, str) and or_tracker != "":
                                    """To my knowledge only deals with feats and ability scores"""
                                    passing = []
                                    if or_tracker.count("-") == 2:
                                        option1 = or_tracker.split("-")[1]
                                        option2 = or_tracker.split("-")[2]
                                    else:
                                        option1 = or_tracker.split("-")[1]
                                        option2 = ":"
                                    """only passes if option1 is correct or option2 is correct"""
                                    for choise_key, choise_value in choises.items():
                                        if choise_key[0] == option1.split(":")[0] and choise_value != None:
                                            passing.append(option1.split(":")[0])
                                        if choise_key[0] == option2.split(":")[0] and choise_value != None:
                                            passing.append(option2.split(":")[0])
                                        # print(option1, passing, choise_key, choise_value)
                                    if len(passing) == int(option1.split(":")[1]) and all(passing_requirement == option1.split(":")[0] for passing_requirement in passing):
                                        print("1")
                                        for key, value in choises.items():
                                            if data[current_class][current_level].get(key[0]) == None:
                                                data[current_class][current_level][key[0]] = []
                                            if value not in data[current_class][current_level][key[0]] or key[0] in ["Ability Score"]:
                                                data[current_class][current_level][key[0]].append(value)
                                        if button_text == "Next Level":
                                            temp_data = get_player_choises(char, screen, clock,(class_id, current_level), data)
                                        else:
                                            temp_data = get_player_choises(char, screen, clock, (class_id + 1, 0), data)
                                    elif len(passing) == int(option2.split(":")[1]) and all(passing_requirement == option2.split(":")[0] for passing_requirement in passing):
                                        for key, value in choises.items():
                                            if data[current_class][current_level].get(key[0]) == None:
                                                data[current_class][current_level][key[0]] = []
                                            if value not in data[current_class][current_level][key[0]] and value != None:
                                                if value[1] == "key":
                                                    data[current_class][current_level][key[0]].append(value[2])
                                                else:
                                                    data[current_class][current_level][key[0]].append(value)
                                        if button_text == "Next Level":
                                            temp_data = get_player_choises(char, screen, clock, (class_id, current_level), data)
                                        else:
                                            temp_data = get_player_choises(char, screen, clock, (class_id + 1, 0), data)
                                if temp_data != None:
                                    data.update(temp_data)
                                    running = False
                        elif pressed == 1:
                            """pressed previous"""
                            return None
                        elif pressed == 2:
                            if describtion_button_text == "Description":
                                describtion_button_text = "Simple"
                            elif describtion_button_text == "Simple":
                                describtion_button_text = "At Higher Levels"
                            elif describtion_button_text == "At Higher Levels":
                                describtion_button_text = "Description"
                            button_dict[1][0] = describtion_button_text
                            text_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 4), pg.SRCALPHA)
                            display_spell_describtion(text_surface, hold_Value, id, describtion_button_text, data)

                    if isinstance(pressed, tuple):
                        """Dropboxes"""
                        if pressed == selected_dropbox:
                            """enables closing the dropbox by clicking on the top arrow"""
                            selected_dropbox = -1
                            hovering_mouse = -1
                        else:
                            selected_dropbox = pressed
                    else:
                        selected_dropbox = -1
                        hovering_mouse = -1

                    pressed = -1
                else:
                    selected_dropbox = -1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 4 or event.type == pg.KEYDOWN and event.key == pg.K_UP:
                """going up"""
                scroll -= 1
                if scroll < 0:
                    scroll = 0
                if selected_dropbox == -1:
                    text_scroll -= 1
                    if text_scroll < 0:
                        text_scroll = 0
                hovering_mouse = -1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5 or event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                """going down"""
                scroll += 1
                if selected_dropbox == -1:
                    text_scroll += 1
                hovering_mouse = -1
            elif event.type == pg.MOUSEMOTION:
                for key, value in dropboxes.items():
                    if isinstance(value, dict) and selected_dropbox != -1:
                        for name, rect in value.items():
                            if rect.collidepoint(adjusted_pos):
                                hovering_mouse = [key, name, rect]
                                break
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 4 and keys[pg.K_LSHIFT]:
                if y_scroll < 0:
                    y_scroll += 1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5 and keys[pg.K_LSHIFT]:
                y_scroll -= 1
        s.blit(entry_screen1, (0, 0))
        s.blit(entry_screen2, (0, 0))
        if hovering_mouse != -1:
            hold_Value = hovering_mouse
            """Make the rect colored and display the text untop of the color"""
            pg.draw.rect(s, "light blue", hovering_mouse[2])
            F.display_text(s, hovering_mouse[1], int(S.SCREEN_HEIGHT * 0.03 / 2.4), (hovering_mouse[2][0] + 5, hovering_mouse[2][1]))
            """Display the text and the spell"""
            text_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 4), pg.SRCALPHA)
            display_spell_describtion(text_surface, hovering_mouse, id, describtion_button_text, data)
        if text_surface != None:
            s.blit(text_surface, (0, text_scroll * -20))
        if AA == 1:
            s.fill("#222222")
        screen.blit(s, (0, y_scroll * 30))
        if running:
            pg.display.flip()
            clock.tick(120)
    return data

def get_race_choises(char, screen, clock, data):
    displayed_lower_flag = False
    if S.Race_data == {}:
        with open(S.local_path + "/Races.json", 'r') as file:
            S.Race_data = json.load(file)

    race = char["Race"]
    race_data = S.Race_data[race].copy()
    scroll = 0
    id = (0, 0)
    text_scroll = 0
    running = True
    text_size = 30
    pressed = -1
    describtion_button_text = "Description"
    button_dict = {
        0: [describtion_button_text, "background", "background", "rect-place-holder", "black"]
    }
    if data.get(race) == None:
        data[race] = {}

    button_text = "Next Page"

    selected_dropbox = -1
    dropboxes = {}
    choises = {}
    hold_Value = -1
    hovering_mouse = -1

    chosen_subrace = ""
    # entry_screen2 = screen.copy()
    text_surface = None
    json_commands = {"choises": choises,
                     "EQUAL": operator.eq,
                    }
    y_scroll = 0
    s = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 3), pg.SRCALPHA).convert_alpha()

    while running:
        s.fill((0,0,0,0))
        if chosen_subrace != "" and chosen_subrace != None:
            race_data = S.Race_data[race].copy()
            for d, v in S.Race_data[chosen_subrace].items():
                if race_data.get(d) == None:
                    race_data[d] = v
                elif race_data[d][0] == "--CODE" and v[0] == "--CODE":
                    race_data[d].append(v[1])
                else:
                    print(race_data[d], v)
            chosen_subrace = ""
            data[race] = {}
        entry_screen1 = pg.surface.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.SRCALPHA)
        entry_screen2 = pg.surface.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.SRCALPHA)
        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.05

        start_x = S.SCREEN_WIDTH * 0.07
        start_y = S.SCREEN_HEIGHT * 0.07
        x_pos = []
        y_pos = start_y + button_height * 2

        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")

        buttons = F.display_back_button(screen, button_text)
        buttons = buttons + F.display_other_buttons(screen, text_size, ([S.SCREEN_WIDTH * 0.5, S.SCREEN_WIDTH * 0.225], S.SCREEN_HEIGHT * 0.9, S.SCREEN_WIDTH / 4, S.SCREEN_HEIGHT / 20), button_dict)
        for i in range(0, 2):
            x_pos.insert(i, start_x + i * button_width)

        F.display_text(s, char["Race"], text_size, (start_x, start_y))
        fill_needed = 0
        for i in range(0, len(list(race_data.keys()))):
            key = list(race_data.keys())[i]
            value = race_data[key]
            if "IF0" == key:
                skip = True
                if json_commands[value[0]] == choises:
                    if json_commands[value[0]].get((value[1], 0)) != None and json_commands[value[2]](json_commands[value[0]][value[1], 0], value[3]):
                        """ IF choises[Kobolt Legacy, 0] == Draconic Sorcery """
                        key = value[4]
                        value = value[5:]
                        skip = False
                if skip:
                    continue
            if isinstance(value, list) and "--" in value[0]:
                if "--LEVEL_REQ" in value[0]:
                    level_requirement = int(value[0].split(":")[1])
                    if int(char["Level"].split(", ")[0]) >= level_requirement:
                        value = value[1:]
                    else:
                        continue
                if "--CHOOSE" in value[0] and value[0][2] == "C":
                    """--Choose found in class.json, make a choice between certain parameters"""
                    if "OR" not in value[0]:
                        """if its CHOOSE and not CHOOSE_OR"""
                        if isinstance(fill_needed, str):
                            fill_needed = 0
                        fill_needed += int(value[0].split(":")[1])
                    else:
                        """Its CHOOSE_OR used for calculating how much filling is needed before going to next page."""
                        if fill_needed == 0:
                            fill_needed = "OR"
                        fill_needed += "-" + key + ":" + value[0].split(":")[1]
                if "--DEPENDANT" in value[0]:
                    _, dependant_key, dependant_choise, dependant_further_action = value[0].split("__")
                    if choises.get((dependant_key, 0)) != None:
                        if key == choises.get((dependant_key, 0)):
                            value = [dependant_further_action] + value[1:]

                temp_dropbox, displayed_lower_flag = deal_with_commands_from_JSON(key, value, (s, entry_screen1, entry_screen2),(x_pos[0], y_pos), selected_dropbox, choises, scroll, data, id)

                if temp_dropbox != None:
                    dropboxes.update(temp_dropbox)
                if "ADD" in value[0] and value[0][2] != "D":
                    temp_value = value.copy()
                    for ii in range(2, len(temp_value)):
                        if "_" in temp_value[ii]:
                            temp_value[ii] = temp_value[ii].split("_")[1]
                    value_string = ", ".join(temp_value[2:])
                    F.display_text(s, key + ": " + value_string, int(text_size / 3), (x_pos[0], y_pos))
                    if data[race].get(key) == None:
                        data[race][key] = []
                    if value not in data[race][key]:
                        data[race][key].append(value)
                    if "ADD_NOW" in value[0]:
                        handle_add_NOW(value)
                        y_pos += button_height
                        continue
                if "CODE" in value[0]:
                    if data[race].get(key) == None:
                        data[race][key] = []
                    if value not in data[race][key]:
                        data[race][key].append(value)
                    continue
            else:
                """Display text because no functions exist"""
                value_string = ", ".join(value)
                was_added = False
                text_rect = F.display_text(s, key + ": ", int(text_size / 3), (x_pos[0], y_pos))
                for w in value_string.split(" "):
                    text_rect = F.display_text(s, w + " ", int(text_size / 3), (text_rect.x + text_rect.w, text_rect.y))
                    if text_rect.x + text_rect.w > S.SCREEN_WIDTH * 0.8:
                        text_rect.x = x_pos[0]
                        text_rect.w = 0
                        text_rect.y += button_height
                        was_added = True
                # if not was_added:
                #     text_rect.y += button_height
                y_pos = text_rect.y
            y_pos += button_height

        for event in pg.event.get():
            keys = pg.key.get_pressed()
            mouse_pos = pg.mouse.get_pos()
            adjusted_pos = (mouse_pos[0], mouse_pos[1] - y_scroll * 30)
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
                text_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 4), pg.SRCALPHA)
                display_spell_describtion(text_surface, hold_Value, id, describtion_button_text, data)
                s = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 3), pg.SRCALPHA).convert_alpha()

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                hovering_mouse = -1
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(mouse_pos):
                        pressed = i
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                        break
                for key, value in dropboxes.items():
                    if isinstance(value, pg.Rect) and value.collidepoint(adjusted_pos):
                        """When pressing dropboxes closed"""
                        pressed = key
                        pg.draw.rect(s, "black", value, width=3)
                        break
                    elif isinstance(value, dict) and selected_dropbox != -1:
                        """when pressing dropboxes opened"""
                        for name, rect in value.items():
                            if rect.collidepoint(adjusted_pos):
                                """found the rect of the choise"""
                                pressed = key
                                if choises.get(pressed) != None and len(dropboxes.keys()) != 1:
                                    """If the choise was already made and you idiot decided to change your mind. need to set the skill to no longer proficient assuming it was never proficient"""
                                    """because if it was proficient technicly it shouldn't have been part of the list in the first place."""
                                    """ I ALSO NEED TO REMOVE THIS CHOISE FROM EXPERTISE APPARENTLY"""
                                    skill_to_look_for = choises[pressed]
                                    for choise_key, choise_value in choises.items():
                                        if choise_key != pressed and choise_value == skill_to_look_for:
                                            if pressed[0] == "Skills":
                                                """Make sure skills can change expertise, and expertise cant change skills"""
                                                choises[choise_key] = None
                                    if "Skills" == key[0]:
                                        """Means we are dealing with proficiencies and not expertise"""
                                        skills = char["Skills"].split(",")
                                        index = list(V.Skills.keys()).index(choises[pressed])
                                        skills[index] = choises[pressed] + ":1"
                                        char["Skills"] = ",".join(skills)
                                    elif "Expertise" == key[0]:
                                        skills = char["Skills"].split(",")
                                        index = list(V.Skills.keys()).index(choises[pressed])
                                        skills[index] = choises[pressed] + ":" + str(V.Proficiecy_bonus)
                                        char["Skills"] = ",".join(skills)
                                choises[pressed] = name

                                if key[0] == "Sub-Race":
                                    chosen_subrace = choises[pressed]
                                if key[0] == "Cantrip":
                                    V.chosen_cantrips[key[1]] = choises[pressed]
                                elif key[0] == "Spell":
                                    V.chosen_spells[key[1]] = choises[pressed]

                                pg.draw.rect(s, "black", rect, width=3)
                                break

            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if isinstance(pressed, int) and buttons[pressed].collidepoint(mouse_pos):
                        """Buttons"""
                        if pressed == 0:
                            """pressed next"""
                            for choise in choises.keys():
                                """ Deals with adding IF0 and DEPENDANT key values to the data, example Kobold race"""
                                if choise[0] not in data[race].values() and choise[0] not in ["Ability Score", "Kobold Legacy"]:
                                    if choise[0] == "Sub-Race":
                                        data[race][choise[0]] = [["--ADD", choises[choise]]]
                                    elif choise[0] == "Extra Languages":
                                        if data[race].get("Languages") == None:
                                            data[race]["Languages"] = [['--ADD', 'Char:Languages']]
                                        data[race]["Languages"][0].append(choises[choise])
                                    elif choise[0] == "Skills":
                                        if data[race].get("Skills") == None:
                                            data[race][choise[0]] = [["--ADD"]]
                                        data[race][choise[0]][0].append(choises[choise])
                                    elif data[race].get("Code") != None and choise[0] not in data[race]["Code"][0][1]:
                                        if choise[0] == "Craftiness":
                                            data[race]["Skills"] = [["--ADD", "Char:Skills", choises[choise]]]
                                        else:
                                            data[race][choise[0]] = [["--ADD", choises[choise]]]
                                elif choise[0] in ["Ability Score"]:
                                    if data[race].get(choise[0]) == None:
                                        data[race][choise[0]] = []
                                    data[race][choise[0]].append(choises[choise])
                                elif choise[0] in ["Draconic Sorcery", "Primary Ability", "Kobold Legacy"]:
                                    if choises[choise] in ["Defiance", "Draconic Sorcery"]:
                                        """Doesnt allow other abilityies to be placed in here if they are not chosen."""
                                        data[race][choise[0]] = [["--ADD", choises[choise]]]
                                        if data[race].get("Code") == None:
                                            data[race]["Code"] = [[]]
                                        data[race]["Code"][0].append("Feature:"+choises[choise])
                            return data
                        elif pressed == 2:
                            if describtion_button_text == "Description":
                                describtion_button_text = "Simple"
                            elif describtion_button_text == "Simple":
                                describtion_button_text = "At Higher Levels"
                            elif describtion_button_text == "At Higher Levels":
                                describtion_button_text = "Description"
                            button_dict[1][0] = describtion_button_text
                            text_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 4), pg.SRCALPHA)
                            display_spell_describtion(text_surface, hold_Value, id, describtion_button_text, data)

                    if isinstance(pressed, tuple):
                        """Dropboxes"""
                        if pressed == selected_dropbox:
                            """enables closing the dropbox by clicking on the top arrow"""
                            selected_dropbox = -1
                            hovering_mouse = -1
                        else:
                            """Makes the dropbox drop"""
                            selected_dropbox = pressed
                    else:
                        selected_dropbox = -1
                        hovering_mouse = -1

                    pressed = -1
                else:
                    selected_dropbox = -1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 4 or event.type == pg.KEYDOWN and event.key == pg.K_UP:
                """going up"""
                scroll -= 1
                if scroll < 0:
                    scroll = 0
                if selected_dropbox == -1:
                    text_scroll -= 1
                    if text_scroll < 0:
                        text_scroll = 0
                hovering_mouse = -1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5 or event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                """going down"""
                scroll += 1
                if selected_dropbox == -1:
                    text_scroll += 1
                hovering_mouse = -1
            elif event.type == pg.MOUSEMOTION:
                for key, value in dropboxes.items():
                    if isinstance(value, dict) and selected_dropbox != -1:
                        for name, rect in value.items():
                            if rect.collidepoint(adjusted_pos):
                                hovering_mouse = [key, name, rect]
                                break
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 4 and keys[pg.K_LSHIFT]:
                if y_scroll < 0:
                    y_scroll += 1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5 and keys[pg.K_LSHIFT]:
                y_scroll -= 1
        s.blit(entry_screen1, (0, 0))
        s.blit(entry_screen2, (0, 0))
        if hovering_mouse != -1:
            hold_Value = hovering_mouse
            """Make the dropbox rect colored and display the text untop of the color"""
            pg.draw.rect(s, "light blue", hovering_mouse[2])
            F.display_text(s, hovering_mouse[1], int(S.SCREEN_HEIGHT * 0.03 / 2.4), (hovering_mouse[2][0] + 5, hovering_mouse[2][1]))
            """Display the text and the spell"""
            text_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 4), pg.SRCALPHA)
            display_spell_describtion(text_surface, hovering_mouse, id, describtion_button_text, data)
        if text_surface != None:
            s.blit(text_surface, (0, text_scroll * -20))
        screen.blit(s, (0, y_scroll * 30))

        if running:
            pg.display.flip()
            clock.tick(60)
    return data


def deal_with_commands_from_JSON(key, value, screens, pos, selected_dropbox, choises, scroll, data, id):
    displayed_lower_flag = 0
    data_dict = {}
    data_list = [None]
    rect_list = []
    char = V.character_dict[V.char_name]
    char_class = char["Class"].split(", ")[id[0]]
    char_level = id[1] + 1
    spell_class = ""
    screen, entry_screen1, entry_screen2 = screens

    # print(key, value, V.character_dict[V.char_name])
    if "--CHOOSE" in value[0] and value[0][2] == "C":
        """need to choose between some things"""
        option_count = value[0].split(":")[1]
        if "FROM" == value[1]:
            """choosing from a list of something the choises are made only once"""
            if "--" not in value[2]:
                for i in range(2, len(value)):
                    data_list.append(value[i])
            else:
                if "feat" in value[2].lower():
                    if S.feat_data == {}:
                        with open(S.local_path + "/" + str(value[2].replace("--", "").capitalize()) + ".json", 'r') as file:
                            S.feat_data = json.load(file, encoding="utf-8")
                    V.some_data = S.feat_data.copy()
                elif "spells" in value[2].lower():
                    if S.spell_data == {}:
                        with open(S.local_path + "/" + str(value[2].capitalize().replace("--", "")) + ".json", 'r') as file:
                            S.spell_data = json.load(file)
                    V.some_data = S.spell_data.copy()
                elif "cantrips" in value[2].lower():
                    cantrip_file = value[2]
                    if ":" in value[2].lower():
                        spell_class = value[2].split(":")[1]
                        cantrip_file = value[2].split(":")[0]
                    if S.cantrip_data == {}:
                        with open(S.local_path + "/" + str(cantrip_file.capitalize().replace("--", "")) + ".json", 'r') as file:
                            S.cantrip_data = json.load(file)
                    V.some_data = S.cantrip_data.copy()
                else:
                    with open(S.local_path + "/" + str(value[2].capitalize().replace("--", "")) + ".json", 'r') as file:
                        V.some_data = json.load(file)


                for feat_key, feat_value in V.some_data.items():
                    if feat_value.get("Prerequisite") == None or feat_value["Prerequisite"] == "":
                        """No prequisite exists for this attribute"""
                        if "spells" in value[2].lower():
                            spell_name = feat_key
                            if spell_name in list(V.chosen_spells.values()):
                                """if this spell was already chosen"""
                                continue
                            if S.spell_data[spell_name].get("Level") == None or S.spell_data[spell_name].get("Class") == None:
                                """If this spell doesnt have a level or a class to it, means not finished spell"""
                                continue
                            elif int(S.spell_data[spell_name]["Level"]) > int(V.Available_spells_data[char["Class"].split(", ")[id[0]]][int(char["Level"].split(",")[id[0]])][4]):
                                """If the level of the spell is higher than the highest available spell slot of this class and this level character then continue"""
                                continue
                            if char_class not in S.spell_data[spell_name]["Class"]:
                                """if this spell is not for this class"""
                                continue
                        if "cantrips" in value[2].lower():
                            cantrip_name = feat_key
                            if cantrip_name in list(V.chosen_cantrips.values()):
                                """if this cantrip was already chosen"""
                                continue
                            if S.cantrip_data[cantrip_name].get("Class") == None:
                                """if this cantrip doesnt have a class programed in"""
                                continue
                            if spell_class == "" and char_class not in S.cantrip_data[cantrip_name]["Class"]:
                                """if this cantrips usable class is not char class"""
                                continue
                            if spell_class != "" and spell_class not in S.cantrip_data[cantrip_name]["Class"]:
                                continue
                        data_list.append(feat_key)
                    else:
                        """there is a requirement for the feat"""
                        if ">" in feat_value["Prerequisite"][0]:
                            """if something is higher than something usualy ability score"""
                            if feat_value['Prerequisite'][0].split('>')[0].upper() in V.Ability_score_list:
                                """this is an ability score"""
                                index = V.Ability_score_list.index(feat_value['Prerequisite'][0].upper().split('>')[0])
                                current_ability_score = V.character_dict[V.char_name]["Ability_Scores"].split(",")[index]
                                if any(int(current_ability_score) > int(feat_requirement.split(">")[1]) for feat_requirement in feat_value['Prerequisite']):
                                    data_list.append(feat_key)
                            else:
                                F.print_debug("IM CONFUSED HELP PROGRAMMER!!!!!!!!!!!!!!", debug="ERROR")
                        elif "Proficiency" in feat_value["Prerequisite"][0]:
                            print(feat_value['Prerequisite'][0])
                            if "Martial" in feat_value['Prerequisite'][0]:
                                """Checking if there is a proficiency in Martial weapons"""
                            else:
                                """Checking if there is a proficiency in player skills"""
                                if feat_value['Prerequisite'][0].replace('Proficiency:', '') in V.character_dict[V.char_name]["Skills"]:
                                    if any(skill.split(":")[0] == feat_value['Prerequisite'][0].replace('Proficiency:', '') and int(skill.split(":")[1]) > 1 for skill in V.character_dict[V.char_name]["Skills"].split(",")):
                                        data_list.append(feat_key)
                        elif "Class" in feat_value["Prerequisite"][0]:
                            race = V.character_dict[V.char_name]["Race"]
                            if any(race == race_requirement.split(":")[1].capitalize() for race_requirement in feat_value["Prerequisite"]):
                                data_list.append(feat_key)
                        elif "Spellcasting" in feat_value["Prerequisite"][0]:
                            if V.character_dict[V.char_name].get("Spell Slots") != None:
                                data_list.append(feat_key)
                        elif "Level" in feat_value["Prerequisite"][0]:
                            level = V.character_dict[V.char_name]["Level"].split(",")[id[0]] # gets current class level
                            pass_grade = 0
                            for requirement in feat_value["Prerequisite"]:
                                if "Level" in requirement:
                                    level_requirement = requirement.split(":")[1]
                                    if int(level) >= int(level_requirement):
                                        pass_grade += 1
                                elif "Boon" in requirement:
                                    if V.character_dict[V.char_name].get("Boon") != None:
                                        if requirement.split[":"][1] in V.character_dict[V.char_name]["Boon"]:
                                            pass_grade += 1
                            if pass_grade == len(feat_value["Prerequisite"]):
                                data_list.append(feat_key)

                        elif "Boon" in feat_value["Prerequisite"][0]:
                            if V.character_dict[V.char_name].get("Boon") != None:
                                for requirement in feat_value["Prerequisite"]:
                                    if requirement.split[":"][1] in V.character_dict[V.char_name]["Boon"]:
                                        data_list.append(feat_key)
                        elif "Cantrip" in feat_value["Prerequisite"][0]:
                            cantrips = V.chosen_cantrips
                            if feat_value["Prerequisite"][0].split(":")[1] in list(cantrips.values()):
                                data_list.append(feat_key)
                        else:
                            F.print_debug(feat_value["Prerequisite"], debug="ERROR")
            data_list = F.enable_scrolling(data_list, scroll)
        elif "PROFICIENCY" == value[1]:
            """choosing a skill from a list of available skills for this class, first need to check if the skill is not yet proficient."""
            for i in range(2, len(value)):
                index = list(V.Skills.keys()).index(value[i])
                skill_proficiency = V.character_dict[V.char_name]["Skills"].split(",")[index]
                skill_name, skill_proficiency = skill_proficiency.split(":")
                if skill_proficiency == "1":
                    """Not proficient"""
                    data_list.append(value[i])
            """After checking and filling the data_list variable with the correct values we can now display a choosing method"""
        elif "EXPERTISE" == value[1]:
            """chosing a proficiency from a list of available proficiencies for this class. first need to check if skill is only proficient."""
            skill_names = list(V.Skills.keys())
            skills = V.character_dict[V.char_name]["Skills"].split(",")
            if value[2] != "":
                for extra_proficiencies in value[2].split(","):
                    if any(proficiency.split(":")[0] == extra_proficiencies and proficiency.split(":")[1] == str(V.Proficiecy_bonus) for proficiency in skills):
                        data_list.append(extra_proficiencies)
            for i in range(0, len(skill_names)):
                if skills[i].split(":")[1] == str(V.Proficiecy_bonus) and V.Skills[skill_names[i]][1] in V.Ability_score_list:
                    data_list.append(skill_names[i])
        elif "SUBCLASS" == value[1]:
            """Subclass, do everything like before but also drop describtion on sublasses and extra options to choose from."""
            for i in range(2, len(value)):
                data_list.append(value[i])
        elif "INCLUDING_FROM" == value[1]:
            """can make a choise but doesnt need to be diferent"""
            for i in range(2, len(value)):
                data_list.append(value[i])
        x, y = pos

        for i in range(0, int(option_count)):
            choise = choises.get((key, i))
            rect = F.display_dropbox(entry_screen1, "Choose " + key, (x, y), data_list, "closed", choise, (S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.03))
            data_dict[key, i] = rect
            x = x + S.SCREEN_WIDTH * 0.21
            if i != 0 and i % 3 == 0:
                """displays dropboxes lower on the y if they are crossing the x coordinate"""
                y += S.SCREEN_HEIGHT * 0.05
                x = pos[0]
                displayed_lower_flag += 1
        y = pos[1]
        if selected_dropbox != -1 and key == selected_dropbox[0]:
            """Drop box is down"""


            x = pos[0] + S.SCREEN_WIDTH * 0.21 * selected_dropbox[1]
            if selected_dropbox[1] > 3:
                """if selected drop box is technicly over the screen, this is used to adjust it lower, where it is displayed on the closed ones"""
                x = pos[0] + S.SCREEN_WIDTH * 0.21 * (selected_dropbox[1] - 4)
                y = pos[1] + S.SCREEN_HEIGHT * 0.05

            choise = choises.get((selected_dropbox[0], selected_dropbox[1]))
            rect = F.display_dropbox(entry_screen2, "Choose " + key, (x, y), data_list, "open", choise, (S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.03))
            data_dict[selected_dropbox[0], selected_dropbox[1]] = rect
            if choise != None:
                """Choise has been made"""
                if value[1] in ["PROFICIENCY", "EXPERTISE"]:
                    skills = V.character_dict[V.char_name]["Skills"].split(",")
                    index = list(V.Skills.keys()).index(choise)
                    if "PROFICIENCY" == value[1]:
                        """if proficiency is the choise"""
                        skills[index] = choise + ":" + str(V.Proficiecy_bonus)
                        V.character_dict[V.char_name]["Skills"] = ",".join(skills)
                    elif "EXPERTISE" == value[1]:
                        skills[index] = choise + ":" + str(V.Proficiecy_bonus * 2)
                        V.character_dict[V.char_name]["Skills"] = ",".join(skills)
                        """if expertise is the choise"""
                # else:
                    # V.character_dict[V.char_name]["Sub_Class"] = choise
        return data_dict, displayed_lower_flag

    if "--ADD" in value[0] and value[0][2] != "D":
        if "PROFICIENCY" in value[1]:
            for i in range(2, len(value)):
                property = "TOOL"
                if "Saving" in value[i]:
                    property = "Saving Throw"
                V.Skills[value[i]] = [V.Proficiecy_bonus, property]
                if V.character_dict[V.char_name].get("Skills") == None:
                    V.character_dict[V.char_name]["Skills"] = "Acrobatics:1,Animal Handling:1,Arcana:1,Athletics:1,Deception:1,Hitory:1,Insight:1,Intimidation:1,Investigation:1,Medicine:1,Nature:1,Perception:1,Performance:1,Persuasion:1,Religion:1,Sleight of Hand:1,Stealth:1,Survival:1"
                if value[i] not in V.character_dict[V.char_name]["Skills"]:
                    V.character_dict[V.char_name]["Skills"] += "," + value[i] + ":" + str(V.Proficiecy_bonus)
                else:
                    skills = V.character_dict[V.char_name]["Skills"].split(",")
                    if any(proficiency.split(":")[0] == value[i] and proficiency.split(":")[1] == "1" for proficiency in skills):
                        skills = [item if value[i] not in item else value[i] + ":" + str(V.Proficiecy_bonus) for item in skills]
                        V.character_dict[V.char_name]["Skills"] = ",".join(skills)
    return None, 0

def display_spell_describtion(screen, hovering_mouse, id, mode, data):
    color_school = {
        "Enchantment": "Dark BLue", # charming others, getting into their head
        "Abjuration": "Light Blue", # protective spells
        "Evocation": "Purple", # creating things out of nothing
        "Conjuration": "Dark Red", # summoning things, teleporting
        "Transmutation": "Gold", # change things into other things
        "Necromancy": "Dark Green", # death
        "Illusion": "Yellow", # changing appearance of things, creating sounds
        "Divination": "Magenta" # revealing information
    }
    spell_data = None
    subclass_data = None
    feat_data = None
    tool_data = None
    current_ability_scores = None
    if hovering_mouse == -1:
        return
    if len(hovering_mouse) == 3:
        combobox, name, rect = hovering_mouse
        combobox_type = combobox[0]
    if name == None:
        return
    if combobox_type == "Cantrip":
        spell_data = S.cantrip_data[name]
    elif combobox_type == "Spell":
        spell_data = S.spell_data[name]
    elif combobox_type in V.available_subclasses:
        if S.subclass_data == {}:
            with open(S.local_path + "/SubClass.json", 'r') as file:
                S.subclass_data = json.load(file)
        subclass_data = S.subclass_data[combobox_type][name]
    elif combobox_type in ["Feat"]:
        if S.feat_data == {}:
            with open(S.local_path + "/Feat-list.json", 'r') as file:
                S.feat_data = json.load(file)
        feat_data = S.feat_data[name]
    elif combobox_type == "Eldritch Invocations":
        if S.eldritch_incantations == {}:
            with open(S.local_path + "/Eldritch invocations.json", 'r') as file:
                S.eldritch_incantations = json.load(file)
        feat_data = S.eldritch_incantations[name]
    elif combobox_type in ["Fighting Style", "Fortune from the Many lv3"]:
        if S.Class_features != {}:
            feat_data = S.Class_features[combobox_type][name]

    elif combobox_type == "Tool Proficiencies":
        tool_data = V.item_dict[name.replace("'", "")]
    elif combobox_type == "Ability Score":
        current_ability_scores = V.character_dict[V.char_name]["Ability_Scores"].split(",")
        for k in data.keys():
            if data[k].get("Ability Score") != None:
                for i, sc_name in enumerate(V.Ability_score_list):
                    current_ability_scores[i] = int(current_ability_scores[i]) + data[k]["Ability Score"].count(sc_name)
    else:
        print("Returning", combobox, name, rect, combobox_type)
        return
    if spell_data != None:
        step_y = S.SCREEN_HEIGHT * 0.03
        F.display_text(screen, name, 30, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.05), color=color_school[spell_data["School"]])
        rect = F.display_text(screen, "School: ", 15, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1))
        F.display_text(screen, spell_data["School"], 15, (rect.x + rect.w, rect.y), italic=True)
        step_y += S.SCREEN_HEIGHT * 0.03

        F.display_text(screen, "Casting Time: " + spell_data["Casting Time"], 15, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1 + step_y))
        step_y += S.SCREEN_HEIGHT * 0.03

        F.display_text(screen, "Range: " + spell_data["Range"], 15, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1 + step_y))
        step_y += S.SCREEN_HEIGHT * 0.03

        F.display_text(screen, "Duration: " + spell_data["Duration"], 15, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1 + step_y))
        step_y += S.SCREEN_HEIGHT * 0.03

        F.display_text(screen, "Components: " + spell_data["Components"], 15, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1 + step_y))
        step_y += S.SCREEN_HEIGHT * 0.03

        if spell_data.get("Level"):
            F.display_text(screen, "Level: " + spell_data["Level"], 15, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1 + step_y))
            step_y += S.SCREEN_HEIGHT * 0.03

        if spell_data.get("Ritual"):
            F.display_text(screen, "Ritual: " + spell_data["Ritual"], 15, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1 + step_y))
            step_y += S.SCREEN_HEIGHT * 0.03

        start_x = S.SCREEN_WIDTH * 0.5
        start_y =  S.SCREEN_HEIGHT * 0.1 + step_y
        description = "Description: "
        if mode == "Simple":
            mode = "Description_for_dummies"
            if spell_data.get("Damage") != None:
                F.display_text(screen, "1st Level Damage: " + spell_data["Damage"], 15, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1 + step_y))
                step_y += S.SCREEN_HEIGHT * 0.03

            if spell_data.get("Type") != None:
                F.display_text(screen, "Type: " + spell_data["Type"], 15, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1 + step_y))
                step_y += S.SCREEN_HEIGHT * 0.03

            start_y = S.SCREEN_HEIGHT * 0.1 + step_y
            description = "Simplefied: "
        elif mode == "At Higher Levels":
            mode = "At higher levels"
            if spell_data.get("Damage") != None:
                F.display_text(screen, "1st Level Damage: " + spell_data["Damage"], 15, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1 + step_y))
                step_y += S.SCREEN_HEIGHT * 0.03

            if spell_data.get("Type") != None:
                F.display_text(screen, "Type: " + spell_data["Type"], 15, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1 + step_y))
                step_y += S.SCREEN_HEIGHT * 0.03

            start_y = S.SCREEN_HEIGHT * 0.1 + step_y
            description = "At Higher Levels: "


        if spell_data.get(mode) != None:
            word_length = F.display_text(screen, description, 15, (start_x, start_y))
            y_step = 0
            start_x += word_length.w
            for word in spell_data[mode].split(" "):
                if 'â€™' in word:
                    word = word.replace('â€™', "'")
                word = word.replace("\n\n", " ")
                word = word.replace("\n", " ")
                word_length = F.display_text(screen, word + " ", 15,(start_x, start_y + y_step))
                start_x = word_length.x + word_length.w
                if word_length.w + word_length.x >= S.SCREEN_WIDTH - 100:
                    y_step += S.SCREEN_HEIGHT * 0.03
                    word_length.w = 0
                    start_x = S.SCREEN_WIDTH * 0.5
    elif subclass_data != None:
        start_x = S.SCREEN_WIDTH * 0.5
        start_y = S.SCREEN_HEIGHT * 0.05
        step_y = S.SCREEN_HEIGHT * 0.05
        F.display_text(screen, name, 30, (start_x, start_y))
        for text_key, text_value in subclass_data.items():
            start_y = start_y + step_y + S.SCREEN_HEIGHT * 0.02
            step_y = S.SCREEN_HEIGHT * 0.03

            F.display_text(screen, text_key + ": ", 20, (start_x, start_y))
            for text_sub_key, text_sub_value in text_value.items():
                if mode == "Description" and text_sub_key not in ["Description"]:
                    continue

                elif mode == "Simple" and text_sub_key in ["Description", "At higher levels"]:
                    continue

                elif mode.lower() == "at higher levels" and text_sub_key not in ["At higher levels"]:
                    continue

                if text_sub_key == "Description_for_dummies":
                    text_sub_key = "Simplified"
                if text_sub_key == "":
                    continue
                word_length = F.display_text(screen, text_sub_key + ": ", 13, (start_x, start_y + step_y))
                start_x += word_length.w
                if isinstance(text_sub_value, list):
                    text_sub_value = " ".join(text_sub_value)
                if isinstance(text_sub_value, dict):
                    text_sub_value = str(text_sub_value)
                for word in text_sub_value.split(" "):
                    word = word.replace('â€™', "'")
                    word = word.replace("\n\n", " ")
                    word = word.replace("\n", " ")

                    word_length = F.display_text(screen, word + " ", 13, (start_x, start_y + step_y))
                    start_x = word_length.x + word_length.w
                    if word_length.w + word_length.x >= S.SCREEN_WIDTH - 100:
                        step_y += S.SCREEN_HEIGHT * 0.02
                        word_length.w = 0
                        start_x = S.SCREEN_WIDTH * 0.5
                step_y += S.SCREEN_HEIGHT * 0.03
                start_x = S.SCREEN_WIDTH * 0.5
    elif feat_data != None:
        start_x = S.SCREEN_WIDTH * 0.5
        start_y = S.SCREEN_HEIGHT * 0.05
        step_y = S.SCREEN_HEIGHT * 0.02
        F.display_text(screen, name, 30, (start_x, start_y))
        for text_key, text_value in feat_data.items():
            start_y = start_y + step_y
            step_y = S.SCREEN_HEIGHT * 0.03

            if mode == "Description" and text_key in ["Description_for_dummies"]:
                continue

            elif mode == "Simple" and text_key in ["Description", "At higher levels"]:
                continue

            elif mode.lower() == "at higher levels" and text_key not in ["At higher levels"]:
                continue

            if text_key == "Description_for_dummies":
                text_key = "Simplified"

            if text_value == "":
                continue

            word_length = F.display_text(screen, text_key.capitalize() + ": ", 15, (start_x, start_y + step_y))
            start_x += word_length.w
            if isinstance(text_value, list):
                text_value = " ".join(text_value)

            for word in text_value.split(" "):
                word = word.replace("\n\n", " ")
                word = word.replace("\n", " ")

                word_length = F.display_text(screen, word + " ", 15, (start_x, start_y + step_y))
                start_x = word_length.x + word_length.w
                if word_length.w + word_length.x >= S.SCREEN_WIDTH - 150:
                    step_y += S.SCREEN_HEIGHT * 0.03
                    word_length.w = 0
                    start_x = S.SCREEN_WIDTH * 0.5
            step_y += S.SCREEN_HEIGHT * 0.03
            start_x = S.SCREEN_WIDTH * 0.5
    elif tool_data != None:
        start_x = S.SCREEN_WIDTH * 0.5
        start_y = S.SCREEN_HEIGHT * 0.05
        step_y = S.SCREEN_HEIGHT * 0.02
        F.display_text(screen, name, 30, (start_x, start_y))
        start_y = S.SCREEN_HEIGHT * 0.08
        for text_key, text_value in tool_data.items():
            step_y = S.SCREEN_HEIGHT * 0.03
            if text_key in ["image", "Type", "Properties"]:
                continue
            if text_value == "":
                continue
            start_y += step_y

            if text_key == "Extra":
                text_key = "Description"
            word_length = F.display_text(screen, text_key.capitalize() + ": ", 15, (start_x, start_y))
            start_x += word_length.w
            if isinstance(text_value, list):
                text_value = " ".join(text_value)

            for i, word in enumerate(text_value.split(" ")):
                word = word.replace("\n\n", " ")
                word = word.replace("\n", " ")

                word_length = F.display_text(screen, word + " ", 15, (start_x, start_y))
                start_x = word_length.x + word_length.w
                if word_length.w + word_length.x >= S.SCREEN_WIDTH - 150:
                    start_y += step_y
                    word_length.w = 0
                    start_x = S.SCREEN_WIDTH * 0.5
            start_x = S.SCREEN_WIDTH * 0.5
    elif current_ability_scores != None:
        start_x = S.SCREEN_WIDTH * 0.5
        start_y = S.SCREEN_HEIGHT * 0.05
        for ab_id, ab_name in enumerate(V.Ability_score_list):
            word_length = F.display_text(screen, ab_name + ": " + str(current_ability_scores[ab_id]), 15, (start_x, start_y))
            start_x += word_length.w * 1.1


def reformat_data(data):
    unwanted_data_list = ['--ADD', 'PROFICIENCY', 'key', "--CODE", "--ADD_NOW"]
    def extract_values(nested_list):
        """Extract only relevant values from nested lists, filtering out unwanted elements."""
        if isinstance(nested_list, list):
            if len(nested_list) > 0 and isinstance(nested_list[0], list):
                # Flatten the list and remove unwanted elements
                return [item for item in nested_list[0] if item not in unwanted_data_list]
            else:
                # If it's not a nested list, return it as is
                return [item for item in nested_list if item not in unwanted_data_list]
        return nested_list

    reformatted = {}
    for class_name, levels in data.items():
        reformatted[class_name] = {}
        for level, attributes in levels.items():
            reformatted[class_name][level] = {}
            if isinstance(attributes, dict):
                for attribute, value in attributes.items():
                    reformatted[class_name][level][attribute] = extract_values(value)
            elif isinstance(attributes, list):
                if len(attributes) == 1:
                    reformatted[class_name][level] = extract_values(attributes)
                elif len(attributes) == 3 and level == "Ability Score":
                    reformatted[class_name][level] = extract_values(attributes)
                else:
                    raise ValueError(f"Attribute format error {attributes}")
                # if len(attributes) == 1:
                #     if attributes[0][0] == "--ADD":
                #         if "Char" in attributes[0][1]:
                #             if "Ability_Scores" in attributes[0][1]:
                #                 ability_score, count = attributes[0][2].split(":")
                #                 index = V.Ability_score_list.index(ability_score)
                #                 scores = V.character_dict[V.char_name]["Ability_Scores"].split(",")
                #                 scores[index] = str(int(scores[index]) + int(count))
                #                 V.character_dict[V.char_name]["Ability_Scores"] = ",".join(scores)
                #             elif "," in attributes[0][1]:
                #                 attribute = attributes[0][1].replace("Char:","").split(",")
                #                 for i in range(0, len(attribute)):
                #                     if attributes[0][2].split(",")[i] not in V.character_dict[V.char_name][attribute[i]]:
                #                         char_values = V.character_dict[V.char_name][attribute[i]].split(",")
                #                         char_values.append(attributes[0][2].split(",")[i])
                #                         V.character_dict[V.char_name][attribute[i]] = ",".join(char_values)
                #             else:
                #                 V.character_dict[V.char_name][attributes[0][1].split(":")[1]] = attributes[0][2]
                #         else:
                #             F.print_debug("no char in here: ", attributes)
                # else:
                #     raise ValueError(f"Attribute format error {attributes}")
                # F.print_debug("Attributes: ", attributes, "level: ", level)
    return reformatted


def load_char_data(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    """reset values"""
    V.character_dict[V.char_name]["Skills"] = "Acrobatics:1,Animal Handling:1,Arcana:1,Athletics:1,Deception:1,History:1,Insight:1,Intimidation:1,Investigation:1,Medicine:1,Nature:1,Perception:1,Performance:1,Persuasion:1,Religion:1,Sleight of Hand:1,Stealth:1,Survival:1"
    if V.character_dict[V.char_name].get("Sub_Class") != None:
        del V.character_dict[V.char_name]["Sub_Class"]
    V.character_dict[V.char_name]["Spell Slots"] = ""
    V.chosen_cantrips = {}
    V.chosen_spells = {}

    for char_class, value in data.items():
        if char_class in ["Chosen_spells", "Notes", "Chosen_cantrips"]:
            continue
        for char_level, value_2 in value.items():
            if isinstance(value_2, dict):
                for property, values in value_2.items():
                    # F.print_debug("PROPERTY: ", property, "VALUES: ", values)
                    if property in V.available_subclasses:
                        property = "SubClass"
                    if V.character_dict[V.char_name].get(property) == None:
                        V.character_dict[V.char_name][property] = ""
                    for val in values:
                        if property == "Saving Throw Proficiencies":
                            val = val.replace("Saving_", "")
                        if property == "Skills":
                            skills = V.character_dict[V.char_name]["Skills"].split(",")
                            index = skills.index(val + ":1")
                            skills[index] = val + ":" + str(V.Proficiecy_bonus)
                            V.character_dict[V.char_name]["Skills"] = ",".join(skills)
                            continue
                        if property == "Expertise":
                            skills = V.character_dict[V.char_name]["Skills"].split(",")
                            index = skills.index(val + ":" + str(V.Proficiecy_bonus))
                            skills[index] = val + ":" + str(V.Proficiecy_bonus * 2)
                            V.character_dict[V.char_name]["Skills"] = ",".join(skills)
                            if V.character_dict[V.char_name].get(property) == "":
                                del V.character_dict[V.char_name][property]
                            continue
                        if property == "Ability Score":
                            ability_scores = V.character_dict[V.char_name]["Ability_Scores"].split(",")
                            index = V.Ability_score_list.index(val)
                            ability_scores[index] = str(int(ability_scores[index]) + 1)
                            V.character_dict[V.char_name]["Ability_Scores"] = ",".join(ability_scores)
                            if V.character_dict[V.char_name].get(property) == "":
                                del V.character_dict[V.char_name][property]
                            continue
                        if V.character_dict[V.char_name][property] == "" or property in ["Sneak Attack", "Proficiency Bonus", "Spell Slots", "Rage", "Hit dice", "Hemocraft_die", "Arcane Recovery", "Sorcery Points"]:
                            """Updatable properties aka replaces the old value with the new if it is bigger."""
                            if property in ["Hit dice", "Hemocraft_die"]:
                                multipyer, dice = val.split("d")
                                maximum_roll = int(dice) * int(multipyer)
                                if V.character_dict[V.char_name][property] != "" and int(V.character_dict[V.char_name][property].split("d")[0]) * int(V.character_dict[V.char_name][property].split("d")[1]) > int(maximum_roll):
                                    """if current hit dice average is bigger than the new one dont save it."""
                                    continue
                                V.character_dict[V.char_name][property] = str(val)
                                continue
                            if property == "Proficiency Bonus" and V.character_dict[V.char_name][property] != "" and int(V.character_dict[V.char_name][property]) > int(val):
                                continue
                            V.character_dict[V.char_name][property] = str(val)
                        else:
                            if val not in V.character_dict[V.char_name][property]:
                                V.character_dict[V.char_name][property] += "," + str(val)
                            elif property in ["Extra Attack"]:
                                V.character_dict[V.char_name][property] = str(int(V.character_dict[V.char_name][property]) + int(val))
            elif isinstance(value_2, list):
                property = char_level
                values = value_2
                if property == "Ability Score":
                    property = "Ability_Scores"
                if V.character_dict[V.char_name].get(property) == None:
                    V.character_dict[V.char_name][property] = ""
                for val in values:

                    if "Char:" in val:
                        property = val.split(":")[1]
                        continue
                    if property == "Saving Throw Proficiencies":
                        val = val.replace("Saving_", "")
                    if property == "Skills":
                        skills = V.character_dict[V.char_name]["Skills"].split(",")
                        index = skills.index(val + ":1")
                        skills[index] = val + ":" + str(V.Proficiecy_bonus)
                        V.character_dict[V.char_name]["Skills"] = ",".join(skills)
                        continue
                    if property == "Expertise":
                        skills = V.character_dict[V.char_name]["Skills"].split(",")
                        index = skills.index(val + ":" + str(V.Proficiecy_bonus))
                        skills[index] = val + ":" + str(V.Proficiecy_bonus * 2)
                        V.character_dict[V.char_name]["Skills"] = ",".join(skills)
                        if V.character_dict[V.char_name].get(property) == "":
                            del V.character_dict[V.char_name][property]
                        continue
                    if property == "Ability Score" or property == "Ability_Scores":
                        ability_scores = V.character_dict[V.char_name]["Ability_Scores"].split(",")
                        index = V.Ability_score_list.index(val)
                        ability_scores[index] = str(int(ability_scores[index]) + 1)
                        V.character_dict[V.char_name]["Ability_Scores"] = ",".join(ability_scores)
                        if V.character_dict[V.char_name].get(property) == "":
                            del V.character_dict[V.char_name][property]
                        continue
                    if V.character_dict[V.char_name][property] == "" or property in ["Sneak Attack","Proficiency Bonus","Spell Slots", "Speed"]:
                        if property == "Proficiency Bonus" and V.character_dict[V.char_name][property] != "" and int(V.character_dict[V.char_name][property]) > int(val):
                            continue
                        V.character_dict[V.char_name][property] = str(val)
                    else:
                        if val not in V.character_dict[V.char_name][property]:
                            V.character_dict[V.char_name][property] += "," + str(val)

    return data


def compare_JSON_DN(data, screen, clock):
    """Checks the max level recorded in the json data vs the level it should be"""
    classes_lv = {}
    for char_class, value in data.items():
        max_lv = 0
        if char_class in ["Chosen_spells", "Notes", "Chosen_cantrips"]:
            continue
        for char_lv, values in value.items():
            if any(not char.isdigit() for char in char_lv):
                continue
            if int(char_lv) > max_lv:
                max_lv = int(char_lv)
        classes_lv[char_class] = max_lv

    char_classes = V.character_dict[V.char_name]["Class"].split(", ")
    char_levels = V.character_dict[V.char_name]["Level"].split(",")
    if classes_lv[char_classes[0]] != int(char_levels[0]):
        data = get_player_choises(V.character_dict[V.char_name], screen, clock, (0, classes_lv[char_classes[0]]), data={})
        data = reformat_data(data)
        F.create_char_JSON(V.char_name, data)
    if len(char_classes) == 2 and classes_lv[char_classes[1]] != int(char_levels[1]):
        data = get_player_choises(V.character_dict[V.char_name], screen, clock, (1, classes_lv[char_classes[1]]), data={})
        data = reformat_data(data)
        F.create_char_JSON(V.char_name, data)

def dice_roll_Thread(count):
    while True:
        time.sleep(0.1)
        if S.Thread_variable["D20"] == -2:
            break
        if S.Thread_variable["D20"] != -1:
            S.Thread_variable["D20"] += 1
            if S.Thread_variable["D20"] >= count:
                S.Thread_variable["D20"] = -1

def display_reactions(screen):
    if V.Reactions != {}:
        file_dict = {"Feature": S.Class_features,
                     "Spell": S.spell_data,
                     "Cantrip": S.cantrip_data}
        step_y = 0
        for reaction_name, reaction_type in V.Reactions.items():
            data = file_dict[reaction_type]
            trigger = data[reaction_name]["Trigger"]
            if trigger == "Damaged":
                F.display_text(screen, "Use " + reaction_name + " " + reaction_type, 20, (S.SCREEN_WIDTH * 0.7, S.SCREEN_HEIGHT * 0.58 + step_y), color="red")
                step_y += S.SCREEN_HEIGHT * 0.04
            elif "Damaged by:" in trigger:
                F.display_text(screen, "If you were damaged by: " + trigger.split(":")[1] + ", then use " + reaction_name, 20, (S.SCREEN_WIDTH * 0.7, S.SCREEN_HEIGHT * 0.58 + step_y))
                step_y += S.SCREEN_HEIGHT * 0.04

def handle_add_NOW(value):
    if "Char" in value[1]:
        if "Skills" in value[1]:
            char_skills = V.character_dict[V.char_name]["Skills"].split(",")
            skill_names = list(V.Skills.keys())
            index = skill_names.index(value[2])
            char_skills[index] = value[2] + ":" + str(V.Proficiecy_bonus)
            V.character_dict[V.char_name]["Skills"] = ",".join(char_skills)


def roll_and_check_concentration_keeping(screen, clock, character, hp):
    if V.consentration != {}:
        dtwenty = random.randint(1, 20)
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        F.display_text(screen, "Checking if consentration breaks", 30, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1), case="C")
        F.Roll_3d_dice(screen, clock, "D20", str(dtwenty), (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.5))
        rolled_20 = dtwenty
        """Get keep concentration SAVE DC"""
        if hp < 20:
            save_dc = 10
        else:
            save_dc = int(hp / 2)

        if "CON" in character["Saving Throw Proficiencies"]:
            dtwenty += V.Proficiecy_bonus
        dtwenty += V.score_modifiers["CON"]
        """ add proficiency if applicable and CON mod """
        F.add_to_roll_history(str(rolled_20), str(dtwenty), "Concentration check")

        if dtwenty < save_dc:
            """if concentration lost, change variable value"""
            V.consentration = str(list(V.consentration.keys())[0]) + ":" + str(list(V.consentration.values())[0][0]) + ":60"

def update_choise(value, char, id):
    if "MOD" in value[0]:
        value[0] = value[0].replace(" MOD", "")
        value_split = value[0].split(":")
        add_1, add_2 = value_split[1].split("+")
        add_1 = V.score_modifiers[add_1]
        if not add_2.isdigit():
            if add_2.lower() == "lv":
                add_2 = char["Level"].split(",")[id[0]]
        value_split[1] = str(int(add_1) + int(add_2))
        value[0] = ":".join(value_split)
    return value


