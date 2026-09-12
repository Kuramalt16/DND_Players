import pygame as pg, random, time, copy, math
import Variables as V, Settings as S, Functions as F, conditions as C, Actions as A, Items

def display_char_skills(character, screen, clock):
    running = True
    text_size = 30
    pressed = -1
    skill_dict = {}
    skill_list = character["Skills"].split(",")
    button_dict = {
        (0, 0): ["Acrobatics", "background", "background", "rect-place-holder", "black"],
        (0, 1): ["Animal Handling", "background", "background", "rect-place-holder", "black"],
        (0, 2): ["Arcana", "background", "background", "rect-place-holder", "black"],
        (0, 3): ["Athletics", "background", "background", "rect-place-holder", "black"],
        (0, 4): ["Deception", "background", "background", "rect-place-holder", "black"],
        (0, 5): ["History", "background", "background", "rect-place-holder", "black"],
        (0, 6): ["Insight", "background", "background", "rect-place-holder", "black"],
        (0, 7): ["Intimidation", "background", "background", "rect-place-holder", "black"],
        (0, 8): ["Investigation", "background", "background", "rect-place-holder", "black"],
        (3, 0): ["Medicine", "background", "background", "rect-place-holder", "black"],
        (3, 1): ["Nature", "background", "background", "rect-place-holder", "black"],
        (3, 2): ["Perception", "background", "background", "rect-place-holder", "black"],
        (3, 3): ["Performance", "background", "background", "rect-place-holder", "black"],
        (3, 4): ["Persuasion", "background", "background", "rect-place-holder", "black"],
        (3, 5): ["Religion", "background", "background", "rect-place-holder", "black"],
        (3, 6): ["Sleight of Hand", "background", "background", "rect-place-holder", "black"],
        (3, 7): ["Stealth", "background", "background", "rect-place-holder", "black"],
        (3, 8): ["Survival", "background", "background", "rect-place-holder", "black"],
    }
    """Make a skill dict for easyer use"""
    if len(skill_list) == 18:
        for skill in skill_list:
            skill_dict[skill.split(":")[0]] = int(skill.split(":")[1])
    """reform the colors of the buttons. colored: Proficient"""
    for key in button_dict.keys():
        if skill_dict[button_dict[key][0]] > 1:
            button_dict[key][4] = S.Proficient_button_color
        else:
            skill_dict[button_dict[key][0]] = 0
        gap = ": "
        if skill_dict[button_dict[key][0]] + V.Skills[button_dict[key][0]][0] > 0:
            gap = ": +"
        button_dict[key][0] += gap + str(skill_dict[button_dict[key][0]] + V.Skills[button_dict[key][0]][0])

    ability_score_button_dict = {
        (1, 1): ["STR", "background", "background", "rect-place-holder", "black"],
        (1, 2): ["DEX", "background", "background", "rect-place-holder", "black"],
        (1, 3): ["CON", "background", "background", "rect-place-holder", "black"],
        (2, 1): ["INT", "background", "background", "rect-place-holder", "black"],
        (2, 2): ["WIS", "background", "background", "rect-place-holder", "black"],
        (2, 3): ["CHA", "background", "background", "rect-place-holder", "black"],
        (1, 5): ["STR", "background", "background", "rect-place-holder", "black"],
        (1, 6): ["DEX", "background", "background", "rect-place-holder", "black"],
        (1, 7): ["CON", "background", "background", "rect-place-holder", "black"],
        (2, 5): ["INT", "background", "background", "rect-place-holder", "black"],
        (2, 6): ["WIS", "background", "background", "rect-place-holder", "black"],
        (2, 7): ["CHA", "background", "background", "rect-place-holder", "black"],
    }
    for key, values in ability_score_button_dict.items():
        """Set Saving throw proficiencies, change their colors and add their modifyers to screen"""
        if key[1] in [5, 6, 7]:
            bonus = 0
            gap = " "
            if values[0] in character["Saving Throw Proficiencies"]:
                ability_score_button_dict[key][4] = S.Proficient_button_color
                bonus = V.Proficiecy_bonus
            if int(bonus + V.score_modifiers[values[0]]) >= 1:
                gap = " +"
            ability_score_button_dict[key][0] = ability_score_button_dict[key][0] + ":" + gap + str(int(bonus + V.score_modifiers[values[0]]))
        else:
            gap = " "
            if V.score_modifiers[values[0]] >= 1:
                gap = " +"
            ability_score_button_dict[key][0] = ability_score_button_dict[key][0] + ":" + gap + str(int(V.score_modifiers[values[0]]))

    dtwenty = -1
    rolled_sum = -1
    dice_color = "Dark green"
    image_path = S.local_path + "/Images/Background/Roling_Dice/D20/"
    critical_fail = False
    critical_success = False
    while running:
        # V.d20_dice_images = []
        # for i in range(0, V.d20_img_count):
        #     img = pg.image.load(image_path + "/D20_" + str(i) + ".png")
        #     img = pg.transform.scale(img, (S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.2))
        #     V.d20_dice_images.append(img)
        button_width = S.SCREEN_WIDTH * 0.3
        button_height = S.SCREEN_HEIGHT * 0.05
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        F.display_text(screen, "Proficient Skills - " + S.Proficient_button_color, 20, (S.SCREEN_WIDTH * 0.85, S.SCREEN_HEIGHT * 0.02), case="C", color=S.Proficient_button_color)
        if not S.Seisure:
            F.display_text(screen, "Critical Success - Purple", 20, (S.SCREEN_WIDTH * 0.85, S.SCREEN_HEIGHT * 0.06), case="C", color="Purple")
            F.display_text(screen, "Critical Fail - Black", 20, (S.SCREEN_WIDTH * 0.85, S.SCREEN_HEIGHT * 0.1), case="C", color="Black")
        if rolled_sum != -1:
            F.display_text(screen, "Rolled: " + str(dtwenty) + "+" + str(rolled_sum - dtwenty) + "=" + str(rolled_sum), 20, (S.SCREEN_WIDTH * 0.169, S.SCREEN_HEIGHT * 0.85), case="C", color=dice_color)

        C.skill_conditions(screen)

        buttons = F.display_back_button(screen, "Back")
        x_pos = [S.SCREEN_WIDTH * 0.01, S.SCREEN_WIDTH * 0.33, S.SCREEN_WIDTH * 0.5, S.SCREEN_WIDTH * 0.67]
        y_pos = [S.SCREEN_HEIGHT * 0.15, S.SCREEN_HEIGHT * 0.22, S.SCREEN_HEIGHT * 0.29, S.SCREEN_HEIGHT * 0.36,
                 S.SCREEN_HEIGHT * 0.43, S.SCREEN_HEIGHT * 0.5, S.SCREEN_HEIGHT * 0.57, S.SCREEN_HEIGHT * 0.64,
                 S.SCREEN_HEIGHT * 0.71, S.SCREEN_HEIGHT * 0.78]

        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)
        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width / 2, button_height, ability_score_button_dict)

        F.display_text(screen, "Ability Check", 20, (S.SCREEN_WIDTH * 0.48, S.SCREEN_HEIGHT * 0.17), case="C")
        F.display_text(screen, "Saving Throw", 20, (S.SCREEN_WIDTH * 0.49, S.SCREEN_HEIGHT * 0.45), case="C")

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
                                pressed = [value[0], "Skill"]
                                pg.draw.rect(screen, "black", buttons[i], width=3)
                        for key, value in ability_score_button_dict.items():
                            if value[3] == buttons[i]:
                                pressed = [value[0], "Ability"]
                                if key[1] in [5, 6, 7]:
                                    """Hard coded"""
                                    pressed = [value[0], "Save"]
                                pg.draw.rect(screen, "black", buttons[i], width=3)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == "Back":
                        """go back"""
                        return
                    disadvantage = False
                    advantage = False
                    bonus = 0
                    dtwenty = random.randint(1, 20)
                    if pressed[1] == "Skill":
                        """SKILL CHECKS"""
                        if V.Special_Flags.get("Rage") != None:
                            if V.Skills[pressed[0].split(":")[0]][1] == "STR":
                                advantage = True
                        bonus = int(skill_dict[pressed[0].split(": ")[0]]) + int(V.Skills[pressed[0].split(": ")[0]][0])
                        ability_name = V.Skills[pressed[0].split(":")[0]][1]
                        disadvantage = Items.handle_stealth_disadvantage(pressed, disadvantage)
                        if V.Condition in ["Exhaustion lv1", "Exhaustion lv2", "Exhaustion lv3", "Exhaustion lv4", "Exhaustion lv5", "Exhaustion lv6", "Poisoned"] or V.Condition in ["Heavily Encumbered"] and ability_name in ["STR","DEX", "CON"]:
                            disadvantage = True
                        elif V.Condition in ["Incapacitated", "Paralyzed", "Petrified", "Stunned", "Unconscious", "Over Encumbered"]:
                            continue
                        disadvantage = Items.handle_armor_proficiencies(character, disadvantage, ability_name)

                    elif pressed[1] == "Ability":
                        """ABILITY CHECKS"""
                        if V.Special_Flags.get("Rage") != None:
                            if pressed[0].split(":")[0] == "STR":
                                advantage = True
                        bonus = int(pressed[0].split(":")[1])
                        if V.Condition in ["Exhaustion lv1", "Exhaustion lv2", "Exhaustion lv3", "Exhaustion lv4", "Exhaustion lv5", "Exhaustion lv6", "Poisoned"] or V.Condition in ["Heavily Encumbered"] and pressed[0].split(":")[0] in ["STR","DEX", "CON"]:
                            disadvantage = True
                        elif V.Condition in ["Incapacitated", "Paralyzed", "Petrified", "Stunned", "Unconscious", "Over Encumbered"]:
                            continue
                        disadvantage = Items.handle_armor_proficiencies(character, disadvantage, pressed[0].split(":")[0])

                    else:
                        if V.Special_Flags.get("Rage") != None:
                            if pressed[0].split(":")[0] == "STR":
                                advantage = True
                        """Saving throw"""
                        dtwenty = C.saving_throw_conditions(dtwenty, pressed)

                        if pressed[0].split(":")[0] in character["Saving Throw Proficiencies"]:
                            bonus = V.Proficiecy_bonus
                        bonus = int(V.score_modifiers[pressed[0].split(":")[0]]) + bonus

                        if V.Condition in ["Exhaustion lv3", "Exhaustion lv4", "Exhaustion lv5", "Exhaustion lv6"] or V.Condition in ["Heavily Encumbered"] and pressed[0].split(":")[0] in ["STR","DEX", "CON"]:
                            disadvantage = True
                        if V.Condition in ["Restrained"] and pressed[0].split(":")[0] in ["DEX"]:
                            disadvantage = True

                        disadvantage = Items.handle_armor_proficiencies(character, disadvantage, pressed[0].split(":")[0])

                        if V.Condition in ["Over Encumbered"]:
                            continue

                    F.Roll_3d_dice(screen, clock, "D20", str(dtwenty), (S.SCREEN_WIDTH * 0.3, S.SCREEN_HEIGHT * 0.3))
                    rolled_sum, dtwenty = handle_disadvantage_rolls(screen, clock, "1D20", dtwenty, (disadvantage, advantage), bonus)
                    dice_color, critical_fail, critical_success = A.handle_critical_fail_success_colors(dtwenty)
                    F.add_to_roll_history(dtwenty, rolled_sum, str(pressed[1]) + ": " + str(pressed[0].split(":")[0]))
                    pressed = -1



        critical_fail, critical_success = F.display_nat_20_or_1(screen, critical_fail, critical_success)
        pg.display.flip()
        clock.tick(60)

def handle_disadvantage_rolls(screen, clock, dice, first_roll_result, disadvantage, bonus):
    disadvantage, advantage = disadvantage
    if disadvantage or advantage:
        count, dice_type = dice.lower().split("d")
        if int(count) == 1:
            second_roll = random.randint(1, int(dice_type))
            F.Roll_3d_dice(screen, clock, "D" + dice_type, str(second_roll), (S.SCREEN_WIDTH * 0.4, S.SCREEN_HEIGHT * 0.3))
            if first_roll_result < second_roll:
                if disadvantage:
                    return bonus + first_roll_result, first_roll_result
                elif advantage:
                    return bonus + second_roll, second_roll
            else:
                if disadvantage:
                    return bonus + second_roll, second_roll
                elif advantage:
                    return bonus + first_roll_result, first_roll_result
        else:
            """not done yet"""
            F.print_debug("CANT DO MULTIPLE DICE ROLLS", [count, dice_type], "ERROR")
    else:
        return bonus + first_roll_result, first_roll_result

def display_mob_skills(mob, screen, clock):
    running = True
    character = V.character_dict[V.char_name]
    text_size = 30
    pressed = -1
    skill_dict = {}
    skill_list = character["Skills"].split(",")
    mob_saving_throw_bonuses = mob["Saving Throws"]
    mob_skill_bonuses = []
    if mob["Skills"] != None:
        mob_skill_bonuses = mob["Skills"].split(" ")

    mob_skill_bonuses_refactored = {item.split(":")[0] for item in mob_skill_bonuses}

    V_Skills = copy.deepcopy(V.Skills)  # Use deepcopy to avoid shared references

    AB_dict = {"STR":0,
               "DEX":1,
               "CON":2,
               "INT":3,
               "WIS":4,
               "CHA":5,
               }

    """add mob bonuses to skills"""
    for skill_name, value in V_Skills.items():
        V_Skills[skill_name][0] = 0
        if skill_name in mob_skill_bonuses_refactored:
            for sk in mob_skill_bonuses:
                if skill_name == sk.split(":")[0]:
                    add = sk.split(":")[1].strip("+")
                    V_Skills[skill_name][0] = int(add)

    button_dict = {
        (0, 0): ["Acrobatics", "background", "background", "rect-place-holder", "black"],
        (0, 1): ["Animal Handling", "background", "background", "rect-place-holder", "black"],
        (0, 2): ["Arcana", "background", "background", "rect-place-holder", "black"],
        (0, 3): ["Athletics", "background", "background", "rect-place-holder", "black"],
        (0, 4): ["Deception", "background", "background", "rect-place-holder", "black"],
        (0, 5): ["History", "background", "background", "rect-place-holder", "black"],
        (0, 6): ["Insight", "background", "background", "rect-place-holder", "black"],
        (0, 7): ["Intimidation", "background", "background", "rect-place-holder", "black"],
        (0, 8): ["Investigation", "background", "background", "rect-place-holder", "black"],
        (3, 0): ["Medicine", "background", "background", "rect-place-holder", "black"],
        (3, 1): ["Nature", "background", "background", "rect-place-holder", "black"],
        (3, 2): ["Perception", "background", "background", "rect-place-holder", "black"],
        (3, 3): ["Performance", "background", "background", "rect-place-holder", "black"],
        (3, 4): ["Persuasion", "background", "background", "rect-place-holder", "black"],
        (3, 5): ["Religion", "background", "background", "rect-place-holder", "black"],
        (3, 6): ["Sleight of Hand", "background", "background", "rect-place-holder", "black"],
        (3, 7): ["Stealth", "background", "background", "rect-place-holder", "black"],
        (3, 8): ["Survival", "background", "background", "rect-place-holder", "black"],
    }
    """Make a skill dict for easyer use"""
    if len(skill_list) == 18:
        for skill in skill_list:
            skill_dict[skill.split(":")[0]] = int(skill.split(":")[1])

    """reform the colors of the buttons. colored: Proficient"""
    for key in button_dict.keys():
        if skill_dict[button_dict[key][0]] > 1:
            button_dict[key][4] = S.Proficient_button_color
        else:
            skill_dict[button_dict[key][0]] = 0

        gap = ": "
        """adds skill dict and V_Skills V_Skills holds the values added from ability modifyers, skill dict adds from proficiencies"""
        if skill_dict[button_dict[key][0]] + V_Skills[button_dict[key][0]][0] > 0:
            gap = ": +"
        button_dict[key][0] += gap + str(skill_dict[button_dict[key][0]] + V_Skills[button_dict[key][0]][0])

    ability_score_button_dict = {
        (1, 1): ["STR", "background", "background", "rect-place-holder", "black"],
        (1, 2): ["DEX", "background", "background", "rect-place-holder", "black"],
        (1, 3): ["CON", "background", "background", "rect-place-holder", "black"],
        (2, 1): ["INT", "background", "background", "rect-place-holder", "black"],
        (2, 2): ["WIS", "background", "background", "rect-place-holder", "black"],
        (2, 3): ["CHA", "background", "background", "rect-place-holder", "black"],
        (1, 5): ["STR", "background", "background", "rect-place-holder", "black"],
        (1, 6): ["DEX", "background", "background", "rect-place-holder", "black"],
        (1, 7): ["CON", "background", "background", "rect-place-holder", "black"],
        (2, 5): ["INT", "background", "background", "rect-place-holder", "black"],
        (2, 6): ["WIS", "background", "background", "rect-place-holder", "black"],
        (2, 7): ["CHA", "background", "background", "rect-place-holder", "black"],
    }
    for key, values in ability_score_button_dict.items():

        if key[1] in [5, 6, 7]:
            """Set Saving throw proficiencies, change their colors and add their modifyers to screen"""
            bonus = 0
            gap = " "
            if values[0] in character["Saving Throw Proficiencies"]:
                ability_score_button_dict[key][4] = S.Proficient_button_color
                bonus = V.Proficiecy_bonus
            if int(bonus + V.score_modifiers[values[0]]) >= 1:
                gap = " +"
            if mob_saving_throw_bonuses.split(",")[AB_dict[values[0]]] != "":
                bonus += int(mob_saving_throw_bonuses.split(",")[AB_dict[values[0]]])
            ability_score_button_dict[key][0] = ability_score_button_dict[key][0] + ":" + gap + str(int(bonus + V.score_modifiers[values[0]]))
        else:
            """Set Ability score stats"""
            gap = " "
            if V.score_modifiers[values[0]] >= 1:
                gap = " +"
            if ability_score_button_dict[key][0]  in ["INT", "WIS", "CHA"]:
                ability_score_button_dict[key][0] = ability_score_button_dict[key][0] + ":" + gap + str(int(V.score_modifiers[values[0]]))
            else:
                """Add mob scores"""
                score_mod = math.floor((int(mob["Ability Score"].split(",")[key[1] - 1]) - 10)/2)
                gap = " "
                if score_mod >= 1:
                    gap = " +"
                ability_score_button_dict[key][0] = ability_score_button_dict[key][0] + ":" + gap + str(score_mod)

    dtwenty = -1
    rolled_sum = -1
    dice_color = "Dark green"
    image_path = S.local_path + "/Images/Background/Roling_Dice/D20/"
    critical_fail = False
    critical_success = False
    while running:
        # V.d20_dice_images = []
        # for i in range(0, V.d20_img_count):
        #     img = pg.image.load(image_path + "/D20_" + str(i) + ".png")
        #     img = pg.transform.scale(img, (S.SCREEN_WIDTH * 0.2, S.SCREEN_HEIGHT * 0.2))
        #     V.d20_dice_images.append(img)
        button_width = S.SCREEN_WIDTH * 0.3
        button_height = S.SCREEN_HEIGHT * 0.05
        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        F.display_text(screen, "Proficient Skills - " + S.Proficient_button_color, 20,(S.SCREEN_WIDTH * 0.85, S.SCREEN_HEIGHT * 0.02), case="C", color=S.Proficient_button_color)
        if not S.Seisure:
            F.display_text(screen, "Critical Success - Purple", 20, (S.SCREEN_WIDTH * 0.85, S.SCREEN_HEIGHT * 0.06),
                           case="C", color="Purple")
            F.display_text(screen, "Critical Fail - Black", 20, (S.SCREEN_WIDTH * 0.85, S.SCREEN_HEIGHT * 0.1),
                           case="C", color="Black")
        if rolled_sum != -1:
            F.display_text(screen, "Rolled: " + str(dtwenty) + "+" + str(rolled_sum - dtwenty) + "=" + str(rolled_sum),
                           20, (S.SCREEN_WIDTH * 0.169, S.SCREEN_HEIGHT * 0.85), case="C", color=dice_color)

        C.skill_conditions(screen)

        buttons = F.display_back_button(screen, "Back")
        x_pos = [S.SCREEN_WIDTH * 0.01, S.SCREEN_WIDTH * 0.33, S.SCREEN_WIDTH * 0.5, S.SCREEN_WIDTH * 0.67]
        y_pos = [S.SCREEN_HEIGHT * 0.15, S.SCREEN_HEIGHT * 0.22, S.SCREEN_HEIGHT * 0.29, S.SCREEN_HEIGHT * 0.36,
                 S.SCREEN_HEIGHT * 0.43, S.SCREEN_HEIGHT * 0.5, S.SCREEN_HEIGHT * 0.57, S.SCREEN_HEIGHT * 0.64,
                 S.SCREEN_HEIGHT * 0.71, S.SCREEN_HEIGHT * 0.78]

        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)
        buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width / 2, button_height,ability_score_button_dict)

        F.display_text(screen, "Ability Check", 20, (S.SCREEN_WIDTH * 0.48, S.SCREEN_HEIGHT * 0.17), case="C")
        F.display_text(screen, "Saving Throw", 20, (S.SCREEN_WIDTH * 0.49, S.SCREEN_HEIGHT * 0.45), case="C")

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
                                pressed = [value[0], "Skill"]
                                pg.draw.rect(screen, "black", buttons[i], width=3)
                        for key, value in ability_score_button_dict.items():
                            if value[3] == buttons[i]:
                                pressed = [value[0], "Ability"]
                                if key[1] in [5, 6, 7]:
                                    """Hard coded"""
                                    pressed = [value[0], "Save"]
                                pg.draw.rect(screen, "black", buttons[i], width=3)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == "Back":
                        """go back"""
                        return
                    disadvantage = False
                    bonus = 0
                    dtwenty = random.randint(1, 20)

                    if pressed[1] == "Skill":
                        bonus = int(skill_dict[pressed[0].split(": ")[0]]) + int(V_Skills[pressed[0].split(": ")[0]][0])
                        if V.Condition in ["Exhaustion lv1", "Exhaustion lv2", "Exhaustion lv3", "Exhaustion lv4",
                                           "Exhaustion lv5", "Exhaustion lv6", "Poisoned"]:
                            disadvantage = True
                        elif V.Condition in ["Incapacitated", "Paralyzed", "Petrified", "Stunned", "Unconscious"]:
                            continue
                    elif pressed[1] == "Ability":
                        bonus = int(pressed[0].split(":")[1])
                        if V.Condition in ["Exhaustion lv1", "Exhaustion lv2", "Exhaustion lv3", "Exhaustion lv4",
                                           "Exhaustion lv5", "Exhaustion lv6", "Poisoned"]:
                            disadvantage = True
                        elif V.Condition in ["Incapacitated", "Paralyzed", "Petrified", "Stunned", "Unconscious"]:
                            continue
                    else:
                        """Saving throw"""
                        dtwenty = C.saving_throw_conditions(dtwenty, pressed)

                        if pressed[0].split(":")[0] in character["Saving Throw Proficiencies"]:
                            bonus = V.Proficiecy_bonus
                        bonus = int(V.score_modifiers[pressed[0].split(":")[0]]) + bonus
                        if mob_saving_throw_bonuses.split(",")[AB_dict[pressed[0].split(":")[0]]] != "":
                            bonus += int(mob_saving_throw_bonuses.split(",")[AB_dict[pressed[0].split(":")[0]]])
                        if V.Condition in ["Exhaustion lv3", "Exhaustion lv4", "Exhaustion lv5", "Exhaustion lv6"]:
                            disadvantage = True
                        if V.Condition in ["Restrained"] and pressed[0].split(":")[0] in ["DEX"]:
                            disadvantage = True

                    F.Roll_3d_dice(screen, clock, "D20", str(dtwenty), (S.SCREEN_WIDTH * 0.3, S.SCREEN_HEIGHT * 0.3))
                    rolled_sum, dtwenty = handle_disadvantage_rolls(screen, clock, "1D20", dtwenty,(disadvantage, False), bonus)
                    dice_color, critical_fail, critical_success = A.handle_critical_fail_success_colors(dtwenty)
                    F.add_to_roll_history(dtwenty, rolled_sum, str(pressed[1]) + ": " + str(pressed[0].split(":")[0]))
                    pressed = -1

        critical_fail, critical_success = F.display_nat_20_or_1(screen, critical_fail, critical_success)

        pg.display.flip()
        clock.tick(60)
