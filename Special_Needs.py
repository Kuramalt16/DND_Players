import pygame as pg, math, json, random
import Functions as F, Variables as V, Settings as S, Skills as sk, conditions as C, DisplayChar as dCh, Actions as A, Help as H

def handle_special_flag_needs(screen, clock, character):
    if character.get("Code") == None or 'Natural Recovery' not in character["Code"]:
        return
    if V.Special_Flags.get("Natural_Recovery_Used") == None:
        V.Special_Flags["Natural_Recovery_Used"] = 0
        return
    else:
        if V.Special_Flags["Natural_Recovery_Used"] != 1:
            return

    feature = "Natural Recovery"
    available_functions = {'Natural Recovery': feature}
    backup_dict_1 = {}
    backup_dict_2 = {}

    if "Druid" in character["Class"] and feature == "Natural Recovery":
        """GET How many 1st level slots can be used"""
        temp_index = character["Class"].split(", ").index("Druid")
        temp_value = character["Level"].split(",")[temp_index]
        temp_value = int(temp_value) / 2
        temp_value = math.floor(temp_value) + 1
        available_functions["Natural Recovery"] = temp_value
        backup_dict_1 = V.spell_slots.copy()
        """GET a list of fully recovered spell slots"""
        remainder_slot_dict = {}
        full_slot_dict = {}
        classes = []
        classes.append(V.character_dict[V.char_name]["Class"].split(", "))
        classes.append(V.character_dict[V.char_name]["SubClass"].split(","))
        position = lambda x, t: 0 if x == t[0] else 1 if x == t[-1] else None
        """Adds spell slots based on class"""
        for i in range(0, len(classes)):
            for char_class in classes[i]:
                level = V.character_dict[V.char_name]["Level"].split(",")[position(char_class, classes[i])]
                if V.Available_spells_data.get(char_class) != None:
                    slots = V.Available_spells_data[char_class][int(level)][3]
                    for slot in slots.split(","):
                        type, amount = slot.split(":")
                        if int(type[0]) > 5:
                            continue
                        if full_slot_dict.get(type) == None:
                            full_slot_dict[type] = 0
                        full_slot_dict[type] += int(amount)

        """subtract the used slots from the full list to get the diferance"""
        for type, amount in full_slot_dict.items():
            if remainder_slot_dict.get(type) == None:
                remainder_slot_dict[type] = 0
            if V.spell_slots.get(type) != None:
                remainder_slot_dict[type] = amount - V.spell_slots[type]
            else:
                remainder_slot_dict[type] = amount

        backup_dict_2 = remainder_slot_dict.copy()
    else:
        F.print_debug("I DONT KNOW THIS ONE PLEASE HELP", debug="ERROR")
        return

    text_size = 30
    pressed = -1
    button_dict = {
        (0, 0): ["Reset", "background", "background", "rect-place-holder", "black"],
    }
    running = True
    slot_buttons = {}
    while running:
        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.05
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Back")
        x_pos = [S.SCREEN_WIDTH * 0.52]
        y_pos = [S.SCREEN_HEIGHT * 0.9]

        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)
        F.display_text(screen, feature, 30, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1), case="C")

        start_x = S.SCREEN_WIDTH * 0.25
        start_y = S.SCREEN_HEIGHT * 0.2
        step_y = S.SCREEN_HEIGHT * 0.05
        step_x = S.SCREEN_WIDTH * 0.1
        if feature == "Natural Recovery":
            F.display_text(screen, "Natural Recovery points left: " + str(available_functions[feature]) + " Press on the slot images or reset if you goofy", 20, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.15), case="C")
            slot_w = S.SCREEN_WIDTH * 0.05
            slot_h = S.SCREEN_WIDTH * 0.05
            for type, amount in remainder_slot_dict.items():
                if amount != 0:
                    F.display_text(screen, type, 15, (start_x + step_x, start_y), case="C")
                    for i in range(0, amount):
                        rect = F.add_image_to_screen(screen, type, (start_x + step_x, start_y + step_y, slot_w, slot_h), "background")
                        slot_buttons[(type, i)] = rect
                        step_y += S.SCREEN_HEIGHT * 0.1
                    step_x += S.SCREEN_WIDTH * 0.07
                    step_y = S.SCREEN_HEIGHT * 0.05

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
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                        for key, value in button_dict.items():
                            if value[3] == buttons[i]:
                                pressed = value[0]
                if feature == "Natural Recovery":
                    for (type, id), rect in slot_buttons.items():
                        if rect.collidepoint(mouse_pos):
                            pressed = (type, id)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    mouse_pos = pg.mouse.get_pos()
                    if pressed == "Back":
                        if V.Special_Flags["Natural_Recovery_Used"] == 1: V.Special_Flags["Natural_Recovery_Used"] = 0
                        return
                    elif pressed == "Reset":
                        if feature == "Natural Recovery":
                            V.spell_slots = backup_dict_1.copy()
                            remainder_slot_dict = backup_dict_2.copy()
                            available_functions["Natural Recovery"] = temp_value
                            V.Special_Flags["Natural_Recovery_Used"] = 0
                    elif feature == "Natural Recovery" and isinstance(pressed, tuple) and slot_buttons[pressed].collidepoint(mouse_pos):
                        if int(pressed[0][0]) <= available_functions[feature]:
                            available_functions[feature] -= int(pressed[0][0])
                            remainder_slot_dict[pressed[0]] -= 1
                            if V.spell_slots.get(pressed[0]) == None:
                                V.spell_slots[pressed[0]] = 0
                            V.spell_slots[pressed[0]] += 1
                            V.Special_Flags["Natural_Recovery_Used"] = 2
                    pressed = -1

        pg.display.flip()
        clock.tick(60)


def display_wild_shapes(screen, clock):
    if V.Special_Flags.get("Wild Shape") == None:
        return
    character = V.character_dict[V.char_name]

    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)

    if char_config_data["Choises"].get("Beasts") == None:
        char_config_data["Choises"]["Beasts"] = []
        mob_names = []
    else:
        mob_names = char_config_data["Choises"]["Beasts"].copy()

    running = True
    dict = {
        0: ["Add Wild Shapes", "background", "background", "rect-place-holder", "black"],
        1: ["Wild Shape", "background", "background", "rect-place-holder", "dark grey"],
    }
    text_size = 30
    mob_buttons = {}
    pressed = -1
    selected_mob = False
    while running:
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        F.display_text(screen, "Choose a shape with left mouse click", 30, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.05), case="C")
        if mob_names != []:
            x = S.SCREEN_WIDTH * 0.1
            y = S.SCREEN_HEIGHT * 0.15
            w = S.SCREEN_WIDTH * 0.08
            h = S.SCREEN_WIDTH * 0.08
            for mob in mob_names:
                rect = F.add_image_to_screen(screen, mob, (x, y, w, h), "mob")
                mob_buttons[mob] = rect
                F.display_text(screen, str(mob), 20, (x + w / 2, y + h / 2), "blue", "C")
                x += S.SCREEN_WIDTH * 0.1
                if x + w >= S.SCREEN_WIDTH * 0.9:
                    x = S.SCREEN_WIDTH * 0.1
                    y += S.SCREEN_HEIGHT * 0.15


        buttons = F.display_back_button(screen, "Back")

        button_width = S.SCREEN_WIDTH / 4
        button_height = S.SCREEN_HEIGHT / 20
        screen_top = S.SCREEN_HEIGHT * 0.9
        x_pos = [S.SCREEN_WIDTH * 0.45, S.SCREEN_WIDTH * 0.15]

        dict[1][4] = "dark grey"
        if selected_mob:
            dict[1][4] = "black"
        buttons = buttons + F.display_other_buttons(screen, 30, (x_pos, screen_top, button_width, button_height), dict)
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
                for mob_name, rect in mob_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        pressed = mob_name
                        pg.draw.rect(screen, "black", rect, width=3)


            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                if pressed != -1 and isinstance(pressed, int) and buttons[pressed].collidepoint(mouse_pos):
                    if pressed == 0:
                        """Back button pressed"""
                        del V.Special_Flags["Wild Shape"]
                        running = False
                    elif pressed == 1:
                        """add wild shape"""
                        mob_name = add_wild_shape(screen, clock, char_config_data["Choises"]["Beasts"])
                        if mob_name != None:
                            if char_config_data["Choises"]["Beasts"] == None:
                                char_config_data["Choises"]["Beasts"] = []
                            char_config_data["Choises"]["Beasts"].append(mob_name)
                            """SAVING"""
                            F.create_char_JSON(V.char_name, char_config_data)
                            mob_names.append(mob_name)


                            # F.save_data(text_dict, "characters")
                    elif selected_mob and pressed == 2:
                        WildShape(screen, clock, selected_mob)
                        del V.Special_Flags["Wild Shape"]
                        running = False
                elif isinstance(pressed, str) and mob_buttons[pressed].collidepoint(mouse_pos):
                    selected_mob_display(pressed, screen, clock)


                pressed = -1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                mouse_pos = pg.mouse.get_pos()
                selected_mob = False
                for mob_name, rect in mob_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        selected_mob = mob_name


        if selected_mob:
            pg.draw.rect(screen, "green", mob_buttons[selected_mob], width=2)
        pg.display.flip()
        clock.tick(60)  # limits FPS to 60

def add_wild_shape(screen, clock, existing_beasts):
    """"""
    running = True
    pressed = -1
    mob_buttons = {}
    while running:
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        x = S.SCREEN_WIDTH * 0.1
        y = S.SCREEN_HEIGHT * 0.05
        w = S.SCREEN_WIDTH * 0.08
        h = S.SCREEN_WIDTH * 0.08
        buttons = F.display_back_button(screen, "Back")
        for mob_name, values in V.mob_dict.items():
            if values["Type"] == "Beast" and mob_name not in existing_beasts:
                rect = F.add_image_to_screen(screen, mob_name, (x, y, w, h), "mob")
                mob_buttons[mob_name] = rect
                F.display_text(screen, str(mob_name), 20, (x + w / 2, y + h / 2), "blue", "C")
                x += S.SCREEN_WIDTH * 0.1
                if x + w >= S.SCREEN_WIDTH * 0.9:
                    x = S.SCREEN_WIDTH * 0.1
                    y += S.SCREEN_HEIGHT * 0.15
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
                for name, rect in mob_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        pressed = name
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                if pressed != -1 and isinstance(pressed, int) and buttons[pressed].collidepoint(mouse_pos):
                    if pressed == 0:
                        """Back button pressed"""
                        running = False
                elif isinstance(pressed, str):
                    """add wild shape"""
                    return pressed
                else:
                    pressed = -1

        pg.display.flip()
        clock.tick(60)  # limits FPS to 60


def selected_mob_display(selected, screen, clock):
    running = True
    pressed = -1

    while running:
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        display_mob(V.mob_dict[selected], screen, selected)
        buttons = F.display_back_button(screen, "Back")
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(mouse_pos):
                        pressed = i
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                if pressed != -1 and buttons[pressed].collidepoint(mouse_pos):
                    if pressed == 0:
                        """Back button pressed"""
                        running = False
                else:
                    pressed = -1
        pg.display.flip()
        clock.tick(60)  # limits FPS to 60

def display_mob(mob, screen, mob_name, pos=None, disp_hp=True, override=None):
    img_x = S.SCREEN_WIDTH * 0.7
    img_y = S.SCREEN_HEIGHT * 0.05
    img_w = S.SCREEN_WIDTH * 0.25
    img_h = S.SCREEN_HEIGHT * 0.3
    start_y = S.SCREEN_HEIGHT * 0.02
    start_x = S.SCREEN_WIDTH * 0.02
    step_y = S.SCREEN_HEIGHT * 0.05
    if override != None and "Health" in override:
        mob_hp = override["Health"]
    else:
        mob_hp = mob["Health"]

    if pos != None:
        img_x = pos[0]
        img_y = pos[1]
        img_w = pos[2]
        img_h = pos[3]
        start_y = pos[4]
        start_x = pos[5]
        step_y = pos[6]

    rect = F.add_image_to_screen(screen, mob_name, (img_x, img_y, img_w, img_h), "mob")
    if disp_hp:
        remainder = round(((int(mob_hp[0]) / int(mob_hp[1])) - 1) * -1, 3)
        health_bar_x = rect.x
        health_bar_w = rect.w
        health_bar_y = rect.y + rect.h
        health_bar_h = 0
        health_bar_h_final = rect.h
        pg.draw.rect(screen, "red", pg.Rect(health_bar_x, health_bar_y - (health_bar_h_final * remainder), health_bar_w,health_bar_h + (health_bar_h_final * remainder)))

        if remainder >= 1:
            F.display_text(screen, "DEAD", 30, (rect.x + rect.w / 2, rect.y + rect.h / 2), case="C")




    speed_dict = {0: "Walking",
                  1: "Climbing",
                  2: "Swimming",
                  3: "Flying",
                  4: "Burrowing",
    }
    sense_dict = {
        0: "Passive Perception: ",
        1: "Darkvision: ",
        2: "Tremorsense: ",
        3: "Blindsight: ",
        4: "Truesight: "
    }
    saving_throw_dict = {
        0: "STR: ",
        1: "DEX: ",
        2: "CON: ",
        3: "INT: ",
        4: "WIS: ",
        5: "CHA: ",
    }

    AB_score_dict = {
        0: "STR: ",
        1: "DEX: ",
        2: "CON: ",
        3: "INT: ",
        4: "WIS: ",
        5: "CHA: ",
    }

    F.display_text(screen, "Name: " + mob_name, 20, (start_x, start_y))
    start_y += step_y

    F.display_text(screen, "Challange: " + mob["Challange"], 20, (start_x, start_y))
    start_y += step_y

    r = F.display_text(screen, "Health: ", 20, (20, start_y))
    F.display_text(screen, str(mob_hp[0]) + "|" + str(mob_hp[1]), 20, (start_x + r.w, start_y), color="red")
    start_y += step_y

    r = F.display_text(screen, "Type: " + mob["Type"], 20, (20, start_y))
    F.display_text(screen, ", Size: " + mob["Size"], 20, (r.x + r.w, start_y))
    start_y += step_y

    F.display_text(screen, "Alignment: " + V.character_dict[V.char_name]["Alignment"], 20, (start_x, start_y))
    start_y += step_y

    speed = mob["Speed"].split(",")
    r = pg.Rect(start_x, start_y, 0, 0)
    for i in range(0, len(speed)):
        if speed[i] != "":
            r = F.display_text(screen, speed_dict[i], 20, (r.x + r.w, start_y))
            if V.Condition != "" and V.Condition in ["Exhaustion lv2", "Exhaustion lv3", "Exhaustion lv4", "Exhaustion lv5", "Exhaustion lv6", "Restrained", "Grappled", "Unconscious", "Stunned", "Petrified", "Paralyzed"]:
                if V.Condition in ["Exhaustion lv5", "Exhaustion lv6", "Restrained", "Grappled", "Unconscious", "Stunned", "Petrified", "Paralyzed"]:
                    r = F.display_text(screen, " speed: 0 ", 20, (r.x + r.w, start_y))
                else:
                    """If condition is above exhaustion level 2 but bellow level 5"""
                    r = F.display_text(screen, " speed: " + str(math.floor(int(speed[i]) / 2)) + " ", 20, (r.x + r.w, start_y))
            else:
                r = F.display_text(screen, " speed: " + speed[i] + " ", 20, (r.x + r.w, start_y))
    start_y += step_y




    F.display_text(screen, "AC: " + mob["AC"], 20, (start_x, start_y))
    start_y += step_y

    r = pg.Rect(start_x, start_y, 0, 0)
    for i in range(0, len(mob["Ability Score"].split(","))):
        if AB_score_dict[i] in ["INT: ", "WIS: ", "CHA: "]:
            r = F.display_text(screen, AB_score_dict[i] + V.character_dict[V.char_name]["Ability_Scores"].split(",")[i] + " ", 20, (r.x + r.w, start_y))
        else:
            r = F.display_text(screen, AB_score_dict[i] + mob["Ability Score"].split(",")[i] + " ", 20, (r.x + r.w, start_y))
    start_y += step_y



    if mob.get("Skills") != None:
        F.display_text(screen, "Skills: " + mob["Skills"], 20, (start_x, start_y))
    else:
        F.display_text(screen, "Skills: ", 20, (start_x, start_y))
    start_y += step_y

    r = F.display_text(screen, "Sences: ", 20, (start_x, start_y))
    for i in range(0, len(mob["Sences"].split(","))):
        if mob["Sences"].split(",")[i] == "":
            continue
        r = F.display_text(screen, sense_dict[i] + mob["Sences"].split(",")[i] + " ", 20, (r.x + r.w, start_y))
    start_y += step_y

    r = F.display_text(screen, "Saving Throws: ", 20, (start_x, start_y))
    for i in range(0, len(mob["Saving Throws"].split(","))):
        if mob["Saving Throws"].split(",")[i] == "":
            continue
        r = F.display_text(screen, saving_throw_dict[i] + mob["Saving Throws"].split(",")[i] + " ", 20, (r.x + r.w, start_y))
    start_y += step_y

    F.display_text(screen, "Languages: " + mob["Languages"], 20, (start_x, start_y))
    start_y += step_y

    F.display_text(screen, "Abilities: " + mob["Abilities"], 20, (start_x, start_y))
    start_y += step_y

    F.display_text(screen, "Actions: " + mob["Actions"], 20, (start_x, start_y))
    start_y += step_y

    if V.Condition in ["Petrified"]:
        F.display_text(screen, "Resistances: " + mob["Resistances"] + " All Damage Types", 20, (start_x, start_y))
    elif V.Condition in ["Invisible"]:
        F.display_text(screen, "Resistances: " + mob["Resistances"] + " Disadvantage All Attack rolls", 20, (start_x, start_y))
    elif V.Condition in ["Prone"]:
        F.display_text(screen, "Resistances: " + mob["Resistances"] + " Disadvantage ranged Attack rolls", 20, (start_x, start_y))
    else:
        F.display_text(screen, "Resistances: " + mob["Resistances"], 20, (start_x, start_y))
    start_y += step_y


    if V.Condition in ["Petrified"]:
        F.display_text(screen, "Immunities: " + mob["Immunities"] + " Poison, Disease", 20, (start_x, start_y))
    else:
        F.display_text(screen, "Immunities: " + mob["Immunities"], 20, (start_x, start_y))
    start_y += step_y


    F.display_text(screen, "Vulnerabilities: " + mob["Vulnerabilities"], 20, (start_x, start_y))
    if V.Condition in ["Prone"]:
        F.display_text(screen, "Vulnerabilities: " + mob["Vulnerabilities"] + " Advantage for Close range attack rolls", 20, (start_x, start_y))
    elif V.Condition in ["Stunned", "Restrained", "Petrified", "Blinded"]:
        F.display_text(screen, "Vulnerabilities: " + mob["Vulnerabilities"] + " Advantage for All Attack rolls", 20, (start_x, start_y))
    elif V.Condition in ["Unconscious", "Paralyzed"]:
        F.display_text(screen, "Vulnerabilities: " + mob["Vulnerabilities"] + " Advantage for All Attack rolls, Critical damage for close range attacks", 20, (start_x, start_y))
    else:
        F.display_text(screen, "Vulnerabilities: " + mob["Vulnerabilities"], 20, (start_x, start_y))
    start_y += step_y


def WildShape(screen, clock, selected, special_case="Wildshape"):
    running = True
    pressed = -1

    button_dict = {
        (3, 0): ["Update Hp", "background", "background", "rect-place-holder", "black"],
        (1, 1): ["Skills", "background", "background", "rect-place-holder", "black"],
        (2, 1): ["Actions", "background", "background", "rect-place-holder", "black"],
        (2, 0): ["Conditions", "background", "background", "rect-place-holder", "black"],
    }
    timer = 10
    txt_dict = {"Heal": ["", 0]}
    selected_entry = -1

    if special_case == "Ranger's Companion" and V.Ranger_Companion == {}:
        if int(V.character_dict[V.char_name]["Level"]) * 4 > int(V.mob_dict[selected]["Health"][1]):
            disp_hp = int(V.character_dict[V.char_name]["Level"]) * 4
        else:
            disp_hp = int(V.mob_dict[selected]["Health"][1])

        V.Ranger_Companion = {
            "Name": selected,
            "Health": [disp_hp, disp_hp],
        }
        V.mob_dict[selected]["Health"] = V.Ranger_Companion["Health"]

    elif special_case == "Ranger's Companion" and V.Ranger_Companion != {}:
        V.mob_dict[selected]["Health"] = V.Ranger_Companion["Health"]

    while running:
        if int(V.mob_dict[selected]["Health"][0]) <= 0 and special_case == "Wildshape":
            """IF mob gets too hurt reduce player hp tiek kiek persinesa wildshape only"""
            V.character_dict[V.char_name]["Health"][0] += int(V.mob_dict[selected]["Health"][0])
            V.mob_dict[selected]["Health"] = [int(V.mob_dict[selected]["Health"][1]), int(V.mob_dict[selected]["Health"][1])]
            return
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")

        """Display hp entry"""
        x = S.SCREEN_WIDTH * 0.4
        y = S.SCREEN_HEIGHT * 0.5
        w = S.SCREEN_WIDTH * 0.25
        h = S.SCREEN_HEIGHT * 0.04
        enter_hp = F.add_entry_to_list((x + S.SCREEN_WIDTH * 0.3, S.SCREEN_HEIGHT * 0.44, w, h), "hp", screen, "", 20, (x - S.SCREEN_WIDTH * 0.2, y))

        """Display mob data"""
        display_mob(V.mob_dict[selected], screen, selected)


        """Display back button"""
        buttons = F.display_back_button(screen, "Switch back")

        """Display other buttons"""
        x_pos = [S.SCREEN_WIDTH * 0.02, S.SCREEN_WIDTH * 0.27, S.SCREEN_WIDTH * 0.52, S.SCREEN_WIDTH * 0.77]
        y_pos = [S.SCREEN_HEIGHT * 0.8, S.SCREEN_HEIGHT * 0.9]
        button_width = S.SCREEN_WIDTH / 5
        button_height = S.SCREEN_HEIGHT / 20
        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)

        """Run user input commands"""
        for event in pg.event.get():
            keys = pg.key.get_pressed()

            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
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
                        """Update hp"""

                        txt_dict, selected_entry, got_damaged = dCh.update_char_hp_based_on_entry(V.mob_dict[selected], txt_dict, selected_entry, screen, clock, temp_hp=False)
                    elif pressed == "Skills":
                        """Display Skills"""
                        sk.display_mob_skills(V.mob_dict[selected], screen, clock)
                    elif pressed == "Actions":
                        """Display Actions"""
                        if V.Condition not in ["Incapacitated", "Unconscious", "Stunned", "Petrified", "Paralyzed"]:
                            pass
                            Initialize_mob_actions(V.character_dict[V.char_name], screen, clock, selected)
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
                """Update hp"""
                txt_dict, selected_entry, got_damaged = dCh.update_char_hp_based_on_entry(V.mob_dict[selected], txt_dict, selected_entry, screen, clock, temp_hp=False)
        F.update_text(txt_dict, [enter_hp], screen)

        if selected_entry != -1:
            F.flash_marker(selected_entry, [enter_hp], screen, timer, txt_dict)

        pg.display.flip()
        clock.tick(60)
        timer = F.reset_timer(timer)

    if special_case == "Ranger's Companion":
        V.Ranger_Companion["Health"] = V.mob_dict[selected]["Health"]

def Initialize_mob_actions(character, screen, clock, mob_name):
    """Items have actions spell slots have actions"""
    """Display all action types"""

    weapon_list = F.get_equiped_weapons()
    weapon_list.remove("Unarmed Strike")
    weapon_list.remove("Improvised Attack")

    unknown_list = []
    spell_list = []
    feat_list = []

    ammo_count = {}
    for key, value in character.items():
        if key == "Code":
            extra_action_values = []
            for extra_action in value.split(","):
                if extra_action.count(':') > 1:
                    """Removes the first part of the title for example SubClass:Druid Circle:Land:Bonus Cantrip becomes Land:Bonus Cantrip"""
                    extra_action_values = extra_action.split(":")
                    extra_action = ":".join(extra_action_values[-2:])
                if extra_action not in unknown_list:
                    unknown_list.append(extra_action)
                    if S.Class_features.get(extra_action.split(":")[1]) != None and "Changed_Spell_Slot" in S.Class_features[extra_action.split(":")[1]]["Action_Type"]:
                        unknown_list.pop()
                        unknown_list.append(extra_action.replace("Feature", "Spell_slot"))
                    elif S.Class_features.get(extra_action.split(":")[1]) != None and "Class_Spell_Slot" in S.Class_features[extra_action.split(":")[1]]["Action_Type"]:
                        if "Spell_slot:" + extra_action.split(":")[1] not in unknown_list:
                            unknown_list.pop()
                            unknown_list += A.handle_slot_commands_from_subclass_json(S.Class_features[extra_action.split(":")[1]]["Spell_slot"], extra_action.split(":")[1])
                            """This change makes the code come here only initialy"""
                            S.Class_features[extra_action.split(":")[1]]["Action_Type"] = "Spell_Slot"
                    elif S.Class_features.get(extra_action.split(":")[1]) == None:
                        """Class features needs to have data on the list in unknown_list so because it was already appended, we remove the last member and we add it again"""
                        unknown_list.pop()
                        """Only deals with subclass features spells cantrips traits and shit"""
                        if extra_action_values != [] and extra_action_values[0] == "SubClass":
                            data = S.subclass_data.copy()
                            for key in extra_action_values[1:]:
                                """filters data"""
                                data = data.get(key, None)
                                if data is None:
                                    break
                            """Since this data doesn't exist in the Class Features, adding it, this is needed for the data in display actions->display features, if addding to unknown list, data must be in class features"""
                            S.Class_features[extra_action.split(":")[1]] = data
                            """sorts what type of subclass feature this is"""
                            if "Spell_Slot" in data["Action_Type"]:
                                slots = data["Spell_slot"]
                                unknown_list += A.handle_slot_commands_from_subclass_json(slots, extra_action.split(":")[1])
                                continue
                            if "Spell" == data["Action_Type"]:
                                spells = data["Spell"]
                                for spell in spells.split(","):
                                    spell_list.append(spell)
                            if "Feature:" + extra_action.split(":")[1] not in unknown_list:
                                unknown_list.append("Feature:" + extra_action.split(":")[1])
                            if "Subclass path" == data["Action_Type"]:
                                if data["Subclass"][0] == "CHOOSE":
                                    choise_made = F.check_if_choise_was_already_made(extra_action)
                                    if not choise_made:
                                        res = A.make_a_choise(data["Subclass"], screen, clock, extra_action_values)
                                        F.save_choise_json(extra_action, res)
        elif key == "Feat":
            for feat in value.split(","):
                if feat not in feat_list:
                    feat_list.append(feat)

    """get mob attacks"""
    mob_dict = V.mob_dict[mob_name]
    mob_attacks = get_mob_attacks(mob_dict)
    mob_abilities = get_mob_abilities(mob_dict)

    running = True
    pressed = -1
    button_dict = {
        (2, 0): ["Initiative", "background", "background", "rect-place-holder", "black"],
        (0, 0): ["Help", "background", "background", "rect-place-holder", "black"]
    }
    hovering_mouse = -1

    mini_window_w = S.SCREEN_WIDTH * 0.3
    mini_window_h = S.SCREEN_HEIGHT * 0.3

    dtwenty = 0
    rolled_sum = -1
    dice_color = "Dark green"
    critical_success = False
    critical_fail = False

    feature_scroll = 0
    spell_scroll = 0
    weapon_scroll = 0

    notice = [] # Place holder for notes to the user
    if "Feature:Wild Shape" in unknown_list:
        unknown_list.remove("Feature:Wild Shape")

    show_slots = False  # a flag used to show the player his spell slots
    ammo_count = F.get_ammo_count(weapon_list)
    slot_to_display = (0, 0)

    while running:
        if V.Condition == 'Exhaustion lv6':
            return
        text_surface = pg.Surface((mini_window_w, mini_window_h), pg.SRCALPHA)
        spell_screen = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 0.85), pg.SRCALPHA)
        weapon_screen = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 0.85), pg.SRCALPHA)
        feature_screen = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 0.85), pg.SRCALPHA)

        mini_window_w = S.SCREEN_WIDTH * 0.3
        mini_window_h = S.SCREEN_HEIGHT * 0.3

        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.05

        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        if not S.Seisure:
            F.display_text(screen, "Critical Success - Purple", 20, (S.SCREEN_WIDTH * 0.85, S.SCREEN_HEIGHT * 0.02), case="C", color="Purple")
            F.display_text(screen, "Critical Fail - Black", 20, (S.SCREEN_WIDTH * 0.85, S.SCREEN_HEIGHT * 0.06), case="C", color="Black")
        if rolled_sum != -1:
            F.display_text(screen, "Rolled: " + str(dtwenty) + "+" + str(rolled_sum - dtwenty) + "=" + str(rolled_sum), 20, (S.SCREEN_WIDTH * 0.85, S.SCREEN_HEIGHT * 0.1), case="C", color=dice_color)

        buttons = F.display_back_button(screen, "Back")

        # slot_rect = F.display_text(screen, "Spell Slots", 20, (S.SCREEN_WIDTH * 0.88, S.SCREEN_HEIGHT * 0.2))
        # pg.draw.rect(screen, "black", slot_rect, width=2)

        x_pos = [S.SCREEN_WIDTH * 0.05, S.SCREEN_WIDTH * 0.27, S.SCREEN_WIDTH * 0.52]
        y_pos = [S.SCREEN_HEIGHT * 0.9, S.SCREEN_HEIGHT * 0.12]

        slot_to_add_dict = F.display_spell_slots(screen, slot_to_display)

        button_dict = A.handle_Consentration(screen, button_dict)

        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)

        rect_dict, start_y = A.display_weapons(weapon_screen, weapon_list, ammo_count, weapon_scroll)
        rect_dict.update(display_mob_attacks(weapon_screen, mob_attacks, weapon_scroll, mob_name, rect_dict, start_y))
        rect_dict.update(display_mob_abilities(spell_screen, mob_abilities, spell_scroll, mob_name))
        rect_dict.update(A.display_features(feature_screen, unknown_list, feat_list, feature_scroll))


        notice = F.display_notice(screen, notice, (S.SCREEN_WIDTH * 0.02, S.SCREEN_HEIGHT * 0.95))

        C.display_condition_effects_actions(screen)

        A.draw_action_grid(screen)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                """quit"""
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
                for name, value in rect_dict.items():
                    for property, rect in value.items():
                        if isinstance(rect, pg.Rect) and rect.collidepoint(mouse_pos) and property in ["Hit", "Damage", "Cast", "Throw", "Versatile", "Spell_slot"]:
                            pressed = [property, name]
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if isinstance(pressed, str):
                        """Handles button pressing: back, initiative, end concentration, help buttons."""
                        if pressed == "Back":
                            return
                        elif pressed == "Initiative":
                            dtwenty = random.randint(1, 20)

                            screen.blit(weapon_screen, (0, 0))
                            screen.blit(spell_screen, (0, 0))
                            screen.blit(feature_screen, (0, 0))

                            F.Roll_3d_dice(screen, clock, "D20", str(dtwenty),(S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.4))
                            rolled_sum = dtwenty + V.score_modifiers["DEX"]
                            F.add_to_roll_history(dtwenty, rolled_sum, "Mob:Initiative")


                        elif pressed == "End Concentration":
                            """Deletting end concentration button"""
                            del button_dict[(1, 0)]
                            V.consentration = {}
                        elif pressed == "Help":
                            """Display Help"""
                            H.render_help(screen, clock)
                    elif isinstance(pressed, list):
                        cancel_rect = False
                        rect_list = list(rect_dict[pressed[1]].values())
                        for rect in rect_list:
                            if isinstance(rect, pg.Rect):
                                if rect.y + rect.h >= S.SCREEN_HEIGHT * 0.85:
                                    cancel_rect = True
                        if cancel_rect:
                            continue
                        if pressed[0] == "Hit":
                            """is this a spell?"""
                            enough_ammo = True
                            if V.item_dict.get(pressed[1]) != None and "ammo" in V.item_dict[pressed[1]]["Properties"].lower():
                                """if ammo is used and clicked on an item"""
                                if "Arrows" not in character["Items"]:
                                    enough_ammo = False
                                    notice = ["Not Enough Arrows", 100]
                                else:
                                    F.remove_item_from_char("Arrows", character)
                                    ammo_count["Arrows"] -= 1
                                    if ammo_count["Arrows"] == 0:
                                        del ammo_count["Arrows"]
                                        weapon_list.remove("Arrows")
                                    """Need to update the json as well"""
                            if enough_ammo:
                                advantage = False
                                disadvantage = False
                                if V.Condition in ["Exhaustion lv3", "Exhaustion lv4", "Exhaustion lv5", "Exhaustion lv6", "Restrained", "Prone", "Poisoned", "Blinded"]:
                                    disadvantage = True
                                if V.Condition in ["Invisible"]:
                                    advantage = True

                                dtwenty = random.randint(1, 20)

                                screen.blit(weapon_screen, (0, 0))
                                screen.blit(spell_screen, (0, 0))
                                screen.blit(feature_screen, (0, 0))

                                F.Roll_3d_dice(screen, clock, "D20", str(dtwenty),(S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.5))
                                F.add_to_roll_history(dtwenty, rolled_sum, "Mob:Hit:" + str(pressed[1]))
                                rolled_sum, dtwenty = sk.handle_disadvantage_rolls(screen, clock, "1D20", dtwenty, (disadvantage, advantage), int(rect_dict[pressed[1]]["Roll_mod"]))

                                dice_color, critical_fail, critical_success = A.handle_critical_fail_success_colors(dtwenty)

                        elif pressed[0] == "Damage":
                            dice = rect_dict[pressed[1]]["Damage_Die"]
                            if "d" in dice:
                                """clicked on a dice roll"""
                                count = int(dice.split("d")[0])

                                multiple_rolls = []
                                for i in range(0, count):
                                    multiple_rolls.append(random.randint(1, int(dice.split("d")[1])))
                                if count == 1:
                                    multiple_rolls = str(multiple_rolls[0])
                                    dtwenty = int(multiple_rolls)
                                else:
                                    dtwenty = sum(multiple_rolls)

                                screen.blit(weapon_screen, (0, 0))
                                screen.blit(spell_screen, (0, 0))
                                screen.blit(feature_screen, (0, 0))
                                F.Roll_3d_dice(screen, clock, dice[1:].upper(), multiple_rolls, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.5))
                                rolled_sum = int(dtwenty) + int(rect_dict[pressed[1]]["Damage_mod"])
                                F.add_to_roll_history(dtwenty, rolled_sum, "Mob:Damage:" + str(pressed[1]))


                        elif pressed[0] == "Throw":
                            if V.item_dict.get(pressed[1]) != None and "thrown" in V.item_dict[pressed[1]]["Properties"].lower():
                                """if thrown item remove it from player"""
                                F.remove_item_from_char(pressed[1], character)
                                if pressed[1] not in character["Items"]:
                                    weapon_list.remove(pressed[1])
                                dtwenty = random.randint(1, 20)
                                F.Roll_3d_dice(screen, clock, "D20", str(dtwenty),(S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.5))
                                dice_color, critical_fail, critical_success = A.handle_critical_fail_success_colors(dtwenty)
                                rolled_sum = dtwenty + int(rect_dict[pressed[1]]["Roll_mod"])
                                if "Giant's Havoc" in V.character_dict[V.char_name]["Code"] and rect_dict[pressed[1]]["Mod_Name"] == "STR":
                                    rolled_sum += int(V.character_dict[V.char_name]["Rage Damage"])
                                if V.character_dict[V.char_name].get("Fighting Style") != None and "Thrown Weapon Fighting" in V.character_dict[V.char_name]["Fighting Style"]:
                                    rolled_sum += 2
                                F.add_to_roll_history(dtwenty, rolled_sum, "Mob:Throw:" + str(pressed[1]))

                        elif pressed[0] == "Versatile":
                            dice = rect_dict[pressed[1]]["Versatile_dice"]
                            if "d" in dice:
                                """clicked on a dice roll"""
                                count = int(dice.split("d")[0])
                                multiple_rolls = []
                                for i in range(0, count):
                                    multiple_rolls.append(random.randint(1, int(dice.split("d")[1])))
                                if count == 1:
                                    multiple_rolls = str(multiple_rolls[0])
                                    dtwenty = int(multiple_rolls)
                                else:
                                    dtwenty = sum(multiple_rolls)
                                F.Roll_3d_dice(screen, clock, dice[1:].upper(), multiple_rolls, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.5))
                                rolled_sum = int(dtwenty) + int(rect_dict[pressed[1]]["Damage_mod"])
                                F.add_to_roll_history(dtwenty, rolled_sum, "Mob:Two-handed:" + str(pressed[1]))

                        elif pressed[0] == "Spell_slot":
                            if S.Class_features[pressed[1]]["Action_Type"] == "Changed_Spell_Slot":
                                if S.Class_features[pressed[1]]["Change"][0:2] == ["REMOVE", "1"]:
                                    """Checking was there a spellslot change or not used for Wild Companion"""
                                    was_it_removed = F.remove_spell_slot(S.Class_features[pressed[1]]["Change"][2])
                                elif S.Class_features[pressed[1]]["Change"][0] == "ROLL":
                                    was_it_removed = True
                                    dice_to_roll = S.Class_features[pressed[1]]["Change"][2]
                                    die = character[dice_to_roll]
                                    if rect_dict[pressed[1]].get("Dice") == None:
                                        rect_dict[pressed[1]]["Dice"] = die
                                elif "ADD_ROLL_REMOVE" in S.Class_features[pressed[1]]["Change"][0]:
                                    was_it_removed = F.remove_spell_slot(S.Class_features[pressed[1]]["Change"][2].split("__")[2])
                                    dice_to_roll = S.Class_features[pressed[1]]["Change"][2].split("__")[1]
                                    die = character[dice_to_roll]
                                    if rect_dict[pressed[1]].get("Dice") == None:
                                        rect_dict[pressed[1]]["Dice"] = die
                                else:
                                    was_it_removed = False
                                    F.print_debug("IDK WHAT TO DO BOSS: ", [pressed], "ERROR")
                            else:
                                """Every other feature"""
                                was_it_removed = F.remove_spell_slot(pressed[1])
                            if not was_it_removed:
                                notice = ["Not Enough Spell Slots", 100]
                            else:
                                """enough spell slots and slot was consumed"""
                                A.handle_special_flags(pressed)
                                if rect_dict[pressed[1]].get("Dice") != None:
                                    dice = rect_dict[pressed[1]]["Dice"]
                                    dtwenty = random.randint(1, int(dice.split("d")[1]))
                                    F.Roll_3d_dice(screen, clock, dice[1:].upper(), str(dtwenty),(S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.5))
                                    rolled_sum = dtwenty
                                    F.add_to_roll_history(dtwenty, rolled_sum, "Mob:Feature:" + str(pressed[1]))

                    pressed = -1
            elif event.type == pg.MOUSEMOTION:
                mouse_pos = pg.mouse.get_pos()
                didnt_find_it = True
                for name, value in rect_dict.items():
                    for property, rect in value.items():
                        if isinstance(rect, pg.Rect) and rect.collidepoint(mouse_pos):
                            hovering_mouse = [name, property, rect, rect_dict[name]["Type"], mob_name]
                            didnt_find_it = False
                            break
                slot_to_display = (0, 0)
                for slot in slot_to_add_dict:
                    for plus_or_minus, rect in slot_to_add_dict[slot].items():
                        if rect.collidepoint(mouse_pos):
                            slot_to_display = (slot, plus_or_minus)
                            break
                if didnt_find_it:
                    hovering_mouse = -1
                # if slot_rect.collidepoint(mouse_pos):
                #     """When colliding with this rect shows spells"""
                #     show_slots = True
                # else:
                #     show_slots = False
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 4 or event.type == pg.KEYDOWN and event.key == pg.K_UP:
                mouse_pos = pg.mouse.get_pos()
                if mouse_pos[0] in range(int(S.SCREEN_WIDTH * 0.31), int(S.SCREEN_WIDTH * 0.5)):
                    spell_scroll += 20
                elif mouse_pos[0] in range(int(S.SCREEN_WIDTH * 0.51), int(S.SCREEN_WIDTH * 0.76)):
                    feature_scroll += 20
                elif mouse_pos[0] in range(int(S.SCREEN_WIDTH * 0.01), int(S.SCREEN_WIDTH * 0.26)):
                    weapon_scroll += 20
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5 or event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                mouse_pos = pg.mouse.get_pos()
                if mouse_pos[0] in range(int(S.SCREEN_WIDTH * 0.31), int(S.SCREEN_WIDTH * 0.5)):
                    spell_scroll -= 20
                elif mouse_pos[0] in range(int(S.SCREEN_WIDTH * 0.51), int(S.SCREEN_WIDTH * 0.76)):
                    feature_scroll -= 20
                elif mouse_pos[0] in range(int(S.SCREEN_WIDTH * 0.01), int(S.SCREEN_WIDTH * 0.26)):
                    weapon_scroll -= 20

        text_surface = A.display_mini_screen(hovering_mouse, mini_window_w, mini_window_h, text_surface)

        screen.blit(weapon_screen, (0, 0))
        screen.blit(spell_screen, (0, 0))
        screen.blit(feature_screen, (0, 0))

        mouse_pos = pg.mouse.get_pos()

        if mouse_pos[1] <= S.SCREEN_HEIGHT * 0.85:
            screen.blit(text_surface, mouse_pos)

        critical_fail, critical_success = F.display_nat_20_or_1(screen, critical_fail, critical_success)
        # if slot_surface != 0:
        #     screen.blit(slot_surface, (0, 0))
        pg.display.flip()
        clock.tick(60)

def get_mob_attacks(mob_dict):
    mob_actions = mob_dict["Actions"].split(", ")
    return  mob_actions
def display_mob_attacks(screen, mob_actions, scroll, mob_name, rect_dict, start_y):
    for weapon_name, values in rect_dict.items():
        for key, rect in values.items():
            if isinstance(rect, pg.Rect) and rect.y > start_y:
                start_y = rect.y + rect.h + S.SCREEN_HEIGHT * 0.1
    F.display_text(screen, "Beast Attacks", 30, (S.SCREEN_WIDTH * 0.01, start_y))
    start_X = S.SCREEN_WIDTH * 0.02
    step_y = S.SCREEN_HEIGHT * 0.05
    tab = S.SCREEN_WIDTH * 0.01
    displayed_rects = {}
    for action in mob_actions:
        info_rect = F.display_text(screen, action, 15, (start_X, start_y + step_y))
        if action not in list(displayed_rects.keys()):
            displayed_rects[action] = {"Info": info_rect, "Type": "Beast_Weapon"}
        step_y += S.SCREEN_HEIGHT * 0.031


        if S.mob_abilities[action].get(mob_name) != None:
            damage_mod = 0
            roll_modifyer = 0
            dice = "-"
            type = "-"
            if S.mob_abilities[action][mob_name].get("DICE_MOD") != None:
                damage_mod = int(S.mob_abilities[action][mob_name].get("DICE_MOD"))
            if S.mob_abilities[action][mob_name].get("HIT") != None:
                roll_modifyer = int(S.mob_abilities[action][mob_name].get("HIT"))
            if S.mob_abilities[action][mob_name].get("DICE") != None:
                dice = S.mob_abilities[action][mob_name].get("DICE")
            if S.mob_abilities[action].get("Type") != None:
                type = S.mob_abilities[action].get("Type")


            roll_gap = " +"
            if roll_modifyer < 0:
                roll_gap = " "
            gap = " +"
            if damage_mod < 0:
                gap = " "
            if action == "Multiattack":
                del displayed_rects[action]
                for attack in S.mob_abilities[action][mob_name]["Attack_list"]:
                    displayed_rects["Multiattack:" + attack] = {"Info": info_rect, "Type": "Beast_Weapon"}
                    roll_modifyer = 0
                    if S.mob_abilities[attack][mob_name].get("HIT") != None:
                        roll_modifyer = int(S.mob_abilities[attack][mob_name].get("HIT"))
                    r = F.display_text(screen, "Hit: ", 15, (start_X + tab, start_y + step_y))
                    r2 = F.display_text(screen, "1d20" + roll_gap + str(roll_modifyer), 15, (r.x + r.w, r.y))
                    rect = r.union(r2)
                    pg.draw.rect(screen, "black", rect, width=1)
                    displayed_rects["Multiattack:" + attack]["Hit"] = rect
                    step_y += S.SCREEN_HEIGHT * 0.031

                    dice = S.mob_abilities[attack][mob_name]["DICE"]
                    damage_mod = int(S.mob_abilities[attack][mob_name].get("DICE_MOD"))
                    r = F.display_text(screen, "Damage: ", 15, (start_X + tab, start_y + step_y))
                    r2 = F.display_text(screen, dice + gap + str(damage_mod), 15, (r.x + r.w, r.y))
                    rect = r.union(r2)
                    pg.draw.rect(screen, "black", rect, width=1)
                    displayed_rects["Multiattack:" + attack]["Damage"] = rect
                    step_y += S.SCREEN_HEIGHT * 0.031

                    type = S.mob_abilities[attack].get("Type")
                    r = F.display_text(screen, "Type: ", 15, (start_X + tab, start_y + step_y))
                    F.display_text(screen, type, 15, (r.x + r.w, r.y))
                    step_y += S.SCREEN_HEIGHT * 0.031

                    displayed_rects["Multiattack:" + attack]["Roll_mod"] = roll_modifyer
                    displayed_rects["Multiattack:" + attack]["Damage_mod"] = damage_mod
                    displayed_rects["Multiattack:" + attack]["Damage_Die"] = dice
                continue


            r = F.display_text(screen, "Hit: ", 15, (start_X + tab, start_y + step_y))
            r2 = F.display_text(screen, "1d20" + roll_gap + str(roll_modifyer), 15, (r.x + r.w, r.y))
            rect = r.union(r2)
            pg.draw.rect(screen, "black", rect, width=1)
            displayed_rects[action]["Hit"] = rect
            step_y += S.SCREEN_HEIGHT * 0.031

            r = F.display_text(screen, "Damage: ", 15, (start_X + tab, start_y + step_y))
            r2 = F.display_text(screen,  dice + gap + str(damage_mod), 15, (r.x + r.w, r.y))
            rect = r.union(r2)
            pg.draw.rect(screen, "black", rect, width=1)
            displayed_rects[action]["Damage"] = rect
            step_y += S.SCREEN_HEIGHT * 0.031

            r = F.display_text(screen, "Type: ", 15, (start_X + tab, start_y + step_y))
            F.display_text(screen, type, 15, (r.x + r.w, r.y))
            step_y += S.SCREEN_HEIGHT * 0.031

            displayed_rects[action]["Roll_mod"] = roll_modifyer
            displayed_rects[action]["Damage_mod"] = damage_mod
            displayed_rects[action]["Damage_Die"] = dice

    return displayed_rects

def display_mob_abilities(screen, mob_abilities, scroll, mob_name):
    F.display_text(screen, "Beast Abilities", 30, (S.SCREEN_WIDTH * 0.3, S.SCREEN_HEIGHT * 0.01 + scroll))
    start_y = S.SCREEN_HEIGHT * 0.06 + scroll
    start_X = S.SCREEN_WIDTH * 0.31
    step_y = 0
    tab = S.SCREEN_WIDTH * 0.01
    displayed_rects = {}
    for ability in mob_abilities:
        if ability == "":
            continue
        info_rect = F.display_text(screen, ability, 15, (start_X, start_y + step_y))
        if ability not in list(displayed_rects.keys()):
            displayed_rects[ability] = {"Info": info_rect, "Type": "Ability"}
        step_y += S.SCREEN_HEIGHT * 0.031

        if S.mob_abilities[ability].get(mob_name) != None:
            damage_mod = 0
            roll_modifyer = 0
            dice = "-"
            type = "-"
            if S.mob_abilities[ability][mob_name].get("DICE_MOD") != None:
                damage_mod = int(S.mob_abilities[ability][mob_name].get("DICE_MOD"))
            if S.mob_abilities[ability][mob_name].get("HIT") != None:
                roll_modifyer = int(S.mob_abilities[ability][mob_name].get("HIT"))
            if S.mob_abilities[ability][mob_name].get("DICE") != None:
                dice = S.mob_abilities[ability][mob_name].get("DICE")
            if S.mob_abilities[ability].get("Type") != None:
                type = S.mob_abilities[ability].get("Type")

            roll_gap = " +"
            if roll_modifyer < 0:
                roll_gap = " "
            gap = " +"
            if damage_mod < 0:
                gap = " "

            if dice != "-":
                if S.mob_abilities[ability][mob_name].get("HIT") != None:
                    r = F.display_text(screen, "Hit: ", 15, (start_X + tab, start_y + step_y))
                    r2 = F.display_text(screen, "1d20" + roll_gap + str(roll_modifyer), 15, (r.x + r.w, r.y))
                    rect = r.union(r2)
                    pg.draw.rect(screen, "black", rect, width=1)
                    displayed_rects[ability]["Hit"] = rect
                    step_y += S.SCREEN_HEIGHT * 0.031

                r = F.display_text(screen, "Damage: ", 15, (start_X + tab, start_y + step_y))
                r2 = F.display_text(screen, dice + gap + str(damage_mod), 15, (r.x + r.w, r.y))
                rect = r.union(r2)
                pg.draw.rect(screen, "black", rect, width=1)
                displayed_rects[ability]["Damage"] = rect
                step_y += S.SCREEN_HEIGHT * 0.031

            if type != "-":
                r = F.display_text(screen, "Type: ", 15, (start_X + tab, start_y + step_y))
                F.display_text(screen, type, 15, (r.x + r.w, r.y))
                step_y += S.SCREEN_HEIGHT * 0.031

            displayed_rects[ability]["Roll_mod"] = roll_modifyer
            displayed_rects[ability]["Damage_mod"] = damage_mod
            displayed_rects[ability]["Damage_Die"] = dice

    return displayed_rects

def get_mob_abilities(mob_dict):
    mob_abilities = mob_dict["Abilities"].split(", ")
    return mob_abilities

def rage_check(button_dict):
    if V.Special_Flags.get("Rage") != None:
        S.Background_image = "Conditions/Rage"
        S.Standart_color = "white"
        V.consentration = {}
        if button_dict.get((1, 0)) != None and button_dict[(1, 0)][0] == "End Concentration":
            del button_dict[(1, 0)]
        if button_dict.get((1, 0)) == None:
            button_dict[(1, 0)] = ["End Rage", "background", "background", "rect", "white"]
    return button_dict

def handle_diferent_special_flags(function_name, screen, clock, character):
    data = S.Class_features[function_name]["Special_Flag"]
    data_type = data[0]
    if "CHOOSE" in data_type:
        universal_combobox_screen(screen, clock, character, data, function_name)

    elif "CHOOSE_OR" in data_type:
        universal_combobox_screen(screen, clock, character, data, function_name)

def universal_combobox_screen(screen, clock, character, first_combobox_data, function_name):

    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)
    functions_implemented = ["Favoured Enemy", "Natural Explorer", "Ranger's Companion"]
    running = True
    combobox_choises = {}
    big_rect = {}
    if char_config_data.get("Choises") != None and char_config_data["Choises"].get(function_name) != None:
        return

    if function_name not in functions_implemented:
        F.print_debug("DONT KNOW THE FUNCTION, pLS HELP SPECIAL_NEEDS.py universal_combobox_screen", function_name, debug="ERROR")
        running = False

    if "--" in first_combobox_data[2]:
        """--Mob:Beast"""
        new_list = []
        if first_combobox_data[2].split(":")[0] == "--Mob":
            type = first_combobox_data[2].split(":")[1]
            if V.mob_dict == {}:
                mob_data = F.read_db_table("monsters")
                V.mob_dict = F.add_to_dict_db_results(mob_data, V.mob_dict, "mobs")
                F.get_mob_actions()
            for mob in V.mob_dict:
                if type == V.mob_dict[mob]["Type"]:
                    if function_name == "Ranger's Companion" and float(V.mob_dict[mob]["Challange"]) <= 0.25:
                        """Added check that CR must be lower or equal to 0.25"""
                        new_list.append(mob)
            first_combobox_data[2:] = new_list

    if "CHOOSE_OR" == first_combobox_data[0]:
        amounts = [int(first_combobox_data[1]), int(S.Class_features[function_name]["Chose_Or"][1])]
        choises_list = [first_combobox_data[2:], S.Class_features[function_name]["Chose_Or"][2:]]
        functions = [function_name, function_name + "|Humanoid"]
    elif "CHOOSE" == first_combobox_data[0]:
        amounts = [int(first_combobox_data[1])]
        choises_list = [first_combobox_data[2:]]
        functions = [function_name]
    else:
        amounts = [0]
        functions = []
        choises_list = []
    pressed = -1
    limited_choises = []


    to_display = "Description"
    y_scroll = 0
    while running:
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Save")
        pos = F.display_text(screen, function_name, 28, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1), case="C")

        d = F.display_text(screen, to_display + ": ", 14, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1 + pos.h * 2 + y_scroll))
        for w in S.Class_features[function_name][to_display].split(" "):
            w = w.replace("\n\n", "")
            d = F.display_text(screen, w + " ", 14, (d.x + d.w, d.y))
            if d.x + d.w > S.SCREEN_WIDTH * 0.9:
                d.x = S.SCREEN_WIDTH * 0.5
                d.w = 0
                d.y += d.h * 1.1

        for ii, key in enumerate(functions):
            if big_rect.get(key) == None:
                big_rect[key] = []
            if "CHOOSE_OR" in first_combobox_data[0]:
                if key not in limited_choises:
                    limited_choises.append(key)
            amount = amounts[ii]
            choises = choises_list[ii]
            while len(big_rect[key]) < amount:
                big_rect[key].append(pg.Rect(0, 0, 0, 0))

            pos = F.display_text(screen, key, 14, (S.SCREEN_WIDTH * 0.1, pos.y + pos.h * 1.3))

            for i in range(amount):
                if combobox_choises.get(key + str(i)) == None:
                    combobox_choises[key + str(i)] = {"Text": "Choose",
                                                      "Rect": 0,
                                                      "Expand": False,
                                                      "Hover": "",
                                                      "Choises": []}

                pg.draw.rect(screen, (240, 240, 240, 255), big_rect[key][i])
                pos = F.display_text(screen, f"{combobox_choises[key + str(i)]["Text"]}", 14, (S.SCREEN_WIDTH * 0.1, pos.y + pos.h * 1.2))
                pg.draw.rect(screen, (100, 100, 100, 255) if pressed == key + str(i) else (240, 240, 240, 255), (pos))
                F.display_text(screen, f"{combobox_choises[key + str(i)]["Text"]}", 14, (pos.x, pos.y))  # Redraw text
                pg.draw.line(screen, S.Standart_color, (pos.x, pos.y + pos.h), (pos.x + big_rect[key][i].w, pos.y + pos.h), width=2)
                if not combobox_choises[key + str(i)]["Expand"]:
                    big_rect[key][i] = pos
                    combobox_choises[key + str(i)]["Rect"] = pg.draw.rect(screen, S.Standart_color, (pos.x - 2, pos.y - 2, pos.w + 4, pos.h + 4), width=2)
                else:
                    for choise in choises:
                        pos = F.display_text(screen, f"{choise}", 14, (S.SCREEN_WIDTH * 0.1, pos.y + pos.h))
                        pg.draw.rect(screen, (100, 100, 100, 255) if combobox_choises[key + str(i)]["Hover"] == choise + ":" + key + str(i) else (240, 240, 240, 255),(pos.x, pos.y + 1, big_rect[key][i].w, pos.h - 1))
                        F.display_text(screen, f"{choise}", 14, (pos.x, pos.y))
                        highlight = 2 if pressed == choise + ":" + key + str(i) else 1
                        combobox_choises[key + str(i)]["Choises"].append((pg.Rect(pos.x, pos.y, big_rect[key][i].w, pos.h), choise))
                        pg.draw.line(screen, S.Standart_color, (pos.x, pos.y + pos.h), (pos.x + big_rect[key][i].w, pos.y + pos.h), width=highlight)
                        if big_rect[key][i].w < pos.w:
                            big_rect[key][i].w = pos.w
                    big_rect[key][i] = pg.Rect(big_rect[key][i].x, big_rect[key][i].y, big_rect[key][i].w, (pos.y + pos.h + 4) - big_rect[key][i].y)
                    pg.draw.rect(screen, S.Standart_color, (big_rect[key][i].x - 2, big_rect[key][i].y - 2, big_rect[key][i].w + 4, (pos.y + pos.h + 4) - big_rect[key][i].y), width=2)

        if function_name == "Ranger's Companion" and combobox_choises[function_name + "0"]["Text"] != "Choose":
            p = [
                S.SCREEN_WIDTH * 0.38,
                S.SCREEN_HEIGHT * 0.2,
                S.SCREEN_WIDTH * 0.1,
                S.SCREEN_HEIGHT * 0.15,
                S.SCREEN_HEIGHT * 0.21,
                S.SCREEN_WIDTH * 0.02,
                S.SCREEN_HEIGHT * 0.04
            ]
            display_mob(V.mob_dict[combobox_choises[function_name + "0"]["Text"]], screen, combobox_choises[function_name + "0"]["Text"], pos=p, disp_hp=False)


        for event in pg.event.get():
            mouse_pos = pg.mouse.get_pos()
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
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                        # for key, value in button_dict.items():
                        #     if value[3] == buttons[i]:
                        #         pressed = value[0]
                if combobox_choises != {}:
                    found = False
                    for key, value in combobox_choises.items():
                        if value["Rect"].collidepoint(mouse_pos):
                            pressed = key
                        if value["Expand"]:
                            """Expanded, check the rects for collision and secure the choise"""
                            for (ch_rect, ch) in value["Choises"]:
                                if ch_rect.collidepoint(mouse_pos):
                                    pressed = "Chose_Made:" + key + ":" + ch
                                    found = True
                                    break
                        if found:
                            break
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == "Back":
                        if char_config_data.get("Choises") == None:
                            char_config_data["Choises"] = {}
                        for key in combobox_choises:
                            if combobox_choises[key]["Text"] != "Choose":
                                if char_config_data["Choises"].get(key[:-1].replace("|Humanoid", "")) == None:
                                    char_config_data["Choises"][key[:-1].replace("|Humanoid", "")] = combobox_choises[key]["Text"]
                                else:
                                    if not isinstance(char_config_data["Choises"][key[:-1].replace("|Humanoid", "")], list):
                                        char_config_data["Choises"][key[:-1].replace("|Humanoid", "")] = [char_config_data["Choises"][key[:-1].replace("|Humanoid", "")]]
                                    char_config_data["Choises"][key[:-1].replace("|Humanoid", "")].append(combobox_choises[key]["Text"])

                        with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'w') as file:
                            json.dump(char_config_data, file, indent=4)
                        return
                    elif combobox_choises.get(pressed) != None and combobox_choises[pressed]["Rect"].collidepoint(mouse_pos):
                        """Clicked on combobox, expand it."""
                        if combobox_choises[pressed]["Expand"]:
                            combobox_choises[pressed]["Expand"] = False
                        else:
                            combobox_choises[pressed]["Expand"] = True
                            combobox_choises[pressed]["Text"] = "Choose"
                            if pressed[:-1] in limited_choises:
                                """Pressed a limited choise combobox, cancel the other ones"""
                                for k in limited_choises:
                                    if k != pressed[:-1]:
                                        for i in range(999):
                                            if combobox_choises.get(k + str(i)) != None:
                                                combobox_choises[k + str(i)]["Expand"] = False
                                                combobox_choises[k + str(i)]["Text"] = "Choose"
                                            else:
                                                break
                    elif "Chose_Made:" in pressed:
                        key = pressed.split(":")[1]
                        choise = pressed.split(":")[2]
                        combobox_choises[key]["Text"] = choise
                        combobox_choises[key]["Expand"] = False
                else:
                    for choise in combobox_choises:
                        if combobox_choises[choise]["Expand"]:
                            combobox_choises[choise]["Expand"] = False
                pressed = -1
            elif event.type == pg.MOUSEMOTION:
                found = False
                for choise in combobox_choises:
                    if combobox_choises[choise]["Expand"]:
                        for (ch_rect, ch) in combobox_choises[choise]["Choises"]:
                            if ch_rect.collidepoint(mouse_pos):
                                combobox_choises[choise]["Hover"] = ch + ":" + choise
                                found = True
                                break
                            if found:
                                break
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 2:
                if to_display == "Description":
                    to_display = "Description_for_dummies"
                else:
                    to_display = "Description"
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5:
                y_scroll -= 20
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 4:
                y_scroll += 20
                if y_scroll > 0:
                    y_scroll = 0
        pg.display.flip()
        clock.tick(60)

def draw_combobox(screen, pos, text, state, data=[], text_size=10):
    if state == "Closed":
        rect = pg.Rect(pos[0], pos[1], pos[2], pos[3])
        pg.draw.rect(screen, "white", rect)
        pg.draw.rect(screen, "black", rect, width=1)
        F.display_text(screen, text, text_size, (rect.x, rect.y))
        points = [
            (rect.x + rect.w * 0.85, rect.y + rect.h * 0.2),
            (rect.x + rect.w * 0.95, rect.y + rect.h * 0.2),
            (rect.x + rect.w * 0.9, rect.y + rect.h * 0.8),
        ]
        pg.draw.polygon(screen, "dark gray", points)


    else:
        r = []
        rect = pg.Rect(pos[0], pos[1], pos[2], pos[3])
        r.append(rect)
        pg.draw.rect(screen, "white", rect)
        pg.draw.rect(screen, "black", rect, width=1)
        F.display_text(screen, text, text_size, (rect.x, rect.y))
        points = [
            (rect.x + rect.w * 0.85, rect.y + rect.h * 0.8),
            (rect.x + rect.w * 0.95, rect.y + rect.h * 0.8),
            (rect.x + rect.w * 0.9, rect.y + rect.h * 0.2),
        ]
        pg.draw.polygon(screen, "dark gray", points)

        x = pos[0]
        y = pos[1]
        for i in range(2, len(data)):
            pg.draw.rect(screen, "white", (x, y, pos[2], pos[3]))
            pg.draw.rect(screen, "black", (x, y, pos[2], pos[3]), width=1)
            F.display_text(screen, data[i], text_size, (x, y))
            y += pos[3]


    return rect

def handle_unarmored_defense(char):
    V.BASE_AC = 10 + V.score_modifiers["DEX"]
    char["AC"] = V.BASE_AC
    if "Unarmored Defense" in char["Code"]:
        armor_list = F.get_equiped_armor()
        if armor_list == []:
            temp_ac = 10 + V.score_modifiers["CON"] + V.score_modifiers["DEX"]
            if int(char["AC"]) < int(temp_ac):
                char["AC"] = temp_ac
                V.BASE_AC = temp_ac
        else:
            V.BASE_AC = 10 + V.score_modifiers["DEX"]
            char["AC"] = V.BASE_AC
    if char.get("Fighting Style") != None and "Defense" in char["Fighting Style"]:
        V.BASE_AC += 1
        char["AC"] = V.BASE_AC


def handle_fast_movement(char):
    if "Fast Movement" in char["Code"]:
        flag = 0
        armor_list = F.get_equiped_armor()
        for armor in armor_list:
            if "Heavy" in V.item_dict[armor]["Properties"]:
                flag = 1
        if flag == 0:
            V.SPEED_OFFSET += 10
        char["Speed"] = str(int(V.BASE_SPEED) + int(V.SPEED_OFFSET))

def handle_blood_hunter_spell_slots(pressed, rect_dict, screen, clock):
    handle_rites(pressed, rect_dict, screen, clock)


def handle_rites(pressed, rect_dict, screen, clock):
    dice = rect_dict[pressed[1]]["Dice"]
    if V.EQUIPED_CHAR_ITEMS != {} and pressed[1] in ["Crimson Rite"]:
        if V.EQUIPED_CHAR_ITEMS.get("Weapons") != "" or V.EQUIPED_CHAR_ITEMS.get("Weapons") != None or V.EQUIPED_CHAR_ITEMS.get("Magic Weapon") != "" or V.EQUIPED_CHAR_ITEMS.get("Magic Weapon") != None:
            """If a weapon is equiped"""
            existing_rites = {"Rite of the Dawn": "Radiant",
                              "Rite of the Flame": "Fire",
                              "Rite of the Frozen": "Cold",
                              "Rite of the Storm": "Lightning",
                              "Rite of the Dead": "Necrotic",
                              "Rite of the Oracle": "Psychic",
                              "Rite of the Roar": "Thunder"
                            }
            for rite in existing_rites:
                if rite in V.character_dict[V.char_name]["Code"]:
                    if rite not in V.Rites:
                        V.Rites[rite] = ""

            choose_rites(screen, clock)


def choose_rites(screen, clock):
    character = V.character_dict[V.char_name]
    running = True
    text_size = 10
    pressed = -1
    colors = []
    for a in range(0, 10):
        colors.append((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    equiped_weapons = V.EQUIPED_CHAR_ITEMS.get("Weapons")
    equiped_magic_weapons = V.EQUIPED_CHAR_ITEMS.get("Magic Weapon")
    equiped_weapons = equiped_magic_weapons.split(",") + equiped_weapons.split(",")

    equiped_weapons_final = []
    for weapon in equiped_weapons:
        if weapon in ["", '', None, " "]:
            continue
        amount = character["Items"].count(weapon)
        if amount > 1:
            amount = 1
            """Blocks multiple items of the same name having diferent rites."""
        equiped_weapons_final += [weapon] * amount

    button_dict = {}
    x, y = 0, 0
    for i in range(0, len(equiped_weapons_final)):
        if equiped_weapons_final[i] in equiped_magic_weapons:
            path = "Magic Weapon/"
        else:
            path = "Weapons/"
        path += equiped_weapons_final[i]
        button_dict[(x, y)] = [equiped_weapons_final[i], path, "Items", "rect-place-holder", "black"]
        x += 1
        if x >= 3:
            x = 0
            y += 1

    x, y = 0, 0
    for key in V.Rites:
        button_dict[(x+4, y)] = [key, key, "Rites", "rect-place-holder", "black"]
        x += 1
        if x >= 3:
            x = 0
            y += 1


    selected_rite = 0
    selected_item = 0
    while running:
        button_width = S.SCREEN_WIDTH * 0.1
        button_height = S.SCREEN_HEIGHT * 0.1
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Back")
        x_pos = []
        y_pos = []
        for i in range(0, 8):
            x_pos.append(button_width * 1.1 * i + S.SCREEN_WIDTH * 0.1)
            y_pos.append(button_height * 1.1 * i + S.SCREEN_HEIGHT * 0.1)

        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict, text_size)

        if selected_rite != 0 and selected_item != 0:
            buttons = buttons + F.display_back_button(screen, "Apply", x_pos=[S.SCREEN_WIDTH * 0.52])

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
                        if buttons[i].x <= S.SCREEN_WIDTH * 0.52:
                            pressed = "Apply"
                        for key, value in button_dict.items():
                            if value[3] == buttons[i]:
                                pressed = value
                        pg.draw.rect(screen, "black", buttons[i], width=3)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == "Back":
                        print("Back")
                        return
                    elif pressed == "Apply":
                        if selected_item[0] not in list(V.Rites.values()):
                            V.Rites[selected_rite[0]] = selected_item[0]
                        return
                    else:
                        if pressed[0] in equiped_weapons_final or "Rite" in pressed[0]:
                            if "Rite" in pressed[0]:
                                if selected_rite == pressed:
                                    selected_rite = 0
                                else:
                                    selected_rite = pressed
                            else:
                                if selected_item == pressed:
                                    selected_item = 0
                                else:
                                    selected_item = pressed
                    pressed = -1

        if selected_item != 0:
            pg.draw.rect(screen, "red", selected_item[3], width=5)
        if selected_rite != 0:
            pg.draw.rect(screen, "Green", selected_rite[3], width=5)

        rite_count = 0
        for rite, item_name in V.Rites.items():
            if item_name == "":
                continue
            for key, value in button_dict.items():
                if value[0] == item_name:
                    pg.draw.rect(screen, colors[rite_count], value[3], width=5)
                if value[0] == rite:
                    pg.draw.rect(screen, colors[rite_count], value[3], width=5)
            rite_count += 1


        pg.display.flip()
        clock.tick(60)


def Arcane_Recovery(screen, clock, slots_to_recover):
    running = True
    text_size = 30
    pressed = -1
    button_dict = {}
    recovery = []
    x, y = 0, 0
    for i in range(0, len(slots_to_recover)):
        button_dict[(x, y)] = [slots_to_recover[i], slots_to_recover[i], "background", "rect-place-holder", "black"]
        x += 1
        if x > 5:
            x = 0
            y += 1
    while running:
        button_width = S.SCREEN_WIDTH * 0.1
        button_height = S.SCREEN_HEIGHT * 0.1
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Back")

        F.display_text(screen, "Select spell slots to recover", 20, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.1), case="C")

        x_pos = []
        y_pos = []
        start_x = S.SCREEN_WIDTH * 0.08
        start_y = S.SCREEN_HEIGHT * 0.2
        step_x = 0
        step_y = 0
        for a in range(0, 7):  # Loop through y (rows)
            x_pos.append(start_x + step_x)
            y_pos.append(start_y + step_y)
            step_x += S.SCREEN_WIDTH * 0.15
            step_y += S.SCREEN_HEIGHT * 0.15

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
                        for key, value in button_dict.items():
                            if value[3] == buttons[i]:
                                pressed = value[0]
                        pg.draw.rect(screen, "black", buttons[i], width=3)
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == "Back":
                        for slot in recovery:
                            if V.spell_slots.get(slot) == None:
                                V.spell_slots[slot] = 0
                            V.spell_slots[slot] += 1
                        return
                    else:
                        if int(pressed[0]) <= int(V.character_dict[V.char_name]["Arcane Recovery"]) and recovery == []:
                            """recovery empty and clicking alowed"""
                            recovery.append(pressed)
                            for key in list(button_dict.keys()):
                                if button_dict[key][0] == pressed:
                                    del button_dict[key]
                                    break  # Remove only one matching entry
                        elif int(pressed[0]) > int(V.character_dict[V.char_name]["Arcane Recovery"]):
                            pass
                        else:
                            """recovery isn't empty"""
                            if recovery.count("1st") + recovery.count("2nd") * 2 + recovery.count("3rd") * 3 + recovery.count("4th") * 4 + recovery.count("5th") * 5 + recovery.count("6th") * 6 + recovery.count("7th") * 7 + recovery.count("8th") * 8 + recovery.count("9th") * 9 + int(pressed[0]) <= int(V.character_dict[V.char_name]["Arcane Recovery"]):
                                recovery.append(pressed)
                                for key in list(button_dict.keys()):
                                    if button_dict[key][0] == pressed:
                                        del button_dict[key]
                                        break  # Remove only one matching entry

                    pressed = -1

        pg.display.flip()
        clock.tick(60)

def handle_font_of_magic(pressed, screen, clock):
    running = True
    text_size = 30
    pressed = -1
    if V.spell_slots.get("Font of Magic") == None or V.spell_slots["Font of Magic"] == 0:
        return False
    sorcery_points = V.spell_slots["Font of Magic"]
    button_dict = {
        (0, 0): ["1st", "background", "background", "rect-place-holder", "black"],
        (1, 0): ["2nd", "background", "background", "rect-place-holder", "black"],
        (2, 0): ["3rd", "background", "background", "rect-place-holder", "black"],
    }

    while running:
        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.05
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Back")
        x_pos = [S.SCREEN_WIDTH * 0.27, S.SCREEN_WIDTH * 0.52, S.SCREEN_WIDTH * 0.77]
        y_pos = [S.SCREEN_HEIGHT * 0.8, S.SCREEN_HEIGHT * 0.12]
        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)
        F.display_text(screen, "Sorcery points available: " + str(sorcery_points), 15, (S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.1), case="C")


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
                        V.spell_slots["Font of Magic"] = sorcery_points
                        return True
                    elif pressed in ["1st", "2nd", "3rd"] and sorcery_points >= int(pressed[0]):
                        if V.spell_slots.get(pressed) == None:
                            V.spell_slots[pressed] = 0
                        V.spell_slots[pressed] += 1
                        sorcery_points -= int(pressed[0])

                    pressed = -1

        pg.display.flip()
        clock.tick(60)