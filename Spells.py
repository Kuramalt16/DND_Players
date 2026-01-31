import pygame as pg, json, Special_Needs as special
import Variables as V, Functions as F, Settings as S, Actions as A


def check_if_spells_are_correct(character):
    class_list = F.get_all_char_classes(character)
    """class class subclass subclass"""

    for char_class in class_list:
        if V.Available_spells_data.get(char_class) != None:
            index = class_list.index(char_class)
            index = index % 2
            level = int(character["Level"].split(",")[index])
            available_spells = V.Available_spells_data[char_class][level]
            Cantrips = available_spells[0]
            Spells = available_spells[1]
            Total_Spell_Slots = available_spells[2]
            Spell_Slot_levels = available_spells[3]
            if character.get("Cantrip") != None:
                player_cantrips = len(character["Cantrip"].split(","))
            player_spells = len(character["Spell"].split(","))
            player_total_Spell_Slots = 0
            player_spell_slot_level = character["Spell Slots"]
            for spell_slot in character["Spell Slots"].split(","):
                player_total_Spell_Slots += int(spell_slot.split(":")[1])
            if character.get("Cantrip") != None:
                if player_cantrips != Cantrips:
                    F.print_debug("Not enough cantrips", player_cantrips, debug="WARNING")
            elif player_spells != Spells:
                F.print_debug("Not enough Spells", debug="WARNING")
            elif player_spell_slot_level != Spell_Slot_levels:
                F.print_debug("Spell slot level incorrect", debug="WARNING")
            elif player_total_Spell_Slots != Total_Spell_Slots:
                F.print_debug("not enough spell slots", debug="WARNING")


def initialize_spells(screen, clock):
    extra_action_values = []
    character = V.character_dict[V.char_name]
    unknown_list = []
    cantrip_list = []
    spell_list = []
    for extra_action in character["Code"].split(","):
        if extra_action.count(':') > 1:
            """Removes the first part of the title for example SubClass:Druid Circle:Land:Bonus Cantrip becomes Land:Bonus Cantrip"""
            extra_action_values = extra_action.split(":")
            extra_action = ":".join(extra_action_values[-2:])
        if extra_action not in unknown_list:
            unknown_list.append(extra_action)
            function_name = extra_action.split(":")[1]
            if "Eldritch Invocations" in extra_action:
                """If feature exists in class features and its a eldritch invocation"""
                data = S.eldritch_incantations[function_name]
                S.Class_features[function_name] = data
            elif S.Class_features.get(function_name) != None:
                if "Bonus" in S.Class_features[function_name]["Action_Type"]:
                    """If feature exists in class features and its a bonus action"""
                    V.Bonus_actions[function_name] = "Feature"
                elif "Reaction" in S.Class_features[function_name]["Action_Type"]:
                    """If feature exists in class features and its a reaction"""
                    V.Reactions[function_name] = "Feature"
                elif "Free Spell" in S.Class_features[function_name]["Action_Type"]:
                    spells = S.Class_features[function_name]["Spell"]
                    spell_list += A.get_cantrips_from_subclass_entry(spells, screen, clock, extra_action, mode="Spell")
                elif "Class_Spell_Slot_and_spell" == S.Class_features[function_name]["Action_Type"]:
                    if "Spell_slot:" + function_name not in unknown_list:
                        """Need to come here only once"""
                        unknown_list.pop()
                        unknown_list += A.handle_slot_commands_from_subclass_json(S.Class_features[function_name]["Spell_slot"], function_name)

                        spells = S.Class_features[function_name]["Spell"]
                        spell_list += A.get_cantrips_from_subclass_entry(spells, screen, clock, extra_action, mode="Spell")

                        """This change makes the code come here only initialy"""
                        S.Class_features[function_name]["Action_Type"] = "Spell_Slot"
                elif "Changed_Spell_Slot" in S.Class_features[function_name]["Action_Type"]:
                    unknown_list.pop()
                    unknown_list.append("Spell_slot:" + function_name)
                elif "Class_Spell_Slot" in S.Class_features[function_name]["Action_Type"]:
                    if "Spell_slot:" + function_name not in unknown_list:
                        unknown_list.pop()
                        unknown_list += A.handle_slot_commands_from_subclass_json(S.Class_features[function_name]["Spell_slot"], function_name)
                        """This change makes the code come here only initialy"""
                        S.Class_features[function_name]["Action_Type"] = "Spell_Slot"
                elif S.Class_features[function_name].get("Special_Flag") != None:
                    """handle special flag for fuctions that aren't user based like cast, weapon, hit or spell slot"""
                    special.handle_diferent_special_flags(function_name, screen, clock, character)
                elif character.get(function_name) != None and character[function_name].isdigit() and int(character[function_name]) > 1:
                    unknown_list.append(extra_action)
            elif S.Class_features.get(function_name) == None:
                """Class features needs to have data on the list in unknown_list so because it was already appended, we remove the last member and we add it again"""
                unknown_list.pop()
                """Only deals with subclass features spells cantrips traits and shit"""
                if extra_action_values != [] and extra_action_values[0] == "SubClass":
                    data = S.subclass_data.copy()
                    for k in extra_action_values[1:]:
                        """filters data"""
                        data = data.get(k, None)
                        if data is None:
                            break
                    """Since this data doesn't exist in the Class Features, adding it, this is needed for the data in display actions->display features, if addding to unknown list, data must be in class features"""
                    S.Class_features[extra_action.split(":")[1]] = data
                    """sorts what type of subclass feature this is"""
                    if "Changed_Spell_Slot" in data["Action_Type"]:
                        unknown_list.append("Spell_slot:" + function_name)
                        continue
                    if "Spell_Slot" in data["Action_Type"]:
                        slots = data["Spell_slot"]
                        unknown_list += A.handle_slot_commands_from_subclass_json(slots, extra_action.split(":")[1])
                        continue
                    if "Free Cantrip" == data["Action_Type"]:
                        """Enters here with Conan Druid cantrip Shillelagh"""
                        cantrips = data["Cantrip"]
                        cantrip_list += A.get_cantrips_from_subclass_entry(cantrips, screen, clock, extra_action)
                    if "Spell" == data["Action_Type"]:
                        spells = data["Spell"]
                        for spell in spells.split(","):
                            spell_list.append(spell)
                    if "Feature:" + extra_action.split(":")[1] not in unknown_list:
                        unknown_list.append("Feature:" + extra_action.split(":")[1])
                    if "Free Spell" == data["Action_Type"]:
                        spells = data["Spell"]
                        spell_list += A.get_cantrips_from_subclass_entry(spells, screen, clock, extra_action, extra_action_values, mode="Spell")
                    if "Subclass path" == data["Action_Type"]:
                        if data["Subclass"][0] == "CHOOSE":
                            choise_made = F.check_if_choise_was_already_made(extra_action)
                            if not choise_made:
                                res = A.make_a_choise(data["Subclass"], screen, clock, extra_action_values)
                                F.save_choise_json(extra_action, res)

def count_max_cantrip_count(spell_data):
    cantrip_count = 0
    cantrip_count += spell_data[0] # cantrips based on class
    char = V.character_dict[V.char_name]
    if char.get("Sub-Race") != None and char["Sub-Race"] in ["High Elf"]:
        cantrip_count += 1
    if "Druid" in char["Class"].split(", ") and char.get("SubClass") != None and char["SubClass"] in ["Land"]:
        cantrip_count += 1
    return cantrip_count

def count_max_spell_count(spell_data, current_level):
    spell_count = 0
    char = V.character_dict[V.char_name]

    if isinstance(spell_data[1], str):
        if "MOD" in spell_data[1]:
            modifier = spell_data[1][0:3]
            val = int(V.score_modifiers[modifier])
            add = 0
            if "+" in spell_data[1]:
                if spell_data[1].split("+")[1].isdigit():
                    add = int(spell_data[1].split("+")[1])
                elif spell_data[1].split("+")[1] == "lv":
                    add = current_level
            spell_data[1] = val + add

    spell_count += spell_data[1]
    if "Druid" in char["Class"].split(", ") and char.get("Code") != None and "Circle Spells lv3" in char["Code"]:
        spell_count += 2
    if "Druid" in char["Class"].split(", ") and char.get("Code") != None and "Circle Spells lv5" in char["Code"]:
        spell_count += 2
    if "Druid" in char["Class"].split(", ") and char.get("Code") != None and "Circle Spells lv7" in char["Code"]:
        spell_count += 2
    if "Druid" in char["Class"].split(", ") and char.get("Code") != None and "Circle Spells lv9" in char["Code"]:
        spell_count += 2


    return spell_count

def display_char_spells(screen, clock):
    character = V.character_dict[V.char_name]
    initialize_spells(screen, clock)
    check_if_spells_are_correct(character)
    if character.get("Spell") == None:
        character["Spell"] = ""
    cantrip_list = []
    if character.get("Cantrip") != None:
        cantrip_list = character["Cantrip"].split(",")
    spells = character["Spell"]
    if V.SECRETS.get(character["Name"]) != None and V.SECRETS[character["Name"]]["Spells"]:
        spells = "UNKNOWN"
    running = True
    text_size = 30
    pressed = -1
    button_dict = {
        (0, 0): ["Manage Spells", "background", "background", "rect-place-holder", "black"],
    }

    spell_list = spells.split(",")


    spell_rects = {}
    hovering_mouse = []
    scroll = 0
    text_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 4), pg.SRCALPHA)
    mode = "Description"
    notice = []
    while running:
        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.05
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        if notice != []:
            F.display_text(screen, notice[0], 10, (S.SCREEN_WIDTH * 0.05, S.SCREEN_HEIGHT * 0.05), case="c")
            notice[1] -= 1
            if notice[1] == 0:
                notice = []
        pg.draw.line(screen, "black", (S.SCREEN_WIDTH * 0.48, 0), (S.SCREEN_WIDTH * 0.48, S.SCREEN_HEIGHT))
        buttons = F.display_back_button(screen, "Back")
        x_pos = [S.SCREEN_WIDTH * 0.05, S.SCREEN_WIDTH * 0.62]
        y_pos = [S.SCREEN_HEIGHT * 0.9, S.SCREEN_HEIGHT * 0.9]
        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)
        F.display_text(screen, "Cantrips: ", 30, (S.SCREEN_WIDTH * 0.02, S.SCREEN_HEIGHT * 0.05))
        step_y = 0
        max_width = 0
        if cantrip_list != []:
            for cantrip in cantrip_list:
                rect = F.display_text(screen, cantrip, 20, (S.SCREEN_WIDTH * 0.04, S.SCREEN_HEIGHT * 0.1 + step_y))
                step_y += S.SCREEN_HEIGHT * 0.039
                spell_rects[cantrip] = rect


        F.display_text(screen, "Spells: ", 30, (S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.05))
        step_y = 0
        for spell in spell_list:
            rect = F.display_text(screen, spell, 20, (S.SCREEN_WIDTH * 0.22, S.SCREEN_HEIGHT * 0.1 + step_y))
            step_y += S.SCREEN_HEIGHT * 0.039
            spell_rects[spell] = rect


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
                        return
                    elif pressed == "Manage Spells":
                        if "Wizard" in character["Class"]:
                            if V.EQUIPED_CHAR_ITEMS.get("Special") == None:
                                V.EQUIPED_CHAR_ITEMS["Special"] = ""
                            if "Spellbook" not in V.EQUIPED_CHAR_ITEMS["Special"]:
                                F.display_text(screen, "You need a spell book, wizard", 15, (S.SCREEN_WIDTH * 0.1, S.SCREEN_HEIGHT * 0.1))
                                continue
                        old_spells = character["Spell"]
                        old_cantrips = character["Cantrip"]
                        A.Manage_spells(screen, clock)
                        update_chosen_spells(old_spells, old_cantrips)
                    pressed = -1
            elif event.type == pg.MOUSEMOTION:
                mouse_pos = pg.mouse.get_pos()
                for spell, rect in spell_rects.items():
                    if rect.collidepoint(mouse_pos):
                        hovering_mouse = [spell, rect]
                        break
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 4 or event.type == pg.KEYDOWN and event.key == pg.K_UP:
                scroll += 20
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5 or event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                scroll -= 20
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 2 or event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
                if mode == "Description":
                    mode = "Simple"
                elif mode == "Simple":
                    mode = "At Higher Levels"
                elif mode == "At Higher Levels":
                    mode = "Description"

        if hovering_mouse != []:
            id = []
            text_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 4), pg.SRCALPHA)
            F.display_text(text_surface, "Click Mouse Wheel", 15, (S.SCREEN_WIDTH * 0.75, S.SCREEN_HEIGHT * 0.03), case="C")
            if hovering_mouse[0] in cantrip_list and len(hovering_mouse) == 2:
                """Its a cantrip"""
                hovering_mouse.append("Cantrip")
            elif hovering_mouse[0] in spell_list and len(hovering_mouse) == 2:
                """Its a spell"""
                hovering_mouse.append("Spell")
            # if hovering_mouse[0] in cantrip_list and len(hovering_mouse) == 2:
            #     hovering_mouse.append("Cantrip")
            #     for cantrip, values in S.cantrip_data.items():
            #         if cantrip == hovering_mouse[0]:
            #             id = (spell_class, int(cantrip level))
            # elif hovering_mouse[0] in spell_list and len(hovering_mouse) == 2:
            #     hovering_mouse.append("Spell")
            #     for spell_level, values in S.spell_data.items():
            #         for spell_name, value in values.items():
            #             id = (spell_class, int(spell_level))




            # if id[0] == character["Class"].split(", ")[0]:
            #     id = 0, id[1]
            #     """ First char class spell """
            # else:
            #     """Secibd char class spell"""
            #     id = 1, id[1]
            display_only_spell_descriptions(text_surface, hovering_mouse, id, mode)
        screen.blit(text_surface, (0, scroll))
        pg.display.flip()
        clock.tick(60)


def display_only_spell_descriptions(screen, hovering_mouse, id, mode):
    color_school = {
        "Enchantment": "Dark BLue", # charming others, getting into their head
        "Abjuration": "Light Blue", # protective spells
        "Evocation": "Purple", # creating things out of nothing
        "Conjuration": "Navy", # summoning things, teleporting
        "Transmutation": "Gold", # change things into other things
        "Necromancy": "Dark Green", # death
        "Illusion": "Yellow", # changing appearance of things, creating sounds
        "Divination": "Magenta", # revealing information
        "Blood Curse": "Dark Red" # revealing information
    }
    if hovering_mouse == -1:
        return
    if len(hovering_mouse) == 3:
        name, rect, type = hovering_mouse

    if type == "Cantrip" and name != "UNKNOWN":
        spell_data = S.cantrip_data[name]
    elif type == "Spell" and name != "UNKNOWN":
        spell_data = S.spell_data[name]
    else:
        return


    if spell_data != None:
        start_x = S.SCREEN_WIDTH * 0.5
        start_y = S.SCREEN_HEIGHT * 0.1
        step_y = S.SCREEN_HEIGHT * 0.03
        F.display_text(screen, name, 30, (start_x, S.SCREEN_HEIGHT * 0.05), color=color_school[spell_data["School"]])

        r = F.display_text(screen, "School: ", 15, (start_x, start_y), color=color_school[spell_data["School"]])
        F.display_text(screen, spell_data["School"], 15, (r.x + r.w, r.y))

        r = F.display_text(screen, "Casting Time: ", 15, (start_x, start_y + step_y), color=color_school[spell_data["School"]])
        F.display_text(screen, spell_data["Casting Time"], 15, (r.x + r.w, r.y))
        step_y += S.SCREEN_HEIGHT * 0.03

        r = F.display_text(screen, "Level: ", 15, (start_x, start_y + step_y), color=color_school[spell_data["School"]])
        if spell_data.get("Level") == None:
            F.display_text(screen, "0", 15, (r.x + r.w, r.y))
        else:
            F.display_text(screen, spell_data["Level"], 15, (r.x + r.w, r.y))
        step_y += S.SCREEN_HEIGHT * 0.03

        r = F.display_text(screen, "Range: ", 15, (start_x, start_y + step_y), color=color_school[spell_data["School"]])
        F.display_text(screen, spell_data["Range"], 15, (r.x + r.w, r.y))
        step_y += S.SCREEN_HEIGHT * 0.03

        if spell_data.get("Duration") != None:
            r = F.display_text(screen, "Duration: ", 15, (start_x, start_y + step_y), color=color_school[spell_data["School"]])
            F.display_text(screen, spell_data["Duration"], 15, (r.x + r.w, r.y))
            step_y += S.SCREEN_HEIGHT * 0.03

        if spell_data.get("Components") != None:
            r = F.display_text(screen, "Components: ", 15, (start_x, start_y + step_y), color=color_school[spell_data["School"]])
            F.display_text(screen, spell_data["Components"], 15, (r.x + r.w, r.y))
            step_y += S.SCREEN_HEIGHT * 0.03

        if spell_data.get("Ritual"):
            r = F.display_text(screen, "Ritual: ", 15, (start_x, start_y + step_y), color=color_school[spell_data["School"]])
            F.display_text(screen,spell_data["Ritual"], 15, (r.x + r.w, r.y))
            step_y += S.SCREEN_HEIGHT * 0.03

        if mode == "Description":
            start_y += step_y
            description = "Description: "
        if mode == "Simple":
            mode = "Description_for_dummies"
            if spell_data.get("Damage") != None:
                r = F.display_text(screen, "1st Level Damage: ", 15, (start_x, start_y + step_y), color=color_school[spell_data["School"]])
                F.display_text(screen, str(spell_data["Damage"]), 15, (r.x + r.w, r.y))
                step_y += S.SCREEN_HEIGHT * 0.03

            if spell_data.get("Type") != None:
                r = F.display_text(screen, "Type: ", 15, (start_x, start_y + step_y), color=color_school[spell_data["School"]])
                F.display_text(screen, str(spell_data["Type"]), 15, (r.x + r.w, r.y))
                step_y += S.SCREEN_HEIGHT * 0.03
            start_y += step_y
            description = "Simplefied: "
        elif mode == "At Higher Levels":
            mode = "At higher levels"
            if spell_data.get("Damage") != None:
                r = F.display_text(screen, "1st Level Damage: ", 15, (start_x, start_y + step_y), color=color_school[spell_data["School"]])
                F.display_text(screen, str(spell_data["Damage"]), 15, (r.x + r.w, r.y))
                step_y += S.SCREEN_HEIGHT * 0.03

            if spell_data.get("Type") != None:
                r = F.display_text(screen, "Type: ", 15, (start_x, start_y + step_y), color=color_school[spell_data["School"]])
                F.display_text(screen, str(spell_data["Type"]), 15, (r.x + r.w, r.y))
                step_y += S.SCREEN_HEIGHT * 0.03
            start_y += step_y
            description = "At Higher Levels: "


        if spell_data.get(mode) != None:
            word_length = F.display_text(screen, description, 15, (start_x, start_y), color=color_school[spell_data["School"]])
            y_step = 0
            start_x += word_length.w
            for word in spell_data[mode].split(" "):
                if 'â€™' in word:
                    word = word.replace('â€™', "'")
                if 'â€“' in word:
                    word = word.replace('â€“', "-")
                word = word.replace("\n\n", " ")
                word = word.replace("\n", " ")
                word_length = F.display_text(screen, word + " ", 15,(start_x, start_y + y_step))
                start_x = word_length.x + word_length.w
                if word_length.w + word_length.x >= S.SCREEN_WIDTH - 100:
                    y_step += S.SCREEN_HEIGHT * 0.03
                    word_length.w = 0
                    start_x = S.SCREEN_WIDTH * 0.5

def update_chosen_spells(old_spells, old_cantrips):
    character = V.character_dict[V.char_name]
    print(old_cantrips, old_spells)

    if old_spells != character["Spell"]:
        with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
            char_config_data = json.load(file)
        if char_config_data.get("Chosen_spells") == None:
            char_config_data["Chosen_spells"] = []
        char_config_data["Chosen_spells"] = character["Spell"]
    if old_cantrips != character["Cantrip"]:
        with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
            char_config_data = json.load(file)
        if char_config_data.get("Chosen_cantrips") == None:
            char_config_data["Chosen_cantrips"] = []
        char_config_data["Chosen_cantrips"] = character["Cantrip"]

        F.create_char_JSON(V.char_name, char_config_data)

