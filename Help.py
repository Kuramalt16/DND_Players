import Functions as F, Settings as S, Variables as V
import pygame as pg, random

def render_help(screen, clock):
    running = True
    text_size = 30
    pressed = -1
    # button_dict = {
    #     (0, 0): ["Manage Spells", "background", "background", "rect-place-holder", "black"],
    # }
    rect_dict = {}
    hovering_mouse = -1
    scroll = 0
    help_dice = ["4", "6", "8", "10", "12", "20"]
    dtwenty = 0
    while running:
        mini_window_w = S.SCREEN_WIDTH * 0.3
        mini_window_h = S.SCREEN_HEIGHT * 0.3
        text_surface = pg.Surface((mini_window_w, mini_window_h), pg.SRCALPHA)

        F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        buttons = F.display_back_button(screen, "Back")
        Combat_start_x = S.SCREEN_WIDTH * 0.02
        Conditions_start_x = S.SCREEN_WIDTH * 0.22
        Others_x = S.SCREEN_WIDTH * 0.42
        House_rules_x = S.SCREEN_WIDTH * 0.62
        start_y = S.SCREEN_HEIGHT * 0.02
        gap = S.SCREEN_WIDTH * 0.01
        step_y = 0
        F.display_text(screen, "Combat: ", 20, (Combat_start_x, start_y))
        if dtwenty != 0:
            F.display_text(screen, "Rolled: " + str(dtwenty), 20, (S.SCREEN_WIDTH * 0.8, S.SCREEN_HEIGHT * 0.8), color="Dark Green")

        for value in list(V.Actions.keys()):
            step_y += S.SCREEN_HEIGHT * 0.03
            rect = F.display_text(screen, value, 15, (Combat_start_x + gap, start_y + step_y))
            rect_dict[value] = rect

        step_y = 0
        F.display_text(screen, "Conditions: ", 20, (Conditions_start_x, start_y))
        for value in list(V.Conditions.keys()):
            step_y += S.SCREEN_HEIGHT * 0.03
            rect = F.display_text(screen, value, 15, (Conditions_start_x + gap, start_y + step_y))
            rect_dict[value] = rect

        step_y = 0
        F.display_text(screen, "Other things: ", 20, (Others_x, start_y))
        for value in (V.Other_caviots.keys()):
            step_y += S.SCREEN_HEIGHT * 0.03
            rect = F.display_text(screen, value, 15, (Others_x + gap, start_y + step_y))
            rect_dict[value] = rect

        step_y = 0
        F.display_text(screen, "House Rules: ", 20, (House_rules_x, start_y))
        for value in (V.House_Rules.keys()):
            step_y += S.SCREEN_HEIGHT * 0.03
            rect = F.display_text(screen, value, 15, (House_rules_x + gap, start_y + step_y))
            rect_dict[value] = rect

        x = S.SCREEN_WIDTH / (10)
        y = S.SCREEN_HEIGHT * 0.8
        w = S.SCREEN_WIDTH * 0.1
        h = S.SCREEN_HEIGHT * 0.1
        r = pg.Rect(0, y, 0, 0)
        pg.draw.line(screen, "black",  (0, y), (S.SCREEN_WIDTH, y), width=3)

        for d in range(1, len(help_dice) + 1):
            r = pg.Rect(x + r.x, r.y, w, h)
            di = help_dice[d - 1]
            folder_path = S.local_path + "\\images\\Background\\Roling_Dice\\" + di
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
                S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                for i in range(0, len(buttons)):
                    if buttons[i].collidepoint(mouse_pos):
                        if i == 0:
                            pressed = "Back"
                        else:
                            pressed = i
                        pg.draw.rect(screen, "black", buttons[i], width=3)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if pressed != -1:
                    if pressed == "Back":
                        return
                    else:
                        dice = help_dice[pressed-1]
                        dtwenty = random.randint(1, int(dice))
                        F.Roll_3d_dice(screen, clock, "D" + str(dice), str(dtwenty), (S.SCREEN_WIDTH * 0.5, S.SCREEN_HEIGHT * 0.5))
                        F.add_to_roll_history(str(dtwenty), str(dtwenty), "Help: D" + dice)

                    pressed = -1
            elif event.type == pg.MOUSEMOTION:
                mouse_pos = pg.mouse.get_pos()
                didnt_find_it = True
                for name, rect in rect_dict.items():
                    if isinstance(rect, pg.Rect) and rect.collidepoint(mouse_pos):
                        hovering_mouse = [name, rect]
                        didnt_find_it = False
                        break
                if didnt_find_it:
                    hovering_mouse = -1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 4 or event.type == pg.KEYDOWN and event.key == pg.K_UP:
                scroll += 1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5 or event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                scroll -= 1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 2 or event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
                scroll = 0

        if hovering_mouse != -1:
            text_surface = pg.Surface((mini_window_w, mini_window_h), pg.SRCALPHA)
            temp_surface = pg.Surface((mini_window_w, mini_window_h * 5), pg.SRCALPHA)
            F.add_image_to_screen(text_surface, "background", (0, 0, mini_window_w, mini_window_h), "Background")
            pg.draw.rect(text_surface, "black", pg.Rect(0, 0, mini_window_w, mini_window_h), width=2)
            F.display_text(temp_surface, hovering_mouse[0], 15,(mini_window_w * 0.02, mini_window_w * 0.02))
            step_y = 0
            if hovering_mouse[0] in list(V.Actions.keys()):
                data_dict = V.Actions
            elif hovering_mouse[0] in list(V.Conditions.keys()):
                data_dict = V.Conditions
            elif hovering_mouse[0] in list(V.Other_caviots.keys()):
                data_dict = V.Other_caviots
            else:
                data_dict = V.House_Rules
            r = pg.Rect(0, 0, 0, 0)
            if data_dict[hovering_mouse[0]].get("Description") != None:
                """Display the description for weapons"""
                r = F.display_text(temp_surface, "Description: ", 10,(mini_window_w * 0.02, mini_window_h * 0.15 + step_y))
                for word in data_dict[hovering_mouse[0]]["Description"].split(" "):
                    if word == "\n":
                        r.w = 0
                        r.x = mini_window_w * 0.02
                        step_y += mini_window_h * 0.1
                        continue
                    r = F.display_text(temp_surface, word + " ", 10, (r.x + r.w, mini_window_h * 0.15 + step_y))
                    if r.x + r.w >= mini_window_w * 0.9:
                        r.w = 0
                        r.x = mini_window_w * 0.02
                        step_y += mini_window_h * 0.1

            if r.y + r.h > mini_window_h:
                """if the window is small, expand it"""
                text_surface_enlarged = pg.Surface((mini_window_w * 1.05, r.y + r.h + mini_window_h * 0.1), pg.SRCALPHA)
                F.add_image_to_screen(text_surface_enlarged, "background", (0, 0, mini_window_w * 1.05, r.y + r.h + mini_window_h * 0.05), "Background")
                pg.draw.rect(text_surface_enlarged, "black", pg.Rect(0, 0, mini_window_w * 1.05, r.y + r.h + mini_window_h * 0.05), width=2)
                text_surface_enlarged.blit(temp_surface, (0, scroll * 20))
                text_surface = text_surface_enlarged.copy()

            text_surface.blit(temp_surface, (0, scroll * 20))

        mouse_pos = pg.mouse.get_pos()
        screen.blit(text_surface, mouse_pos)

        pg.display.flip()
        clock.tick(60)

""" In SubClass Action_Type dictates what needs to be done.
 *Learnable Spell* will have a key called *Spells" the first list member could be [ADD] second member is the amount, third and on will be names of spells/cantrips
 *Free Cantrip* needs a new key called *Cantrip* to be created inside a list, first list member, command, [ADD,CHOOSE], second member, amount, third member list of cantrips or {CANTRIPS:Druid}
 *Spell_Slot* needs to have *Spell_slot* key which dictates how many spell slots are gained, *Dice* key which dictates what type of dice is used, and *reset* key which dictates when the slots are replenished. reset may be [LR, SR] reset can be "inf", Dice may be [1d6, 1d4, 1d8, 1d10, 1d20] or if not used then it doesn't need to be there, Spell_slot will be a list first member can be ["COMMAND", "ADD"] if the first member is command, second is variable name, could be ["Char"] third one will be a key in the dictionary ["Class"] fourth one will be the value to be found ["Warlock", "Druid"] fifth one will be another key ["Level"] sixth one will be any additions or subtractions ["+1", "/2"] if the first is "ADD" then second member is how much example: ["1"]  
 *Free Spell* Needs a new key called *Spell* to be created inside a list, first list member command [ADD,CHOOSE], second member, amount, third member, list of spells or {SPELLS:Druid} or {CHOSEN|variable to check in chosen dict|values:where:to:find:them} example: {CHOSEN|Land:Subclass path|} Can have the extra key "Cost" which dictates what can be used to cast this spell if it isnt present just use spell slots 
 *Subclass path* needs a new key called *Subclass* and a key called *Outcome* in the outcome there will be spells or cantrips that are displayed for the player to make a better choise, in the *Subclass* will be choises or just add like before
 *Changed_Spell_Slot* needs a new key called *Change* in there is a list which shows what to do: First would could be ["REMOVE"] second amount, third which one, example: ["REMOVE", "1", "Wild Shape"] after casting, removes one wildshape.
 *Reaction still unknown
 *Weapon Attack must have Damage_Dice which has the dice needed to roll and Modifyer for a modifyer
 *Char_buf still unknown, but should have a property key and how much to increese it
 """


""" V.spell_slots Holds data like this: Name of the feature, spell """

""" in Spells.json the Spell Type key dictates what damage the spell can do, this doesnt work when the spell type is Heal 
when Higher levels apply add a key called *Level Up* and a list in it e.g. ["ADD"] first member, second key of what needs to be improved e.g. ["Damage", "Damage_extra"] third member by how much e.g. ["1d6"], forth member since what level.
If spell does two damages, aka roll once for hit and twice for effect add a list to damage, only programed for two, and add a list for typing aswell
If spell has  "Material" then the material must be entered as the name in the item dict, also it can be "GOLD:10" in gold pieces (gp) if the second member of the list is False: Material consumed, if True spellcasting focus can be used
"""

"""in Class.json if you add --Code you need to add that feature to the class_based_features.json
"""

""" in Class_based_features.json
 *Class_Spell_Slot* new thing but the same as Spell_Slot just for classes specificly, Spell_Slot is for subclasses
 *Choise* new thing for niche things.
 *Class_Spell_Slot_and_spell* a the same as Class_spell_slot and Free spell combined requires: "Spell_slot": ["ADD", "Proficiency Bonus"], "reset": "LR" and "Spell": ["ADD","2", spell list"] reset can be "inf
"""

"""Special_Flags variable will hold special flags, very niche based stuff, currently in use for Natural Recovery and Wild Companion if flag is set when short resting can recuperate some spell slots. if special flag needs to be used, it has to be entered in the subclass.json as a new key and current example is "Special_Flag": ["SR"], ["CAST"] basicly when is special flag activated. also they need to be programed in Special_needs.py"""


""" TEMPLATE """
# def display_char_spells(character, screen, clock):
#     running = True
#     text_size = 30
#     pressed = -1
#     button_dict = {
#         (0, 0): ["Manage Spells", "background", "background", "rect-place-holder", "black"],
#     }
#     while running:
#         button_width = S.SCREEN_WIDTH * 0.2
#         button_height = S.SCREEN_HEIGHT * 0.05
#         F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
#         buttons = F.display_back_button(screen, "Back")
#         x_pos = [S.SCREEN_WIDTH * 0.05, S.SCREEN_WIDTH * 0.62]
#         y_pos = [S.SCREEN_HEIGHT * 0.05, S.SCREEN_HEIGHT * 0.12]
#         buttons = buttons + F.display_any_buttons(screen, x_pos, y_pos, button_width, button_height, button_dict)
#
#         for event in pg.event.get():
#             keys = pg.key.get_pressed()
#             if event.type == pg.QUIT:
#                 running = False
#             elif event.type == pg.VIDEORESIZE:
#                 # Update window size based on new dimensions
#                 S.SCREEN_WIDTH, S.SCREEN_HEIGHT = event.w, event.h
#                 screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)
#             if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
#                 mouse_pos = pg.mouse.get_pos()
#                 for i in range(0, len(buttons)):
#                     if buttons[i].collidepoint(mouse_pos):
#                         pressed = "Back"
#                         for key, value in button_dict.items():
#                             if value[3] == buttons[i]:
#                                 pressed = value[0]
#                         pg.draw.rect(screen, "black", buttons[i], width=3)
#             elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
#                 if pressed != -1:
#                     if pressed == "Back":
#                         return
#                     pressed = -1
#
#         pg.display.flip()
#         clock.tick(60)