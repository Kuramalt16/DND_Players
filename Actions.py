import math, copy
import random

import pygame as pg, time, Variables as V, Functions as F, Settings as S, Help as H, Skills as sk, conditions as C, DisplayChar as dCh, Special_Needs as special, Spells as Sp
import Items
import json

import Special_Needs


def pause():
    run = True
    pg.display.flip()
    clock = pg.time.Clock()
    while run:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                run = False
        clock.tick(120)

def Initialize_actions(screen, clock):
    """Items have actions spell slots have actions"""
    """Display all action types"""
    character = V.character_dict[V.char_name]
    V.item_dict["Unarmed Strike"] = {"Extra": "1:Bludgeoning", "Properties": "Light"}
    V.item_dict["Improvised Attack"] = {"Extra": "1d4:Bludgeoning", "Properties": "Light"}
    weapon_proficiencies = []

    V.Reactions = {}
    V.Bonus_actions = {}

    weapon_list = F.get_equiped_weapons()
    unknown_list = check_if_two_weapon_fighting_feature_applies()
    cantrip_list = []
    spell_list = []
    feat_list = []
    free_spell_list = []
    ammo_count = F.get_ammo_count(weapon_list)
    for key, value in character.items():
        if key == "Weapon Proficiencies":
            for item in value.split(","):
                if item not in weapon_proficiencies:
                    weapon_proficiencies.append(item)
        elif key == "Cantrip" and value != "":
            for cantrip in value.split(","):
                if cantrip == "":
                    continue
                if cantrip not in cantrip_list:
                    cantrip_list.append(cantrip)
                    if "Bonus" in S.cantrip_data[cantrip]["Casting Time"]:
                        V.Bonus_actions[cantrip] = "Cantrip"
        elif key == "Spell":
            for spell in value.split(","):
                if spell not in spell_list:
                    if spell == '':
                        continue
                    spell_list.append(spell)
                    if S.spell_data.get(spell) != None and "Bonus" in S.spell_data[spell]["Casting Time"]:
                        V.Bonus_actions[spell] = "Spell"
                    if S.spell_data.get(spell) != None and "Reaction" in S.spell_data[spell]["Casting Time"]:
                        V.Reactions[spell] = "Spell"
        elif key == "Code":
            extra_action_values = []
            for extra_action in value.split(","):
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
                            spell_list += get_cantrips_from_subclass_entry(spells, screen, clock, extra_action, mode="Spell")
                        elif "Class_Spell_Slot_and_spell" == S.Class_features[function_name]["Action_Type"]:
                            if "Spell_slot:" + function_name not in unknown_list:
                                """Need to come here only once"""
                                unknown_list.pop()
                                unknown_list += handle_slot_commands_from_subclass_json(S.Class_features[function_name]["Spell_slot"], function_name)

                                spells = S.Class_features[function_name]["Spell"]
                                spell_list += get_cantrips_from_subclass_entry(spells, screen, clock, extra_action, mode="Spell")

                                """This change makes the code come here only initialy"""
                                S.Class_features[function_name]["Action_Type"] = "Spell_Slot"
                        elif "Changed_Spell_Slot" in S.Class_features[function_name]["Action_Type"]:
                            unknown_list.pop()
                            unknown_list.append("Spell_slot:" + function_name)
                        elif "Class_Spell_Slot" in S.Class_features[function_name]["Action_Type"]:
                            if "Spell_slot:" + function_name not in unknown_list:
                                unknown_list.pop()
                                unknown_list += handle_slot_commands_from_subclass_json(S.Class_features[function_name]["Spell_slot"], function_name)
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
                                unknown_list += handle_slot_commands_from_subclass_json(slots, extra_action.split(":")[1])
                                continue
                            if "Free Cantrip" == data["Action_Type"]:
                                """Enters here with Conan Druid cantrip Shillelagh"""
                                cantrips = data["Cantrip"]
                                cantrip_list += get_cantrips_from_subclass_entry(cantrips, screen, clock, extra_action)
                            if "Spell" == data["Action_Type"]:
                                spells = data["Spell"]
                                for spell in spells.split(","):
                                    spell_list.append(spell)
                            if "Feature:" + extra_action.split(":")[1] not in unknown_list:
                                unknown_list.append("Feature:" + extra_action.split(":")[1])
                            if "Free Spell" == data["Action_Type"]:
                                spells = data["Spell"]
                                spell_list += get_cantrips_from_subclass_entry(spells, screen, clock, extra_action, extra_action_values, mode="Spell")
                            if "Subclass path" == data["Action_Type"]:
                                if data["Subclass"][0] == "CHOOSE":
                                    choise_made = F.check_if_choise_was_already_made(extra_action)
                                    if not choise_made:
                                        res = make_a_choise(data["Subclass"], screen, clock, extra_action_values)
                                        F.save_choise_json(extra_action, res)
                            if S.Class_features[function_name].get("Special_Flag") != None:
                                """handle special flag for fuctions that aren't user based like cast, weapon, hit or spell slot"""
                                special.handle_diferent_special_flags(function_name, screen, clock, character)
        elif key == "Feat":
            for feat in value.split(","):
                if feat not in feat_list:
                    feat_list.append(feat)
        elif key == "Free_Spells":
            for val in value:
                free_spell_list.append(val)
        elif key in ["Fighting Style", "Metamagic"]:
            if "," in value:
                for i in range(0, value.count(",")+1):
                    unknown_list.append("Sub_Feature:" + key + "_" + value.split(",")[i])
            else:
                unknown_list.append("Sub_Feature:" + key + "_" + value)
        elif key in ["Crimson Rites"]:
            if value not in V.Rites:
                V.Rites[value] = ""


        elif key not in ["Race", "Class", "Experience", "Level", "Health", "Ability_Scores", "Background", "Alignment", "Gold", "AC", "Skills", "Speed", "Immunity", "Resistance", "Vulnerabilities", "Languages", "Items", "Spell Slots", "Cantrip", "Extra", "Size", "Hit dice", "Armor Proficiencies", "Tool Proficiencies", "Saving Throw Proficiencies", "Proficiency Bonus", "Primary Ability", "Slot Level", "Rage Damage", "Name", "Wild Companion", "Wild Shape", "Rage", "Hemocraft_die", "Beasts", "Darkvision", "Second Ability Score", "Second Wind", "Extra Attack", "Action Surge", "Unarmored Defense", "SubClass", "Reckless Attack", "Fast Movement", "Blood Curses Known", "Font of Magic", "Sorcery Points", "Arcane Recovery", "Magical Guidance", "Favoured Enemy", "Natural Explorer", "Primeval Awareness"]:
            F.print_debug(f"Not included: {key}", value, debug="DEBUG")

    running = True
    pressed = -1
    button_dict = {
        (2, 0): ["Initiative", "background", "background", "rect-place-holder", "black"],
        (0, 0): ["Help", "background", "background", "rect-place-holder", "black"],
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
    mini_screen_scroll = 0
    spell_tracker = {} # tracks spells that have Hit and Damage rolls

    notice = [] # Place holder for notes to the user

    show_slots = False  # a flag used to show the player his spell slots
    show_history = False  # a flag used to show the player his roll history
    show_notes = 0

    enough_components = False # place holder for component check for spells, if spell has HIT then check there first and dont erase the value so checking in DAMAGE wouldn't be neccesary, if checking in damage first then it should be FALSE
    mode = "Description"
    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        V.char_config = json.load(file)

    was_it_removed = False
    scroll_amount = 30
    slot_to_display = (0, 0)
    selected_entry = -1
    txt_dict = {"Heal": ["", 0]}
    timer = 10

    while running:
        special.display_wild_shapes(screen, clock)
        if V.Condition == 'Exhaustion lv6':
            return
        button_dict = special.rage_check(button_dict)
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
            F.display_text(screen, "Critical Success - Purple", 15, (S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.09), color="Purple")
            F.display_text(screen, "Critical Fail - Black", 15, (S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.12), color="Black")

        if rolled_sum != -1:
            F.display_text(screen, "Rolled: " + str(dtwenty) + "+" + str(rolled_sum - dtwenty) + "=" + str(rolled_sum), 15, (S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.06), color=dice_color)

        char_AC = character["AC"]
        if V.spell_effects.get("Char") != None and V.spell_effects["Char"].get("AC") != None:
            char_AC = str(V.spell_effects["Char"]["AC"])
        F.display_text(screen, "Armor Class: " + str(char_AC), 15, (S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.00), color="red")
        F.display_text(screen, "Spell Save DC: " + str(V.Spell_save_DC), 15,(S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.03), color="purple")

        buttons = F.display_back_button(screen, "Back")

        # slot_rect = F.display_text(screen, "Spell Slots", 20, (S.SCREEN_WIDTH * 0.88, S.SCREEN_HEIGHT * 0.2))
        # pg.draw.rect(screen, "black", slot_rect, width=2)

        hist_rect = F.display_text(screen, "Roll History", 20, (S.SCREEN_WIDTH * 0.88, S.SCREEN_HEIGHT * 0.205))
        pg.draw.rect(screen, "black", hist_rect, width=2)

        note_rect = F.display_text(screen, "Notes", 20, (S.SCREEN_WIDTH * 0.88, S.SCREEN_HEIGHT * 0.2505))
        pg.draw.rect(screen, "black", note_rect, width=2 + int(show_notes/2))

        x_pos = [S.SCREEN_WIDTH * 0.05, S.SCREEN_WIDTH * 0.27, S.SCREEN_WIDTH * 0.52, S.SCREEN_WIDTH * 0.795]
        y_pos = [S.SCREEN_HEIGHT * 0.9, S.SCREEN_HEIGHT * 0.12, S.SCREEN_HEIGHT * 0.3]

        slot_to_add_dict = F.display_spell_slots(screen, slot_to_display)
        dice_hist_surface = F.display_spell_history(screen, show_history)
        show_notes = handle_notes(screen, clock, show_notes, note_rect)

        button_dict = handle_Consentration(screen, button_dict)

        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)

        rect_dict = display_actions((screen, weapon_screen, spell_screen, feature_screen), weapon_list, ammo_count, cantrip_list, spell_list, unknown_list, feat_list, free_spell_list, (weapon_scroll, spell_scroll, feature_scroll))

        notice = F.display_notice(screen, notice, (S.SCREEN_WIDTH * 0.02, S.SCREEN_HEIGHT * 0.95))

        C.display_condition_effects_actions(screen)

        draw_action_grid(screen)

        F.display_text(screen, "HP: ", 14, (S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.15))
        enter_hp = F.add_entry_to_list((S.SCREEN_WIDTH * 0.84, S.SCREEN_HEIGHT * 0.15, S.SCREEN_WIDTH * 0.05, S.SCREEN_HEIGHT * 0.04), "hp", screen, "", 20, (S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.5))
        text_a = F.display_text(screen, str(character["Health"]), 14, (S.SCREEN_WIDTH * 0.89, S.SCREEN_HEIGHT * 0.15))
        if character.get("Temp_hp") != None and character["Temp_hp"] != 0:
            F.display_text(screen, str(character["Temp_hp"]), 14, (text_a.x + text_a.w, text_a.y), color="red")

        for event in pg.event.get():
            keys = pg.key.get_pressed()
            mouse_pos = pg.mouse.get_pos()
            if event.type == pg.QUIT:
                """quit"""
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
                if V.images.get("SLOT SCREEN") != None:
                    del V.images["SLOT SCREEN"]
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                selected_entry = -1
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(mouse_pos):
                        pressed = "Back"
                        for key, value in button_dict.items():
                            if value[3] == buttons[i]:
                                pressed = value[0]
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                if pressed in ["Back", -1]:
                    for name, value in rect_dict.items():
                        for property, rect in value.items():
                            if isinstance(rect, pg.Rect) and rect.collidepoint(mouse_pos) and property in ["Hit", "Damage", "Cast", "Throw", "Versatile", "Spell_slot", "Damage_extra", "Rite", "Sub_Feature_Spell_slot", "Ritual", "Use"]:
                                pressed = [property, name]
                for slot in slot_to_add_dict:
                    for plus_or_minus, rect in slot_to_add_dict[slot].items():
                        if rect.collidepoint(mouse_pos):
                            pressed = (slot, plus_or_minus)
                            break
                if enter_hp.collidepoint(mouse_pos):
                    selected_entry = 0
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

                            F.Roll_3d_dice(screen, clock, "D20", str(dtwenty))
                            rolled_sum = dtwenty + V.score_modifiers["DEX"]
                            F.add_to_roll_history(dtwenty, rolled_sum, "Initiative")

                        elif pressed == "End Concentration":
                            """Deletting end concentration button"""
                            del button_dict[(1, 0)]
                            V.consentration = {}
                        elif pressed == "Help":
                            H.render_help(screen, clock)
                        elif pressed == "End Rage":
                            del V.Special_Flags["Rage"]
                            S.Background_image = "background"
                            S.Standart_color = "black"
                            del button_dict[(1, 0)]
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
                            cant_use_spell = False
                            enough_components, component_name = handle_component_checks(spell_tracker, rect_dict, pressed)
                            if enough_components:
                                was_it_removed = True
                                if rect_dict[pressed[1]]["Type"] in ["Spell"]:
                                    """do we have enought spell slots for this spell? spell is not free cuz we checking for Spell not Free Spell"""
                                    if ":" in pressed[1]:
                                        spell_name, casting_level = pressed[1].split(":")
                                        was_it_removed = F.remove_spell_slot(casting_level)
                                    else:
                                        was_it_removed = F.remove_spell_slot(S.spell_data[pressed[1]]["Level"])
                                    if not was_it_removed:
                                        notice = ["Not Enough Spell Slots", 100]
                                if rect_dict[pressed[1]]["Type"] in ["Spell", "Cantrip"] and was_it_removed:
                                    """check consentration"""
                                    if S.spell_data.get(pressed[1]) != None and "Concentration" in S.spell_data[pressed[1]]["Duration"]:
                                        V.consentration[pressed[1]] = ["Spell", pg.time.get_ticks()]
                                    if S.cantrip_data.get(pressed[1]) != None and "Concentration" in S.cantrip_data[pressed[1]]["Duration"]:
                                        V.consentration[pressed[1]] = ["Cantrip", pg.time.get_ticks()]

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
                                if enough_ammo and was_it_removed:
                                    advantage = False

                                    disadvantage = handle_heavy_weapon_disadvantage(screen, clock, pressed, character)
                                    if rect_dict[pressed[1]]["Type"] in ["Spell", "Cantrip"]:
                                        if Items.handle_armor_proficiencies(character, cant_use_spell, "Magic"):
                                            notice = ["Not proficient with armor", 100]
                                            enough_components = False
                                            component_name = ""
                                            continue

                                    else:
                                        disadvantage = Items.handle_armor_proficiencies(character, disadvantage, "STR")


                                    if V.Condition in ["Exhaustion lv3", "Exhaustion lv4", "Exhaustion lv5", "Exhaustion lv6", "Restrained", "Prone", "Poisoned", "Blinded", "Heavily Encumbered"]:
                                        disadvantage = True
                                    if V.Condition in ["Invisible"]:
                                        advantage = True

                                    dtwenty = random.randint(1, 20)

                                    screen.blit(weapon_screen, (0, 0))
                                    screen.blit(spell_screen, (0, 0))
                                    screen.blit(feature_screen, (0, 0))

                                    F.Roll_3d_dice(screen, clock, "D20", str(dtwenty))

                                    rolled_sum, dtwenty = sk.handle_disadvantage_rolls(screen, clock, "1D20", dtwenty, (disadvantage, advantage), int(rect_dict[pressed[1]]["Roll_mod"]))
                                    F.add_to_roll_history(dtwenty, rolled_sum, "Hit:" + str(pressed[1]))
                                    dice_color, critical_fail, critical_success = handle_critical_fail_success_colors(dtwenty)
                            else:
                                notice = ["Not enough components, Need: " + component_name, 100]
                                component_name = ""
                                enough_components = False
                        elif pressed[0] == "Damage":
                            dice = rect_dict[pressed[1]]["Damage_Die"]

                            if "d" in dice:
                                """clicked on a dice roll"""
                                if enough_components == False:
                                    """Only if the value is set to false are we checking again, because if the item was checked in the HIT section and it passed we dont need to check again,
                                    if the item was not checked in the HIT that means it should be false"""
                                    enough_components, component_name = handle_component_checks(spell_tracker, rect_dict, pressed)
                                if was_it_removed == False:
                                    was_it_removed = True
                                    if rect_dict[pressed[1]]["Type"] in ["Spell"]:
                                        """this is a spell are there enough spell slots? and later add checking if this spell was already rolled for to use a spell slot. maybe add a must click HIT beofre Dammage becomes usable. but it's shit, what if with advantage or sth.. maybe a timer? check how long after clicking hit and damage. but it's too unreliable"""

                                        if ":" in pressed[1]:
                                            spell_name, casting_level = pressed[1].split(":")
                                            was_it_removed = F.remove_spell_slot(casting_level)
                                        else:
                                            was_it_removed = F.remove_spell_slot(S.spell_data[pressed[1]]["Level"])
                                        if not was_it_removed:
                                            notice = ["Not Enough Spell Slots", 100]

                                if enough_components and was_it_removed:
                                    enough_components = False
                                    if was_it_removed:
                                        if component_name != "-":
                                            """enough components was an item not a boolean"""
                                            F.remove_item_from_char(component_name, character)
                                            if component_name == "Arrows":
                                                ammo_count["Arrows"] -= 1
                                                if ammo_count["Arrows"] == 0:
                                                    del ammo_count["Arrows"]
                                                    weapon_list.remove("Arrows")
                                        if S.spell_data.get(pressed[1]) != None and "Concentration" in S.spell_data[pressed[1]]["Duration"]:
                                            V.consentration[pressed[1]] = ["Spell", pg.time.get_ticks()]
                                        if S.cantrip_data.get(pressed[1]) != None and "Concentration" in S.cantrip_data[pressed[1]]["Duration"]:
                                            V.consentration[pressed[1]] = ["Cantrip", pg.time.get_ticks()]
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
                                        enough_components = False
                                        F.Roll_3d_dice(screen, clock, dice[1:].upper(), multiple_rolls)
                                        rolled_sum = int(dtwenty) + int(rect_dict[pressed[1]]["Damage_mod"])
                                        F.add_to_roll_history(dtwenty, rolled_sum, "Damage:" + str(pressed[1]))
                                        was_it_removed = False
                                else:
                                    if enough_components:
                                        notice = ["Not enough Spell Slots", 100]
                                    else:
                                        notice = ["Not enough components, Need: " + component_name, 100]
                                    component_name = ""
                                    enough_components = False
                        elif pressed[0] == "Cast":
                            if Items.handle_armor_proficiencies(character, False, "Magic"):
                                notice = ["Not proficient with armor", 100]
                                enough_components = False
                                continue
                            enough_components, component_name = handle_component_checks(spell_tracker, rect_dict, pressed)
                            handle_spell_effects(pressed[1], rect_dict[pressed[1]]["Type"])


                            if enough_components:

                                """If enough components check if this is a spell and we need to remove spell slots or not"""
                                if rect_dict[pressed[1]]["Type"] == "Spell":
                                    """lets remove spell slots"""
                                    spell_name, casting_level = pressed[1].split(":")
                                    spell_level = S.spell_data[spell_name]["Level"]
                                    if spell_level != casting_level:
                                        spell_level = casting_level
                                    was_it_removed = F.remove_spell_slot(spell_level)
                                    if not was_it_removed:
                                        """not casted lacking spell slots"""
                                        notice = ["Not Enough Spell Slots", 100]
                                    else:
                                        """casted enough spell slots for this spell"""
                                        if component_name != "-":
                                            F.remove_item_from_char(component_name, character)
                                    enough_components = False
                                """Casted, this was a cantrip"""
                            else:
                                """Not casted lacking components"""
                                enough_components = False
                                notice = ["Not enough components, Need: " + component_name, 100]
                                component_name = ""
                        elif pressed[0] == "Throw":
                            if V.item_dict.get(pressed[1]) != None and "thrown" in V.item_dict[pressed[1]]["Properties"].lower():
                                """if thrown item remove it from player"""
                                F.remove_item_from_char(pressed[1], character)
                                if pressed[1] not in character["Items"]:
                                    weapon_list.remove(pressed[1])

                                dtwenty = random.randint(1, int(rect_dict[pressed[1]]["Damage_Die"].split("d")[1]))

                                F.Roll_3d_dice(screen, clock, "D" + rect_dict[pressed[1]]["Damage_Die"].split("d")[1], str(dtwenty))
                                # rolled_sum, dtwenty = sk.handle_disadvantage_rolls(screen, clock, "D" + rect_dict[pressed[1]]["Damage_Die"].split("d")[1], dtwenty, (disadvantage, advantage), int(rect_dict[pressed[1]]["Damage_mod"]))
                                rolled_sum = dtwenty + int(rect_dict[pressed[1]]["Damage_mod"])

                                if "Giant's Havoc" in V.character_dict[V.char_name]["Code"] and rect_dict[pressed[1]]["Mod_Name"] == "STR":
                                    rolled_sum += int(V.character_dict[V.char_name]["Rage Damage"])
                                if V.character_dict[V.char_name].get("Fighting Style") != None and "Thrown Weapon Fighting" in V.character_dict[V.char_name]["Fighting Style"]:
                                    rolled_sum += 2
                                F.add_to_roll_history(dtwenty, rolled_sum, "Throw:" + str(pressed[1]))
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
                                F.Roll_3d_dice(screen, clock, dice[1:].upper(), multiple_rolls)
                                rolled_sum = int(dtwenty) + int(rect_dict[pressed[1]]["Damage_mod"])
                                F.add_to_roll_history(dtwenty, rolled_sum, "Two-handed:" + str(pressed[1]))
                        elif pressed[0] == "Spell_slot":

                            if S.Class_features[pressed[1]]["Action_Type"] == "Changed_Spell_Slot":
                                if S.Class_features[pressed[1]]["Change"][0] == "REMOVE":
                                    """Checking was there a spellslot change or not used for Wild Companion"""
                                    slot_to_remove = F.level_to_name(S.Class_features[pressed[1]]["Change"][2])
                                    if V.spell_slots.get(slot_to_remove) != None and V.spell_slots[slot_to_remove] >= int(S.Class_features[pressed[1]]["Change"][1]):
                                        for i in range(int(S.Class_features[pressed[1]]["Change"][1])):
                                            was_it_removed = F.remove_spell_slot(S.Class_features[pressed[1]]["Change"][2])
                                    else:
                                        was_it_removed = False
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
                                    F.print_debug("IDK WHAT TO DO BOSS: ", pressed, "ERROR")
                            else:
                                """Every other feature"""
                                if S.Class_features[pressed[1]].get("reset") != None and S.Class_features[pressed[1]]["reset"] == "inf":
                                    was_it_removed = True
                                else:
                                    if pressed[1] != "Font of Magic":
                                        was_it_removed = F.remove_spell_slot(pressed[1])
                                    else:
                                        was_it_removed = special.handle_font_of_magic(pressed, screen, clock)

                            if not was_it_removed:
                                notice = ["Not Enough Spell Slots", 100]
                            else:
                                """enough spell slots and slot was consumed"""
                                handle_special_flags(pressed)
                                if rect_dict[pressed[1]].get("Dice") != None:
                                    dice = rect_dict[pressed[1]]["Dice"]
                                    special.handle_blood_hunter_spell_slots(pressed, rect_dict, screen, clock)
                                    add = 0
                                    if "+" in dice:
                                        add_to_dice_list = dice.split(" + ")
                                        dice = add_to_dice_list[0] # sets dice for rolling
                                        add = add_to_dice_list[1]
                                        if ":" in add_to_dice_list[1]:
                                            """add to dice list isnt an int, need to get a value"""
                                            if add_to_dice_list[1].split(":")[0] == "Char" and add_to_dice_list[1].split(":")[1] == "Class" and add_to_dice_list[1].split(":")[2] == "Fighter" and add_to_dice_list[1].split(":")[3] == "LV":
                                                class_index = V.character_dict[V.char_name]["Class"].split(", ").index(add_to_dice_list[1].split(":")[2])
                                                add = V.character_dict[V.char_name]["Level"].split(",")[class_index]
                                        add = int(add)
                                    dtwenty = random.randint(1, int(dice.split("d")[1]))
                                    F.Roll_3d_dice(screen, clock, dice[1:].upper(), str(dtwenty))
                                    rolled_sum = dtwenty + add
                                    F.add_to_roll_history(dtwenty, rolled_sum, "Feature:" + str(pressed[1]))

                                    if pressed[1] == "Second Wind":
                                        notice = ["Second Wind: Healed: " + str(rolled_sum), 100]
                                        V.character_dict[V.char_name]["Health"][0] += rolled_sum
                                        if V.character_dict[V.char_name]["Health"][0] > V.character_dict[V.char_name]["Health"][1]:
                                            V.character_dict[V.char_name]["Health"][0] = V.character_dict[V.char_name]["Health"][1]

                        elif pressed[0] == "Damage_extra":
                            dice = rect_dict[pressed[1]]["Damage_Die_extra"]
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
                                F.Roll_3d_dice(screen, clock, dice[1:].upper(), multiple_rolls)

                                rolled_sum = int(dtwenty) + int(rect_dict[pressed[1]]["Damage_mod_extra"])
                                F.add_to_roll_history(dtwenty, rolled_sum, "Extra Damage:" + str(pressed[1]))
                        elif pressed[0] == "Rite":
                            add = 0
                            hemocraft_die = character["Hemocraft_die"]
                            dtwenty = random.randint(1, int(hemocraft_die.split("d")[1]))
                            F.Roll_3d_dice(screen, clock, hemocraft_die[1:].upper(), str(dtwenty))
                            rolled_sum = dtwenty + add
                            F.add_to_roll_history(dtwenty, rolled_sum, "Rite:" + str(pressed[1]))
                        elif pressed[0] == "Sub_Feature_Spell_slot":
                            was_it_removed = False
                            sub_name = rect_dict[pressed[1]]["Type"].split(":")[1]
                            action_type = S.Class_features[sub_name][pressed[1]]["Action_Type"]
                            if action_type == "Changed_Spell_Slot":
                                change = S.Class_features[sub_name][pressed[1]]["Change"]
                                if change[0] == "REMOVE":
                                    slot_to_remove = F.level_to_name(change[2])
                                    if V.spell_slots.get(slot_to_remove) != None and V.spell_slots[slot_to_remove] >= int(change[1]):
                                        for i in range(0, int(change[1])):
                                            was_it_removed = F.remove_spell_slot(change[2])
                                    else:
                                        was_it_removed = False
                            else:
                                F.print_debug("UNKNOWN SLOT TYPE FOR SUB FEATURES", action_type, "ERROR")
                            if not was_it_removed:
                                notice = ["Not Enough Spell Slots", 100]
                        elif pressed[0] == "Ritual":
                            if Items.handle_armor_proficiencies(character, False, "Magic"):
                                notice = ["Not proficient with armor", 100]
                                enough_components = False
                                continue
                            enough_components, component_name = handle_component_checks(spell_tracker, rect_dict, pressed)
                            handle_spell_effects(pressed[1], rect_dict[pressed[1]]["Type"])
                            if enough_components:
                                """If enough components check if this is a spell and we need to remove spell slots or not"""
                                if rect_dict[pressed[1]]["Type"] == "Spell":
                                    """lets remove spell slots"""
                                    if component_name != True:
                                        F.remove_item_from_char(component_name, character)
                                    enough_components = False
                            else:
                                """Not casted lacking components"""
                                enough_components = False
                                notice = ["Not enough components, Need: " + component_name, 100]
                                component_name = ""
                        elif pressed[0] == "Use":
                            if pressed[1] == "Ranger's Companion":
                                Special_Needs.WildShape(screen, clock, V.char_config["Choises"][pressed[1]], "Ranger's Companion")
                    elif isinstance(pressed, tuple):
                        if slot_to_add_dict[pressed[0]][pressed[1]].collidepoint(mouse_pos):
                            if pressed[1] == "Plus":
                                if int(V.spell_slots[pressed[0]]) + 1 <= int(V.max_spell_slots[pressed[0]]):
                                    V.spell_slots[pressed[0]] += 1
                            elif pressed[1] == "Minus":
                                V.spell_slots[pressed[0]] -= 1
                                if V.spell_slots[pressed[0]] < 0:
                                    V.spell_slots[pressed[0]] = 0
                    pressed = -1

            elif event.type == pg.MOUSEMOTION:
                mouse_pos = pg.mouse.get_pos()
                didnt_find_it = True
                for name, value in rect_dict.items():
                    for property, rect in value.items():
                        if isinstance(rect, pg.Rect) and rect.collidepoint(mouse_pos):
                            hovering_mouse = [name, property, rect, rect_dict[name]["Type"]]
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
                #     show_history = False
                elif hist_rect.collidepoint(mouse_pos):
                    """When colliding with this rect shows spells"""
                    show_slots = False
                    show_history = True
                elif note_rect.collidepoint(mouse_pos) and show_notes == 0:
                    """When colliding with this rect shows spells"""
                    show_notes = 1
                    show_slots = False
                    show_history = False
                else:
                    show_slots = False
                    show_history = False
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 4 or event.type == pg.KEYDOWN and event.key == pg.K_UP:
                mouse_pos = pg.mouse.get_pos()
                if hovering_mouse == -1:
                    if mouse_pos[0] in range(int(S.SCREEN_WIDTH * 0.29), int(S.SCREEN_WIDTH * 0.54)):
                        spell_scroll += scroll_amount
                    elif mouse_pos[0] in range(int(S.SCREEN_WIDTH * 0.54), int(S.SCREEN_WIDTH * 0.79)):
                        feature_scroll += scroll_amount
                    elif mouse_pos[0] in range(0, int(S.SCREEN_WIDTH * 0.29)):
                        weapon_scroll += scroll_amount
                else:
                    mini_screen_scroll += scroll_amount/2

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5 or event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                mouse_pos = pg.mouse.get_pos()
                if hovering_mouse == -1:
                    if mouse_pos[0] in range(int(S.SCREEN_WIDTH * 0.29), int(S.SCREEN_WIDTH * 0.54)):
                        spell_scroll -= scroll_amount
                    elif mouse_pos[0] in range(int(S.SCREEN_WIDTH * 0.54), int(S.SCREEN_WIDTH * 0.79)):
                        feature_scroll -= scroll_amount
                    elif mouse_pos[0] in range(0, int(S.SCREEN_WIDTH * 0.29)):
                        weapon_scroll -= scroll_amount
                else:
                    mini_screen_scroll -= scroll_amount/2
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 2 or event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
                if mode == "Description":
                    mode = "Description_for_dummies"
                elif mode == "Description_for_dummies":
                    mode = "At higher levels"
                elif mode == "At higher levels":
                    mode = "Description"

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
                txt_dict, selected_entry, got_damaged = dCh.update_char_hp_based_on_entry(character, txt_dict, selected_entry, screen, clock)

        text_surface = display_mini_screen(hovering_mouse, mini_window_w, mini_window_h, text_surface, mode, scroll=mini_screen_scroll)

        screen.blit(weapon_screen, (0, 0))
        screen.blit(spell_screen, (0, 0))
        screen.blit(feature_screen, (0, 0))

        mouse_pos = pg.mouse.get_pos()

        if pressed != -1 and isinstance(pressed, list):
            pg.draw.rect(screen, "red", rect_dict[pressed[1]][pressed[0]], width=3)

        if mouse_pos[1] <= S.SCREEN_HEIGHT * 0.85:
            screen.blit(text_surface, mouse_pos)

        critical_fail, critical_success = F.display_nat_20_or_1(screen, critical_fail, critical_success)
        # if slot_surface != 0:
        #     screen.blit(slot_surface, (0, 0))
        if dice_hist_surface != 0:
            screen.blit(dice_hist_surface, (0, 0))

        F.update_text(txt_dict, [enter_hp], screen)

        if selected_entry != -1:
            F.flash_marker(selected_entry, [enter_hp], screen, timer, txt_dict)

        pg.display.flip()
        clock.tick(60)
        timer = F.reset_timer(timer)

def display_mini_screen(hovering_mouse, mini_window_w, mini_window_h, text_surface, mode="Description", scroll=0):
    if hovering_mouse != -1 and hovering_mouse[1].lower() == "info":
        properties = []
        if mode == "Description":
            title = "Description: "
        elif mode == "Description_for_dummies":
            title = "Simplified: "
        elif mode == "At higher levels":
            title = "At Higher Levels: "

        text_surface = pg.Surface((mini_window_w, mini_window_h), pg.SRCALPHA)
        temp_surface = pg.Surface((mini_window_w, mini_window_h*5), pg.SRCALPHA)
        F.add_image_to_screen(text_surface, "background", (0, 0, mini_window_w, mini_window_h), "Background")
        pg.draw.rect(text_surface, "black", pg.Rect(0, 0, mini_window_w, mini_window_h), width=2)

        if "Multiattack" in hovering_mouse[0]:
            hovering_mouse[0] = hovering_mouse[0].split(":")[0]
        if ":" in hovering_mouse[0] and hovering_mouse[3] in ["Spell", "Free Spell"]:
            """Removing the casting level from the spell key for displaying only"""
            hovering_mouse[0] = hovering_mouse[0].split(":")[0]
        F.display_text(temp_surface, hovering_mouse[0] + " (" + hovering_mouse[3] + ")", 15, (mini_window_w * 0.02, mini_window_w * 0.02 + scroll))
        step_y = 0
        data_dict = {}
        if hovering_mouse[3] == "Weapon":
            properties = ["Rarity", "Properties", "Cost"]
            data_dict = V.item_dict.copy()
        elif hovering_mouse[3] in ["Cantrip"]:
            """Get properties and add saving throw for cantrip text display"""
            properties = ["School", "Casting Time", "Range", "Duration", "Components", "Saving Throw"]
            data_dict = S.cantrip_data.copy()
            if "saving throw" in S.cantrip_data[hovering_mouse[0]]["Description_for_dummies"]:
                description_words = S.cantrip_data[hovering_mouse[0]]["Description_for_dummies"].split(" ")
                for i in range(0, len(description_words)-1):
                    description_words[i+1] = description_words[i+1].replace(",", "")
                    if description_words[i] == "saving" and description_words[i + 1] == "throw":
                        # Check if the word before "saving throw" is in the list of valid options
                        if description_words[i - 1] in V.Ability_score_list:
                            S.cantrip_data[hovering_mouse[0]]["Saving Throw"] = description_words[i - 1]
                            break
        elif hovering_mouse[3] in ["Spell", "Free Spell"]:
            """Get properties and add saving throw for spell text display"""
            properties = ["School", "Level", "Casting Time", "Range", "Duration", "Components", "Saving Throw", "Ritual"]
            if S.spell_data == {}:
                with open(S.local_path + "/Spells.json", 'r') as file:
                    S.spell_data = json.load(file)
            if "saving throw" in S.spell_data[hovering_mouse[0]]["Description_for_dummies"]:
                description_words = S.spell_data[hovering_mouse[0]]["Description_for_dummies"].split(" ")
                for i in range(0, len(description_words)-1):
                    description_words[i+1] = description_words[i+1].replace(",", "")
                    if description_words[i] == "saving" and description_words[i + 1] == "throw":
                        # Check if the word before "saving throw" is in the list of valid options
                        if description_words[i - 1] in V.Ability_score_list:
                            S.spell_data[hovering_mouse[0]]["Saving Throw"] = description_words[i - 1]
                            break

            data_dict = S.spell_data.copy()

        elif hovering_mouse[3] in ["Feature", "Feat", "Eldritch Invocations", "Spell_slot"]:
            data_dict = S.Class_features.copy()
            properties = ["Action_Type", "Choice"]

        elif hovering_mouse[3] in ["Ability", "Beast_Weapon"]:
            properties = []
            data_dict = copy.deepcopy(S.mob_abilities)
            mob_name = hovering_mouse[4]
            change_dict = data_dict[hovering_mouse[0]][mob_name]
            for key, value in change_dict.items():
                if key.isupper():
                    data_dict[hovering_mouse[0]]["Description"] = data_dict[hovering_mouse[0]]["Description"].replace("*" + key + "*", value)
            data_dict[hovering_mouse[0]]["Description"] = data_dict[hovering_mouse[0]]["Description"].replace("*", "")

        elif "Sub_Feature" in hovering_mouse[3]:
            sub_key = hovering_mouse[3].split(":")[1]
            data_dict = S.Class_features[sub_key].copy()
            properties = ["Action_Type"]
        for prop in properties:
            """Iterate through each property checking if the property exists, if it does display it"""
            if data_dict[hovering_mouse[0]].get(prop) != None:
                if prop in ["Saving Throw"]:
                    color = "red"
                else:
                    color = "black"
                if prop in ["Components"]:
                    if len(prop + ": " + data_dict[hovering_mouse[0]][prop]) > 40:
                        letter_count = 0
                        text_to_print = prop + ": " + data_dict[hovering_mouse[0]][prop]
                        for i in range(1, int(len(prop + ": " + data_dict[hovering_mouse[0]][prop]) / 40)+2):
                            F.display_text(temp_surface, text_to_print[letter_count:i*40], 10,(mini_window_w * 0.02, mini_window_h * 0.15 + step_y + scroll), color=color)
                            step_y += mini_window_h * 0.1
                            letter_count += 40
                        continue

                F.display_text(temp_surface, prop + ": " + data_dict[hovering_mouse[0]][prop], 10,(mini_window_w * 0.02, mini_window_h * 0.15 + step_y + scroll), color=color)
                step_y += mini_window_h * 0.1
            elif prop == "Choice" and hovering_mouse[3] in ["Feature"]:
                if "Special_Flag" in data_dict[hovering_mouse[0]]:
                    if isinstance(data_dict[hovering_mouse[0]]["Special_Flag"], list) and "CHOOSE" in data_dict[hovering_mouse[0]]["Special_Flag"][0]:
                        if V.char_config.get("Choises") != None and V.char_config["Choises"].get(hovering_mouse[0]) != None:
                            F.display_text(temp_surface, prop + ": " + str(V.char_config["Choises"][hovering_mouse[0]]), 10, (mini_window_w * 0.02, mini_window_h * 0.15 + step_y + scroll))
                            step_y += mini_window_h * 0.1

        r = pg.Rect(0, 0, 0, 0) # initialise the rect used by weapons that do not have a description (eg arrows)
        if data_dict[hovering_mouse[0]].get(mode) != None and hovering_mouse[3] == "Weapon":
            """Display the description for weapons"""

            r = F.display_text(temp_surface, title, 10, (mini_window_w * 0.02, mini_window_h * 0.15 + step_y + scroll))
            for word in data_dict[hovering_mouse[0]][mode].split(" "):
                r = F.display_text(temp_surface, word + " ", 10, (r.x + r.w, mini_window_h * 0.15 + step_y + scroll))
                if r.x + r.w >= mini_window_w * 0.85:
                    r.w = 0
                    r.x = mini_window_w * 0.02
                    step_y += mini_window_h * 0.1
        elif data_dict[hovering_mouse[0]].get(mode) != None and hovering_mouse[3] in ["Spell", "Cantrip", "Feature", "Feat", "Eldritch Invocations", "Spell_slot", "Free Spell"] or data_dict[hovering_mouse[0]].get(mode) != None and "Sub_Feature:" in hovering_mouse[3]:
            """Display the description for spells"""
            r = F.display_text(temp_surface, title, 10, (mini_window_w * 0.02, mini_window_h * 0.15 + step_y + scroll))
            if isinstance(data_dict[hovering_mouse[0]][mode], list):
                data_dict[hovering_mouse[0]][mode] = data_dict[hovering_mouse[0]][mode][0]
            data_dict[hovering_mouse[0]][mode] = data_dict[hovering_mouse[0]][mode].replace("\n\n", " *** ")
            data_dict[hovering_mouse[0]][mode] = data_dict[hovering_mouse[0]][mode].replace("\n", " *** ")
            for word in data_dict[hovering_mouse[0]][mode].split(" "):
                word = word.replace("â€™", "'")
                word = word.replace("â€“", "-")
                if word == "***":
                    step_y += mini_window_h * 0.1
                    r.w = 0
                    r.x = mini_window_w * 0.02
                    continue

                r = F.display_text(temp_surface, word + " ", 10, (r.x + r.w, mini_window_h * 0.15 + step_y + scroll))
                if r.x + r.w >= mini_window_w * 0.85:
                    r.w = 0
                    r.x = mini_window_w * 0.02
                    step_y += mini_window_h * 0.1
        elif data_dict[hovering_mouse[0]].get(mode) != None and hovering_mouse[3] in ["Feature", "Eldritch Invocations", "Spell_slot"]:
            """Display the description for features"""
            r = F.display_text(temp_surface, title, 10, (mini_window_w * 0.02, mini_window_h * 0.15 + step_y + scroll))

            data_dict[hovering_mouse[0]][mode] = data_dict[hovering_mouse[0]][mode].replace("\n\n", " *** ")
            data_dict[hovering_mouse[0]][mode] = data_dict[hovering_mouse[0]][mode].replace("\n", " *** ")

            for word in data_dict[hovering_mouse[0]][mode][0].split(" "):

                if word == "***":
                    step_y += mini_window_h * 0.1
                    r.w = 0
                    r.x = mini_window_w * 0.02
                    continue

                r = F.display_text(temp_surface, word + " ", 10, (r.x + r.w, mini_window_h * 0.15 + step_y + scroll))
                if r.x + r.w >= mini_window_w * 0.85:
                    r.w = 0
                    r.x = mini_window_w * 0.02
                    step_y += mini_window_h * 0.1
        elif data_dict[hovering_mouse[0]].get(mode) != None and hovering_mouse[3] in ["Ability", "Beast_Weapon"]:
            """Display the description for features"""
            r = F.display_text(temp_surface, title, 10, (mini_window_w * 0.02, mini_window_h * 0.15 + step_y + scroll))
            for word in data_dict[hovering_mouse[0]][mode].split(" "):
                r = F.display_text(temp_surface, word + " ", 10, (r.x + r.w, mini_window_h * 0.15 + step_y + scroll))
                if r.x + r.w >= mini_window_w * 0.85:
                    r.w = 0
                    r.x = mini_window_w * 0.02
                    step_y += mini_window_h * 0.1

        if r.y + r.h > mini_window_h:
            """if the window is small, expand it"""
            text_surface_enlarged = pg.Surface((mini_window_w * 1.05, r.y + r.h + mini_window_h*0.05), pg.SRCALPHA)
            F.add_image_to_screen(text_surface_enlarged, "background", (0, 0, mini_window_w * 1.05, r.y + r.h + mini_window_h*0.05), "Background")
            pg.draw.rect(text_surface_enlarged, "black", pg.Rect(0, 0, mini_window_w * 1.05, r.y + r.h + mini_window_h*0.05), width=2)
            text_surface_enlarged.blit(temp_surface, (0, 0))
            return text_surface_enlarged

        text_surface.blit(temp_surface, (0, 0))
    return text_surface

def display_actions(screen, weapon_list, ammo_count, cantrip_list, spell_list, unknown_list, feat_list, free_spell_list, scroll):
    screen, weapon_screen, spell_screen, feature_screen = screen
    displayed_rects, start_y = display_weapons(weapon_screen, weapon_list, ammo_count, scroll[0])
    displayed_rects.update(display_spells(spell_screen, cantrip_list, spell_list, free_spell_list, scroll[1]))
    displayed_rects.update(display_features(feature_screen, unknown_list, feat_list, scroll[2]))
    return displayed_rects

def display_weapons(screen, weapon_list, ammo_count, scroll):
    character = V.character_dict[V.char_name]
    F.display_text(screen, "Weapons", 30, (S.SCREEN_WIDTH * 0.01, S.SCREEN_HEIGHT * 0.01 + scroll))

    if "Unarmed Strike" not in character["Weapon Proficiencies"]:
        character["Weapon Proficiencies"] += ",Unarmed Strike"

    melee_weapon_list = ["Light", "Heavy", "Reach", "Thrown", "Versatile"]
    ranged_weapon_list = ["Loading", "Range", "Ammo"]
    start_X = S.SCREEN_WIDTH * 0.02
    start_y = S.SCREEN_HEIGHT * 0.06 + scroll
    step_y = 0
    tab = S.SCREEN_WIDTH * 0.01
    displayed_rects = {}
    for weapon in weapon_list:
        damage_type1 = 0
        damage_type2 = 0
        info_rect = F.display_text(screen, weapon, 15, (start_X, start_y + step_y))
        if weapon not in list(displayed_rects.keys()):
            displayed_rects[weapon] = {"Info": info_rect, "Type": "Weapon"}
        step_y += S.SCREEN_HEIGHT * 0.031


        if V.item_dict[weapon].get("Extra") != None and V.item_dict[weapon].get("Properties") != None:
            if "Ammunition" in V.item_dict[weapon]["Properties"]:
                r = F.display_text(screen, "Amount: ", 15, (start_X + tab, start_y + step_y))
                F.display_text(screen,  str(ammo_count[weapon]), 15, (r.x + r.w, r.y))
                step_y += S.SCREEN_HEIGHT * 0.031
                continue
            multiplyer = is_weapon_proficient(weapon, character)

            if set(V.item_dict[weapon]["Properties"].split(",")) & set(ranged_weapon_list) and "Finesse" not in V.item_dict[weapon]["Properties"].split(","):
                """setting dex modifyer"""
                modifyer = int(V.score_modifiers["DEX"])
                mod_name = "DEX"
            elif set(V.item_dict[weapon]["Properties"].split(",")) & set(melee_weapon_list) and "Finesse" not in V.item_dict[weapon]["Properties"].split(","):
                """setting str modifyer"""
                modifyer = int(V.score_modifiers["STR"])
                mod_name = "STR"
            else:
                """its a finesse weapon, set the higher from str and dex"""
                modifyer = int(V.score_modifiers["STR"]) if int(V.score_modifiers["STR"]) > int(V.score_modifiers["DEX"]) else int(V.score_modifiers["DEX"])
                mod_name = "STR" if int(V.score_modifiers["STR"]) > int(V.score_modifiers["DEX"]) else "DEX"
            roll_modifyer = modifyer + multiplyer * V.Proficiecy_bonus

            if "+1" in weapon or " + " not in V.item_dict[weapon]["Extra"] and "+" in V.item_dict[weapon]["Extra"]:
                modifyer += 1
                roll_modifyer += 1

            roll_gap = " +"
            if roll_modifyer < 0:
                roll_gap = " "
            gap = " +"
            if modifyer < 0:
                gap = " "

            r = F.display_text(screen, "Hit: ", 15, (start_X + tab, start_y + step_y))
            r2 = F.display_text(screen, "1d20" + roll_gap + str(roll_modifyer), 15, (r.x + r.w, r.y))
            rect = r.union(r2)
            pg.draw.rect(screen, "black", rect, width=1)
            displayed_rects[weapon]["Hit"] = rect

            if "Thrown" in V.item_dict[weapon]["Properties"]:
                """add the amount of item next to the name"""
                amount = character["Items"].split(",").count(weapon)
                F.display_text(screen, " *" + str(amount), 15, (info_rect.x + info_rect.w, info_rect.y))

                """display throw rect"""
                rect = F.display_text(screen, "Throw", 15, (start_X + tab + rect.w * 1.05, start_y + step_y))
                pg.draw.rect(screen, "black", rect, width=1)
                displayed_rects[weapon]["Throw"] = rect

            step_y += S.SCREEN_HEIGHT * 0.031

            r = F.display_text(screen, "Damage: ", 15, (start_X + tab, start_y + step_y))
            if V.Special_Flags.get("Rage") != None:
                modifyer += int(character["Rage Damage"])
            if "d" not in V.item_dict[weapon]["Extra"].split(":")[0]:
                damage = int(V.item_dict[weapon]["Extra"].split(":")[0]) + int(modifyer)
                if damage <= 1:
                    damage = 1

                r2 = F.display_text(screen, str(damage), 15,(r.x + r.w, r.y))
            else:
                if " + " in V.item_dict[weapon]["Extra"]:
                    """Extra die"""
                    damage1, damage2 = V.item_dict[weapon]["Extra"].split(" + ")
                    damage1, damage_type1 = damage1.split(":")
                    damage2, damage_type2 = damage2.split(":")
                    r2 = F.display_text(screen, damage1 + gap + str(modifyer), 15,(r.x + r.w, r.y))

                    step_y += S.SCREEN_HEIGHT * 0.031
                    r3 = F.display_text(screen, "Damage: ", 15, (start_X + tab, start_y + step_y))
                    r4 = F.display_text(screen, damage2, 15, (r3.x + r3.w, r3.y))
                    rect = r3.union(r4)
                    pg.draw.rect(screen, "black", rect, width=1)
                    displayed_rects[weapon]["Damage_extra"] = rect
                elif "+" in V.item_dict[weapon]["Extra"]:
                    """Only bonus to attack e.g. Dragon Slayer"""
                    r2 = F.display_text(screen, str(V.item_dict[weapon]["Extra"].split("+")[0].split(":")[0]) + gap + str(modifyer), 15,(r.x + r.w, r.y))



                else:
                    r2 = F.display_text(screen,  V.item_dict[weapon]["Extra"].split(":")[0] + gap + str(modifyer), 15, (r.x + r.w, r.y))
            rect = r.union(r2)
            pg.draw.rect(screen, "black", rect, width=1)
            displayed_rects[weapon]["Damage"] = rect

            if "Versatile" in V.item_dict[weapon]["Properties"]:
                """display versatile rect"""
                rect = F.display_text(screen, "Two-handed", 15, (start_X + tab + rect.w * 1.05, start_y + step_y))
                pg.draw.rect(screen, "black", rect, width=1)
                property_index = V.item_dict[weapon]["Properties"].find("Versatile")
                property = V.item_dict[weapon]["Properties"][property_index:].replace("Versatile(", "").replace(")", "").split(",")[0]
                """Extract the hit dice of the versatile weapon"""
                displayed_rects[weapon]["Versatile"] = rect
                displayed_rects[weapon]["Versatile_dice"] = property

            step_y += S.SCREEN_HEIGHT * 0.031

            if damage_type1 != 0 and damage_type2 != 0:
                r = F.display_text(screen, "Type: ", 15, (start_X + tab, start_y + step_y))
                r = F.display_text(screen, V.item_dict[weapon]["Extra"].split(" + ")[0].split(":")[1] + ", ", 15, (r.x + r.w, r.y))
                F.display_text(screen, V.item_dict[weapon]["Extra"].split(" + ")[1].split(":")[1], 15, (r.x + r.w, r.y))
                step_y += S.SCREEN_HEIGHT * 0.031
            else:
                r = F.display_text(screen, "Type: ", 15, (start_X + tab, start_y + step_y))
                F.display_text(screen, V.item_dict[weapon]["Extra"].split(":")[1], 15, (r.x + r.w, r.y))
                step_y += S.SCREEN_HEIGHT * 0.031

            if weapon in list(V.Rites.values()):
                rite_id = list(V.Rites.values()).index(weapon)
                rite_name = list(V.Rites.keys())[rite_id]
                rite_rect = F.display_text(screen, rite_name, 15, (start_X + tab, start_y + step_y))
                pg.draw.rect(screen, "black", rite_rect, width=1)
                displayed_rects[weapon]["Rite"] = rite_rect
                displayed_rects[weapon]["Rite_name"] = rite_name
                step_y += S.SCREEN_HEIGHT * 0.031

                # F.add_image_to_screen(screen, rite_name,, "rite")


            displayed_rects[weapon]["Roll_mod"] = roll_modifyer
            displayed_rects[weapon]["Mod_Name"] = mod_name
            displayed_rects[weapon]["Damage_mod"] = modifyer
            if " + " in V.item_dict[weapon]["Extra"]:
                displayed_rects[weapon]["Damage_Die"] = V.item_dict[weapon]["Extra"].split(" + ")[0].split(":")[0]
                displayed_rects[weapon]["Damage_Die_extra"] = V.item_dict[weapon]["Extra"].split(" + ")[1].split(":")[0]
                displayed_rects[weapon]["Damage_mod_extra"] = 0
            elif "+" in V.item_dict[weapon]["Extra"]:
                displayed_rects[weapon]["Damage_Die"] = V.item_dict[weapon]["Extra"].split("+")[0].split(":")[0]
            else:
                displayed_rects[weapon]["Damage_Die"] = V.item_dict[weapon]["Extra"].split(":")[0]



    return displayed_rects, start_y

def display_spells(screen, cantrip_list, spell_list, free_spell_list, scroll):
    start_y = S.SCREEN_HEIGHT * 0.01 + scroll
    if cantrip_list != []:
        F.display_text(screen, "Cantrips", 25, (S.SCREEN_WIDTH * 0.3, S.SCREEN_HEIGHT * 0.01 + scroll))
        start_y = S.SCREEN_HEIGHT * 0.06 + scroll
    character = V.character_dict[V.char_name]
    start_X = S.SCREEN_WIDTH * 0.31

    step_y = 0
    tab = S.SCREEN_WIDTH * 0.01
    displayed_rects = {}
    if V.SECRETS.get(V.char_name) != None and V.SECRETS[V.char_name]["Spells"]:
        return displayed_rects

    for cantrip in cantrip_list:
        modifyer = 0
        if "reaction" in S.cantrip_data[cantrip]["Casting Time"].lower():
            color = "Red"
        elif "bonus action" in S.cantrip_data[cantrip]["Casting Time"].lower():
            color = "Navy"
        else:
            color = "Black"
        rect_info = F.display_text(screen, cantrip, 15, (start_X, start_y + step_y), color=color)

        if cantrip not in list(displayed_rects.keys()):
            displayed_rects[cantrip] = {"Info": rect_info, "Type": "Cantrip"}

        if S.cantrip_data[cantrip].get("Type") != None:
            """If Type exists it is a rolling dice spell"""
            if "spellcasting ability modifier" in S.cantrip_data[cantrip]["Damage"]:
                modifyer = V.spellcasting_ability_mod

            if S.cantrip_data[cantrip]["Attack"] in ["Ranged Spell Attack", "Melee Spell Attack"]:
                """Roll to hit"""
                step_y += S.SCREEN_HEIGHT * 0.031
                displayed_rects[cantrip]["Roll_mod"] = V.Spell_attack
                rect_hit = F.display_text(screen, "Hit: 1d20 + " + str(V.Spell_attack), 15, (start_X + tab, start_y + step_y))
                pg.draw.rect(screen, "black", rect_hit, width=1)
                displayed_rects[cantrip]["Hit"] = rect_hit

            """Roll Damage"""
            step_y += S.SCREEN_HEIGHT * 0.031
            spell_damage1 = S.cantrip_data[cantrip]["Damage"].replace("+spellcasting ability modifier", "+" + str(V.spellcasting_ability_mod))
            spell_damage = update_cantrip_spell_damage(spell_damage1, cantrip)
            rect_damage = F.display_text(screen, "Damage: " + str(spell_damage), 15, (start_X + tab, start_y + step_y))
            pg.draw.rect(screen, "black", rect_damage, width=1)
            displayed_rects[cantrip]["Damage"] = rect_damage
            displayed_rects[cantrip]["Damage_mod"] = modifyer
            displayed_rects[cantrip]["Damage_Die"] = spell_damage.split("+")[0]

            step_y += S.SCREEN_HEIGHT * 0.031
            F.display_text(screen, "Type: " + S.cantrip_data[cantrip]["Type"], 15, (start_X + tab, start_y + step_y))
        else:
            step_y += S.SCREEN_HEIGHT * 0.031
            rect_hit = F.display_text(screen, "Cast", 15, (start_X + tab, start_y + step_y))
            pg.draw.rect(screen, "black", rect_hit, width=1)
            displayed_rects[cantrip]["Cast"] = rect_hit

        step_y += S.SCREEN_HEIGHT * 0.031

    max_spell_level = 0
    classes = V.character_dict[V.char_name]["Class"].split(", ")
    levels = V.character_dict[V.char_name]["Level"].split(",")
    for i in range(len(classes)):
        if V.Available_spells_data.get(classes[i]) != None:
            max_spell_level = V.Available_spells_data[classes[i]][int(levels[i])][4] + 1

    for i in range(1, max_spell_level):
        F.display_text(screen, "Level " + str(i) + " Spells", 25, (S.SCREEN_WIDTH * 0.3, start_y + step_y))
        step_y += S.SCREEN_HEIGHT * 0.045
        for spell in spell_list:
            if spell == "":
                continue
            spell_level = S.spell_data[spell]["Level"]
            if spell_level == str(i) or S.spell_data[spell].get("At higher levels") != None and int(spell_level) < i:
                start_y, step_y = display_single_spell(screen, spell, start_X, start_y, step_y, displayed_rects, tab, i)

    if free_spell_list != []:
        F.display_text(screen, "Feature Spells", 25, (S.SCREEN_WIDTH * 0.3, start_y + step_y))
        step_y += S.SCREEN_HEIGHT * 0.045

        for free_spell in free_spell_list:
            rect_info = F.display_text(screen, free_spell, 15, (start_X, start_y + step_y))
            if free_spell not in list(displayed_rects.keys()):
                displayed_rects[free_spell] = {"Info": rect_info, "Type": "Free Spell"}

            if S.spell_data[free_spell].get("Type") != None:
                if S.spell_data[free_spell]["Attack"] in ["Ranged Spell Attack", "Melee Spell Attack"]:
                    step_y += S.SCREEN_HEIGHT * 0.031
                    rect_hit = F.display_text(screen, "Hit: 1d20", 15, (start_X + tab, start_y + step_y))
                    pg.draw.rect(screen, "black", rect_hit, width=1)
                    displayed_rects[free_spell]["Hit"] = rect_hit
                    displayed_rects[free_spell]["Roll_mod"] = V.Spell_attack
                elif S.spell_data[free_spell]["Attack"] in ["Melee weapon effect"]:
                    melee_weapon_effect = True # or whatever

                step_y += S.SCREEN_HEIGHT * 0.031
                rect_damage = F.display_text(screen, "Damage: " + S.spell_data[free_spell]["Damage"], 15, (start_X + tab, start_y + step_y))
                pg.draw.rect(screen, "black", rect_damage, width=1)
                displayed_rects[free_spell]["Damage"] = rect_damage
                displayed_rects[free_spell]["Damage_mod"] = 0
                displayed_rects[free_spell]["Damage_Die"] = S.spell_data[free_spell]["Damage"]

                step_y += S.SCREEN_HEIGHT * 0.031
                F.display_text(screen, "Type: " + S.spell_data[free_spell]["Type"], 15, (start_X + tab, start_y + step_y))

            else:
                step_y += S.SCREEN_HEIGHT * 0.031
                rect_hit = F.display_text(screen, "Cast", 15, (start_X + tab, start_y + step_y))
                pg.draw.rect(screen, "black", rect_hit, width=1)
                displayed_rects[free_spell]["Cast"] = rect_hit

            step_y += S.SCREEN_HEIGHT * 0.031

    return displayed_rects

def display_features(screen, unknown_list, feat_list, scroll):
    F.display_text(screen, "Features", 30, (S.SCREEN_WIDTH * 0.55, S.SCREEN_HEIGHT * 0.01 + scroll))
    character = V.character_dict[V.char_name]
    start_X = S.SCREEN_WIDTH * 0.57
    start_y = S.SCREEN_HEIGHT * 0.06 + scroll
    step_y = 0
    tab = S.SCREEN_WIDTH * 0.01
    displayed_rects = {}
    for feat in feat_list:
        rect_info = F.display_text(screen, feat, 15, (start_X, start_y + step_y))

        if feat not in list(displayed_rects.keys()):
            displayed_rects[feat] = {"Info": rect_info, "Type": "Feat"}

        step_y += S.SCREEN_HEIGHT * 0.031

    if V.SECRETS.get(V.char_name) != None and V.SECRETS[V.char_name]["Features"]:
        return displayed_rects

    for feature in unknown_list:
        action, name = feature.split(":")

        if action == "Sub_Feature":
            sub_key, name = name.split("_")
            rect_info = F.display_text(screen, name, 15, (start_X, start_y + step_y))
            displayed_rects[name] = {"Info": rect_info, "Type": "Sub_Feature:" + sub_key, "Action": action}
            step_y += S.SCREEN_HEIGHT * 0.031
            if S.Class_features[sub_key][name].get("Action_Type") != None:
                if S.Class_features[sub_key][name]["Action_Type"] == "Changed_Spell_Slot":
                    r = F.display_text(screen, "Cast", 15, (start_X + tab, start_y + step_y))
                    step_y += S.SCREEN_HEIGHT * 0.031
                    pg.draw.rect(screen, "black", r, width=1)
                    displayed_rects[name]["Sub_Feature_Spell_slot"] = r

            continue
        rect_info = F.display_text(screen, name, 15, (start_X, start_y + step_y))
        if name not in list(displayed_rects.keys()) and action in ["Eldritch Invocations", "Spell_slot"]:
            displayed_rects[name] = {"Info": rect_info, "Type": action, "Action": action}
        elif name not in list(displayed_rects.keys()) and name in ["Ranger's Companion"]:
            displayed_rects[name] = {"Info": rect_info, "Type": "Feature", "Action": "Use"}
            step_y += S.SCREEN_HEIGHT * 0.031
            r = F.display_text(screen, "Cast", 15, (start_X + tab, start_y + step_y))
            pg.draw.rect(screen, "black", r, width=1)
            displayed_rects[name]["Use"] = r
        elif name not in list(displayed_rects.keys()):
            displayed_rects[name] = {"Info": rect_info, "Type": "Feature", "Action": action}



        if "Damage" in S.Class_features[name]:
            displayed_rects[name]["Damage_Die"] = S.Class_features[name]["Damage"]
            if S.Class_features[name]["Damage"] == "Char_dict":
                displayed_rects[name]["Damage_Die"] = character[name]
                displayed_rects[name]["Damage_mod"] = 0

            step_y += S.SCREEN_HEIGHT * 0.031
            r = F.display_text(screen, "Damage: ", 15, (start_X + tab, start_y + step_y))
            r2 = F.display_text(screen, displayed_rects[name]["Damage_Die"], 15, (r.x + r.w, r.y))
            rect = r.union(r2)
            pg.draw.rect(screen, "black", rect, width=1)
            displayed_rects[name]["Damage"] = rect

        if "Spell_slot" in S.Class_features[name]:
            step_y += S.SCREEN_HEIGHT * 0.031
            r = F.display_text(screen, "Cast", 15, (start_X + tab, start_y + step_y))
            pg.draw.rect(screen, "black", r, width=1)
            displayed_rects[name]["Spell_slot"] = r
            if "Dice" in S.Class_features[name]:
                displayed_rects[name]["Dice"] = S.Class_features[name]["Dice"]
        if "Change" in S.Class_features[name]:
            step_y += S.SCREEN_HEIGHT * 0.031
            r = F.display_text(screen, "Cast", 15, (start_X + tab, start_y + step_y))
            pg.draw.rect(screen, "black", r, width=1)
            displayed_rects[name]["Spell_slot"] = r
            if "Dice" in S.Class_features[name]:
                displayed_rects[name]["Dice"] = S.Class_features[name]["Dice"]

        step_y += S.SCREEN_HEIGHT * 0.031

    return displayed_rects

def is_weapon_proficient(weapon, character):
    weapon_profciencies = character["Weapon Proficiencies"].split(",")
    if weapon in weapon_profciencies:
        return 1
    else:
        properties = V.item_dict[weapon]["Properties"]
        if set(properties.split(",")) & set(weapon_profciencies):
            return 1
    return 0

def draw_action_grid(screen):
    spell_start_x = S.SCREEN_WIDTH * 0.29
    button_start_y = S.SCREEN_HEIGHT * 0.85
    spell_width = S.SCREEN_WIDTH * 0.25
    feature_start = spell_start_x + spell_width
    feature_width = S.SCREEN_WIDTH * 0.25
    comments_start = feature_start + feature_width
    comments_height = S.SCREEN_HEIGHT * 0.2
    """Weapon Grid"""
    pg.draw.rect(screen, "black", pg.Rect(0, 0, spell_start_x, button_start_y), width=1)
    """Spell Grid"""
    pg.draw.rect(screen, "black", pg.Rect(spell_start_x, 0, spell_width, button_start_y), width=1)
    """Feature Grid"""
    pg.draw.rect(screen, "black", pg.Rect(feature_start, 0, feature_width, button_start_y), width=1)
    """Comments Grid"""
    pg.draw.rect(screen, "black", pg.Rect(comments_start, 0, S.SCREEN_WIDTH - comments_start, comments_height), width=1)
    """Spell Slot Grid"""
    pg.draw.rect(screen, "black", pg.Rect(comments_start, comments_height, S.SCREEN_WIDTH - comments_start, button_start_y - comments_height), width=1)
    """Button Grid"""
    pg.draw.rect(screen, "black", pg.Rect(0, button_start_y, S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 0.15), width=1)

def handle_Consentration(screen, button_dict):
    if V.consentration != {}:
        if isinstance(V.consentration, str):
            spell_name = V.consentration.split(":")[0]
            concentration_type = V.consentration.split(":")[1]
            delay = V.consentration.split(":")[2]
            F.display_text(screen, "Concentration broken on the " + spell_name + " " + concentration_type, 15,
                           (S.SCREEN_WIDTH * 0.84, S.SCREEN_HEIGHT * 0.18), case="C")
            delay = str(int(delay) - 1)
            V.consentration = spell_name + ":" + concentration_type + ":" + delay
            if int(delay) <= 0:
                V.consentration = {}
        else:
            if len(list(V.consentration.keys())) > 1:
                to_remove = []
                time_at = 1e100
                for spell_name, value in V.consentration.items():
                    if value[1] < time_at:
                        time_at = value[1]
                        to_remove = [spell_name, value[0]]
                del V.consentration[to_remove[0]]
            F.display_text(screen, "Concentration on the " + str(list(V.consentration.keys())[0]) + " " + str(list(V.consentration.values())[0][0]), 15, (S.SCREEN_WIDTH * 0.84, S.SCREEN_HEIGHT * 0.18), case="C")
            button_dict[(1, 0)] = ["End Concentration", "background", "background", "rect-place-holder", "black"]
    return button_dict

def handle_heavy_weapon_disadvantage(screen, clock, pressed, character):
    """check if weapon is heavy and if race is small."""
    first_roll = -1
    disadvantage = False
    if V.item_dict.get(pressed[1]) and "Heavy" in V.item_dict[pressed[1]]["Properties"]:
        race = character["Race"]
        size = V.race_size[race]
        size_int = V.race_size_to_int[size]
        if "Powerful Build" in character["Code"]:
            size_int += 1
        if size_int == 1:   # Small
            disadvantage = True
    return disadvantage

def handle_critical_fail_success_colors(dtwenty):
    if dtwenty == 1:
        dice_color = "black"
        critical_fail = True
        return dice_color, critical_fail, False
    elif dtwenty == 20:
        dice_color = "Purple"
        critical_success = True
        return dice_color, False, critical_success
    elif dtwenty == 19 and V.character_dict[V.char_name]:
        dice_color = "Purple"
        critical_success = True
        return dice_color, False, critical_success
    else:
        dice_color = "Dark Green"
        return dice_color, False, False

def handle_component_checks(spell_tracker, rect_dict, pressed):
    """checking if material components are used in the spell"""
    """First check if this is a cantrip or spell"""
    spell_name = pressed[1]
    # if ":" in pressed[1]:
    #     spell_name, casting_level = pressed[1].split(":")

    if rect_dict[spell_name]["Type"] in ["Cantrip", "Spell"]:
        """Then find out which data to use, cantrip or spell?"""
        if S.cantrip_data.get(spell_name) != None:
            """This was a cantrip"""
            data_to_check = S.cantrip_data
        else:
            """This is a spell"""
            data_to_check = S.spell_data
        """Third: check if there are material components here"""
        if ":" in pressed[1]:
            spell_name, casting_level = pressed[1].split(":")
        if data_to_check[spell_name].get("Material") != None:
            """Found it"""
            components = data_to_check[spell_name]["Material"]
            if components[-1] == "True":
                """Spellcasting focus can be used, find it in items"""
                spellcasting_focus_exists = search_for_spellcasting_focus()

                if spellcasting_focus_exists:
                    return True, "Spellcasting_Focus"
                else:
                    """You dont have a spellcasting focus maybe materials?"""
                    component = search_for_components(components, pressed, spell_tracker)
                    return component[0], component[1]
            else:
                """Spellcast focus cant be used. use materials"""
                component = search_for_components(components, pressed, spell_tracker)
                return component[0], component[1]

    """is not a spell/cantrip, spell/cantrip doesn't have materials, spell/cantrip material consumed"""
    return True, "-"

def search_for_components(components, pressed, spell_tracker):
    spell_name = pressed[1]
    if "--" in components[0]:
        """This component is not as simple check if cost exists, then cant use spellcasting focus"""
        component_data = components[0].split(":")
        if component_data[0].replace("--", "").lower() in ["weapon"]:
            """component is a weapon"""
            if component_data[1].upper() == "COST":
                """Checking component cost"""
                if component_data[2].upper() == "GREATER":
                    """weapon cost must be greater than 3rd value"""
                    if V.EQUIPED_CHAR_ITEMS != {}:
                        if V.EQUIPED_CHAR_ITEMS.get("Magic Weapon") != None or V.EQUIPED_CHAR_ITEMS.get("Weapons") != None:
                            weapons = []
                            if V.EQUIPED_CHAR_ITEMS.get("Magic Weapon") != None:
                                weapons = V.EQUIPED_CHAR_ITEMS["Magic Weapon"].split(",")
                            if V.EQUIPED_CHAR_ITEMS.get("Weapons") != None:
                                weapons += V.EQUIPED_CHAR_ITEMS["Weapons"].split(",")
                            for weapon in weapons:
                                if weapon == "":
                                    continue
                                if float(V.item_dict[weapon]["Cost"]) >= float(component_data[3]):
                                    return True, weapon
                            return False, "Equip weapon with a greater cost than " + str(component_data[3])
                        else:
                            return False, "Equip weapon with a greater cost than " + str(component_data[3])
                    else:
                        return False, "Equip weapon with a greater cost than " + str(component_data[3])
                else:
                    F.print_debug("ERROR NOT GREATER COMPONENT", component_data[2], "ERROR")
            else:
                F.print_debug("ERROR NOT COST COMPONENT", component_data[1], "ERROR")
        else:
            F.print_debug("ERROR NOT in weapon COMPONENT", component_data[0], "ERROR")

    # elif len(components) > 2:             # Handles where there are more than one component, currently disabled because only the spell "Darkness" had more than one component
    #     passes = 0
    #     for component in components:
    #         if component in V.character_dict[V.char_name]["Items"]:
    #             passes += 1
    #     if len(components) - 1 == passes:
    #         """minus one cuz the last says if item is consumed or not"""
    #         F.print_debug("IDK BOSS HELP COMPONETS", [components, pressed], "ERROR")
    #         return components
    else:
        if components[0] in V.character_dict[V.char_name]["Items"]:
            """Component exists, maybe remove it from the character"""
            """now check if this spell/cantrip uses "HIT" first and "DAMAGE" second, for that use the spell_tracker dict"""
            if pressed[0] == "Hit":
                """if spell has "HIT" then track it"""
                spell_tracker[spell_name] = pressed[0]
            if spell_tracker.get(spell_name) != None and spell_tracker[spell_name] != pressed[0]:
                """If spell is written in the tracker, but type doesnt match. means item was already removed"""
                del spell_tracker[spell_name]
                """dont need to consume material again."""
                return True, components[0]
            """cant remove material now, need to see if spell slots are available."""
            return True, components[0]

        else:
            """didin't have material"""
            return False, components[0]

def search_for_spellcasting_focus():
    if V.character_dict[V.char_name].get("Items") != None:
        for item_name in V.character_dict[V.char_name]["Items"].split(","):
            if item_name == "" or item_name == "None":
                continue
            if "Spellcasting_Focus" in V.item_dict[item_name]["Properties"]:
                return True
    return False

def handle_spell_effects(spell_name, type):
    if type in ["Cantrip", "Spell", "Free Spell"]:
        if type == "Cantrip":
            spell_data = S.cantrip_data[spell_name].copy()
        else:
            spell_name, casting_level = spell_name.split(":")
            spell_data = S.spell_data[spell_name].copy()

        if spell_data.get("Effect") != None:
            """This spell has an effect and now we gonna use it"""
            effect = spell_data["Effect"].split(":")
            F.print_debug("What the f is this? ", [effect, spell_name, spell_data], "ERROR")
            if "Char" in effect[0]:
                char_property = effect[1]
                value = effect[2]
                if "+" in value and "MOD" in value:
                    add_1, add_2 = value.split("+")
                    modifyer = add_2.replace(" MOD", "")
                    add_2 = V.score_modifiers[modifyer]
                    value = int(add_1) + int(add_2)
                    if V.spell_effects.get("Char") == None:
                        V.spell_effects["Char"] = {}
                    V.spell_effects["Char"][char_property] = value
                elif char_property == "Items":
                    items = V.character_dict[V.char_name]["Items"].split(",")
                    for v in value.split(","):
                        items.append(v)
                    V.character_dict[V.char_name]["Items"] = ",".join(items)
                else:
                    F.print_debug("IM CONFUSED HELP ME MASTER at handle_spell_effects in Actions.py: ", value, debug="ERROR")
            else:
                F.print_debug("IM CONFUSED HELP ME MASTER at handle_spell_effects in Actions.py: ", effect, debug="ERROR")

def get_cantrips_from_subclass_entry(subclass_data, screen, clock, extra_action, extra_action_extended=None, mode="Cantrip"):
    result = []
    if subclass_data[0] == "ADD":
        """In SUbclass_data there should be a list first word a command, second word amount, third and so on data"""
        amount = int(subclass_data[1])
        if "{" not in subclass_data[2]:
            named_spells = subclass_data[2:]
            for spell_or_cantrip_name in named_spells:
                result.append(spell_or_cantrip_name)
                char_cantrips = V.character_dict[V.char_name][mode].split(",")
                if char_cantrips == ['']:
                    char_cantrips = []
                if spell_or_cantrip_name not in char_cantrips:
                    char_cantrips.append(spell_or_cantrip_name)
                    V.character_dict[V.char_name][mode] = ",".join(char_cantrips)
        else:

            location = {
                'subclass': S.subclass_data,
                'eldritch_invocations': S.eldritch_incantations,
                'races': S.Race_data,
                'classes': S.class_data,
                'class_features': S.Class_features,
                'spells': S.spell_data,
                'cantrips': S.cantrip_data
            }
            data_to_unpack = subclass_data[2].strip("{").strip("}")
            data_to_unpack = data_to_unpack.split("|")
            if data_to_unpack[0] == "CHOSEN":
                with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
                    char_config_data = json.load(file)
                if char_config_data["Choises"].get(data_to_unpack[1]) != None:
                    data_chosen = char_config_data["Choises"][data_to_unpack[1]]
                    for d in data_to_unpack[2].split(":"):
                        if d == "x":
                            d = data_chosen
                        location = location[d]
                    """location at the end of the looping should become a list of spells or cantrips variable mode decides if its a spell or a cantrip"""
                    for spell_or_cantrip_name in location:
                        result.append(spell_or_cantrip_name)
                        char_cantrips = V.character_dict[V.char_name][mode].split(",")
                        if spell_or_cantrip_name not in char_cantrips:
                            char_cantrips.append(spell_or_cantrip_name)
                            V.character_dict[V.char_name][mode] = ",".join(char_cantrips)




            else:
                F.print_debug("I DONT KNOW BOSS FIRST WORD IS NOT CHOSEN", data_to_unpack, debug="ERROR")

    elif subclass_data[0] == "CHOOSE":
        choise_made = F.check_if_choise_was_already_made(extra_action)
        if not choise_made:
            res = make_a_choise(subclass_data, screen, clock, extra_action)
            F.save_choise_json(extra_action, res)
            result = [res]
            char_cantrips = V.character_dict[V.char_name][mode].split(",")
            char_cantrips.append(res)
            V.character_dict[V.char_name][mode] = ",".join(char_cantrips)
        else:
            result = [choise_made]
            char_cantrips = V.character_dict[V.char_name][mode].split(",")
            if choise_made not in char_cantrips:
                char_cantrips.append(choise_made)
                V.character_dict[V.char_name][mode] = ",".join(char_cantrips)
    updated_result = []
    for s in result:
        if s not in V.character_dict[V.char_name][mode]:
            updated_result.append(s)

    return updated_result

def handle_slot_commands_from_subclass_json(subclass_data, feature_name):
    result = []
    """in subclass_data there is a list first word dictates if this is a command or not"""
    if subclass_data[0] == "COMMAND":
        """second word should be "Char" or something else but basicly a variable"""
        if subclass_data[1] == "Char":
            variable = V.character_dict[V.char_name].copy()
        elif subclass_data[1] in ["MODIFIER"]:
            pass
        else:
            """Some other variables"""
            F.print_debug("HELP CONFUSED, handle_slot_commands_from_subclass_json in Actions.py", debug="ERROR")
            variable = None

        if len(subclass_data) >= 4 and subclass_data[4] == "Level":
            """third member should be a key in the dict fourth member should be a value to look for in the previous class"""
            if subclass_data[2] == "Class":
                split = ", "
            else:
                split = ","
            """index only used if level is needed"""
            index = variable[subclass_data[2]].split(split).index(subclass_data[3])
            v = variable["Level"].split(",")[index]
            if "/" in subclass_data[5]:
                v = float(int(v) / int(subclass_data[5][1:]))
                v = math.floor(v)
            elif "+" in subclass_data[5]:
                v = int(v) + int(subclass_data[5][1:])
            elif "-" in subclass_data[5]:
                v = int(v) - int(subclass_data[5][1:])
                if v <= 0:
                    F.print_debug("v was less than 0 in handle_slot_commands_from_subclass_json :", subclass_data, debug="WARNING")
                    v = 1
        elif len(subclass_data) == 5 and subclass_data[1] == "MODIFIER":
            mod = subclass_data[2]
            m = subclass_data[3]
            value_to_math = subclass_data[4]
            if m == "+":
                mod = V.score_modifiers[mod]
                v = int(mod) + int(value_to_math)
            else:
                F.print_debug("HELP CONFUSED, handle_slot_commands_from_subclass_json in Actions.py 2", debug="ERROR")

        elif len(subclass_data) == 3:
            v = int(variable[subclass_data[2]])

    elif subclass_data[0] == "ADD":
        v = V.Proficiecy_bonus if subclass_data[1] == "Proficiency Bonus" else int(subclass_data[1])

    else:
        F.print_debug("I dont know, help boss with handle_slot_commands_from_subclass_json : ", subclass_data, debug="ERROR")
    result.append("Spell_slot:" + feature_name)
    V.spell_slots[feature_name] = v
    V.max_spell_slots[feature_name] = v
    return result

def make_a_choise(subclass_data, screen, clock, feature_name):
    running = True
    text_size = 30
    hovering_mouse = -1
    hovering_rect_dict = {}
    pressed = -1
    text_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 4), pg.SRCALPHA)
    selected_dropbox = -1
    text_scroll = 0
    amount = subclass_data[1]
    display_text = -1
    spell_shift = 0
    choise = None
    mode = "Description"
    values = []
    text = subclass_data[-1]
    if "{" in subclass_data[2]:
        if "CANTRIPS" in subclass_data[2]:
            for key, value in S.cantrip_data.items():
                if subclass_data[2].split(":")[1].replace("}", "") in value["Class"]:
                    values.append(key)

        elif "SPELLS" in subclass_data[2]:
            for key, value in S.spell_data.items():
                F.print_debug("In Actions.py:make_a_choise PLEASE FIX ME BOSS", value["Level"], debug="ERROR")

    else:
        values = subclass_data[2:-1]
    while running:

        mini_window_w = S.SCREEN_WIDTH * 0.3
        mini_window_h = S.SCREEN_HEIGHT * 0.3
        mini_surface = pg.Surface((mini_window_w, mini_window_h), pg.SRCALPHA)

        dropboxes = []
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Apply")


        for i in range(0, int(amount)):
            x = [S.SCREEN_WIDTH * 0.05]
            y = [S.SCREEN_WIDTH * 0.2]
            if i == selected_dropbox:
                rect = F.display_dropbox(screen, "Choose " + text, (x[i], y[0]), values, "open", choise,(S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.03))
            else:
                rect = F.display_dropbox(screen, "Choose " + text, (x[i], y[0]), values, "closed", choise,(S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.03))

            dropboxes.append(rect)

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
                        pressed = "Apply"
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                for i in range(0, len(dropboxes)):
                    if isinstance(dropboxes[i], pg.Rect) and dropboxes[i].collidepoint(mouse_pos):
                        pressed = i

            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                if selected_dropbox != -1:
                    selected_dropbox = -1
                if pressed != -1:
                    if pressed == "Apply":
                        return choise
                    selected_dropbox = pressed
                    pressed = -1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 4 or event.type == pg.KEYDOWN and event.key == pg.K_UP:
                """going up"""
                # values = F.enable_scrolling(values, -1)
                for _ in range((1)):
                    values = [values[-1]] + values[:-1]

                if selected_dropbox == -1:
                    text_scroll -= 10
                hovering_mouse = -1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5 or event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                """going down"""
                # values = F.enable_scrolling(values, 1)
                values = F.enable_scrolling(values, 1)

                if selected_dropbox == -1:
                    text_scroll += 10
                    if text_scroll >= 0:
                        text_scroll = 0
                hovering_mouse = -1
            elif event.type == pg.MOUSEMOTION:
                mouse_pos = pg.mouse.get_pos()
                if isinstance(dropboxes[selected_dropbox], dict):
                    for name, rect in dropboxes[selected_dropbox].items():
                        if isinstance(rect, pg.Rect):
                            if rect.collidepoint(mouse_pos):
                                hovering_mouse = [name, rect, text[2:]]
                                choise = name
                                break
                if hovering_rect_dict != {}:
                    for spell_cantrip_name, rect in hovering_rect_dict.items():
                        current_page = rect[1]
                        rect = rect[0]

                        if rect.collidepoint(mouse_pos) and current_page == hovering_mouse[0]:
                            if spell_cantrip_name in S.spell_data:
                                display_text = [spell_cantrip_name, "Info", rect, "Spell"]
                            elif spell_cantrip_name in S.cantrip_data:
                                display_text = [spell_cantrip_name, "Info", rect, "Cantrip"]
                            else:
                                display_text = -1



            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 2 or event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
                if mode == "Description":
                    mode = "Simple"
                elif mode == "Simple":
                    mode = "At Higher Levels"
                elif mode == "At Higher Levels":
                    mode = "Description"
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                spell_shift += 1
                if spell_shift > 1:
                    spell_shift = 0

        if hovering_mouse != -1 and selected_dropbox != -1:
            pg.draw.rect(screen, "light blue", hovering_mouse[1])
            F.display_text(screen, hovering_mouse[0], int(S.SCREEN_HEIGHT * 0.03 / 2.4),(hovering_mouse[1][0] + 5, hovering_mouse[1][1]))
            hovering_mouse[2] = hovering_mouse[2].capitalize()
            text_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 4), pg.SRCALPHA)

            if hovering_mouse[2] in "Subclass path":
                """Means that this is a subclass path choise, need to print out spells that can be aquired"""

                feature_data = S.subclass_data[feature_name[1]][feature_name[2]][feature_name[3]]

                F.display_text(text_surface, hovering_mouse[0], 20, (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.02))

                spells = feature_data["Outcome"][hovering_mouse[0]]
                # info = spells.split(" \n ")

                """print out text"""
                start_y = S.SCREEN_HEIGHT * 0.05
                start_x = S.SCREEN_WIDTH * 0.52
                step_y = S.SCREEN_HEIGHT * 0.02

                for level, spell_list in spells.items():
                    r = F.display_text(text_surface, "Level " + level + ": ", 15, (start_x, start_y + step_y))
                    start_x += r.w
                    for sp in spell_list:
                        r = F.display_text(text_surface, sp, 15, (start_x, start_y + step_y))
                        pg.draw.rect(text_surface, "black", r, width=1)
                        hovering_rect_dict[sp] = (r, hovering_mouse[0])
                        start_x += r.w
                        r = F.display_text(text_surface, ", ", 15, (start_x, start_y + step_y))
                        start_x += r.w
                    step_y += S.SCREEN_HEIGHT * 0.05
                    start_x = S.SCREEN_WIDTH * 0.52

            # for i in info:
                #     level, spell_data = i.split(": ")
                #     r = F.display_text(text_surface, level + ": ", 15, (start_x, start_y + step_y))
                #     start_x += r.w
                #
                #     r = F.display_text(text_surface, spell_data.split(", ")[0], 15, (start_x, start_y + step_y))
                #     pg.draw.rect(text_surface, "black", r, width=1)
                #     hovering_rect_dict[spell_data.split(", ")[0]] = r
                #     start_x += r.w
                #
                #     r = F.display_text(text_surface, ", ", 15, (start_x, start_y + step_y))
                #     start_x += r.w
                #
                #     r = F.display_text(text_surface, spell_data.split(", ")[1], 15, (start_x, start_y + step_y))
                #     hovering_rect_dict[spell_data.split(", ")[1]] = r
                #     pg.draw.rect(text_surface, "black", r, width=1)
                #     step_y += S.SCREEN_HEIGHT * 0.05
                #     start_x = S.SCREEN_WIDTH * 0.52
            else:
                F.display_text(text_surface, "Click Mouse Wheel to change description type", 15,(S.SCREEN_WIDTH * 0.75, S.SCREEN_HEIGHT * 0.03), case="C")
                Sp.display_only_spell_descriptions(text_surface, hovering_mouse, 0, mode)

        screen.blit(text_surface, (0, text_scroll))

        mini_surface = display_mini_screen(display_text, mini_window_w, mini_window_h, mini_surface)
        mouse_pos = pg.mouse.get_pos()
        if mouse_pos[1] <= S.SCREEN_HEIGHT * 0.85:
            screen.blit(mini_surface, mouse_pos)


        pg.display.flip()
        clock.tick(60)

def check_if_two_weapon_fighting_feature_applies():
    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)
    if char_config_data.get("Equiped Items") == None:
        char_config_data["Equiped Items"] = {}
        return []
    if char_config_data["Equiped Items"] == {}:
        return []

    """there have to be atleast two weapons or one weapon without two handed weapon in there"""
    weapon_list = []
    weapon_list += char_config_data["Equiped Items"]["Weapons"].split(",")
    weapon_list += char_config_data["Equiped Items"]["Magic Weapon"].split(",")
    weapon_list += char_config_data["Equiped Items"]["Shield"].split(",")
    weapon_list = list(filter(None, weapon_list))
    if len(weapon_list) >= 2:
        return ["Bonus:Two weapon fighting"]
    elif len(weapon_list) == 1:
        if "Two-handed" not in V.item_dict[weapon_list[0]]["Properties"]:
            amount = V.character_dict[V.char_name]["Items"].split(",").count(weapon_list[0])
            if amount >= 2:
                return ["Bonus:Two weapon fighting"]
    return []

def handle_special_flags(pressed):
    type, name = pressed
    if S.Class_features[name].get("Special_Flag") != None:
        V.Special_Flags[name] = S.Class_features[name].get("Special_Flag")

def display_single_spell(screen, spell, start_X, start_y, step_y, displayed_rects, tab, cast_level):
    modifyer = 0
    display_small_r = False
    if "reaction" in S.spell_data[spell]["Casting Time"].lower():
        color = "Red"
    elif "bonus action" in S.spell_data[spell]["Casting Time"].lower():
        color = "Navy"
    else:
        color = "Black"
    if S.spell_data[spell]["Ritual"] == "True":
        display_small_r = True

    rect_info = F.display_text(screen, spell, 15, (start_X, start_y + step_y), color=color)
    if display_small_r:
        F.display_text(screen, " R", 5, (rect_info.x + rect_info.w, start_y + step_y), color=color)
    if spell not in list(displayed_rects.keys()):
        displayed_rects[spell + ":" + str(cast_level)] = {"Info": rect_info, "Type": "Spell", "Cast_Level": cast_level}
    temp_spell_data = copy.deepcopy(S.spell_data[spell])
    if S.spell_data[spell].get("Type") != None:
        if "spellcasting ability modifier" in S.spell_data[spell]["Damage"]:
            modifyer = V.spellcasting_ability_mod

        if S.spell_data[spell]["Type"] == "Heal":
            step_y += S.SCREEN_HEIGHT * 0.031
            if int(cast_level) > int(S.spell_data[spell]["Level"]):
                if S.spell_data[spell]["Level Up"][0:2] == ["ADD", "Damage"]:
                    leveled_healing = int(cast_level) * int(temp_spell_data["Level Up"][2].split("d")[0])
                    temp_spell_data["Damage"] = temp_spell_data["Damage"].replace(temp_spell_data["Damage"].split("d")[0], str(leveled_healing))
                else:
                    F.print_debug("HELP BOSS THIS SPELL IS WEIRD its a healing spell, but when leveling up it doesnt level up the healing output", debug="ERROR")
            rect_damage = F.display_text(screen, "Heal: " + temp_spell_data["Damage"].replace("+spellcasting ability modifier", "+" + str(V.spellcasting_ability_mod)), 15,(start_X + tab, start_y + step_y))
        else:
            if S.spell_data[spell]["Attack"] in ["Ranged Spell Attack", "Melee Spell Attack"]:
                step_y += S.SCREEN_HEIGHT * 0.031
                rect_hit = F.display_text(screen, "Hit: 1d20", 15, (start_X + tab, start_y + step_y))
                pg.draw.rect(screen, "black", rect_hit, width=1)
                displayed_rects[spell + ":" + str(cast_level)]["Hit"] = rect_hit
                displayed_rects[spell + ":" + str(cast_level)]["Roll_mod"] = V.Spell_attack
            elif S.spell_data[spell]["Attack"] in ["Melee weapon effect"]:
                melee_weapon_effect = True  # or whatever

            step_y += S.SCREEN_HEIGHT * 0.031
            if isinstance(temp_spell_data["Damage"], list):

                rect_damage = F.display_text(screen, "Damage: " + S.spell_data[spell]["Damage"][0].replace("+spellcasting ability modifier", "+" + str(V.spellcasting_ability_mod)), 15,(start_X + tab, start_y + step_y))
                step_y += S.SCREEN_HEIGHT * 0.031

                multiplyer = int(cast_level) - int(temp_spell_data["Level"])
                leveled_healing = multiplyer * int(temp_spell_data["Level Up"][2].split("d")[0])
                changed_value = int(temp_spell_data["Damage"][1].split("d")[0]) + int(leveled_healing)
                temp_spell_data["Damage"][1] = temp_spell_data["Damage"][1].replace(temp_spell_data["Damage"][1].split("d")[0], str(changed_value))

                rect_damage_extra = F.display_text(screen, "Damage: " + temp_spell_data["Damage"][1].replace("+spellcasting ability modifier", "+" + str(V.spellcasting_ability_mod)), 15,(start_X + tab, start_y + step_y))
                pg.draw.rect(screen, "black", rect_damage_extra, width=1)
                displayed_rects[spell + ":" + str(cast_level)]["Damage_extra"] = rect_damage_extra
            else:
                if S.spell_data[spell].get("Level Up") != None and S.spell_data[spell]["Level Up"][0:2] == ["ADD", "Damage"]:
                    multiplyer = int(cast_level) - int(temp_spell_data["Level"])
                    leveled_healing = multiplyer * int(temp_spell_data["Level Up"][2].split("d")[0])
                    changed_value = int(temp_spell_data["Damage"].split("d")[0]) + int(leveled_healing)
                    temp_spell_data["Damage"] = temp_spell_data["Damage"].replace(temp_spell_data["Damage"].split("d")[0], str(changed_value))
                rect_damage = F.display_text(screen, "Damage: " + temp_spell_data["Damage"].replace("+spellcasting ability modifier", "+" + str(V.spellcasting_ability_mod)), 15,(start_X + tab, start_y + step_y))
        pg.draw.rect(screen, "black", rect_damage, width=1)
        displayed_rects[spell + ":" + str(cast_level)]["Damage"] = rect_damage
        displayed_rects[spell + ":" + str(cast_level)]["Damage_mod"] = modifyer
        if isinstance(temp_spell_data["Damage"], list):
            """deals with spells that deal two diferent damage dice like 1d10 piercing and 2d6 cold"""
            displayed_rects[spell + ":" + str(cast_level)]["Damage_Die"] = temp_spell_data["Damage"][0].replace("+spellcasting ability modifier","")
            displayed_rects[spell + ":" + str(cast_level)]["Damage_Die_extra"] = temp_spell_data["Damage"][1].replace("+spellcasting ability modifier","")
            displayed_rects[spell + ":" + str(cast_level)]["Damage_mod_extra"] = modifyer
        else:
            displayed_rects[spell + ":" + str(cast_level)]["Damage_Die"] = temp_spell_data["Damage"].replace("+spellcasting ability modifier","")

        step_y += S.SCREEN_HEIGHT * 0.031
        if isinstance(temp_spell_data["Damage"], list):
            """deals with spells that deal two diferent damage types like piercing and cold"""
            F.display_text(screen, "Type: " + S.spell_data[spell]["Type"][0] + ", " + S.spell_data[spell]["Type"][1] , 15, (start_X + tab, start_y + step_y))
        else:
            if isinstance(S.spell_data[spell]["Type"], list):
                l = F.display_text(screen, "Type: ", 15, (start_X + tab, start_y + step_y))
                type_count = 0
                for type in S.spell_data[spell]["Type"]:
                    if type != S.spell_data[spell]["Type"][-1]:
                        gap = ", "
                    else:
                        gap = ""
                    l = F.display_text(screen, type + gap, 15, (l.x + l.w, start_y + step_y))
                    type_count += 1
                    if type_count > 2:
                        type_count = 0
                        step_y += S.SCREEN_HEIGHT * 0.031
                        l = pg.Rect(start_X + tab, start_y + step_y, 0, 0)

            else:
                F.display_text(screen, "Type: " + S.spell_data[spell]["Type"], 15, (start_X + tab, start_y + step_y))

    else:
        step_y += S.SCREEN_HEIGHT * 0.031
        rect_hit = F.display_text(screen, "Cast", 15, (start_X + tab, start_y + step_y))
        pg.draw.rect(screen, "black", rect_hit, width=1)
        displayed_rects[spell + ":" + str(cast_level)]["Cast"] = rect_hit
        if display_small_r:
            rect_hit = F.display_text(screen, "Ritual", 15, (rect_hit.x + rect_hit.w + tab, start_y + step_y))
            pg.draw.rect(screen, "black", rect_hit, width=1)
            displayed_rects[spell + ":" + str(cast_level)]["Ritual"] = rect_hit

    step_y += S.SCREEN_HEIGHT * 0.031

    return start_y, step_y


def Manage_spells(screen, clock):
    running = False
    text_size = 30
    character = V.character_dict[V.char_name].copy()
    pressed = -1
    case = "Spells"
    level_to_show = 1
    button_dict = {
        (0, 2): ["Back", "background", "background", "rect-place-holder", "black"],
        (1, 2): ["Switch to: " + case, "background", "background", "rect-place-holder", "black"],
        (2, 2): ["Switch Class", "background", "background", "rect-place-holder", "black"],
    }
    if len(character["Class"].split(", ")) == 1:
        del button_dict[(2, 2)]
    class_id = 0
    case = "Cantrips"
    current_class, no_exist, cantrip_list, spell_list, cantrip_count, spell_count, unknown_cantrip_rects, unknown_spell_rects, known_spell_rects, known_cantrip_rects, known_cantrips, known_spells, running, level_to_show = get_spell_data(character, class_id, level_to_show)
    y_scroll = 0
    y_scroll_spell = 0
    hovering_mouse = []
    not_changable_spells, not_changable_cantrips = Sp.get_not_changable_spells(character, cantrip_list, spell_list)
    scroll_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 3), pg.SRCALPHA).convert_alpha()
    text_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.SRCALPHA).convert_alpha()
    mode = "Description"
    while running:
        scroll_surface.fill((0,0,0,0))
        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.05
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        x_pos = [S.SCREEN_WIDTH * 0.77, S.SCREEN_WIDTH * 0.52, S.SCREEN_WIDTH * 0.27, S.SCREEN_WIDTH * 0.02]
        y_pos = [S.SCREEN_HEIGHT * 0.05, S.SCREEN_HEIGHT * 0.12, S.SCREEN_HEIGHT * 0.9]
        buttons = F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)
        F.display_text(screen, "Click Mouse Wheel or Left arrow key", 15, (S.SCREEN_WIDTH * 0.75, S.SCREEN_HEIGHT * 0.03), case="C")
        F.display_text(scroll_surface, current_class +" "+ case, 20, (S.SCREEN_WIDTH * 0.26, S.SCREEN_HEIGHT * 0.03))

        y_step = 0
        if case == "Cantrips":
            for cantrip in cantrip_list:
                color = "black"
                if cantrip in known_cantrips:
                    color = "dark green"
                r = F.display_text(scroll_surface, cantrip, 13, (S.SCREEN_WIDTH * 0.28, S.SCREEN_HEIGHT * 0.09 + y_step), color=color)
                unknown_cantrip_rects[cantrip] = r
                y_step += S.SCREEN_HEIGHT * 0.03
        else:
            for spell in spell_list:
                color = "black"
                if spell in known_spells:
                    color = "dark green"
                r = F.display_text(scroll_surface, spell, 13, (S.SCREEN_WIDTH * 0.28, S.SCREEN_HEIGHT * 0.09 + y_step), color=color)
                unknown_spell_rects[spell] = r
                y_step += S.SCREEN_HEIGHT * 0.03

        pg.draw.line(screen, "black", (S.SCREEN_WIDTH * 0.25, 0), (S.SCREEN_WIDTH * 0.25, S.SCREEN_HEIGHT * 0.85), width=2)
        pg.draw.line(screen, "black", (0, S.SCREEN_HEIGHT * 0.85), (S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 0.85), width=2)



        F.display_text(screen, "Cantrips available: " + str(cantrip_count - len(known_cantrips)), 10, (S.SCREEN_WIDTH * 0.1, S.SCREEN_HEIGHT * 0.03))
        F.display_text(screen, "Spells available: " + str(spell_count - len(known_spells)), 10, (S.SCREEN_WIDTH * 0.1, S.SCREEN_HEIGHT * 0.05))

        y_step = 0
        if known_cantrips == []:
            no_exist = "-"
        F.display_text(screen, "Known cantrips: " + no_exist, 20, (S.SCREEN_WIDTH * 0.01, S.SCREEN_HEIGHT * 0.08), color="Dark Red")
        y_step += S.SCREEN_HEIGHT * 0.04
        if known_cantrips != []:
            for cantrip in known_cantrips:
                color = "black"
                if cantrip in not_changable_cantrips:
                    color = (150, 30, 30, 255)
                r = F.display_text(screen, cantrip, 13,(S.SCREEN_WIDTH * 0.01, S.SCREEN_HEIGHT * 0.08 + y_step), color=color)
                y_step += S.SCREEN_HEIGHT * 0.03
                known_cantrip_rects[cantrip] = r


        no_exist = ""
        if known_spells == []:
            no_exist = "-"
        F.display_text(screen, "Known spells: " + no_exist, 20, (S.SCREEN_WIDTH * 0.01, S.SCREEN_HEIGHT * 0.08 + y_step), color="Dark Red")
        y_step += S.SCREEN_HEIGHT * 0.04
        if known_spells != []:
            for spell in known_spells:
                color = "black"
                if spell in not_changable_spells:
                    color = (150, 30, 30, 255)
                r = F.display_text(screen, spell, 13,(S.SCREEN_WIDTH * 0.01, S.SCREEN_HEIGHT * 0.08 + y_step), color=color)
                y_step += S.SCREEN_HEIGHT * 0.03
                known_spell_rects[spell] = r

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
                scroll_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT * 3), pg.SRCALPHA).convert_alpha()
                text_surface = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.SRCALPHA).convert_alpha()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                pressed = -1
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(mouse_pos):
                        for key, value in button_dict.items():
                            if value[3] == buttons[i]:
                                pressed = value[0]
                                pg.draw.rect(screen, "black", buttons[i], width=3)
                                break
                if pressed == -1:
                    for spell, rect in known_spell_rects.items():
                        if rect.collidepoint(mouse_pos) and spell not in not_changable_spells:
                            pressed = [spell, rect, "KSpell"]
                            break
                    for cantrip, rect in known_cantrip_rects.items():
                        if rect.collidepoint(mouse_pos) and cantrip not in not_changable_cantrips:
                            pressed = [cantrip, rect, "KCantrip"]
                            break
                    mouse_pos = (mouse_pos[0], mouse_pos[1] - y_scroll)
                    for spell, rect in unknown_spell_rects.items():
                        if rect.collidepoint(mouse_pos):
                            pressed = [spell, rect, "USpell"]
                            break
                    for cantrip, rect in unknown_cantrip_rects.items():
                        if rect.collidepoint(mouse_pos):
                            pressed = [cantrip, rect, "UCantrip"]
                            break
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == "Back":
                        V.character_dict[V.char_name] = character.copy()
                        return
                    elif "Switch to: " in pressed:
                        button_dict[(1, 2)][0] = "Switch to: " + case
                        if case == "Cantrips":
                            case = "Spells"
                            button_dict[(3, 2)] = ["Switch Level: " + str(level_to_show), "background", "background", "rect-place-holder", "black"]

                        elif case == "Spells":
                            case = "Cantrips"
                            del button_dict[(3, 2)]
                        unknown_spell_rects = {}
                        unknown_cantrip_rects = {}
                    elif pressed == "Switch Class":
                        if len(character["Class"].split(", ")) != 1:
                            class_id += 1
                            if class_id > 1:
                                class_id = 0
                            current_class, no_exist, cantrip_list, spell_list, cantrip_count, spell_count, unknown_cantrip_rects, unknown_spell_rects, known_spell_rects, known_cantrip_rects, known_cantrips, known_spells, running, level_to_show = get_spell_data(character, class_id, level_to_show)
                    elif pressed == "Switch Level: " + str(level_to_show):
                        level_to_show += 1
                        current_class, no_exist, cantrip_list, spell_list, cantrip_count, spell_count, unknown_cantrip_rects, unknown_spell_rects, known_spell_rects, known_cantrip_rects, known_cantrips, known_spells, running, level_to_show = get_spell_data(character, class_id, level_to_show)
                        button_dict[(3, 2)][0] = "Switch Level: " + str(level_to_show)



                    elif isinstance(pressed, list):
                        """Pressed on text"""
                        if pressed[2][0] == "K":
                            if pressed[2][1] == "S":
                                """Known spell, Remove it"""
                                known_spells.remove(pressed[0])
                                del known_spell_rects[pressed[0]]
                                character["Spell"] = ",".join(known_spells)
                            else:
                                """Known cantrip, Remove it"""
                                known_cantrips.remove(pressed[0])
                                del known_cantrip_rects[pressed[0]]
                                character["Cantrip"] = ",".join(known_cantrips)
                        else:
                            if pressed[2][1] == "S" and spell_count - len(known_spells) > 0 and pressed[0] not in known_spells:
                                """Unknown spell, Add it"""
                                known_spells.append(pressed[0])
                                character["Spell"] = ",".join(known_spells)
                            elif pressed[2][1] == "C" and cantrip_count - len(known_cantrips) > 0 and pressed[0] not in known_cantrips:
                                """Unknown cantrip, Add it"""
                                known_cantrips.append(pressed[0])
                                character["Cantrip"] = ",".join(known_cantrips)

                    pressed = -1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5 or event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                """Going down"""
                mouse_pos = pg.mouse.get_pos()
                if mouse_pos[0] > S.SCREEN_WIDTH * 0.3 and mouse_pos[0] < S.SCREEN_WIDTH * 0.5:
                    y_scroll -= 20
                elif mouse_pos[0] > S.SCREEN_WIDTH * 0.5:
                    y_scroll_spell -= 20
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 4 or event.type == pg.KEYDOWN and event.key == pg.K_UP:
                mouse_pos = pg.mouse.get_pos()
                if mouse_pos[0] > S.SCREEN_WIDTH * 0.3 and mouse_pos[0] < S.SCREEN_WIDTH * 0.5:
                    y_scroll += 20
                    if y_scroll > 0:
                        y_scroll = 0
                elif mouse_pos[0] > S.SCREEN_WIDTH * 0.5:
                    y_scroll_spell += 20
                    if y_scroll_spell > 0:
                        y_scroll_spell = 0
            elif event.type == pg.MOUSEMOTION:
                mouse_pos = pg.mouse.get_pos()
                # hovering_mouse = []
                for spell, rect in unknown_spell_rects.items():
                    if rect.collidepoint((mouse_pos[0], mouse_pos[1] - y_scroll)):
                        hovering_mouse = [spell, rect, "Spell"]
                        break
                for cantrip, rect in unknown_cantrip_rects.items():
                    if rect.collidepoint((mouse_pos[0], mouse_pos[1] - y_scroll)):
                        hovering_mouse = [cantrip, rect, "Cantrip"]
                        break
                for spell, rect in known_spell_rects.items():
                    if rect.collidepoint((mouse_pos[0], mouse_pos[1] - y_scroll)):
                        hovering_mouse = [spell, rect, "Spell"]
                        break
                for cantrip, rect in known_cantrip_rects.items():
                    if rect.collidepoint((mouse_pos[0], mouse_pos[1] - y_scroll)):
                        hovering_mouse = [cantrip, rect, "Cantrip"]
                        break
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 2 or event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
                if mode == "Description":
                    mode = "Simple"
                elif mode == "Simple":
                    mode = "At Higher Levels"
                elif mode == "At Higher Levels":
                    mode = "Description"

        text_surface.fill((0, 0, 0, 0))
        if hovering_mouse != []:
            id = []
            Sp.display_only_spell_descriptions(text_surface, hovering_mouse, id, mode)

        screen.blit(scroll_surface, (0, y_scroll))
        screen.blit(text_surface, (0, y_scroll_spell))
        pg.display.flip()
        clock.tick(60)


def get_spell_data(character, class_id, level_to_show):
    cantrip_count = 0
    spell_count = 0
    current_class = character["Class"].split(", ")[class_id]
    current_level = int(character["Level"].split(",")[class_id])
    if ":" in character["Slot Level"]:
        highest_spell_level = int(character["Slot Level"].split(":")[-1])
    else:
        highest_spell_level = int(character["Slot Level"].split(",")[-1])
    if level_to_show > highest_spell_level:
        level_to_show = 1
    running = False
    if current_class == "Warlock":
        F.print_debug("WARLOCK SPELLS NEED UPDATING", 0, "ERROR")
        spell_slot_d = 0
        return current_class, 0, 0, 0, cantrip_count, spell_count, 0, 0, 0, 0, 0, 0, running, level_to_show
    elif current_class == "Blood Hunter":
        spell_slot_d = [0, int(character["Blood Curses Known"]), 1, "1st:" + str(character["Blood Curses Known"]), 1]
    else:
        spell_slot_d = 0
        if V.Available_spells_data.get(current_class) != None and V.Available_spells_data[current_class].get(current_level) != None:
            spell_slot_d = V.Available_spells_data[current_class][current_level]

    if spell_slot_d != 0:
        cantrip_count = Sp.count_max_cantrip_count(spell_slot_d)
        spell_count = Sp.count_max_spell_count(spell_slot_d, current_level)

    """Spells already known"""
    known_spells = []
    if character.get("Spell") != None and character["Spell"] != "":
        for spell in character["Spell"].split(","):
            spell_in_features = False
            """If the spell can be learned in this class append it"""
            for key in character["Code"].split(","):
                if "Feature:" in key:
                    temp_key = key.replace("Feature:", "")
                    if S.Class_features.get(temp_key) != None:
                        if S.Class_features[temp_key].get("Race") != None and S.Class_features[temp_key]["Race"] == character["Race"] or S.Class_features[temp_key].get("Class") != None and S.Class_features[temp_key]["Class"] == current_class:
                            if S.Class_features[temp_key].get("Spell") != None and spell in S.Class_features[temp_key]["Spell"]:
                                spell_in_features = True
                                break
            if not spell_in_features:
                known_spells.append(spell)

    """Cantrips already known"""
    known_cantrips = []
    if character.get("Cantrip") != None and character["Cantrip"] != "":
        known_cantrips = []
        for cantrip in character["Cantrip"].split(","):
            if cantrip == "":
                continue
            known_cantrips.append(cantrip)


    """Get a list of spells available to learn"""
    spell_list = []
    if spell_count != 0:
        running = True
        for spell, spell_values in S.spell_data.items():
            if current_class in spell_values["Class"]:
                if highest_spell_level >= int(spell_values["Level"]) and level_to_show == int(spell_values["Level"]):
                    spell_list.append(spell)

    """Get a list of cantrips available to learn"""
    cantrip_list = []
    if cantrip_count != 0:
        for cantrip, cantrip_values in S.cantrip_data.items():
            if current_class in cantrip_values["Class"]:
                cantrip_list.append(cantrip)

    no_exist = ""
    known_spell_rects = {}
    known_cantrip_rects = {}
    unknown_spell_rects = {}
    unknown_cantrip_rects = {}
    return current_class, no_exist, cantrip_list, spell_list, cantrip_count, spell_count, unknown_cantrip_rects, unknown_spell_rects, known_spell_rects, known_cantrip_rects, known_cantrips, known_spells, running, level_to_show

def handle_notes(screen, clock, show_notes, note_rect):
    running = False

    if show_notes > 50:
        show_notes = 0
        running = True
    else:
        mouse_pos = pg.mouse.get_pos()
        if note_rect.collidepoint(mouse_pos):
            show_notes += 1
        else:
            show_notes = 0

    text_size = 15
    pressed = -1
    button_dict = {
        (0, 0): ["Erase", "background", "background", "rect-place-holder", "black"],
    }

    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)

    if char_config_data.get("Notes") == None:
        char_config_data["Notes"] = ""
    text = char_config_data["Notes"]
    flash_marker = False
    marker_timer = 0
    cursor_push = [0, 0]
    keys = pg.key.get_pressed()
    pressed_timer = {}
    shift_pressed = False
    shift_track = -1
    undo_memory = []
    copyied_text = ""
    while running:
        button_width = S.SCREEN_WIDTH * 0.2
        button_height = S.SCREEN_HEIGHT * 0.05
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")

        note_surface, text = fill_note(screen, text, text_size, cursor_push, shift_track)

        note_screen_rect = note_surface.get_rect()
        note_screen_rect.topleft = (S.SCREEN_WIDTH * 0.1, S.SCREEN_HEIGHT * 0.05)
        buttons = F.display_back_button(screen, "Back")
        x_pos = [S.SCREEN_WIDTH * 0.52, S.SCREEN_WIDTH * 0.62]
        y_pos = [S.SCREEN_HEIGHT * 0.9, S.SCREEN_HEIGHT * 0.12]
        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)

        for event in pg.event.get():
            keys = pg.key.get_pressed()
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Update window size based on new dimensions
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
                text_size = int(S.SCREEN_WIDTH * 0.013)
                if V.images.get("Note_surf") != None:
                    del V.images["Note_surf"]
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(mouse_pos):
                        pressed = "Back"
                        for key, value in button_dict.items():
                            if value[3] == buttons[i]:
                                pressed = value[0]
                        pg.draw.rect(screen, "black", buttons[i], width=3)
                if pressed == -1:
                    if note_screen_rect.collidepoint(mouse_pos) and not flash_marker:
                        flash_marker = True
                        marker_timer = 10
                        text += "\\cursor0"
                        # cursor_pos = [(S.SCREEN_WIDTH * 0.1, S.SCREEN_HEIGHT * 0.05), (S.SCREEN_WIDTH * 0.1, S.SCREEN_HEIGHT * 0.05 + text_size * 1.8)]
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == "Back":
                        F.save_text_to_json(text)
                        return show_notes
                    elif pressed == "Erase":
                        text = ""
                    pressed = -1
            elif event.type == pg.TEXTINPUT and flash_marker:
                index = len(text)
                if "\\cursor0" in text:
                    index = text.index("\\cursor0")
                    text = text.replace("\\cursor0", "")
                elif "\\cursor1" in text:
                    index = text.index("\\cursor1")
                    text = text.replace("\\cursor1", "")
                if shift_track != -1:
                    current_marker_pos = index + cursor_push[0]
                    if current_marker_pos > shift_track:
                        text = text[:shift_track] + event.text + text[current_marker_pos:]
                    else:
                        cursor_push[0] += len(text[current_marker_pos:shift_track])
                        text = text[:current_marker_pos] + event.text + text[shift_track:]
                    shift_pressed = False
                    shift_track = -1
                else:
                    if cursor_push[0] != 0:
                        text = text[:cursor_push[0]] + event.text + text[cursor_push[0]:]
                    else:
                        text += event.text

                marker_timer = -1
                text += "\\cursor0"
            elif keys[pg.K_RETURN]:
                shift_pressed = False
                shift_track = -1
                text = text.replace("\\cursor0", "")
                text = text.replace("\\cursor1", "")
                if cursor_push[0] != 0:
                    text = text[:cursor_push[0]] + '\n' + text[cursor_push[0]:]
                else:
                    text += '\n'

                marker_timer = -1
                text += "\\cursor0"
            elif keys[pg.K_TAB]:
                shift_pressed = False
                shift_track = -1
                text = text.replace("\\cursor0", "")
                text = text.replace("\\cursor1", "")
                text += '    '
                text += "\\cursor0"
                marker_timer = -1

        if keys[pg.K_LSHIFT]:
            shift_pressed = True
            if shift_track == -1:
                if "\\cursor0" in text:
                    index = text.index("\\cursor0")
                else:
                    index = text.index("\\cursor1")
                shift_track = index + cursor_push[0]
        else:
            shift_pressed = False

        if keys[pg.K_BACKSPACE]:
            if pressed_timer.get(pg.K_BACKSPACE) == None:
                pressed_timer[pg.K_BACKSPACE] = [0, False]
            if pressed_timer[pg.K_BACKSPACE][0] == 0:
                if not pressed_timer[pg.K_BACKSPACE][1]:
                    pressed_timer[pg.K_BACKSPACE][0] = pg.time.get_ticks()
                index = len(text)
                if "\\cursor0" in text:
                    index = text.index("\\cursor0")
                    text = text.replace("\\cursor0", "")
                elif "\\cursor1" in text:
                    index = text.index("\\cursor1")
                    text = text.replace("\\cursor1", "")
                current_marker_pos = index + cursor_push[0]

                if shift_track != -1:
                    if current_marker_pos > shift_track:
                        text = text[:shift_track] + text[current_marker_pos:]
                    else:
                        cursor_push[0] += len(text[current_marker_pos:shift_track])
                        text = text[:current_marker_pos] + text[shift_track:]
                    shift_pressed = False
                    shift_track = -1
                else:
                    if not keys[pg.K_LCTRL]:
                        if index * -1 != cursor_push[0]:
                            text = text[:current_marker_pos - 1] + text[current_marker_pos:]
                    else:
                        stop_index = -1
                        if " " in text or '\n' in text:
                            for i in range(len(text) + cursor_push[0], -1, -1):
                                if text[i - 1] == " " and text[i - 2] != " " or text[i - 1] == "\n":
                                    stop_index = len(text) + cursor_push[0] - i + 1
                                    break
                            if stop_index > -1:
                                text = text[:current_marker_pos - stop_index] + text[current_marker_pos:]
                        else:
                            text = text[current_marker_pos:]
                text += "\\cursor0"
                marker_timer = -1
        elif keys[pg.K_DELETE]:
            if pressed_timer.get(pg.K_DELETE) == None:
                pressed_timer[pg.K_DELETE] = [0, False]

            if pressed_timer[pg.K_DELETE][0] == 0:
                if not pressed_timer[pg.K_DELETE][1]:
                    pressed_timer[pg.K_DELETE][0] = pg.time.get_ticks()
                index = len(text)
                if "\\cursor0" in text:
                    index = text.index("\\cursor0")
                    text = text.replace("\\cursor0", "")
                elif "\\cursor1" in text:
                    index = text.index("\\cursor1")
                    text = text.replace("\\cursor1", "")
                current_marker_pos = index + cursor_push[0]
                if shift_track != -1:
                    if current_marker_pos > shift_track:
                        text = text[:shift_track] + text[current_marker_pos:]
                    else:
                        cursor_push[0] += len(text[current_marker_pos:shift_track])
                        text = text[:current_marker_pos] + text[shift_track:]
                    shift_pressed = False
                    shift_track = -1
                else:
                    if not keys[pg.K_LCTRL]:
                        text = text[:current_marker_pos] + text[current_marker_pos + 1:]
                        cursor_push[0] += 1
                        if cursor_push[0] > 0:
                            cursor_push[0] = 0
                    else:
                        stop_index = -cursor_push[0]
                        if " " in text or '\n' in text:
                            for i in range(cursor_push[0], -1):
                                if text[i] == " " and text[i + 1] != " " or text[i] == "\n":
                                    stop_index = i - cursor_push[0] + 1
                                    break
                            if stop_index > -1:
                                text = text[:len(text) + cursor_push[0]] + text[len(text) + cursor_push[0] + stop_index:]
                                cursor_push[0] += stop_index
                                if cursor_push[0] > 0:
                                    cursor_push[0] = 0
                        else:
                            text = text[:len(text) + cursor_push[0]]
                            cursor_push[0] = 0
                text += "\\cursor0"
                marker_timer = -1

        elif keys[pg.K_LEFT]:
            if pressed_timer.get(pg.K_LEFT) == None:
                pressed_timer[pg.K_LEFT] = [0, False]

            if pressed_timer[pg.K_LEFT][0] == 0:
                if not pressed_timer[pg.K_LEFT][1]:
                    pressed_timer[pg.K_LEFT][0] = pg.time.get_ticks()
                if not shift_pressed:
                    shift_track = -1
                text = text.replace("\\cursor0", "")
                text = text.replace("\\cursor1", "")
                if not keys[pg.K_LCTRL]:
                    cursor_push[0] -= 1
                    if cursor_push[0] < -1 * len(text):
                        cursor_push[0] = -1 * len(text)
                else:
                    marked = False
                    for i in range(len(text)-1 + cursor_push[0], -1, -1):
                        if text[i] == " " and text[i - 1] != " " or text[i] == "\n":
                            cursor_push[0] = cursor_push[0] + (i - (len(text) + cursor_push[0]))
                            marked = True
                            if cursor_push[0] < -1 * len(text):
                                cursor_push[0] = -1 * len(text)
                            break
                    if not marked:
                        cursor_push[0] = -1 * len(text)
                text += "\\cursor0"
                marker_timer = -1
        elif keys[pg.K_RIGHT]:
            if pressed_timer.get(pg.K_RIGHT) == None:
                pressed_timer[pg.K_RIGHT] = [0, False]

            if pressed_timer[pg.K_RIGHT][0] == 0:
                if not pressed_timer[pg.K_RIGHT][1]:
                    pressed_timer[pg.K_RIGHT][0] = pg.time.get_ticks()
                if not shift_pressed:
                    shift_track = -1
                text = text.replace("\\cursor0", "")
                text = text.replace("\\cursor1", "")
                if not keys[pg.K_LCTRL]:
                    cursor_push[0] += 1
                    if cursor_push[0] > 0:
                        cursor_push[0] = 0
                else:
                    for i in range(len(text)-1 + cursor_push[0], len(text)):
                        if i+1 < len(text):
                            if text[i+1] == " " and text[i + 2] != " " or text[i+1] == "\n":
                                cursor_push[0] = cursor_push[0] + abs(len(text) + cursor_push[0] - i-2)
                                if cursor_push[0] > 0:
                                    cursor_push[0] = 0
                                break
                        else:
                            cursor_push[0] = 0
                text += "\\cursor0"
                marker_timer = -1
        elif keys[pg.K_UP]:
            if pressed_timer.get(pg.K_UP) == None:
                pressed_timer[pg.K_UP] = [0, False]

            if pressed_timer[pg.K_UP][0] == 0:
                if not pressed_timer[pg.K_UP][1]:
                    pressed_timer[pg.K_UP][0] = pg.time.get_ticks()
                if not shift_pressed:
                    shift_track = -1
                index = len(text)
                if "\\cursor0" in text:
                    index = text.index("\\cursor0")
                    text = text.replace("\\cursor0", "")
                elif "\\cursor1" in text:
                    index = text.index("\\cursor1")
                    text = text.replace("\\cursor1", "")
                if not keys[pg.K_LCTRL]:
                    if '\n' not in text:
                        cursor_push[0] = -1 * len(text)
                    else:
                        lines = text.split("\n")
                        jumping_from = ""
                        jumping_to = ""
                        letter_count = 0
                        letter_count_2 = 0
                        for line in lines:
                            letter_count += len(line) + 1
                            if index+cursor_push[0] < letter_count:
                                jumping_from = lines.index(line)
                                if jumping_from == len(lines) - 1:
                                    letter_count_2 = letter_count - 1 - index + cursor_push[0] + len(line)
                                else:
                                    letter_count_2 = abs(index + cursor_push[0] - letter_count - 1)
                                jumping_to = jumping_from - 1
                                break
                        if jumping_to < 0:
                            cursor_push[0] = -1 * len(text)
                        else:
                            cursor_push[0] -= (letter_count_2 + len(lines[jumping_to][letter_count_2:]))+1
                            if cursor_push[0] < -1 * len(text):
                                cursor_push[0] = -1 * len(text)

                else:
                    cursor_push[0] = -1 * len(text)
                text += "\\cursor0"
                marker_timer = -1
        elif keys[pg.K_DOWN]:
            if pressed_timer.get(pg.K_DOWN) == None:
                pressed_timer[pg.K_DOWN] = [0, False]

            if pressed_timer[pg.K_DOWN][0] == 0:
                if not pressed_timer[pg.K_DOWN][1]:
                    pressed_timer[pg.K_DOWN][0] = pg.time.get_ticks()
                if not shift_pressed:
                    shift_track = -1
                slash_n_gap = 1
                index = len(text)
                if "\\cursor0" in text:
                    index = text.index("\\cursor0")
                    text = text.replace("\\cursor0", "")
                elif "\\cursor1" in text:
                    index = text.index("\\cursor1")
                    text = text.replace("\\cursor1", "")
                if not keys[pg.K_LCTRL]:
                    if '\n' not in text:
                        cursor_push[0] = 0
                    else:
                        lines = text.split("\n")
                        jumping_from = ""
                        jumping_to = ""
                        letter_count = 0
                        letter_count_2 = 0
                        for line in lines:
                            letter_count += len(line) + slash_n_gap
                            if index+cursor_push[0] < letter_count:
                                jumping_from = lines.index(line)
                                current_cursor_pos = index + cursor_push[0]
                                current_line_right_letters = line[-(letter_count - current_cursor_pos-slash_n_gap):]
                                push_left_by = len(line[:-(letter_count - current_cursor_pos-slash_n_gap)])
                                letter_count_2 = current_cursor_pos + len(current_line_right_letters) + slash_n_gap

                                jumping_to = jumping_from + 1
                                if jumping_to > len(lines) - 1:
                                    break
                                else:
                                    letter_count += len(lines[jumping_to]) + slash_n_gap
                                    next_line_left_letters = lines[jumping_to][:push_left_by]
                                    letter_count_2 += len(next_line_left_letters)

                                break
                        if jumping_to > len(lines)-1:
                            cursor_push[0] = 0
                        else:
                            cursor_push[0] = -1 * len(text) + letter_count_2
                            if cursor_push[0] > 0:
                                cursor_push[0] = 0
                else:
                    cursor_push[0] = 0
                text += "\\cursor0"
                marker_timer = -1
        elif keys[pg.K_LCTRL] and keys[pg.K_z]:
            """CTRL + Z"""
            if pressed_timer.get(pg.K_z) == None:
                pressed_timer[pg.K_z] = [0, False]

            if pressed_timer[pg.K_z][0] == 0:
                if not pressed_timer[pg.K_z][1]:
                    pressed_timer[pg.K_z][0] = pg.time.get_ticks()
                    text_to_bring_back = text.replace("\\cursor0", "")
                    text_to_bring_back = text_to_bring_back.replace("\\cursor1", "")
                    if text_to_bring_back in undo_memory:
                        text_index = undo_memory.index(text_to_bring_back)
                        if text_index != 0:
                            text = undo_memory[text_index - 1]
                            undo_memory.pop(text_index)
                        marker_timer = -1
                        text += "\\cursor0"
        elif keys[pg.K_LCTRL] and keys[pg.K_a]:
            """CTRL + A"""
            shift_track = 0
            cursor_push[0] = 0
        elif keys[pg.K_LCTRL] and keys[pg.K_c] and shift_track != -1 or keys[pg.K_LCTRL] and keys[pg.K_x] and shift_track != -1:
            """CTRL + C | CTRL + X"""
            index = len(text)
            if "\\cursor0" in text:
                index = text.index("\\cursor0")
            elif "\\cursor1" in text:
                index = text.index("\\cursor1")
            current_marker_pos = index + cursor_push[0]
            if current_marker_pos > shift_track:
                copyied_text = text[shift_track:current_marker_pos]
                if keys[pg.K_x]:
                    text = text[:shift_track] + text[current_marker_pos:]
                    text += "\\cursor0"
                    marker_timer = -1
                    shift_track = -1
                    shift_pressed = False
            else:
                copyied_text = text[current_marker_pos:shift_track]
                if keys[pg.K_x]:
                    cursor_push[0] += len(text[current_marker_pos:shift_track])
                    text = text[:current_marker_pos] + text[shift_track:]
                    text += "\\cursor0"
                    marker_timer = -1
                    shift_track = -1
                    shift_pressed = False


        elif keys[pg.K_LCTRL] and keys[pg.K_v] and copyied_text != "":
            """CTRL + V"""
            if pressed_timer.get(pg.K_v) == None:
                pressed_timer[pg.K_v] = [0, False]

            if pressed_timer[pg.K_v][0] == 0:
                if not pressed_timer[pg.K_v][1]:
                    pressed_timer[pg.K_v][0] = pg.time.get_ticks()
                    index = len(text)
                    if "\\cursor0" in text:
                        index = text.index("\\cursor0")
                        text = text.replace("\\cursor0", "")
                    elif "\\cursor1" in text:
                        index = text.index("\\cursor1")
                        text = text.replace("\\cursor1", "")
                    current_marker_pos = index + cursor_push[0]
                    text = text[:current_marker_pos] + copyied_text + text[current_marker_pos:]

                    text += "\\cursor0"
                    marker_timer = -1











        screen.blit(note_surface, (S.SCREEN_WIDTH * 0.1, S.SCREEN_HEIGHT * 0.05))
        if flash_marker:
            if marker_timer < 0:
                text = text.replace("\\cursor1", "\\cursor0")
            else:
                text = text.replace("\\cursor0", "\\cursor1")
            marker_timer -= 1
            if marker_timer < -10:
                marker_timer = 10
        # display_shift(screen, shift_track, text, cursor_push)
        pg.display.flip()
        clock.tick(120)
        for key, t in pressed_timer.items():
            if not keys[key] and key not in [pg.K_z, pg.K_x, pg.K_c, pg.K_v, pg.K_a] or not keys[key] and key in [pg.K_z, pg.K_x, pg.K_c, pg.K_v, pg.K_a] and not keys[pg.K_LCTRL]:
                pressed_timer[key] = [0, False]
            if pg.time.get_ticks() - t[0] > 500 and t[0] != 0:
                pressed_timer[key][0] = 0
                pressed_timer[key][1] = True

        if text.replace("\\cursor0", "") not in undo_memory and text.replace("\\cursor1", "") not in undo_memory:
            text_to_save = text.replace("\\cursor0", "")
            text_to_save = text_to_save.replace("\\cursor1", "")
            undo_memory.append(text_to_save)
            if len(undo_memory) > 100:
                undo_memory.pop(0)
    return show_notes

def fill_note(screen, text, text_size, cursor_push, shift_track):
    if V.images.get("Note_surf") == None:
        V.images["Note_surf"] = pg.Surface((S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.8), pg.SRCALPHA).convert_alpha()
    note_surface = V.images["Note_surf"]
    note_surface.fill((255, 255, 255, 255))
    pg.draw.line(screen, "black", (S.SCREEN_WIDTH * 0.1, S.SCREEN_HEIGHT * 0.85), (S.SCREEN_WIDTH * 0.9, S.SCREEN_HEIGHT * 0.85), width=2)
    pg.draw.line(screen, "black", (S.SCREEN_WIDTH * 0.9, S.SCREEN_HEIGHT * 0.05), (S.SCREEN_WIDTH * 0.9, S.SCREEN_HEIGHT * 0.85), width=2)

    marker_index = -1
    lines = text.split('\n')
    mrk_index_for_shift = -1
    if "\\cursor0" in text:
        marker_index = text.index("\\cursor0") + cursor_push[0]
        mrk_index_for_shift = marker_index
    elif "\\cursor1" in text:
        mrk_index_for_shift = text.index("\\cursor1") + cursor_push[0]


    letter_count = 0
    step_y = 0
    line_pos = -1
    for line in lines:
        step_x = 0
        words = line.split(" ")
        for word in words:
            if "\\cursor0" in word:
                word = word.replace("\\cursor0","")
            elif "\\cursor1" in word:
                word = word.replace("\\cursor1", "")
            if len(words) != 1:
                word = word + " "
                letter_count -= 1
            for i in range(0, len(word)+1):
                invert = False
                if marker_index != -1 and letter_count == marker_index:
                    if " " in word:
                        step_x -= l.w
                    line_pos = [(step_x, step_y), (step_x, step_y + text_size * 1.8)]
                if len(word) > i:
                    if mrk_index_for_shift != -1 and shift_track != -1:
                        if letter_count in range(mrk_index_for_shift, shift_track) or letter_count in range(shift_track, mrk_index_for_shift):
                            invert = True
                    l = F.display_text(note_surface, word[i], text_size, (step_x, step_y), invert_colors=invert)
                    step_x += l.w
                letter_count += 1

            l = F.display_text(note_surface, "", text_size, (step_x, step_y))

        step_y = l.y + l.h
    if line_pos != -1:
        print(line_pos, marker_index, letter_count)

        pg.draw.line(note_surface, "black", line_pos[0], line_pos[1])


    return note_surface, text

def display_shift(screen, shift_track, text, cursor_push):
    if shift_track != -1:
        if "\\cursor0" in text:
            index = text.index("\\cursor0")
        else:
            index = text.index("\\cursor1")
        current_marker_pos = index + cursor_push[0]

def update_cantrip_spell_damage(spell_damage, cantrip):
    if S.cantrip_data[cantrip].get("Level Up") != None:
        level_up_requirements = S.cantrip_data[cantrip]["Level Up"]
        if level_up_requirements[0:2] == ["CHANGE", "Damage"] or level_up_requirements[0:2] == ["CREATE", "Damage"]:
            damages = level_up_requirements[2]
            levels = level_up_requirements[3]
            char_levels = V.character_dict[V.char_name]["Level"].split(",")
            damage_to_replace = ""
            for i in range(0, len(levels)):
                if any(int(char_lv) >= int(levels[i]) for char_lv in char_levels):
                    """If any of the character levels is bigger than the level in the spell, use the new damage"""
                    damage_to_replace = damages[i]
            if damage_to_replace != "":
                if level_up_requirements[0] == "CHANGE":
                    new_dice_amount = int(damage_to_replace.split("d")[0])
                    if len(spell_damage) != len(str(new_dice_amount) + "d" + spell_damage.split("d")[1]):
                        F.print_debug("MISMATCH OF VALUES", [spell_damage, str(new_dice_amount) + "d" + spell_damage.split("d")[1]], "ERROR")
                    spell_damage = str(new_dice_amount) + "d" + spell_damage.split("d")[1]
                elif level_up_requirements[0] == "CREATE":
                    spell_damage = str(damage_to_replace) + spell_damage

        else:
            F.print_debug("DONT KNOW THIS REQUIREMENT SIR", [level_up_requirements, cantrip], "ERROR")
    return spell_damage