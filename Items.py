import random

import pygame as pg, json
import Functions as F, Settings as S, Variables as V
import conditions


def display_char_items(screen, char_name, clock):
    running = True
    pressed = -1
    delete_flag = 0
    equip_flag = False
    text_size = 30
    dict = {
        0: ["Add Items", "background", "background", "rect-place-holder", "black"],
        1: ["Remove Items", "background", "background", "rect-place-holder", "black"],
        2: ["Equip Items", "background", "background", "rect-place-holder", "black"]
    }
    reset = True
    get_equiped_items()
    equiped_item_dict = V.EQUIPED_CHAR_ITEMS.copy()

    char_size = V.character_dict[char_name]["Size"]

    str_score = V.character_dict[char_name]["Ability_Scores"].split(",")[0]
    carry_capacity = 15 * int(str_score)

    char_size_int = V.race_size_to_int[char_size]

    if "Powerful Build" in V.character_dict[char_name]["Code"]:
        char_size_int += 1


    if char_size_int != 2: # MEDIUM
        if char_size_int == 0:
            carry_capacity = int(carry_capacity / 2)
        if char_size_int == 3:
            carry_capacity = int(carry_capacity * 2)
        if char_size_int == 4:
            carry_capacity = int(carry_capacity * 4)
        if char_size_int == 5:
            carry_capacity = int(carry_capacity * 6)

    s = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 0.8), pg.SRCALPHA).convert_alpha()
    show_expertise = False

    while running:
        if reset:
            item_dict, weight = sort_items(char_name, carry_capacity)
        item_buttons = {}
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        """Display the expertise symbols"""
        expertise_rect = F.display_text(screen, "  Item Expertise  ", 30, (S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.05), case="C")
        pg.draw.rect(screen, "black", expertise_rect, width=3)

        """Display char gold"""
        gold_rect = F.display_text(screen, "Gold: " + str(V.character_dict[char_name]["Gold"]), 30, (S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.85), "black", "C")
        pg.draw.rect(screen, "black", pg.Rect(gold_rect.x - 5, gold_rect.y - 5, gold_rect.w + 10, gold_rect.h + 10), width=2)

        """Display char carry weight"""
        weight_rect = F.display_text(screen, "Weight: " + str(weight) + "/" + str(carry_capacity), 30, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.85), "black", "C")
        pg.draw.rect(screen, "black", pg.Rect(weight_rect.x - 5, weight_rect.y - 5, weight_rect.w + 10, weight_rect.h + 10), width=2)


        buttons = F.display_back_button(screen, "Back")
        button_width = S.SCREEN_WIDTH / 5
        button_height = S.SCREEN_HEIGHT / 20
        screen_top = S.SCREEN_HEIGHT * 0.9
        x_pos = [S.SCREEN_WIDTH * 0.52, S.SCREEN_WIDTH * 0.27, S.SCREEN_WIDTH * 0.02]
        buttonsB = F.display_other_buttons(screen, text_size, (x_pos, screen_top, button_width, button_height), dict)
        buttons = buttons + buttonsB
        x = S.SCREEN_WIDTH * 0.1
        y = S.SCREEN_HEIGHT * 0.1
        w = S.SCREEN_WIDTH * 0.08
        h = S.SCREEN_WIDTH * 0.08
        for item, amount in item_dict.items():
            if V.item_dict.get(item) == None:
                if item != "None":
                    F.print_debug(f"Couldn't display {item}", debug="ERROR")
                continue
            rect = F.add_image_to_screen(screen, item, (x, y, w, h), V.item_dict[item]["Type"])
            item_buttons[item] = rect
            F.display_text(screen, str(amount), 20, (x + w / 2, y + h / 2), "blue", "C")
            x += S.SCREEN_WIDTH * 0.1
            if x + w >= S.SCREEN_WIDTH * 0.9:
                x = S.SCREEN_WIDTH * 0.1
                y += S.SCREEN_HEIGHT * 0.15
        for event in pg.event.get():
            pos = pg.mouse.get_pos()
            keys = pg.key.get_pressed()
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(pos):
                        pressed = i
                        pg.draw.rect(screen, "black", buttons[i], width=3)

                for name, rect in item_buttons.items():
                    if rect.collidepoint(pos):
                        pressed = name
                        pg.draw.rect(screen, "black", item_buttons[name], width=3)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1 and isinstance(pressed, int) and buttons[pressed].collidepoint(pos):
                    if pressed == 0:
                        """back"""
                        F.save_equiped_items(equiped_item_dict)
                        running = False
                    elif pressed == 1:
                        """add new item"""
                        add_item(screen, clock, char_name)
                        reset = True
                        text_dict = {}
                        for keyy, value in V.character_dict[char_name].items():
                            if keyy != "Health":
                                text_dict[keyy] = [value, 0]
                        text_dict["Name"] = [char_name, 0]
                        F.update_items_db(V.character_dict[V.char_name])
                        F.update_gold_db(V.character_dict[V.char_name])
                        # F.save_data(text_dict, "characters")
                    elif pressed == 2:
                        delete_flag = (delete_flag + 1) % 3
                    elif pressed == 3:
                        equip_flag = not equip_flag
                if pressed != -1 and isinstance(pressed, str) and item_buttons.get(pressed) != None and item_buttons[pressed].collidepoint(pos):
                    if not delete_flag and not equip_flag:
                        selected_item_display(pressed, screen, clock)
                    else:
                        if delete_flag == 1:
                            reset = True
                            delete_flag = 0
                            result = delete_items(item_dict, pressed)
                            if result != None:
                                equiped_item_dict = result.copy()
                        elif delete_flag == 2:
                            reset = True
                            result = delete_items(item_dict, pressed)
                            if result != None:
                                equiped_item_dict = result.copy()
                        elif equip_flag:
                            equiped_item_dict = handle_equip_items(pressed, equiped_item_dict)




                else:
                    pressed = -1
            elif keys[pg.K_DELETE]:
                delete_flag = (delete_flag + 1) % 3
            elif event.type == pg.MOUSEMOTION:
                show_expertise = False
                if expertise_rect.collidepoint(pos):
                    show_expertise = True

        if equip_flag:
            pg.draw.rect(screen, "green", buttons[3], width=2)
            for key, equiped_item in equiped_item_dict.items():
                if equiped_item == "":
                    continue
                if "," in equiped_item:
                    for item in equiped_item.split(","):
                        if item == "":
                            continue
                        if V.item_dict[item]["Type"] in ["Weapons", "Magic Weapon"]:
                            color = "Red"
                        elif V.item_dict[item]["Type"] in ["Armour", "Magic Armour"]:
                            color = "blue"
                        else:
                            color = "green"
                        pg.draw.rect(screen, color, item_buttons[item], width=5)
                else:
                    if V.item_dict[equiped_item]["Type"] in ["Weapons", "Magic Weapon"]:
                        color = "Red"
                    elif V.item_dict[equiped_item]["Type"] in ["Armour", "Magic Armour"]:
                        color = "blue"
                    else:
                        color = "green"
                    pg.draw.rect(screen, color, item_buttons[equiped_item], width=5)
        if delete_flag == 1:
            pg.draw.rect(screen, "red", buttons[2], width=2)
        elif delete_flag == 2:
            pg.draw.rect(screen, "red", buttons[2], width=5)
        if show_expertise:
            display_expertise(s)
            screen.blit(s, (S.SCREEN_WIDTH - pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]))
        pg.display.flip()
        clock.tick(60)

def display_expertise(surface):
    F.add_image_to_screen(surface, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
    weapon_proficiencies = V.character_dict[V.char_name]['Weapon Proficiencies'].split(",")
    armor_proficiencies = V.character_dict[V.char_name]['Armor Proficiencies'].split(",")
    tool_proficiencies = []
    if V.character_dict[V.char_name].get('Tool Proficiencies') != None:
        tool_proficiencies = V.character_dict[V.char_name]['Tool Proficiencies'].split(",")
    x_start = S.SCREEN_WIDTH * 0.1
    y_start = S.SCREEN_HEIGHT * 0.1
    F.display_text(surface, "Weapon proficiencies: ", 30, (x_start, y_start))
    y_start += S.SCREEN_HEIGHT * 0.1
    for weapon in weapon_proficiencies:
        F.display_text(surface, weapon, 20, (x_start, y_start))
        y_start += S.SCREEN_HEIGHT * 0.05

    x_start += S.SCREEN_WIDTH * 0.3
    y_start = S.SCREEN_HEIGHT * 0.1
    F.display_text(surface, "Armor proficiencies: ", 30, (x_start, y_start))
    y_start += S.SCREEN_HEIGHT * 0.1
    for armor in armor_proficiencies:
        F.display_text(surface, armor, 20, (x_start, y_start))
        y_start += S.SCREEN_HEIGHT * 0.05

    x_start += S.SCREEN_WIDTH * 0.3
    y_start = S.SCREEN_HEIGHT * 0.1
    F.display_text(surface, "Tool proficiencies: ", 30, (x_start, y_start))
    y_start += S.SCREEN_HEIGHT * 0.1
    for tool in tool_proficiencies:
        F.display_text(surface, tool, 20, (x_start, y_start))
        y_start += S.SCREEN_HEIGHT * 0.05


def sort_items(char_name, max_capacity):
    item_dict = {}
    weight = 0
    if V.character_dict[char_name].get("Items") == None:
        V.character_dict[char_name]["Items"] = ""
    for item in V.character_dict[char_name]["Items"].split(","):
        if item_dict.get(item) == None and item != '':
            item_dict[item] = 0
        if item != "":
            item_dict[item] += 1
            if V.item_dict.get(item) != None and V.item_dict[item].get("Weight") != None and V.item_dict[item]["Weight"] != "-":
                weight += float(str(V.item_dict[item]["Weight"]).replace(" (full)", ""))

    V.CARRY_TOO_MUCH = False
    if round(weight,2) > max_capacity * 0.5:
        V.Condition = "Encumbrance"
        if round(weight,2) > max_capacity * 0.75:
            V.Condition = "Heavily Encumbered"
            if round(weight,2) > max_capacity:
                V.Condition = "Over Encumbered"
                V.consentration = {}
        conditions.on_condition_change()
        V.CARRY_TOO_MUCH = True
    else:
        if V.Condition in ["Encumbrance", "Heavily Encumbered", "Over Encumbered"]:
            V.Condition = ""
            conditions.on_condition_change()

    return item_dict, round(weight,2)

def selected_item_display(selected, screen, clock):
    running = True
    pressed = -1
    button_dict = {(0, 0): ["Consume", "background", "background", "rect-place-holder", "black"]}
    while running:
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        display_item(V.item_dict[selected], screen, selected)
        x_pos = [S.SCREEN_WIDTH * 0.52]
        y_pos = [S.SCREEN_HEIGHT * 0.9]
        buttons = F.display_back_button(screen, "Back")
        if V.item_dict[selected]["Type"] in ["Food", "Potions"]:
            button_width = S.SCREEN_WIDTH * 0.2
            button_height = S.SCREEN_HEIGHT * 0.05
            buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(mouse_pos):
                        pressed = ["Back", 0]
                        for key, value in button_dict.items():
                            if value[3] == buttons[i]:
                                pressed = [value[0], i]
                        pg.draw.rect(screen, "black", buttons[i], width=3)


            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                if pressed != -1 and buttons[pressed[1]].collidepoint(mouse_pos):
                    if pressed[0] == "Back":
                        """Back button pressed"""
                        running = False
                    elif pressed[0] == "Consume":
                        rolled_sum = handle_item_consumption(selected, screen, clock)
                        F.remove_item_from_char(selected, V.character_dict[V.char_name])
                        F.display_text(screen, "Healed: " + str(rolled_sum), 15, (S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.1))
                        running = False

                else:
                    pressed = -1
        pg.display.flip()
        clock.tick(120)  # limits FPS to 60




def display_item(item, screen, item_name):
    F.add_image_to_screen(screen, item_name, (800, 50, 300, 300), item["Type"])

    F.display_text(screen, "Name: " + item_name, 20, (20, 20))
    F.display_text(screen, "Type: " + item["Type"], 20, (20, 60))
    F.display_text(screen, "Cost: " + item["Cost"], 20, (20, 100))
    index = list(item.keys()).index("Type")
    if index == 3:
        F.display_text(screen, "Weight: " + str(item["Weight"]), 20, (20, 140))
        F.display_text(screen, "Properties: " + str(item["Properties"]), 20, (20, 180))
        text_rect = F.display_text(screen, "Extra: ", 20, (20, 220))
        x = 20 + text_rect.w
        y = 220
        for txt in str(item["Extra"]).split(" "):
            text_rect = F.display_text(screen, txt + " ", 20, (x, y))
            x = text_rect.x + text_rect.w
            if x >= 500:
                x = 20
                y += 40
    else:
        F.display_text(screen, "Rarity: " + item["Rarity"], 20, (20, 140))
        text_rect = F.display_text(screen, "Describtion: ", 20, (20, 180))
        x = 20 + text_rect.w
        y = 180
        for txt in str(item["Describtion"]).split(" "):
            text_rect = F.display_text(screen, txt + " ", 20, (x, y))
            x = text_rect.x + text_rect.w
            if x >= 500:
                x = 20
                y += 40

def add_item(screen, clock, char_name):
    running = True
    selected_entry = -1
    pressed = -1
    text_dict = {"Item": ["", 0],
                 "Gold": ["", 0]}
    timer = 10
    text_size = 30
    dict = {
        0: ["Add Items", "background", "background", "rect-place-holder", "black"],
        1: ["Add Gold", "background", "background", "rect-place-holder", "black"],
        2: ["Remove Gold", "background", "background", "rect-place-holder", "black"],
    }
    display_texts = []
    send_key = ""
    while running:
        x = S.SCREEN_WIDTH * 0.2
        y = S.SCREEN_HEIGHT * 0.1
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        item_entry = F.add_entry_to_list((x + S.SCREEN_WIDTH * 0.2, y + 8, 200, 30), "item", screen, "Item Name: ", text_size, (x, y))
        x += S.SCREEN_WIDTH * 0.4
        gold_entry = F.add_entry_to_list((x + S.SCREEN_WIDTH * 0.2, y + 8, 200, 30), "item", screen, "Gold: ", text_size, (x, y))
        button_width = S.SCREEN_WIDTH / 5
        button_height = S.SCREEN_HEIGHT / 20
        screen_top = S.SCREEN_HEIGHT * 0.9
        x_pos = [ S.SCREEN_WIDTH * 0.1, S.SCREEN_WIDTH * 0.3, S.SCREEN_WIDTH * 0.5]
        buttons = F.display_back_button(screen, "Back")
        buttons = F.display_other_buttons(screen, text_size, (x_pos, screen_top, button_width, button_height), dict) + buttons
        for event in pg.event.get():
            keys = pg.key.get_pressed()
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                pos = pg.mouse.get_pos()
                if item_entry.collidepoint(pos):
                    selected_entry = 0
                elif gold_entry.collidepoint(pos):
                    selected_entry = 1
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(pos):
                        pressed = i
                        pg.draw.rect(screen, "black", buttons[i], width=3)

            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                pos = pg.mouse.get_pos()
                if selected_entry != -1 and [item_entry, gold_entry][selected_entry].collidepoint(pos):
                    pass
                else:
                    selected_entry = -1
                if pressed != -1 and buttons[pressed].collidepoint(pos):
                    if pressed == 0:
                        send_key = "get_item"
                    if pressed == 1:
                        send_key = "add_gold"
                    if pressed == 2:
                        send_key = "remove_gold"
                    if pressed == 3:
                        running = False
                    pressed = -1



            elif event.type == pg.TEXTINPUT and selected_entry != -1:
                property = list(text_dict.keys())[selected_entry]
                text_dict[property][0] += event.text
            if keys[pg.K_BACKSPACE] and selected_entry != -1 and not keys[pg.K_LCTRL]:
                property = list(text_dict.keys())[selected_entry]
                text_dict[property][0] = text_dict[property][0][:-1]
            elif keys[pg.K_BACKSPACE] and selected_entry != -1 and keys[pg.K_LCTRL]:
                property = list(text_dict.keys())[selected_entry]
                text_dict[property][0] = ""
            elif keys[pg.K_TAB] and selected_entry != -1:
                property = list(text_dict.keys())[selected_entry]
                item_list = find_closest(text_dict[property][0])
                if item_list != []:
                    text_dict[property][0] = item_list[0]

        F.update_text(text_dict, [item_entry, gold_entry], screen)

        ready = check_text_item(text_dict, screen, send_key, char_name)

        if ready:
            text = text_dict[ready][0]
            if send_key == "get_item":
                items = V.character_dict[char_name]["Items"].split(",")
                items.append(text)
                V.character_dict[char_name]["Items"] = ",".join(items)
                # V.character_dict[char_name]["Items"] += "," + text
                display_texts.append("Added " + text)
            elif send_key == "add_gold":
                V.character_dict[char_name]["Gold"] = float(V.character_dict[char_name]["Gold"]) + float(text)
                V.character_dict[char_name]["Gold"] = str(round(V.character_dict[char_name]["Gold"], 2))
                display_texts.append("Added " + text + " Gold")
            elif send_key == "remove_gold":
                display_texts.append("Removed " + text + " Gold")
                V.character_dict[char_name]["Gold"] = float(V.character_dict[char_name]["Gold"]) - float(text)
                V.character_dict[char_name]["Gold"] = str(round(V.character_dict[char_name]["Gold"], 2))
            send_key = ""
        else:
            send_key = ""

        xpos = S.SCREEN_WIDTH * 0.1
        ypos = S.SCREEN_HEIGHT * 0.3
        for textt in display_texts:
            F.display_text(screen, textt, 10, (xpos, ypos), "black", "C")
            ypos += S.SCREEN_HEIGHT * 0.02

        if selected_entry != -1:
            F.flash_marker(selected_entry, [item_entry, gold_entry], screen, timer, text_dict)

        pg.display.flip()
        clock.tick(60)
        timer = F.reset_timer(timer)

def check_text_item(text_dict, screen, key, char_name):
    ready = False
    for name, (text, rect) in text_dict.items():
        if name == "Gold":
            if all(char.isdigit() or char == "." for char in text) and text != "" and key == "add_gold":
                ready = name
            elif all(char.isdigit() or char == "." for char in text) and text != "" and key == "remove_gold":
                if float(V.character_dict[char_name]["Gold"]) > float(text):
                    ready = name
            elif key == "add_gold" or key == "remove_gold":
                F.display_text(screen, "Only add numbers to gold entry", 30, (rect.x - S.SCREEN_WIDTH * 0.3, rect.y + S.SCREEN_HEIGHT * 0.6))
        elif name == "Item":
            item_list = find_closest(text)
            y_off = rect.h
            for i in range(0, 5):
                if len(item_list) >= i + 1:
                    F.display_text(screen, item_list[i], 20, (rect.x + rect.w / 2, rect.y + rect.h / 2 + y_off), "black", "C")
                    y_off += rect.h
                    if text == item_list[i] and key == "get_item":
                        ready = name

    return ready


def find_closest(text):
    similar = []
    if text != "":
        text = text[0].upper() + text[1:]
        for item_name in list(V.item_dict.keys()):
            if text == item_name[:len(text)]:
                similar.append(item_name)
    return similar

def delete_items(item_dict, pressed):
    if item_dict[pressed] == 1:
        "Only one item exists in the bag"
        del item_dict[pressed]
        with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
            char_config_data = json.load(file)
        if char_config_data.get("Equiped Items") != None:
            to_remove = []
            equiped_item_dict = char_config_data["Equiped Items"].copy()
            for key, item_name in equiped_item_dict.items():
                if pressed in item_name:
                    if "," in item_name:
                        items = item_name.split(",")
                        items.remove(pressed)
                        equiped_item_dict[key] = ",".join(items)
                    else:
                        to_remove.append(key)
            for key in to_remove:
                equiped_item_dict[key] = ""
            F.save_equiped_items(equiped_item_dict)
    else:
        item_dict[pressed] -= 1
        equiped_item_dict = None
    V.character_dict[V.char_name]["Items"] = V.character_dict[V.char_name]["Items"].replace(pressed, "", 1).replace(",,",",")
    V.character_dict[V.char_name]["Items"] = V.character_dict[V.char_name]["Items"].replace(",,",",")
    text_dict = {}
    for keyy, value in V.character_dict[V.char_name].items():
        if keyy not in ["Health", "Ability_Scores"]:
            text_dict[keyy] = [value, 0]
    text_dict["Name"] = [V.char_name, 0]
    F.save_data(text_dict, "characters")
    return equiped_item_dict


def handle_equip_items(pressed, equiped_item_dict):
    """removing"""
    remove_flag = False
    for type, item_name in equiped_item_dict.items():
        if pressed in item_name:
            if "," in item_name:
                items = item_name.split(",")
                items.remove(pressed)
                equiped_item_dict[type] = ",".join(items)
                remove_flag = True
            else:
                equiped_item_dict[type] = ""
                remove_flag = True
    if remove_flag:
        V.EQUIPED_CHAR_ITEMS = equiped_item_dict.copy()
        return equiped_item_dict
    else:
        """adding"""
        if equiped_item_dict.get("Weapons") == None:
            equiped_item_dict["Weapons"] = ""
        if equiped_item_dict.get("Magic Weapon") == None:
            equiped_item_dict["Magic Weapon"] = ""
        if equiped_item_dict.get("Shield") == None:
            equiped_item_dict["Shield"] = ""


        """Armour magical and not, and shields"""
        if V.item_dict[pressed]["Type"] in ["Armour", "Magic Armour"] and V.item_dict[pressed]["Properties"] != "Shield":
            equiped_item_dict["Armour"] = ""
            equiped_item_dict["Magic Armour"] = ""
            equiped_item_dict[V.item_dict[pressed]["Type"]] = pressed
        elif V.item_dict[pressed]["Type"] in ["Armour", "Magic Armour"] and V.item_dict[pressed]["Properties"] == "Shield":
            equiped_item_dict["Shield"] = pressed
            if equiped_item_dict["Weapons"] != "" and "," not in equiped_item_dict["Weapons"]:
                if "Two-handed" in V.item_dict[equiped_item_dict["Weapons"]]["Properties"]:
                    equiped_item_dict["Weapons"] = ""
            if equiped_item_dict["Magic Weapon"] != "" and "," not in equiped_item_dict["Magic Weapon"]:
                if "Two-handed" in V.item_dict[equiped_item_dict["Magic Weapon"]]["Properties"]:
                    equiped_item_dict["Magic Weapon"] = ""
            if equiped_item_dict["Weapons"] != "" and "," in equiped_item_dict["Weapons"]:
                """if there are already two regular weapons remove one add shield"""
                items = equiped_item_dict["Weapons"].split(",")
                equiped_item_dict["Weapons"] = items[1]

            if equiped_item_dict["Magic Weapon"] != "" and "," in equiped_item_dict["Magic Weapon"]:
                """if there are already two magic weapons remove one add shield"""
                items = equiped_item_dict["Magic Weapon"].split(",")
                equiped_item_dict["Magic Weapon"] = items[1]

            if equiped_item_dict["Weapons"] != "" and equiped_item_dict["Magic Weapon"] != "":
                """if there is one magic and one regular item selected, remove the regular one, add shield"""
                equiped_item_dict["Weapons"] = ""


        """Two handed weapons"""
        if V.item_dict[pressed]["Type"] in ["Weapons", "Magic Weapon"] and "Two-handed" in V.item_dict[pressed]["Properties"]:
            equiped_item_dict["Weapons"] = ""
            equiped_item_dict["Magic Weapon"] = ""
            equiped_item_dict["Shield"] = ""
            equiped_item_dict[V.item_dict[pressed]["Type"]] = pressed

        """ Not Two Handed weapons """
        if V.item_dict[pressed]["Type"] in ["Weapons", "Magic Weapon"] and "Two-handed" not in V.item_dict[pressed]["Properties"]:
            """if its a weapon or magic weapon that is not two handed"""
            if equiped_item_dict["Weapons"] != "" and "," not in equiped_item_dict["Weapons"]:
                """if there is a two handed weapon or single one handed weapon already"""
                if "Two-handed" in V.item_dict[equiped_item_dict["Weapons"]]["Properties"]:
                    """if there is a two handed weapon already, unequip it"""
                    equiped_item_dict["Weapons"] = ""
            if equiped_item_dict["Magic Weapon"] != "" and "," not in equiped_item_dict["Magic Weapon"]:
                """if there is a two handed weapon or single one handed weapon already"""
                if "Two-handed" in V.item_dict[equiped_item_dict["Magic Weapon"]]["Properties"]:
                    """if there is a two handed weapon already, unequip it"""
                    equiped_item_dict["Magic Weapon"] = ""
            if equiped_item_dict["Weapons"] != "" or equiped_item_dict["Magic Weapon"] != "":
                """if there is a weapon here still"""
                if "," in equiped_item_dict["Weapons"]:
                    """if there are already two regular weapons remove one add new. shield should not have been active"""
                    items = equiped_item_dict["Weapons"].split(",")
                    equiped_item_dict["Weapons"] = items[1] + "," + pressed
                elif "," in equiped_item_dict["Magic Weapon"]:
                    """if there are already two magic weapons remove one add new. shield should not have been active"""
                    items = equiped_item_dict["Magic Weapon"].split(",")
                    equiped_item_dict["Magic Weapon"] = items[1] + "," + pressed
                elif equiped_item_dict["Weapons"] != "" and equiped_item_dict["Magic Weapon"] != "":
                    """if there is already one magical and one regular weapon, change the same type. shield should not have been active"""
                    equiped_item_dict[V.item_dict[pressed]["Type"]] = pressed
                    equiped_item_dict["Shield"] = ""
                else:
                    """If there is only one weapon in one category or both categories"""
                    if equiped_item_dict[V.item_dict[pressed]["Type"]] == "":
                        """if this category is empty fill it, that means the other category had a weapon already"""
                        equiped_item_dict[V.item_dict[pressed]["Type"]] = pressed
                        equiped_item_dict["Shield"] = ""

                    else:
                        """if this category is not empty that means the other one was"""
                        equiped_item_dict[V.item_dict[pressed]["Type"]] += "," + pressed
                        equiped_item_dict["Shield"] = ""

            else:
                """if there are no weapons here"""
                equiped_item_dict[V.item_dict[pressed]["Type"]] = pressed
        if V.item_dict[pressed]["Type"] not in ["Armour", "Magic Armour", "Weapons", "Magic Weapon"]:
            if equiped_item_dict.get(V.item_dict[pressed]["Type"]) == None:
                equiped_item_dict[V.item_dict[pressed]["Type"]] = pressed
            else:
                equiped_item_dict[V.item_dict[pressed]["Type"]] += "," + pressed
            if equiped_item_dict[V.item_dict[pressed]["Type"]][0] == ",":
                equiped_item_dict[V.item_dict[pressed]["Type"]] = equiped_item_dict[V.item_dict[pressed]["Type"]][1:]
        # equiped_item_dict[V.item_dict[pressed]["Type"]] = pressed
    V.EQUIPED_CHAR_ITEMS = equiped_item_dict.copy()
    return equiped_item_dict

def handle_item_consumption(item_name, screen, clock):
    rolled_sum = 0
    value = 0
    if V.item_dict[item_name]["Type"] == "Food":
        food_effects = V.item_dict[item_name]["Extra"]
        if ":" in food_effects:
            food_effects = food_effects.split(":")
            if food_effects[0:2] == ["Char", "Health"]:
                value = food_effects[2]
                if "+" in value:
                    value = int(value.replace("+", ""))

    elif V.item_dict[item_name]["Type"] == "Potions":
        multiple_rolls = []
        dice, modifyer = V.item_dict[item_name]["Extra"].split("+")
        for i in range(0, int(dice[0])):
            a = random.randint(1, 5)
            multiple_rolls.append(a)
        F.Roll_3d_dice(screen, clock, dice[1:].upper(), multiple_rolls, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.5))
        rolled_sum = sum(multiple_rolls) + int(modifyer)
        F.add_to_roll_history(multiple_rolls, rolled_sum, "Consumed: " + item_name)
        value = rolled_sum

    V.character_dict[V.char_name]["Health"][0] += value
    if V.character_dict[V.char_name]["Health"][0] > V.character_dict[V.char_name]["Health"][1]:
        V.character_dict[V.char_name]["Health"][0] = V.character_dict[V.char_name]["Health"][1]

    return rolled_sum

def handle_armor_effects(char):
    armor_list = F.get_equiped_armor()
    if armor_list == []:
        char["AC"] = V.BASE_AC
    else:
        for armor in armor_list:
            a = V.item_dict[armor]["Extra"].split("; ")
            for armor_data in a:
                # print(armor_data)
                if "AC" in armor_data:
                    armor_data = armor_data.replace("AC: ", "")
                    char["AC"] = armor_data
                else:
                    if "speed unless Str > " in armor_data:
                        a_d = armor_data.split("speed unless Str > ")
                        STR = char["Ability_Scores"].split(",")[0]
                        if int(STR) < int(a_d[1]):
                            V.SPEED_OFFSET = int(a_d[0])
                            char["Speed"] = str(int(V.BASE_SPEED) + int(V.SPEED_OFFSET))


def handle_armor_proficiencies(character, disadvantage, case):
    if V.EQUIPED_CHAR_ITEMS != {} and character.get("Armor Proficiencies") != None:
        armor_proficiencies = character["Armor Proficiencies"].split(",")  # shields included
        if V.EQUIPED_CHAR_ITEMS.get("Shield") != '' and V.EQUIPED_CHAR_ITEMS.get("Shield") != None:
            """Shield is equiped"""
            if "Shields" not in armor_proficiencies and case in ["STR", "DEX", "Magic"]:
                disadvantage = True
        if V.EQUIPED_CHAR_ITEMS.get("Armour") != '' and V.EQUIPED_CHAR_ITEMS.get("Armour") != None:
            if V.item_dict[V.EQUIPED_CHAR_ITEMS["Armour"]]["Properties"] + " Armor" not in armor_proficiencies and case in ["STR", "DEX", "Magic"]:
                disadvantage = True
    return disadvantage

def handle_stealth_disadvantage(pressed, disadvantage):
    if "Stealth" in pressed[0] and V.EQUIPED_CHAR_ITEMS != {}:
        if V.EQUIPED_CHAR_ITEMS.get("Armour") != '' or V.EQUIPED_CHAR_ITEMS.get("Armour") != None:
            if V.EQUIPED_CHAR_ITEMS.get("Armour") in ["Plate", "Splint", "Chain mail", "Padded", "Scale mail", "Half plate", "Ring mail"]:
                disadvantage = True
    return disadvantage


def get_equiped_items():
    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)

    V.EQUIPED_CHAR_ITEMS = {}
    if char_config_data.get("Equiped Items") != None:
        equiped_item_dict = char_config_data["Equiped Items"].copy()
        V.EQUIPED_CHAR_ITEMS = equiped_item_dict.copy()


    char_size = V.character_dict[V.char_name]["Size"]

    str_score = V.character_dict[V.char_name]["Ability_Scores"].split(",")[0]

    carry_capacity = 15 * int(str_score)

    char_size_int = V.race_size_to_int[char_size]

    if "Powerful Build" in V.character_dict[V.char_name]["Code"]:
        char_size_int += 1

    if char_size_int != 2:  # MEDIUM
        if char_size_int == 0:
            carry_capacity = int(carry_capacity / 2)
        if char_size_int == 3:
            carry_capacity = int(carry_capacity * 2)
        if char_size_int == 4:
            carry_capacity = int(carry_capacity * 4)
        if char_size_int == 5:
            carry_capacity = int(carry_capacity * 6)


    item_dict, weight = sort_items(V.char_name, carry_capacity)