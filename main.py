import time, os

import pygame as pg, Settings as S, os, Variables as V, Functions as F, conditions as C, Items as I
import DisplayChar as dCh, json, threading, Special_Needs as special
from Settings import SCREEN_HEIGHT, SCREEN_WIDTH
import random, math, shutil


def Start(CODE, screen, clock):
    """ first get dices"""

    # todo Undcomment after done debbuging
    image_path = S.local_path + "/Images/Background/Roling_Dice/D20/"
    V.d20_img_count = len([f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))])
    start = time.perf_counter()
    for dice_type in ["D4", "D6", "D8", "D10", "D12", "D20"]:
    #     make_sheets(S.local_path + f"/Images/Background/Roling_Dice/{dice_type}/", int(dice_type.split("D")[1]))
        thread = threading.Thread(target=load_dice_images, args=(dice_type, ))
        thread.daemon = False
        thread.start()
    print(f"End: {(time.perf_counter() - start)}") # 4.6 sec with reduced quality 5 percent memory increase


    read_json_data()

    secret_data = F.read_db_table("communication")
    if secret_data == None:
        print("Failed to connect to DB")
        return
    V.SECRETS = F.add_to_dict_db_results(secret_data, V.SECRETS, "communications")

    char_name = Choose_char(CODE, screen, clock)
    if char_name == 0:
        return
    V.char_name = char_name

    if V.char_config == {}:
        with open(S.local_path + f"/Created_Players/{V.char_name}_config.json", 'r') as file:
            V.char_config = json.load(file)

    V.Roll_history = []


    if V.character_dict == {}:
        F.print_debug("collecting char data", debug="INFO")
        char_data = F.read_db_table("characters")
        F.print_debug("converting char data to dict", debug="INFO")
        V.character_dict = F.add_to_dict_db_results(char_data, V.character_dict, "characters")
        if V.character_dict.get(V.char_name) == None:
            # V.char_name = "G"
            # V.character_dict[V.char_name] = {'Gold': '10', 'Alignment': 'Neutral', 'Level': '5', 'Class': 'Paladin', 'Race': 'Dwarf', 'Languages': 'Common', 'Ability_Scores': '12,12,12,12,12,12', "Health": [50, 50]}
            Enter_char_details(screen, clock)
            # F.print_debug("UNCOMMENT THIS", "", "Warning")

        mob_data = F.read_db_table("monsters")
        V.mob_dict = F.add_to_dict_db_results(mob_data, V.mob_dict, "mobs")
        F.get_mob_actions()
    else:
        F.print_debug("DIDN'T GET CHAR DICT", debug="ERROR")
        return

    F.read_json_item_data()

    dCh.check_class_features(screen, clock)

    update_character_data(V.char_name)

    if V.character_dict[V.char_name].get("Primary Ability") != None:
        """Check which is bigger, use that"""
        second_mod = 0
        first_mod = int(V.score_modifiers[V.character_dict[V.char_name]["Primary Ability"][0:3].upper()])
        if "," in V.character_dict[V.char_name]["Primary Ability"]:
            second_mod = int(V.score_modifiers[V.character_dict[V.char_name]["Primary Ability"].split(",")[1][0:3].upper()])
        if first_mod > second_mod:
            V.spellcasting_ability_mod = first_mod
        else:
            V.spellcasting_ability_mod = second_mod

    V.Spell_save_DC = 8 + V.Proficiecy_bonus + V.spellcasting_ability_mod
    V.Spell_attack = V.Proficiecy_bonus + V.spellcasting_ability_mod

    I.get_equiped_items()

    get_hp_if_required(screen, clock)
    running = True

    edit_variables_py(CODE)
    # F.print_debug("UNCOMMENT THIS", "", "Warning")
    text_size = 30
    dict = {
        0: ["See Items", "background", "background", "rect-place-holder", "black"],
        1: ["See Character", "background", "background", "rect-place-holder", "black"],
        2: ["Exit", "background", "background", "rect-place-holder", "black"],
    }
    extra = {
        0: ["Short Rest", "background", "background", "rect-place-holder", "black"],
        1: ["Long Rest", "background", "background", "rect-place-holder", "black"],
    }
    extra_2 = {
        0: ["Read Data", "background", "background", "rect-place-holder", "red"],
        1: ["Settings", "background", "background", "rect-place-holder", "black"]
                       }
    pressed = -1

    F.reset_spellSlots(0)
    while running:
        # remove_slot = []
        button_width = S.SCREEN_WIDTH / 5
        button_height = S.SCREEN_HEIGHT / 20
        screen_top1 = S.SCREEN_HEIGHT * 0.9
        screen_top2 = S.SCREEN_HEIGHT * 0.83
        x_pos1 = [S.SCREEN_WIDTH * 0.7, S.SCREEN_WIDTH * 0.4, S.SCREEN_WIDTH * 0.1]
        x_pos2 = [S.SCREEN_WIDTH * 0.55, S.SCREEN_WIDTH * 0.25, S.SCREEN_WIDTH]
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_other_buttons(screen, text_size, ([S.SCREEN_WIDTH * 0.1, S.SCREEN_WIDTH * 0.7], (S.SCREEN_HEIGHT * 0.1), button_width, button_height), extra_2)
        buttons = F.display_other_buttons(screen, text_size, (x_pos2, screen_top2, button_width, button_height), extra) + buttons
        buttons = F.display_other_buttons(screen, text_size, (x_pos1, screen_top1, button_width, button_height), dict) + buttons
        if V.SECRETS.get(V.char_name) != None and V.SECRETS[V.char_name]["Name"] == 1:
            F.display_text(screen, "Hello, Person, Welcome to your world", 30, (S.SCREEN_WIDTH / 2, S.SCREEN_HEIGHT / 4), "black", "C")
        else:
            F.display_text(screen, "Hello, " + V.char_name + ", Welcome to your world", 30, (S.SCREEN_WIDTH / 2, S.SCREEN_HEIGHT / 4), "black", "C")

        for event in pg.event.get():
            if event.type == pg.QUIT:
                if V.Condition == 'Exhaustion lv6':
                    F.print_debug("YOU HAVE DIED", debug="ERROR")
                else:
                    running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                pos = pg.mouse.get_pos()
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(pos):
                        pressed = i
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                # for name, values in displayed_slots.items():
                #     for i in range(len(values)):
                #         if values[i].collidepoint(pos):
                #             pressed = [name, i]
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                pos = pg.mouse.get_pos()
                if pressed != -1 and isinstance(pressed, int) and buttons[pressed].collidepoint(pos):
                    if pressed == 0:
                        if V.Condition == 'Exhaustion lv6':
                            dict = {}
                            extra = {}
                            extra_2 = {}
                            pressed = -1
                            continue
                        I.display_char_items(screen, V.char_name, clock)
                    elif pressed == 1:
                        if V.Condition == 'Exhaustion lv6':
                            dict = {}
                            extra = {}
                            extra_2 = {}
                            pressed = -1
                            continue
                        dCh.selected_char_display(V.char_name, screen, clock)
                        if V.Condition == 'Exhaustion lv6':
                            F.DEATH(screen, clock)


                    elif pressed == 2:
                        if V.Condition == 'Exhaustion lv6':
                            dict = {}
                            extra = {}
                            extra_2 = {}
                            pressed = -1
                            continue
                        running = False
                        return
                    elif pressed == 3:
                        if V.Condition == 'Exhaustion lv6':
                            dict = {}
                            extra = {}
                            extra_2 = {}
                            pressed = -1
                            continue
                        """some features work on short rests"""
                        Take_a_SHORT_rest(screen, clock)

                    elif pressed == 4:
                        if V.Condition == 'Exhaustion lv6':
                            dict = {}
                            extra = {}
                            extra_2 = {}
                            pressed = -1
                            continue
                        Take_a_LONG_rest()

                    elif pressed == 5:
                        if V.Condition == 'Exhaustion lv6':
                            dict = {}
                            extra = {}
                            extra_2 = {}
                            pressed = -1
                            continue
                        ReadData_Clicked(screen, clock)
                    elif pressed == 6:
                        if V.Condition == 'Exhaustion lv6':
                            dict = {}
                            extra = {}
                            extra_2 = {}
                            pressed = -1
                            continue
                        exiting = user_settings(screen, clock)
                        if exiting:
                            return

        pg.display.flip()
        clock.tick(60)

def ReadData_Clicked(screen, clock):
    running = True
    text_size = 30
    button_dict = {
        0: ["Armor", "background", "background", "rect-place-holder", "black"],
        1: ["Weapons", "background", "background", "rect-place-holder", "black"],
        2: ["Special", "background", "background", "rect-place-holder", "black"],
        3: ["Mounts", "background", "background", "rect-place-holder", "black"],
    }
    button2_dict = {
        0: ["Ingredients", "background", "background", "rect-place-holder", "black"],
        1: ["Food", "background", "background", "rect-place-holder", "black"],
        2: ["Potions", "background", "background", "rect-place-holder", "black"],
    }
    button3_dict = {
        0: ["Magic Weapons", "background", "background", "rect-place-holder", "black"],
        1: ["Magic Armor", "background", "background", "rect-place-holder", "black"],
        2: ["Wonderous Items", "background", "background", "rect-place-holder", "black"],
        3: ["Coms", "background", "background", "rect-place-holder", "black"],
    }
    Available_keys = {
        "Armor": ["armour", False],
        "Weapons": ["weapons", False],
        "Special": ["special", False],
        "Mounts": ["mount", False],
        "Potions": ["potions", False],
        "Food": ["food", False],
        "Ingredients": ["ingredient", False],
        "Magic Weapons": ["magic weapon", True],
        "Magic Armor": ["magic armour", True],
        "Wonderous Items": ["Wonderous Item", True],
        "Coms": ["communication", "communications"],
                      }



    pressed = -1
    while running:
        x_pos1 = [S.SCREEN_WIDTH * 0.02, S.SCREEN_WIDTH * 0.27, S.SCREEN_WIDTH * 0.52, S.SCREEN_WIDTH * 0.77]
        screen_top1 = S.SCREEN_HEIGHT * 0.1
        screen_top2 = S.SCREEN_HEIGHT * 0.3
        screen_top3 = S.SCREEN_HEIGHT * 0.5
        button_width = S.SCREEN_WIDTH / 5
        button_height = S.SCREEN_HEIGHT / 20
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Back")
        buttons = F.display_other_buttons(screen, text_size, (x_pos1, screen_top3, button_width, button_height), button3_dict) + buttons
        buttons = F.display_other_buttons(screen, text_size, (x_pos1, screen_top2, button_width, button_height), button2_dict) + buttons
        buttons = F.display_other_buttons(screen, text_size, (x_pos1, screen_top1, button_width, button_height), button_dict) + buttons
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                pos = pg.mouse.get_pos()
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(pos):
                        pressed = "back"
                        if button_dict.get(i) != None:
                            pressed = button_dict[i][0]
                            pg.draw.rect(screen, "black", buttons[i], width=3)
                            break
                        elif button2_dict.get(i - 4) != None:
                            pressed = button2_dict[i-4][0]
                            pg.draw.rect(screen, "black", buttons[i], width=3)
                            break
                        elif button3_dict.get(i - 7) != None:
                            pressed = button3_dict[i-7][0]
                            pg.draw.rect(screen, "black", buttons[i], width=3)
                            break
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if Available_keys.get(pressed) != None:
                        F.print_debug(f"collecting {pressed} data", debug="INFO")
                        data = F.read_db_table(Available_keys[pressed][0])
                        F.print_debug(f"converting {pressed} data to dict", debug="INFO")
                        if pressed != "Coms":
                            V.item_dict = F.add_to_dict_db_results(data, V.item_dict, Available_keys[pressed][1])
                        else:
                            V.SECRETS = {}
                            V.SECRETS = F.add_to_dict_db_results(data, V.SECRETS, Available_keys[pressed][1])
                        F.upload_to_json(V.item_dict, S.local_path + "/" + pressed + ".json", Available_keys[pressed][0])
                        for key, value in button_dict.items():
                            if value[0] == pressed:
                                value[4] = "green"
                        for key, value in button2_dict.items():
                            if value[0] == pressed:
                                value[4] = "green"
                        for key, value in button3_dict.items():
                            if value[0] == pressed:
                                value[4] = "green"
                        pressed = -1
                    else:
                        running = False
                        return
        pg.display.flip()
        clock.tick(60)

def load_dice_images(dice_type):
    S.dice_images[dice_type] = {}
    S.dice_images["Finished"][dice_type] = {}
    img_w = 1920 * 0.2
    img_h = 1080 * 0.2
    for dice_number in range(1, int(dice_type.replace("D", "")) + 1):
        S.dice_images[dice_type][str(dice_number)] = []
        S.dice_images["Finished"][dice_type][str(dice_number)] = False
        # for i in range(0, 100):
        #     try:
        #         img = pg.image.load(S.local_path + "/Images/Background/Roling_Dice/" + dice_type + "/" + str(dice_number) + "/" + str(dice_number) + "_" + str(i) + ".png")
        #         while S.Thread_lock:
        #             time.sleep(0.05)
        #         S.Thread_lock = True
        #         S.dice_images[dice_type][str(dice_number)].append(img)
        #         S.Thread_lock = False
        #     except FileNotFoundError:
        #         break
        while S.Thread_lock:
            time.sleep(0.1)
        S.Thread_lock = True
        img = extract_frames(S.local_path + "/Images/Background/Roling_Dice/" + dice_type + f"/Sprite_{dice_number}.png", img_w, img_h)
        images = []
        for image in img:
            images.append(pg.transform.scale_by(image, 2))
        S.dice_images[dice_type][str(dice_number)] = images
        S.Thread_lock = False
        S.dice_images["Finished"][dice_type][str(dice_number)] = True
    F.print_debug(dice_type, " Finished", debug="INFO")
    # S.dice_images["Finished"][dice_type] = True

def make_sheets(path, amount):
    original_w = 1920
    original_h = 1080
    frame_rect = pg.Rect(original_w * 0.3, original_h * 0.3, original_w * 0.3, original_h * 0.3)
    for dice_num in range(1, amount + 1):
        frames = []
        for i in range(0, 1000):
            try:
                a = pg.image.load(path + f"/{dice_num}/{dice_num}_{i}.png").convert_alpha()
                a = a.subsurface(frame_rect).copy()  # copy to make independent
                frames.append(a)
            except FileNotFoundError:
                break
        if frames != []:
            f_w, f_h = frames[0].get_size()
            sheet_surface = pg.Surface((f_w * len(frames), f_h), pg.SRCALPHA)
            for i, f in enumerate(frames):
                sheet_surface.blit(f, (i * f_w, 0))

            pg.image.save(sheet_surface, path + f"Sprite_Crop{dice_num}.png")
            print(path + f"Sprite_{dice_num}.png Saved")

def extract_frames(path, frame_width, frame_height):
    if not os.path.exists(path):
        return None
    sprite_sheet = pg.image.load(path).convert_alpha()
    img_w, img_h = sprite_sheet.get_size()
    frames = []
    y = 0
    x = 0
    for i in range(0, 1000):
        try:
            frame_rect = pg.Rect(x * frame_width, y * frame_height, frame_width, frame_height)
            frame = sprite_sheet.subsurface(frame_rect).copy()  # copy to make independent
            frames.append(frame)
            x += 1
        except ValueError:
            break

    return frames

def read_json_data():
    if S.class_data == {}:
        with open(S.local_path + '/Classes.json', 'r') as file:
            S.class_data = json.load(file)

    if S.cantrip_data == {}:
        with open(S.local_path + "/Cantrips.json", 'r') as file:
            S.cantrip_data = json.load(file)

    if S.spell_data == {}:
        with open(S.local_path + "/Spells.json", 'r') as file:
            S.spell_data = json.load(file)

    if S.Class_features == {}:
        with open(S.local_path + "/Class_based_features.json", 'r') as file:
            S.Class_features = json.load(file)

    if S.Race_data == {}:
        with open(S.local_path + "/Races.json", 'r') as file:
            S.Race_data = json.load(file)

    if S.subclass_data == {}:
        with open(S.local_path + "/SubClass.json", 'r') as file:
            S.subclass_data = json.load(file)

    if S.eldritch_incantations == {}:
        with open(S.local_path + "/Eldritch invocations.json", 'r') as file:
            S.eldritch_incantations = json.load(file)

    if S.mob_abilities == {}:
        with open(S.local_path + "/mob_abilities.json", 'r') as file:
            S.mob_abilities = json.load(file)
    if S.Setting_data == {}:
        with open(S.local_path + '/Settings.json', 'r') as file:
            S.Setting_data = json.load(file)
    if S.feat_data == {}:
        with open(S.local_path + "/Feat-list.json", 'r') as file:
            S.feat_data = json.load(file)


    S.Seisure = False
    if S.Setting_data["Seisures"] == "True":
        S.Seisure = True

    S.Proficient_button_color = S.Setting_data["Proficiency Color"]
def update_character_data(char_name):
    """Updates stuff like Eldritch incantations, Patrons shit like that"""
    """Should only do stuff if there are proficiency bonuses and stuff."""
    char = V.character_dict[char_name].copy()
    if char.get("Eldritch Invocations") != None:
        extracted_data = {}
        for invocation in char["Eldritch Invocations"].split(","):
            extracted_data.update({invocation : S.eldritch_incantations[invocation]})
        for key, value in extracted_data.items():
            if "Code" in list(value.keys()):
                code_data = value["Code"][0].split(":")
                if "Two" in code_data:
                    code_data = code_data[1:]
                    second_code_data = value["Code2"][0].split(":")
                    get_eldritch_invocation_data(second_code_data, char)

                get_eldritch_invocation_data(code_data, char)
            else:
                char["Code"] += "," + "Eldritch Invocations:" + key

    if char.get("SubClass") != None:
        extracted_data = {}
        final_data = {}
        for sub_class in char["SubClass"].split(","):
            for sub_class_Type, values in S.subclass_data.items():
                for subclass, subclass_dict in values.items():
                    if sub_class == subclass:
                        extracted_data.update( {subclass : subclass_dict} )
                        final_data[sub_class_Type] = extracted_data
                        extracted_data = {}

        for subclass_type, values in final_data.items():
            if subclass_type == "Roguish Archetype":
                char_class = "Rogue"
            elif subclass_type == "Patron":
                char_class = "Warlock"
            elif subclass_type == "Primal Path":
                char_class = "Barbarian"
            elif subclass_type == "Druid Circle":
                char_class = "Druid"
            elif subclass_type == "Martial Archetype":
                char_class = "Fighter"
            elif subclass_type == "Sacred Oath":
                char_class = "Paladin"
            elif subclass_type == "Blood Hunter Order":
                char_class = "Blood Hunter"
            elif subclass_type == "Arcane Tradition":
                char_class = "Wizard"
            elif subclass_type == "Sorcerous Origin":
                char_class = "Sorcerer"
            elif subclass_type == "Ranger Archetype":
                char_class = "Ranger"
            for subclass_name, value in values.items():
                for ability, val in value.items():
                    class_index = char["Class"].split(", ").index(char_class)
                    char_lv = char["Level"].split(",")[class_index]
                    if ability not in ["Expanded Spell List"] and int(val["Level"]) <= int(char_lv):
                        """Places subclass features in this string to be handled in Actions.py"""
                        char["Code"] += ",SubClass:" + subclass_type + ":" + subclass_name + ":" + ability
                    # elif ability in ["Expanded Spell List"]:
                    #     F.print_debug(ability, debug="INFO")
                    #     """When a spell list exists add extra somehow"""

    if "Giant's Power" in char["Code"]:
        if "Giant" not in char["Languages"]:
            l = char["Languages"].split(", ")
            l.append("Giant")
            char["Languages"] = ", ".join(l)

    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)
    if char_config_data.get("Chosen_spells") == None:
        if char.get("Spell") == None:
            char["Spell"] = ""
        char_config_data["Chosen_spells"] = char["Spell"]
    if char_config_data.get("Chosen_cantrips") == None:
        if char.get("Cantrip") == None:
            char["Cantrip"] = ""
        char_config_data["Chosen_cantrips"] = char["Cantrip"]
    char["Spell"] = char_config_data["Chosen_spells"]
    if char.get("Cantrip") != None:
        char["Cantrip"] = char_config_data["Chosen_cantrips"]


    V.character_dict[V.char_name] = char.copy()
    if V.character_dict[V.char_name].get("Cantrip") == None:
        V.character_dict[V.char_name]["Cantrip"] = ""

    if V.character_dict[V.char_name].get("AC") == None:
        V.character_dict[V.char_name]["AC"] = 10 + V.score_modifiers["DEX"]

    V.BASE_AC = 10 + V.score_modifiers["DEX"]
    V.BASE_SPEED = V.character_dict[V.char_name]["Speed"]

    for i in range(0, int(V.character_dict[V.char_name]["Hit dice"].split("d")[0])):
        V.BASE_HIT_DICE.append(V.character_dict[V.char_name]["Hit dice"].split("d")[1])

    if V.character_dict[V.char_name].get("Immunity") == None:
        V.character_dict[V.char_name]["Immunity"] = ""
    if V.character_dict[V.char_name].get("Vulnerabilities") == None:
        V.character_dict[V.char_name]["Vulnerabilities"] = ""
    if V.character_dict[V.char_name].get("Resistance") == None:
        V.character_dict[V.char_name]["Resistance"] = ""
    if V.character_dict[V.char_name].get("Background") == None:
        V.character_dict[V.char_name]["Background"] = ""

def get_eldritch_invocation_data(code_data, char):
    if "Free" in code_data:
        if "Spell" in code_data:
            if char.get("Free_Spells") == None:
                char["Free_Spells"] = []
            char["Free_Spells"].append(code_data[2])
    if "BYPASS" in code_data:
        S.Bypass[code_data[1]] = True
    if "PROFICIENCY" in code_data:
        for prof in code_data[1:]:
            character_skills = char["Skills"].split(",")
            skill_index = list(V.Skills.keys()).index(prof)
            character_skills[skill_index] = prof + ":" + str(V.Proficiecy_bonus)
            char["Skills"] = ",".join(character_skills)
    if "Niche" in code_data:
        if S.Niche.get(code_data[1]) == None:
            S.Niche[code_data[1]] = []
        S.Niche[code_data[1]].append(code_data[2])
    if "Languages" in code_data:
        char["Languages"] += "," + str(code_data[1])

def Take_a_LONG_rest():
    """Removes effects given by spells, one use is the Mage Armour spell"""
    V.spell_effects = {}
    """Cancel consentration"""
    V.consentration = {}
    """Reset spell slots"""
    F.reset_spellSlots("LR")
    """Reduce exhaustion level"""
    if V.Special_Flags.get("Rage") != None:
        del V.Special_Flags["Rage"]
        S.Background_image = "background"
        S.Standart_color = "black"
    C.exhaustion_condition_decreese()
    """Return Hp to original state"""
    V.character_dict[V.char_name]["Health"] = [V.character_dict[V.char_name]["Health"][1], V.character_dict[V.char_name]["Health"][1]]

    V.BASE_HIT_DICE = []
    for i in range(0, int(V.character_dict[V.char_name]["Hit dice"].split("d")[0])):
        V.BASE_HIT_DICE.append(V.character_dict[V.char_name]["Hit dice"].split("d")[1])

    if "Natural Recovery" in V.character_dict[V.char_name]["Code"]:
        V.Special_Flags["Natural_Recovery_Used"] = 0

def Take_a_SHORT_rest(screen, clock):
    """Does something with V.short_rest but doesnt touch hp dont understand it, caused errors, removed it"""
    # for action in V.short_rest:
    #     if action[0] == "hp":
    #         continue
    #     V.spell_slots[action[0]] = int(action[1])

    """if add hp flag not set, then sets it"""
    if ("hp", True) not in V.short_rest:
        V.short_rest.append(("hp", True))

    if V.Special_Flags.get("Rage") != None:
        del V.Special_Flags["Rage"]
        S.Background_image = "background"
        S.Standart_color = "black"

    """recieve back some spell slots"""
    F.reset_spellSlots("SR")

    remove_list = []
    if V.Special_Flags != {}:
        for name, value in V.Special_Flags.items():
            if isinstance(value, str) and "SR" in value:   # NOT USED Naudojom anks2iau for Natural Recovery.
                V.short_rest.append(name)
                remove_list.append(name)

        for name in remove_list:
            del V.Special_Flags[name]

    if V.character_dict[V.char_name].get("Arcane Recovery") != None:
        char_class = V.character_dict[V.char_name]["Class"].split(", ")
        char_lv = V.character_dict[V.char_name]["Level"].split(",")


        spell_slots_expected = {
                                "1st": 0,
                                "2nd": 0,
                                "3rd": 0,
                                "4th": 0,
                                "5th": 0,
                                "6th": 0,
                                "7th": 0,
                                "8th": 0,
                                "9th": 0
                                }
        spell_slots_first_class = V.Available_spells_data[char_class[0]][int(char_lv[0])][3]
        spell_slots_second_class = V.Available_spells_data[char_class[1]][int(char_lv[1])][3]
        for i in range(0, int(V.Available_spells_data[char_class[0]][int(char_lv[0])][4])):
            spell_slots_expected[spell_slots_first_class.split(",")[i].split(":")[0]] = int(spell_slots_first_class.split(",")[i].split(":")[1]) + int(spell_slots_second_class.split(",")[i].split(":")[1])


        slots_to_recover = []
        for slot, value in spell_slots_expected.items():
            if value != 0 and V.spell_slots.get(slot) != None and V.spell_slots[slot] < value:
                slots_to_recover.append(slot)
        if slots_to_recover != []:
            special.Arcane_Recovery(screen, clock, slots_to_recover)

    if V.Special_Flags.get("Natural_Recovery_Used") == None or V.Special_Flags["Natural_Recovery_Used"] == 0:
        """0 - Not used this LR
           1 - Just had a SR can use
           2 - Used"""
        V.Special_Flags["Natural_Recovery_Used"] = 1
def user_settings(screen, clock):
    running = True
    text_size = 30
    pressed = -1
    button_dict = {
        (0, 0): ["Remove Character Data", "background", "background", "rect-place-holder", "red"],
        (1, 0): ["Toggle Seizures", "background", "background", "rect-place-holder", "black"],
        (2, 0): ["Proficiency Color", "background", "background", "rect-place-holder", S.Proficient_button_color],
        (3, 1): ["Apply", "background", "background", "rect-place-holder", "black"],

    }
    remove_count = 0
    color_dict = {
        0: "red",
        1: "blue",
        2: "green",
        3: "yellow",
        4: "purple",
        5: "orange",
        6: "pink",
        7: "brown",
        8: "black",
        9: "white"
    }
    color_count = 0
    while running:
        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.05
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Back", text_size=20)
        x_pos = [S.SCREEN_WIDTH * 0.02, S.SCREEN_WIDTH * 0.27, S.SCREEN_WIDTH * 0.52, S.SCREEN_WIDTH * 0.77]
        y_pos = [S.SCREEN_HEIGHT * 0.9, S.SCREEN_HEIGHT * 0.8]
        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict, text_size=20)
        F.display_text(screen, "Settings", 30, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1), case="C")
        F.display_text(screen, "* Flashing screen: " + str(S.Seisure), 15, (S.SCREEN_WIDTH * 0.02, S.SCREEN_HEIGHT * 0.15))
        F.display_text(screen, "* Proficiency buttons color: " + str(S.Proficient_button_color), 15, (S.SCREEN_WIDTH * 0.02, S.SCREEN_HEIGHT * 0.2))
        F.display_text(screen, "* If you wish to PERMENATELY delete your character data and create a new one, please don't, but if you want click the button five times in 5 seconds", 15, (S.SCREEN_WIDTH * 0.02, S.SCREEN_HEIGHT * 0.25))
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
                        pg.draw.rect(screen, "black", buttons[i], width=3)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == "Back":
                        return False
                    elif pressed == "Toggle Seizures":
                        S.Seisure = not S.Seisure
                        S.Setting_data["Seisures"] = str(S.Seisure)
                    elif pressed == "Remove Character Data":
                        remove_count += 1
                        if remove_count >= 5:
                            F.print_debug("REMOVING DATA", debug="ERROR")
                            os.remove(S.local_path + f"/Created_Players/{V.char_name}_config.json")
                            return True
                    elif pressed == "Proficiency Color":
                        color_count = (color_count + 1) % 10
                        S.Proficient_button_color = color_dict[color_count]
                        button_dict[(2, 0)][4] = S.Proficient_button_color
                        S.Setting_data["Proficiency Color"] = S.Proficient_button_color
                    elif pressed == "Apply":
                        json_output = json.dumps(S.Setting_data, indent=4)
                        # Define the filename using char_name, adding .json extension

                        # Write the JSON output to the file
                        filename = os.path.expanduser("~/Settings.json")
                        with open(filename, "w") as file:
                            file.write(json_output)
                        return False
                    pressed = -1

        pg.display.flip()
        clock.tick(60)
    return False

def Choose_char(CODE, screen, clock):
    running = True
    text_size = 30
    pressed = -1
    char_list = V.Players_to_Chars[CODE]

    while running:
        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.05
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Exit")
        x_pos = [S.SCREEN_WIDTH * 0.05, S.SCREEN_WIDTH * 0.62]
        y_pos = S.SCREEN_HEIGHT * 0.05
        x_pic_pos = S.SCREEN_WIDTH * 0.05
        i = 0
        for name in char_list:
            if V.SECRETS.get(name) != None and V.SECRETS[name]["Apperance"]:
                name = "UNKNOWN"
            elif name == "New":
                b = pg.draw.rect(screen, "#222222", (x_pic_pos, y_pos, button_width, button_width), width=3)
                F.display_text(screen, "New", 30, (b.x + b.w //2, b.y + b.h //2), case="C")
                i += 1
                buttons.append(b)
                x_pic_pos += S.SCREEN_WIDTH * 0.22
                if x_pic_pos > S.SCREEN_WIDTH * 0.9:
                    x_pic_pos = S.SCREEN_WIDTH * 0.05
                    y_pos += button_width + S.SCREEN_HEIGHT * 0.05
                continue
            b = F.add_image_to_screen(screen, name, (x_pic_pos, y_pos, button_width, button_width), "player")
            x_pic_pos += S.SCREEN_WIDTH * 0.22
            if x_pic_pos + button_width > S.SCREEN_WIDTH * 0.95:
                x_pic_pos = S.SCREEN_WIDTH * 0.05
                y_pos += button_width + S.SCREEN_HEIGHT * 0.05

            i+=1
            buttons.append(b)

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
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                        pressed = i
                        break
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == 0:
                        return 0
                    else:
                        return char_list[pressed - 1]
                pressed = -1
        pg.display.flip()
        clock.tick(60)

def Enter_char_details(screen, clock):
    running = True
    text_size = 30
    pressed = -1
    selected_entry = -1
    delay = 0
    notice = ""
    text_dict = {0: "5", 1: "10", 2: "Neutral"}
    race = choose_race(screen, clock)
    char_class = choose_class(screen, clock)
    Ability_score = get_ability_score(screen, clock)
    while running:
        entries = [0]
        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.05
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Save")
        x_pos = [S.SCREEN_WIDTH * 0.4, S.SCREEN_WIDTH * 0.62]
        y_pos = [S.SCREEN_HEIGHT * 0.05, S.SCREEN_HEIGHT * 0.12, S.SCREEN_HEIGHT * 0.19, S.SCREEN_HEIGHT * 0.26, S.SCREEN_HEIGHT * 0.33, S.SCREEN_HEIGHT * 0.4, S.SCREEN_HEIGHT * 0.47, S.SCREEN_HEIGHT * 0.54, S.SCREEN_HEIGHT * 0.61, S.SCREEN_HEIGHT * 0.68]
        # text = ["Level", "Class", "Race", "Ability_Scores", "Gold", "Alignment"]
        text = ["Level", "Gold", "Alignment"]
        # Dont need to save languages at this moment. nor do we need to save Health. just gold, level, class, race AS and allignment.
        for i in range(0, len(text)):
            F.display_text(screen, text[i], 15, (x_pos[0] - S.SCREEN_WIDTH * 0.15, y_pos[i]))
            r = pg.Rect(x_pos[0], y_pos[i], button_width, button_height)
            pg.draw.rect(screen, "black", r, width=2)
            entries.append(r)
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
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                        pressed = i
                for i in range(1, len(entries)):
                    if entries[i].collidepoint(mouse_pos):
                        pressed = i
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == 0:
                        res = Save_new_char(text_dict, text, screen, clock, char_class, race, Ability_score)
                        if isinstance(res, bool) and res:
                            return
                        notice = res
                    else:
                        selected_entry = pressed - 1
                pressed = -1

            elif event.type == pg.TEXTINPUT and selected_entry != -1:
                if text_dict.get(selected_entry) == None:
                    text_dict[selected_entry] = ""
                text_dict[selected_entry] += event.text
            elif keys[pg.K_BACKSPACE] and selected_entry != -1:
                text_dict[selected_entry] = text_dict[selected_entry][:-1]
            elif keys[pg.K_TAB] and selected_entry != -1:
                selected_entry += 1
                if selected_entry >= len(text):
                    selected_entry = 0

        for i in range(0, len(text)):
            if text_dict.get(i) == None:
                text_dict[i] = ""
            F.display_text(screen, text_dict[i], 18, (x_pos[0] + S.SCREEN_WIDTH * 0.02, y_pos[i]))
        if text_dict.get(selected_entry) == None:
            text_dict[selected_entry] = ""
        if selected_entry != -1:
            if delay == 0:
                delay = 20
            if delay != 0:
                delay -= 1
            if delay > 10:
                pg.draw.line(screen, "black", (x_pos[0] + S.SCREEN_WIDTH * 0.005, y_pos[selected_entry] + 3), (x_pos[0] + S.SCREEN_WIDTH * 0.005, y_pos[selected_entry] + S.SCREEN_HEIGHT * 0.05 - 3), width=2)
        if notice != "":
            text_x = S.SCREEN_WIDTH * 0.1
            text_y = S.SCREEN_HEIGHT * 0.75
            for w in notice.split(" "):
                text_rect = F.display_text(screen, w + " ", text_size, (text_x, text_y))
                if text_x + text_rect.w > SCREEN_WIDTH * 0.8:
                    text_x = S.SCREEN_WIDTH * 0.1
                    text_y += S.SCREEN_HEIGHT * 0.1
                else:
                    text_x += text_rect.w

        pg.display.flip()
        clock.tick(60)

def Save_new_char(text_dict, text, screen, clock, char_class, race, Ability_score):
    if V.character_dict.get(V.char_name) == None:
        V.character_dict[V.char_name] = {}

    for key, value in text_dict.items():
        if key == -1:
            continue
        fail = ""
        if text[key] in ["Experience", "Gold"]:
            if text[key] == "Experience":
                try:
                    if int(value) != 0:
                        fail = "Leave experience at 0!!"
                except:
                    fail = "Leave experience at 0 !!"
            else:
                try:
                    if int(value) != 10:
                        fail = "Leave gold at 10!!"
                except:
                    fail = "Leave gold at 10!!"
        elif text[key] == "Health":
            if not value.isdigit():
                fail = "Make sure Health is a number"
        elif text[key] == "Class":
            if value not in V.available_classes:
                fail = f"Please select one of theese: {V.available_classes}"
        elif text[key] == "Race":
            if value not in list(V.race_size.keys()):
                fail = f"Please select one of theese: {list(V.race_size.keys())}"
        elif text[key] == "Languages":
            if value not in V.Languages:
                fail = f"Please select one of theese: {V.Languages}"
        elif text[key] == "Ability_Scores":
            if value.count(",") != 5:
                fail = f"Please write in this Format: STR,DEX,CON,INT,WIS,CHA"
        if fail != "":
            return fail
        if text[key] in ["Level", "Ability_Scores"]:
            V.character_dict[V.char_name][text[key]] = value.replace(", ", ",")
        else:
            V.character_dict[V.char_name][text[key]] = str(value)

    if V.char_name == "New":
        V.char_name = get_char_name(screen, clock)
        V.character_dict[V.char_name] = V.character_dict["New"].copy()
        V.character_dict[V.char_name]["Class"] = char_class
        V.character_dict[V.char_name]["Race"] = race
        Ability_score = f"{Ability_score[0]},{Ability_score[1]},{Ability_score[2]},{Ability_score[3]},{Ability_score[4]},{Ability_score[5]}"
        V.character_dict[V.char_name]["Ability_Scores"] = Ability_score

        V.character_dict["New"] = {}

    # F.print_debug("UNCOMMENT THIS", "", "Warning")
    data_to_save = V.character_dict[V.char_name].copy()
    data_to_save["Name"] = V.char_name
    F.save_char_to_localhost(data_to_save, "characters")
    return True


def get_char_name(screen, clock):
    running = True
    text_size = 30
    pressed = -1
    selected_entry = -1
    delay = 0
    text_dict = {}
    while running:
        entries = [0]
        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.05
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Save")
        x_pos = [S.SCREEN_WIDTH * 0.4, S.SCREEN_WIDTH * 0.62]
        y_pos = [S.SCREEN_HEIGHT * 0.05, S.SCREEN_HEIGHT * 0.12, S.SCREEN_HEIGHT * 0.19, S.SCREEN_HEIGHT * 0.26, S.SCREEN_HEIGHT * 0.33, S.SCREEN_HEIGHT * 0.4, S.SCREEN_HEIGHT * 0.47, S.SCREEN_HEIGHT * 0.54, S.SCREEN_HEIGHT * 0.61, S.SCREEN_HEIGHT * 0.68]
        text = ["Name"]
        for i in range(0, len(text)):
            F.display_text(screen, text[i], 15, (x_pos[0] - S.SCREEN_WIDTH * 0.15, y_pos[i]))
            r = pg.Rect(x_pos[0], y_pos[i], button_width, button_height)
            pg.draw.rect(screen, "black", r, width=2)
            entries.append(r)
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
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                        pressed = i
                for i in range(1, len(entries)):
                    if entries[i].collidepoint(mouse_pos):
                        pressed = i
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == 0:
                        return text_dict[0]
                    else:
                        selected_entry = pressed - 1
                pressed = -1

            elif event.type == pg.TEXTINPUT and selected_entry != -1:
                if text_dict.get(selected_entry) == None:
                    text_dict[selected_entry] = ""
                text_dict[selected_entry] += event.text
            elif keys[pg.K_BACKSPACE] and selected_entry != -1:
                text_dict[selected_entry] = text_dict[selected_entry][:-1]
            elif keys[pg.K_TAB] and selected_entry != -1:
                selected_entry += 1
                if selected_entry >= len(text):
                    selected_entry = 0

        for i in range(0, len(text)):
            if text_dict.get(i) == None:
                text_dict[i] = ""
            F.display_text(screen, text_dict[i], 18, (x_pos[0] + S.SCREEN_WIDTH * 0.02, y_pos[i]))
        if text_dict.get(selected_entry) == None:
            text_dict[selected_entry] = ""
        if selected_entry != -1:
            if delay == 0:
                delay = 20
            if delay != 0:
                delay -= 1
            if delay > 10:
                pg.draw.line(screen, "black", (x_pos[0] + S.SCREEN_WIDTH * 0.005, y_pos[selected_entry] + 3), (x_pos[0] + S.SCREEN_WIDTH * 0.005, y_pos[selected_entry] + S.SCREEN_HEIGHT * 0.05 - 3), width=2)
        pg.display.flip()
        clock.tick(60)

def choose_race(screen, clock):
    running = True
    pressed = -1
    while running:
        buttons = []
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        race_x = S.SCREEN_WIDTH * 0.1
        race_y = S.SCREEN_HEIGHT * 0.1
        race_width = S.SCREEN_WIDTH * 0.25
        race_height = S.SCREEN_HEIGHT * 0.25
        for race in V.race_size.keys():
            r = F.add_button_to_screen(screen, race, pg.Rect(race_x, race_y, race_width, race_height), "Race")
            F.display_text(screen, race, 20, (r.x, r.y), case="C")
            buttons.append(r)
            race_x += race_width * 1.1
            if race_x >= S.SCREEN_WIDTH * 0.8:
                race_x = S.SCREEN_WIDTH * 0.1
                race_y += race_height * 1.1
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
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                        pressed = i
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    return list(V.race_size.keys())[pressed]
                pressed = -1
        pg.display.flip()
        clock.tick(120)

def choose_class(screen, clock):
    running = True
    pressed = -1
    s = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 2), pg.SRCALPHA).convert_alpha()
    y_scroll = 0
    while running:
        buttons = []
        F.add_image_to_screen(s, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 2), "Background")
        race_x = S.SCREEN_WIDTH * 0.1
        race_y = S.SCREEN_HEIGHT * 0.1
        race_width = S.SCREEN_WIDTH * 0.25
        race_height = S.SCREEN_HEIGHT * 0.25
        for race in V.available_classes:
            r = F.add_button_to_screen(s, race, pg.Rect(race_x, race_y, race_width, race_height), "Class")
            F.display_text(s, race, 20, (r.x, r.y), case="C")
            buttons.append(r)
            race_x += race_width * 1.1
            if race_x >= S.SCREEN_WIDTH * 0.8:
                race_x = S.SCREEN_WIDTH * 0.1
                race_y += race_height * 1.1
        for event in pg.event.get():
            keys = pg.key.get_pressed()
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
                s = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 2), pg.SRCALPHA).convert_alpha()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(mouse_pos):
                        pg.draw.rect(s, "black", buttons[i], width=3)
                        pressed = i
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    return V.available_classes[pressed]
                pressed = -1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 4:
                if y_scroll < 0:
                    y_scroll += 1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5:
                y_scroll -= 1
        screen.blit(s, (0, y_scroll * 30))
        pg.display.flip()
        clock.tick(120)

def get_ability_score(screen, clock):
    running = True
    pressed = -1
    y_scroll = 0
    selected_entry = -1
    delay = 0
    text_dict = {}
    text = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    rolled = []
    make_red = []
    while running:
        entries = []

        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 2), "Background")
        buttons = F.display_back_button(screen, "Save")
        if len(rolled) < 6:
            buttons += F.display_back_button(screen, "Roll", x_pos=[S.SCREEN_WIDTH * 0.5])
        race_x = S.SCREEN_WIDTH * 0.2
        race_y = S.SCREEN_HEIGHT * 0.1
        race_width = S.SCREEN_WIDTH * 0.1
        race_height = S.SCREEN_HEIGHT * 0.05
        make_red = {}
        for i, ability in enumerate(text):
            r = pg.Rect(race_x, race_y, race_width, race_height)
            F.display_text(screen, ability, 20, (r.x, r.y - S.SCREEN_HEIGHT * 0.05))
            if i < len(rolled):
                if make_red.get(rolled[i]) == None:
                    make_red[rolled[i]] = 0
                if rolled[i] in list(text_dict.values()) and make_red[rolled[i]] < list(text_dict.values()).count(rolled[i]):
                    col = "red"
                    make_red[rolled[i]] += 1
                else:
                    col = "black"
                F.display_text(screen, rolled[i], 20, (r.x, r.y + S.SCREEN_HEIGHT * 0.05), color=col)
            pg.draw.rect(screen, "black", r, width=2)
            entries.append(r)
            race_x += race_width * 1.1

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
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                        pressed = i
                        break
                for i in range(0, len(entries)):
                    if entries[i].collidepoint(mouse_pos):
                        pressed = "Entry:" + str(i)
                        break
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == 0:
                        return text_dict
                    elif pressed == 1:
                        dice = "4d6"
                        count = int(dice.split("d")[0])
                        multiple_rolls = []
                        for i in range(0, count):
                            multiple_rolls.append(random.randint(1, int(dice.split("d")[1])))
                        if count == 1:
                            multiple_rolls = str(multiple_rolls[0])
                            dtwenty = int(multiple_rolls)
                        else:
                            smallest_roll = min(multiple_rolls)
                            dtwenty = sum(multiple_rolls) - smallest_roll
                        F.Roll_3d_dice(screen, clock, dice[1:].upper(), multiple_rolls, (S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.3))
                        rolled.append(str(dtwenty))
                    elif "Entry:" in pressed:
                        selected_entry = int(pressed.replace("Entry:", ""))
                pressed = -1
            elif event.type == pg.TEXTINPUT and selected_entry != -1:
                if text_dict.get(selected_entry) == None:
                    text_dict[selected_entry] = ""
                if event.text.isdigit():
                    text_dict[selected_entry] += event.text
            elif keys[pg.K_BACKSPACE] and selected_entry != -1:
                text_dict[selected_entry] = text_dict[selected_entry][:-1]
            elif keys[pg.K_TAB] and selected_entry != -1:
                selected_entry += 1
                if selected_entry >= len(text):
                    selected_entry = 0

        for i in range(0, len(text)):
            if text_dict.get(i) == None:
                text_dict[i] = ""
            race_x = S.SCREEN_WIDTH * 0.2
            F.display_text(screen, text_dict[i], 18, (race_x + race_width * 1.1 * i + S.SCREEN_WIDTH * 0.02, race_y))
        if text_dict.get(selected_entry) == None:
            text_dict[selected_entry] = ""
        if selected_entry != -1:
            if delay == 0:
                delay = 20
            if delay != 0:
                delay -= 1
            if delay > 10:
                pg.draw.line(screen, "black", (race_x + race_width * 1.1 * selected_entry + S.SCREEN_WIDTH * 0.005, race_y + 3),(race_x + race_width * 1.1 * selected_entry + S.SCREEN_WIDTH * 0.005, race_y + S.SCREEN_HEIGHT * 0.05 - 3), width=2)

        pg.display.flip()
        clock.tick(120)

def get_hp_if_required(screen, clock):
    if V.character_dict[V.char_name].get("Health") != None and isinstance(V.character_dict[V.char_name]["Health"], list):
        return
    hp_to_add = 0
    running = True
    pressed = -1
    y_scroll = 0
    selected_entry = -1
    delay = 0
    text_dict = {}
    text = ["Hp:"]
    char_classes = V.character_dict[V.char_name]["Class"].split(", ")
    char_levels = V.character_dict[V.char_name]["Level"].split(",")
    hit_dice = []
    for char_class in char_classes:
        hit_dice.append(S.class_data[char_class]["1"]["Hit dice"][2].split("1d")[1])
    higher_hit_die = int(max(hit_dice))
    class_index = hit_dice.index(str(higher_hit_die))
    hit_dice = f"1d{higher_hit_die}"
    class_level = int(char_levels[class_index])
    con_mod = V.score_modifiers["CON"]
    if V.character_dict[V.char_name].get("Health") != None and V.character_dict[V.char_name]["Health"] == "1*lv":
        hp_to_add = class_level
    rolled = [higher_hit_die + con_mod]
    while running:
        entries = []
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 2), "Background")
        buttons = F.display_back_button(screen, "Save")
        if len(rolled) < class_level:
            buttons += F.display_back_button(screen, "Roll", x_pos=[S.SCREEN_WIDTH * 0.5])
        race_x = S.SCREEN_WIDTH * 0.2
        race_y = S.SCREEN_HEIGHT * 0.1
        race_width = S.SCREEN_WIDTH * 0.1
        race_height = S.SCREEN_HEIGHT * 0.05
        F.display_text(screen, f"CON MOD: {con_mod}", 20, (S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.1))
        r = pg.Rect(race_x, race_y, race_width, race_height)
        F.display_text(screen, "HP: " + str(higher_hit_die) + " +", 20, (r.x - r.w, r.y))
        pg.draw.rect(screen, "black", r, width=2)
        entries.append(r)
        race_x += race_width * 1.1

        F.display_text(screen, "Player Hp rolled: " + str(sum(rolled)), 20, (r.x - r.w, r.y + S.SCREEN_HEIGHT * 0.05))
        F.display_text(screen, "Player Hp average: " + str(math.ceil(((higher_hit_die * (class_level - 1)) / 2) + con_mod * (class_level - 1) + higher_hit_die + con_mod)), 20, (r.x - r.w, r.y + S.SCREEN_HEIGHT * 0.1))
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
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                        pressed = i
                        break
                for i in range(0, len(entries)):
                    if entries[i].collidepoint(mouse_pos):
                        pressed = "Entry:" + str(i)
                        break
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == 0:
                        if sum(rolled) == higher_hit_die + con_mod:
                            health = int(text_dict[0]) + hp_to_add
                        else:
                            health = sum(rolled) + hp_to_add
                        data_to_save = V.character_dict[V.char_name].copy()
                        data_to_save["Name"] = V.char_name
                        data_to_save["Health"] = health
                        V.character_dict[V.char_name]["Health"] = [health, health]
                        F.save_char_to_localhost(data_to_save, "characters")
                        return text_dict
                    elif pressed == 1:
                        dice = hit_dice
                        count = int(dice.split("d")[0])
                        multiple_rolls = []
                        for i in range(0, count):
                            multiple_rolls.append(random.randint(1, int(dice.split("d")[1])))
                        if count == 1:
                            multiple_rolls = str(multiple_rolls[0])
                            dtwenty = int(multiple_rolls)
                        else:
                            smallest_roll = min(multiple_rolls)
                            dtwenty = sum(multiple_rolls) - smallest_roll
                        F.Roll_3d_dice(screen, clock, dice[1:].upper(), multiple_rolls, (S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.3))
                        rolled.append(dtwenty + con_mod)
                    elif "Entry:" in pressed:
                        selected_entry = int(pressed.replace("Entry:", ""))
                pressed = -1
            elif event.type == pg.TEXTINPUT and selected_entry != -1:
                if text_dict.get(selected_entry) == None:
                    text_dict[selected_entry] = ""
                if event.text.isdigit():
                    text_dict[selected_entry] += event.text
            elif keys[pg.K_BACKSPACE] and selected_entry != -1:
                text_dict[selected_entry] = text_dict[selected_entry][:-1]
            elif keys[pg.K_TAB] and selected_entry != -1:
                selected_entry += 1
                if selected_entry >= len(text):
                    selected_entry = 0

        for i in range(0, len(text)):
            if text_dict.get(i) == None:
                text_dict[i] = ""
            race_x = S.SCREEN_WIDTH * 0.2
            F.display_text(screen, text_dict[i], 18, (race_x + race_width * 1.1 * i + S.SCREEN_WIDTH * 0.02, race_y))
        if text_dict.get(selected_entry) == None:
            text_dict[selected_entry] = ""
        if selected_entry != -1:
            if delay == 0:
                delay = 20
            if delay != 0:
                delay -= 1
            if delay > 10:
                pg.draw.line(screen, "black", (race_x + race_width * 1.1 * selected_entry + S.SCREEN_WIDTH * 0.005, race_y + 3),(race_x + race_width * 1.1 * selected_entry + S.SCREEN_WIDTH * 0.005, race_y + S.SCREEN_HEIGHT * 0.05 - 3), width=2)

        pg.display.flip()
        clock.tick(120)

def edit_variables_py(CODE):
    re_save = []
    if V.char_name not in V.Players_to_Chars[CODE]:
        with open("Variables.py","r") as file:
            lines = file.readlines()
            for line in lines:
                if "Players_to_Chars" in line:
                    l = ""
                    l += "Players_to_Chars = {"
                    line = line.replace("Players_to_Chars = {", "")
                    line = line.replace("}", "")
                    for section in line.split("],"):
                        name = section.split(": ")[0].replace('"', '')
                        if name == CODE:
                            new_values = section
                            values = section.split(": ")[1][1:].replace('"', '').split(", ")
                            if V.char_name not in values:
                                values.append(V.char_name)
                                new_values = ('", "'.join(values)).replace("\n", '')
                                new_values = '"' + name + '": ["' + new_values + '"'
                            l += new_values
                        else:
                            l += section.replace("\n", "") + "],"
                    l += "}\n"
                    re_save.append(l)
                else:
                    re_save.append(line)

        with open("Variables.py", "w") as file:
            file.writelines(re_save)

    if os.path.exists(S.local_path + f"/Images/Players/{V.char_name}.jpg"):
        return
    elif os.path.exists(S.local_path + f"/Images/Players/{V.char_name}.png"):
        return

    if os.path.exists(S.local_path + f"/Images/Data/Race/{V.character_dict[V.char_name]['Race']}.jpg"):
        shutil.copyfile(S.local_path + f"/Images/Data/Race/{V.character_dict[V.char_name]['Race']}.jpg", S.local_path + f"/Images/Players/{V.char_name}.jpg")

    elif os.path.exists(S.local_path + f"/Images/Data/Race/{V.character_dict[V.char_name]['Race']}.png"):
        shutil.copyfile(S.local_path + f"/Images/Data/Race/{V.character_dict[V.char_name]['Race']}.png", S.local_path + f"/Images/Players/{V.char_name}.png")


