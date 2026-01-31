import time

import Settings as S, pygame as pg, os, Variables as V, pymysql
import json, random, math, datetime
import base64
from PIL import Image
from io import BytesIO
def display_text(screen ,text ,size, pos_tuple, color="black", case="TL", alpha=255, italic=True, rotate=0, invert_colors=False):
    if color == "black":
        color = S.Standart_color
    if S.Fonts.get(('Times New Roman', int(size + S.RESOLUTION * 10))) == None:
        font = pg.font.SysFont('Times New Roman', int(size + S.RESOLUTION * 10), bold=True, italic=italic)
        S.Fonts[('Times New Roman', int(size + S.RESOLUTION * 10))] = font
    else:
        font = S.Fonts[('Times New Roman', int(size + S.RESOLUTION * 10))]
    if text != None:
        text = text.encode('utf-8').decode('utf-8')
        text = text.replace("'", "'")
        text = text.replace('â€™', "'")
    text_surface = font.render(text, True, color)
    if rotate != 0:
        text_surface = pg.transform.rotate(text_surface, rotate)

    text_surface.set_alpha(alpha)  # Set the alpha (transparency)
    text_rect = text_surface.get_rect()
    if case == "TL":
        text_rect.topleft = pos_tuple
    elif case == "C":
        text_rect.center = pos_tuple


    if invert_colors:
        arr = pg.surfarray.pixels3d(text_surface).copy()
        alpha_arr = pg.surfarray.pixels_alpha(text_surface).copy()

        mask_black_invisible = (
                (arr[:, :, 0] == 0) &
                (arr[:, :, 1] == 0) &
                (arr[:, :, 2] == 0) &
                (alpha_arr > 0)  # Only affect visible pixels
        )
        mask_black_visible = (
                (arr[:, :, 0] == 0) &
                (arr[:, :, 1] == 0) &
                (arr[:, :, 2] == 0)
        )
        arr[mask_black_visible] = [0, 120, 255]
        pg.surfarray.blit_array(text_surface, arr)

        arr[mask_black_invisible] = [255, 255, 255]
        pg.surfarray.blit_array(text_surface, arr)



    screen.blit(text_surface, text_rect)
    return text_rect

def get_all_char_classes(character):
    if ", " in character["Class"]:
        character_class_1, character_class_2 = character["Class"].split(", ")
    else:
        character_class_1, character_class_2 = character["Class"], None
    if character.get("SubClass") != None:
        if ", " in character["SubClass"]:
            character_sub_class_1, character_sub_class_2 = character["SubClass"].split(", ")
        else:
            character_sub_class_1, character_sub_class_2 = character["SubClass"], None
    else:
        character_sub_class_1, character_sub_class_2 = None, None

    return [character_class_1, character_class_2, character_sub_class_1, character_sub_class_2]



def dont_display_text(screen ,text ,size, pos_tuple, color="black", case="TL", alpha=255, italic=True, rotate=0):
    if color == "black":
        color = S.Standart_color
    if S.Fonts.get(('Times New Roman', int(size + S.RESOLUTION * 10))) == None:
        font = pg.font.SysFont('Times New Roman', int(size + S.RESOLUTION * 10), bold=True, italic=italic)
        S.Fonts[('Times New Roman', int(size + S.RESOLUTION * 10))] = font
    else:
        font = S.Fonts[('Times New Roman', int(size + S.RESOLUTION * 10))]
    if text != None:
        text = text.encode('utf-8').decode('utf-8')
        text = text.replace("'", "'")
    text_surface = font.render(text, True, color)
    if rotate != 0:
        text_surface = pg.transform.rotate(text_surface, rotate)

    text_surface.set_alpha(alpha)  # Set the alpha (transparency)
    text_rect = text_surface.get_rect()
    if case == "TL":
        text_rect.topleft = pos_tuple
    elif case == "C":
        text_rect.center = pos_tuple
    return text_rect


def add_image_to_screen(screen, name, rect, case):
    # Dictionary for case to image folder mapping
    case_to_folder = {
        "background": "Images/Background",
        "player": "Images/Players",
        "map": "Images/Maps",
        "armor": "Images/Items/Armour",  # armor or armour
        "armour": "Images/Items/Armour",
        "weapon": "Images/Items/Weapons",
        "weapons": "Images/Items/Weapons",
        "mount": "Images/Items/Mount",
        "ingredient": "Images/Items/Ingredient",
        "potion": "Images/Items/Potions",  # potion or potions
        "potions": "Images/Items/Potions",
        "magic weapon": "Images/Items/Magic Weapon",
        "magic armor": "Images/Items/Magic Armour",  # magic armor or magic armour
        "magic armour": "Images/Items/Magic Armour",
        "wonderous": "Images/Items/Wonderous Item",  # wonderous or wonderous item
        "wonderous item": "Images/Items/Wonderous Item",
        "food": "Images/Items/Food",
        "special": "Images/Items/Special",
        "mob": "Images/Mobs",
        "campaign": "Images/Campaign",
        "d20": "Images/Background/Roling_Dice/D20",
        "conditions": "Images/Background/Conditions",
        "rite": "Images/Background/Rites",
        "race": "Images/Data/Race"
    }

    # Convert case to lowercase and use it to find the folder
    case = case.lower()
    case = case_to_folder.get(case, case)  # Default to original case if not found in the dictionary
    if name == "background":
        name = S.Background_image
    if isinstance(rect, tuple) and len(rect) == 4:
        rect = pg.Rect(rect[0], rect[1], rect[2], rect[3])
    if isinstance(rect, pg.Rect) and len(rect) == 4:
        if os.path.exists(S.local_path + "/" + case + "/" + name + ".png") and name.lower() + ".png" != "con.png":
            filepath = S.local_path + "/" + case + "/" + name + ".png"
        elif os.path.exists(S.local_path + "/" + case + "/" + name + ".jpg") and name.lower() + ".jpg" != "con.jpg":
            filepath = S.local_path + "/" + case + "/" + name + ".jpg"
        elif case.lower() != "player":
            print_debug("path doesn't exist", S.local_path + "/" + case + "/" + name + ".png", debug="ERROR")
            return None

        if filepath != None:
            # print_debug(filepath)
            if V.images.get((filepath, (rect.w, rect.h))) == None:
                img = pg.image.load(filepath)
                img = pg.transform.scale(img, (rect[2], rect[3]))
                V.images[(filepath, (rect.w, rect.h))] = img
            else:
                img = V.images[(filepath, (rect.w, rect.h))].copy()
            screen.blit(img, (rect[0], rect[1]))
            return rect
    else:
        print_debug("wrong rect type or length", debug="ERROR")


def add_entry_to_list(rect, name, screen, text, text_size, text_pos):
    if not isinstance(rect, pg.Rect) and len(rect) == 4:
        rect = pg.Rect(rect[0], rect[1], rect[2], rect[3])

    display_text(screen, text, text_size, text_pos)
    pg.draw.rect(screen, "black", rect, width=2)
    return rect

def flash_marker(selected_entry, entries, screen, timer, text_dict):
    """ flash entry marker"""
    if selected_entry != -1 and timer <= 5:
        pushx = 5
        property = list(text_dict.keys())[selected_entry]
        if text_dict[property][0] != "":
            pushx = 5 + text_dict[property][1].w
        pg.draw.line(screen, "black", (entries[selected_entry].x + pushx, entries[selected_entry].y), (entries[selected_entry].x + pushx, entries[selected_entry].y + entries[selected_entry].h - 1))

def reset_timer(timer):
    return (timer + 1) % 10

def update_text(text_dict, entries, screen, hidden=False):
    id = 0
    a = ""
    for key, (text, text_rect) in text_dict.items():
        if hidden:
            for i in range(len(text)):
                a += "*"
            text_rect = display_text(screen, a, 20, (entries[id].x + 5, entries[id].y))
        else:
            text_rect = display_text(screen, text, 20, (entries[id].x + 5, entries[id].y))
        text_dict[key] = [text, text_rect]
        id += 1


def read_db_table(table_name):
    if table_name in ["characters", "armour", "weapons", "mount", "food", "potions", "ingredient", "special",
                      "magic weapon", "magic armour", "Wonderous Item", "monsters", "maps", "campaign", "communication"]:

        print_debug("Attempting to read from table:", table_name, debug="INFO")

        # Establishing connection
        connection = None
        try:
            connection = Connect_to_MySql()
            print_debug("Connected successfully", debug="INFO")

            cursor = connection.cursor()
            sql = f"SELECT * FROM `{table_name}`"
            print_debug("Attempting to execute SQL:", sql, debug="INFO")
            cursor.execute(sql)
            print_debug("Executed successfully", debug="INFO")

            result = cursor.fetchall()
            print_debug("Data fetched successfully", debug="INFO")
            cursor.close()
            connection.close()
            return result

        except pymysql.MySQLError as e:
            print_debug(f"MySQL error occurred: {e}", debug="ERROR")
            if 'MySQL server has gone away' in str(e):
                print_debug("MySQL server connection lost!", debug="ERROR")
            return None
        except Exception as e:
            print_debug(f"An error occurred: {e}", debug="ERROR")
            return None

    else:
        print_debug(f"No connection possible, {table_name} doesn't exist.", debug="ERROR")
        return None


def Connect_to_MySql():
    host = 'lockyourdoors'
    user = 'PyDND'
    password = 'Gythfg167!'
    database = 'dnd'

    print_debug("Attempting to connect to MySQL...", debug="INFO")
    try:
        connection = pymysql.connect(host=host, user=user, password=password, database=database, charset='utf8',
                                     use_unicode=True, connect_timeout=10)
        return connection
    except pymysql.MySQLError as e:
        print_debug(f"MySQL error occurred while connecting: {e}", debug="ERROR")
        return None
    except Exception as e:
        print_debug(f"Error occurred while connecting: {e}", debug="ERROR")
        return None

def add_to_dict_db_results(add_dict, to_dict, type):
    for value in add_dict:
        if type == "mobs":
            to_dict[value[0]] = {
                "Challange": value[1],
                "Health": [value[2], value[2]],
                "Loot": value[3],
                "Gold": value[4],
                "Ability Score": value[5],
                "Speed": value[6],
                "AC": value[7],
                "Skills": value[8],
                "Sences": value[9],
                "Saving Throws": value[10],
                "Languages": value[11],
                "Abilities": value[12],
                "Actions": value[13],
                "Resistances": value[14],
                "Immunities": value[15],
                "Vulnerabilities": value[16],
                "Type": value[17],
                "Size": value[18],
                "Allignment": value[19],
            }
            if value[17] == "Beast":
                table = 'monsters'
                read_image_from_database(table, value[0], S.local_path + "/Images/Mobs/" + value[0] + ".png")
        elif type == "campaign":
            to_dict[value[0]] = {
                "Completed": value[1],
                "Num_of_Players": value[2],
                "First": value[3],
                "Second": value[4],
                "Third": value[5],
                "Fourth": value[6],
                "Fifth": value[6],
                "Sixth": value[7]
            }
        elif type == "maps":
            to_dict[value[0]] = {
                "Floor": value[1],
                "Loot": value[2],
                "Secret": value[3],
                "Area Count": value[4],
                "Describtion": value[5],
                "Image": value[6]
            }
        elif type == "characters":
            to_dict[value[0]] = {
                "Race": value[1],
                "Class": value[2],
                "Experience": value[3],
                "Level": value[4],
                "Health": [value[5], value[5]],
                "Ability_Scores": value[6],
                "Background": value[7],
                "Alignment": value[8],
                "Gold": value[9],
                "AC": value[10],
                "Skills": value[11],
                "Speed": value[12],
                "Immunity": value[13],
                "Resistance": value[14],
                "Vulnerabilities": value[15],
                "Languages": value[16],
                "Items": value[17],
                "Spell Slots": value[19],
                "Extra": value[20],
            }
            # AS = to_dict[value[0]]["Ability_Scores"]
            # if AS != None:
        elif type == "communications":
            to_dict[value[0]] = {
                "Magic items": value[1],
                "Skills": int(value[2]),
                "Spells": int(value[3]),
                "Features": int(value[4]),
                "Actions": int(value[5]),
                "Name": int(value[6]),
                "Apperance": int(value[7]),
                "Race": int(value[8]),
                "Class": int(value[9]),
            }

        elif not type:
            to_dict[value[0]] = {
                "Cost": value[1],
                "Weight": value[2],
                "Properties": value[3],
                "Type": value[4],
                "Extra": value[5],
                "image": value[6],
            }
            table = value[4]
            read_image_from_database(table, value[0], S.local_path + "/Images/Items/" + value[4] + "/" + value[0] + ".png")

        else:
            to_dict[value[0]] = {
                "Rarity": value[1],
                "Properties": value[2],
                "Describtion": value[3],
                "Attunement": value[4],
                "Cost": value[5],
                "Type": value[6],
                "Extra": value[7],
                "image": value[8],
            }

            table = value[6]
            if value[6] == "Armour":
                table = "magic armour"
            read_image_from_database(table, value[0], S.local_path + "/Images/Items/" + table + "/" + value[0] + ".png")
    return to_dict

def read_image_from_database(table, name, output_path):
    if os.path.exists(output_path):
        # print_debug("image already saved", output_path)
        return
    if os.path.exists(output_path.replace(".png", ".jpg")):
        # print_debug("image already saved", output_path.replace(".png", ".jpg"))
        return
    else:
        connection = Connect_to_MySql()
        cursor = connection.cursor()
        sql = "SELECT `Image` FROM `%s` WHERE `Name` = '%s' LIMIT 1" % (table, name)
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            image_blob = result[0]
            with open(output_path, "wb") as f:
                f.write(image_blob)
            print_debug("Image saved to:", output_path, debug="INFO")
        else:
            print_debug("No image found for the specified name.", name, debug="ERROR")
        cursor.close()
        connection.close()


def display_other_buttons(screen, text_size, button_pos, dict):
    x_pos = button_pos[0]
    screen_top = button_pos[1]
    button_width = button_pos[2]
    button_height = button_pos[3]
    buttons = []
    for iteration, (text, path_name, path_case, rect, color) in dict.items():
        rect = pg.Rect(x_pos[iteration], screen_top, button_width, button_height)
        buttons.append(rect)
        add_button_to_screen(screen, path_name, rect, path_case)
        display_text(screen, text, text_size, (x_pos[iteration] + rect.w / 2, screen_top + rect.h / 2), color, "C")
    return buttons

def add_button_to_screen(screen, name, rect, case):
    if case.lower() == "background":
        case = "Images/Background"
    if case.lower() == "conditions":
        case = "Images/Background/Conditions"
    if case.lower() == "items":
        case = "Images/Items"
    if case.lower() == "rites":
        case = "Images/Background/Rites"
    if case.lower() == "race":
        case = "Images/Data/Race"
    if case.lower() == "class":
        case = "Images/Data/Class"
    if isinstance(rect, pg.Rect) or isinstance(rect, tuple) and len(rect) == 4:
        try:
            if V.images.get((S.local_path + "/" + case + "/" + name + ".png", rect[2], rect[3])) == None:
                V.images[(S.local_path + "/" + case + "/" + name + ".png", rect[2], rect[3])] = pg.image.load(S.local_path + "/" + case + "/" + name + ".png").convert_alpha()
            img = V.images[(S.local_path + "/" + case + "/" + name + ".png", rect[2], rect[3])].copy()
        except Exception as e:
            if V.images.get((S.local_path + "/" + case + "/" + name + ".jpg", rect[2], rect[3])) == None:
                V.images[(S.local_path + "/" + case + "/" + name + ".jpg", rect[2], rect[3])] = pg.image.load(S.local_path + "/" + case + "/" + name + ".jpg").convert_alpha()
            img = V.images[(S.local_path + "/" + case + "/" + name + ".jpg", rect[2], rect[3])].copy()

        smaller_rect = rect[0] + rect[2] * 0.005, rect[1] + rect[3] * 0.005, rect[2] * 0.99, rect[3] * 0.99
        img = pg.transform.scale(img, (smaller_rect[2], smaller_rect[3])).convert_alpha()
        pg.draw.rect(screen, "black", rect, width=1)
        screen.blit(img, (smaller_rect[0], smaller_rect[1]))
    else:
        print_debug("wrong rect type or length", debug="ERROR")
    return rect


def save_data(data, table):
    """
    Insert a new entry into the database, or update if the entry already exists.

    :param table_name: The name of the table to insert/update the row
    :param data: A dictionary containing column names as keys and the values to insert
    :param db_config: A dictionary with database connection details (host, user, password, database)
    """
    db_dict = {
        "characters": ["Name", "Race", "Class", "Exp", "Lv", "Hp", "Language", "Ability_Scores", "Gold", "Items", "Extra"],
        "campaign": ["Name", "Number_of_players", "First", "Second", "Third", "Fourth", "Fifth", "Sixth"]
    }
    local_dict = {
        "characters": ["Name", "Race", "Class", "Experience", "Level", "Health", "Languages", "Ability_Scores", "Gold", "Items", "Extra"],
        "campaign": ["Name", "Player Count", "Player Num 1", "Player Num 2", "Player Num 3", "Player Num 4", "Player Num 5", "Player Num 6"]

    }
    remove_list = []
    for i in range(0, len(local_dict[table])):
        if data.get(local_dict[table][i]) == None:
            remove_list.append(i)

    for i in reversed(remove_list):  # Iterate backwards to avoid index shifting
        local_dict[table].pop(i)
        db_dict[table].pop(i)


    result = select_from_DataBase(table, data["Name"][0])
    if result == ():
        """new entry"""
        sql = "INSERT INTO `{}` ({}) VALUES ({})".format(
            table,
            ', '.join(db_dict[table]),  # Column names
            ', '.join([f'"{str(data[local_dict[table][i]][0])}"' for i in range(len(db_dict[table]))])  # Corresponding values
        )
        print_debug(sql, debug="INFO")
        Write_to_DataBase(sql)

    else:
        """update entry"""
        sql = "UPDATE `{}` SET {} WHERE `Name` = '{}'".format(
            table,
            ', '.join(
                [f"`{db_dict[table][i]}` = '{data[local_dict[table][i]][0]}'" for i in range(len(db_dict[table]))]),
            # Set column=value pairs
            str(data[local_dict[table][0]][0])  # Where Name matches the value
        )
        print_debug(sql, debug="INFO")
        Write_to_DataBase(sql)


def save_char_to_localhost(data, table):
    """
    Insert a new entry into the database, or update if the entry already exists.

    :param table_name: The name of the table to insert/update the row
    :param data: A dictionary containing column names as keys and the values to insert
    :param db_config: A dictionary with database connection details (host, user, password, database)
    """
    db_dict = {
        "characters": ["Name", "Race", "Class", "Exp", "Lv", "Hp", "Language", "Ability_Scores", "Gold", "Items", "Extra", "Alignment"],
        "campaign": ["Name", "Number_of_players", "First", "Second", "Third", "Fourth", "Fifth", "Sixth"]
    }
    local_dict = {
        "characters": ["Name", "Race", "Class", "Experience", "Level", "Health", "Languages", "Ability_Scores", "Gold", "Items", "Extra", "Alignment"],
        "campaign": ["Name", "Player Count", "Player Num 1", "Player Num 2", "Player Num 3", "Player Num 4", "Player Num 5", "Player Num 6"]

    }
    remove_list = []
    for i in range(0, len(local_dict[table])):
        if data.get(local_dict[table][i]) == None:
            remove_list.append(i)

    for i in reversed(remove_list):  # Iterate backwards to avoid index shifting
        local_dict[table].pop(i)
        db_dict[table].pop(i)


    result = select_from_DataBase(table, data["Name"])
    if result == ():
        """new entry"""
        sql = "INSERT INTO `{}` ({}) VALUES ({})".format(
            table,
            ', '.join(db_dict[table]),  # Column names
            ', '.join([f'"{str(data[local_dict[table][i]])}"' for i in range(len(db_dict[table]))])  # Corresponding values
        )
        print_debug(sql, debug="INFO")
        Write_to_DataBase(sql)

    else:
        """update entry"""
        sql = "UPDATE `{}` SET {} WHERE `Name` = '{}'".format(
            table,
            ', '.join(
                [f"`{db_dict[table][i]}` = '{data[local_dict[table][i]]}'" for i in range(len(db_dict[table]))]),
            # Set column=value pairs
            str(data[local_dict[table][0]])  # Where Name matches the value
        )
        print_debug(sql, debug="INFO")
        Write_to_DataBase(sql)

def Write_to_DataBase(sql):
    connection = Connect_to_MySql()
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    connection.close()

def select_from_DataBase(table, name):
    sql = "SELECT * from `%s` where `Name`='%s'" % (table, name)
    result = Excecute_MySQL_string(sql)
    return result

def Excecute_MySQL_string(sql):
    connection = Connect_to_MySql()
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def display_spell_slots(screen, show_slots):
    slot_surf = 0
    if V.spell_slots != {} and show_slots == 1:

        if V.images.get("SLOT SCREEN") == None:
            V.images["SLOT SCREEN"] = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.SRCALPHA).convert_alpha()
        slot_surf = V.images["SLOT SCREEN"]
        slot_surf.fill((0,0,0,0))
        add_image_to_screen(slot_surf, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")

        x = S.SCREEN_WIDTH * 0.95
        w = S.SCREEN_WIDTH * 0.05
        h = S.SCREEN_WIDTH * 0.05
        x_step = S.SCREEN_WIDTH * 0.06
        for slot, amount in V.spell_slots.items():
            y = S.SCREEN_HEIGHT * 0.02
            y_step = S.SCREEN_HEIGHT * 0.03
            if slot in ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th"] and V.SECRETS.get(V.char_name) != None and V.SECRETS[V.char_name]["Spells"] == 1:
                continue
            elif V.SECRETS.get(V.char_name) != None and V.SECRETS[V.char_name]["Features"] == 1:
                continue
            display_text(slot_surf, slot, 15, (x-S.SCREEN_WIDTH * 0.02, y-S.SCREEN_HEIGHT * 0.02), rotate=90)
            for i in range(0, int(amount)):
                r = add_image_to_screen(slot_surf, slot, (x, y + y_step, w, h), "background")
                if r == None:
                    add_image_to_screen(slot_surf, "1st", (x, y + y_step, w, h), "background")
                y_step += h
            x -= x_step
    return slot_surf

def display_spell_history(screen, show_hist):
    surf = 0
    if V.Roll_history != [] and show_hist == 1:
        color_cases = {"Initiative": "Navy",
                       "Cast": "Dark Purple",
                       "Extra Damage:": "Midnightblue",
                       "Damage": "Dark Red",
                       "Hit": "Maroon",
                       "Feature": "Dark Green",
                       "Rite": "Gold",
                       "Two-handed": "Sienna",
                       "Throw": "Darkslategray",
                       "Ability": "Darkorange",
                       "Save": "Darkcyan",
                       "Skill": "Indigo"
                       }
        if V.images.get("Hist_SCREEN") == None:
            V.images["Hist_SCREEN"] = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.SRCALPHA).convert_alpha()
        surf = V.images["Hist_SCREEN"]
        surf.fill((0,0,0,0))
        add_image_to_screen(surf, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
        color = "black"
        x = S.SCREEN_WIDTH * 0.1
        y = S.SCREEN_HEIGHT * 0.05
        y_step = 0
        longest_x = 0
        for data in V.Roll_history:
            time = data[0]
            case = data[1]
            rolled = data[2]
            rolled_sum = data[3]
            for cas, col in color_cases.items():
                if cas in case:
                    color = col
                    break

            l = display_text(surf, "Time: " + time, 15, (x, y + y_step))
            if longest_x < l.x + l.w:
                longest_x = l.x + l.w
            l = display_text(surf, "Rolled for: " + case, 15, (x, l.y + l.h), color=color)
            if longest_x < l.x + l.w:
                longest_x = l.x + l.w
            l = display_text(surf, "Rolled Result: " + rolled, 15, (x, l.y + l.h), color=color)
            if longest_x < l.x + l.w:
                longest_x = l.x + l.w
            l = display_text(surf, "Rolled : " + rolled_sum, 15, (x, l.y + l.h), color=color)
            if longest_x < l.x + l.w:
                longest_x = l.x + l.w
            pg.draw.line(surf, "black", (x, l.y + l.h), (longest_x, l.y + l.h))
            y_step = l.h + l.y
            if y_step >= S.SCREEN_HEIGHT * 0.8:
                y_step = 0
                x = S.SCREEN_WIDTH * 0.5
    return surf

def remove_item_from_char(item_name, char):
    item_list = char["Items"].split(",")
    print(item_name)
    item_list.remove(item_name)
    char["Items"] = ",".join(item_list)
    update_items_db(char)

    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)
    if char_config_data.get("Equiped Items") == None:
        return
    for key, item in char_config_data["Equiped Items"].items():
        if item_name in item:
            if "," in item:
                items = item.split(",")
                items.remove(item_name)
                char_config_data["Equiped Items"][key] = ",".join(items)
            else:
                char_config_data["Equiped Items"][key] = ""

    create_char_JSON(V.char_name, char_config_data)

def upload_to_json(data, json_filename, key_name):
    """
    This function uploads data to a JSON file, converting any BLOB (binary) data to base64 encoding.

    :param data: The data read from the database (could include BLOB image data).
    :param json_filename: The name of the JSON file to save data to.
    :param key_name: A unique key that identifies the data for the JSON file.
    """
    # If the data contains BLOBs, encode them as base64 strings
    temp_data = data.copy()

    # Update the JSON data with the new data
    new_data = {}
    for item_name, values in temp_data.items():
        if values["Type"].lower() == key_name.lower():
            values = encode_value(values)
            new_data[item_name] = values
    json_data = new_data  # Store the updated data under the key_name

    # Write the updated data back to the JSON file
    with open(json_filename, 'w') as file:
        json.dump(json_data, file, indent=4)

    print_debug(f"Data  has been uploaded to {json_filename}.", debug="INFO")


def encode_value(value):
    """
    Encodes the value to base64. It will handle strings and binary data (like image BLOBs) properly.

    :param value: The value to encode (could be string, number, or binary data).
    :return: Base64 encoded value (as a string).
    """
    if isinstance(value, str):
        # For strings, encode the string as bytes and then to base64
        return base64.b64encode(value.encode('utf-8')).decode('utf-8')
    elif isinstance(value, bytes):
        # For binary data (like image BLOBs), directly encode to base64
        return base64.b64encode(value).decode('utf-8')
    elif isinstance(value, (int, float)):
        # For numbers, we convert them to string first and then base64 encode
        return base64.b64encode(str(value).encode('utf-8')).decode('utf-8')
    elif isinstance(value, dict):
        for key, values in value.items():
            value[key] = encode_value(values)
        return value
    else:
        # If the value is none of the above types, return as is
        print_debug("not enocoded", value, debug="ERROR")
        return value


def encode_json_values(json_data):
    """
    This function recursively encodes the values of the JSON data.

    :param json_data: The JSON data to be encoded.
    :return: The updated JSON data with encoded values.
    """
    for key, value in json_data.items():
        if isinstance(value, dict):
            # If the value is a dictionary, recurse into it
            json_data[key] = encode_json_values(value)
        else:
            # Otherwise, encode the value
            json_data[key] = encode_value(value)
    return json_data

def read_json_item_data():

    decoded_armor_data = read_and_decode_json(S.local_path + "/Armor.json")
    decoded_food_data = read_and_decode_json(S.local_path + "/Food.json")
    decoded_Ingredient_data = read_and_decode_json(S.local_path + "/Ingredients.json")
    decoded_mArmor_data = read_and_decode_json(S.local_path + "/Magic Armor.json")
    decoded_mweapon_data = read_and_decode_json(S.local_path + "/Magic Weapons.json")
    decoded_Mounts_data = read_and_decode_json(S.local_path + "/Mounts.json")
    decoded_Potions_data = read_and_decode_json(S.local_path + "/Potions.json")
    decoded_Special_data = read_and_decode_json(S.local_path + "/Special.json")
    decoded_Weapons_data = read_and_decode_json(S.local_path + "/Weapons.json")
    decoded_Witems_data = read_and_decode_json(S.local_path + "/Wonderous Items.json")
    V.item_dict = {}
    V.item_dict.update(decoded_Witems_data)
    V.item_dict.update(decoded_Weapons_data)
    V.item_dict.update(decoded_Special_data)
    V.item_dict.update(decoded_Potions_data)
    V.item_dict.update(decoded_Mounts_data)
    V.item_dict.update(decoded_mweapon_data)
    V.item_dict.update(decoded_mArmor_data)
    V.item_dict.update(decoded_Ingredient_data)
    V.item_dict.update(decoded_food_data)
    V.item_dict.update(decoded_armor_data)

    check_and_save_images(V.item_dict, S.local_path + "/Images/Items/")
    print_debug("data collected", debug="INFO")


def check_and_save_images(item_dict, image_directory):
    """
    This function checks for each item's image, and if it does not exist in the specified path,
    it decodes the image and saves it.

    :param item_dict: The dictionary containing item data with "image" as one of the keys.
    :param image_directory: The directory where the images should be stored.
    """

    for item_name, item_data in item_dict.items():
        # Extract the image data from the 'image' key
        image_data = item_data.get('image')
        type = item_data.get("Type")
        if image_data:
            # Construct the full path to check for image
            image_path = os.path.join(image_directory + type, f"{item_name}.png")  # Assuming PNG extension
            image_path2 = os.path.join(image_directory + type, f"{item_name}.jpg")  # Assuming PNG extension

            # Check if the image already exists
            if not os.path.exists(image_path) and not os.path.exists(image_path2):
                print_debug(f"Image for '{item_name}' not found. Generating image...", debug="WARNING")
                # Save the image if it doesn't exist
                save_image(image_data, image_path2)
            # else:
            #     print_debug(f"Image for '{item_name}' already exists at {image_path}.")
        else:
            print_debug(f"No image data found for item '{item_name}'.", debug="ERROR")


def save_image(image_data, image_path):
    """
    This function saves the decoded image data to the specified image path.

    :param image_data: The decoded image data (bytes).
    :param image_path: The path where the image should be saved.
    """
    try:
        # If image_data is base64 encoded, decode it first
        if isinstance(image_data, str):  # If it's a base64 string
            image_data = base64.b64decode(image_data)

        # Convert bytes data to an image and save
        image = Image.open(BytesIO(image_data))
        image.save(image_path)  # Save as an image (auto-detected file type from extension)
        print_debug(f"Image saved to {image_path}", debug="INFO")
    except Exception as e:
        print_debug(f"Error while saving image: {e}", debug="ERROR")

def read_and_decode_json(json_filename):
    """
    This function reads a JSON file, decodes all base64 encoded values, and returns a dictionary.

    :param json_filename: The name of the JSON file to read and decode.
    :return: A dictionary with the decoded data.
    """
    try:
        # Open and read the JSON file
        with open(json_filename, 'r') as file:
            data = json.load(file)

        # Decode the values in the JSON data
        decoded_data = decode_json_values(data)
        return decoded_data

    except FileNotFoundError:
        print_debug(f"Error: The file '{json_filename}' does not exist.", debug="ERROR")

    except json.JSONDecodeError:
        print_debug(f"Error: Failed to decode JSON from the file '{json_filename}'.", debug="ERROR")
    except Exception as e:
        print_debug(f"An unexpected error occurred: {e}", debug="ERROR")


def decode_json_values(json_data):
    """
    This function recursively decodes the base64 encoded values in the JSON data.

    :param json_data: The JSON data to be decoded (should be a dictionary).
    :return: The updated JSON data with decoded values.
    """
    for key, value in json_data.items():
        if isinstance(value, dict):
            # If the value is a dictionary, recurse into it
            json_data[key] = decode_json_values(value)
        else:
            # Otherwise, decode the value
            json_data[key] = decode_value(value)
    return json_data


def decode_value(base64_string):
    """
    This function decodes a base64 encoded string back to its original value.

    :param base64_string: The base64 encoded string to decode.
    :return: The original value (string, number, or binary data).
    """
    if base64_string == None:
        return None
    decoded_bytes = base64.b64decode(base64_string)
    try:
        # Try to decode it as a UTF-8 string
        return decoded_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # If it's not a UTF-8 string (e.g., binary data), return the raw bytes
        return decoded_bytes

def display_back_button(screen, text, text_size=30, x_pos=0):
    buttons = []
    button_width = S.SCREEN_WIDTH / 5
    button_height = S.SCREEN_HEIGHT / 20
    screen_top = S.SCREEN_HEIGHT * 0.9
    if x_pos == 0:
        x_pos = [S.SCREEN_WIDTH * 0.77]
    dict = {
        0: [text, "background", "background", "rect-place-holder", "black"],
    }

    for iteration, (text, path_name, path_case, rect, color) in dict.items():
        rect = pg.Rect(x_pos[iteration], screen_top, button_width, button_height)
        buttons.append(rect)
        add_button_to_screen(screen, path_name, rect, path_case)
        display_text(screen, text, text_size, (x_pos[iteration] + rect.w / 2, screen_top + rect.h / 2), color, "C")
    return buttons

def display_any_buttons(screen, xpos, ypos, buttonW, buttonH, dict, text_size=30):
    buttons = []
    for (iX, iY), (text, path_name, path_case, rect, color) in dict.items():
        rect = pg.Rect(xpos[iX], ypos[iY], buttonW, buttonH)
        buttons.append(rect)
        dict[iX, iY][3] = rect
        add_button_to_screen(screen, path_name, rect, path_case)
        display_text(screen, text, text_size, (xpos[iX] + rect.w / 2, ypos[iY] + rect.h / 2), color, "C")
    return buttons

def display_dropbox(screen, text, pos, options, case, choise, size=(S.SCREEN_WIDTH * 0.2,S.SCREEN_HEIGHT * 0.02)):
    dropbox_rect = pg.Rect(pos[0], pos[1], size[0], size[1])
    if choise != None:
        text = choise

    pg.draw.rect(screen, "white", dropbox_rect)
    pg.draw.rect(screen, "black", dropbox_rect, width=2)
    text_size = int(size[1] / 2.4)
    display_text(screen ,text ,text_size, (pos[0] + 5, pos[1]))
    triangle_size = size[0] / 15
    start_point_x = pos[0] + triangle_size * 13.5
    start_point_y = pos[1] + triangle_size * 0.3

    if case.lower() == "closed":
        points = [(start_point_x, start_point_y), (start_point_x + triangle_size / 2, start_point_y + triangle_size), (start_point_x + triangle_size, start_point_y)]
    else:
        dropbox_rect_dict = {}
        points = [(start_point_x, start_point_y + triangle_size), (start_point_x + triangle_size / 2, start_point_y), (start_point_x + triangle_size, start_point_y + triangle_size)]
        step_y = size[1]
        for i in range(0, len(options)):
            new_rect = pg.Rect(pos[0], pos[1] + step_y, size[0], size[1])
            pg.draw.rect(screen, "white", new_rect)
            pg.draw.rect(screen, "black", new_rect, width=1)
            display_text(screen, options[i], text_size, (pos[0] + 5, pos[1] + step_y))
            step_y = step_y + size[1]
            dropbox_rect_dict[options[i]] = new_rect
        pg.draw.polygon(screen, "gray", points)
        return dropbox_rect_dict
    pg.draw.polygon(screen, "gray", points)
    return dropbox_rect

def enable_scrolling(data_list, scroll):
    for _ in range(scroll):
        data_list = data_list[1:] + [data_list[0]]
    return data_list

def Roll_Dice_gif(screen, clock, image_count, dice_images, rolled_score, pos):
    delay = 100
    image_id = 0
    start_time = pg.time.get_ticks()
    screen_copy = screen.copy()
    counter = 10
    while True:
        clear_screen = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.SRCALPHA)
        clear_screen.blit(dice_images[image_id], pos)
        if counter != 10:
            display_text(clear_screen, str(rolled_score), 15, (pos[0] + dice_images[image_id].get_size()[0] / 2, pos[1] + dice_images[image_id].get_size()[1] / 2), case='C')
        if pg.time.get_ticks() - start_time >= delay:
            image_id += 1
            start_time = pg.time.get_ticks()
            if image_id >= image_count:
                counter -= 1
                image_id -= 1
                if counter <= 0:
                    return
        screen.blit(screen_copy, (0,0))
        screen.blit(clear_screen, (0, 0))
        pg.display.flip()
        clock.tick(60)

def Roll_3d_dice(screen, clock, dice_type, dice_rolled, pos):
    if isinstance(dice_rolled, str):
        """singular dice roll"""
        if S.dice_images["Finished"].get(dice_type) != None and S.dice_images["Finished"][dice_type].get(dice_rolled) != None and S.dice_images["Finished"][dice_type][dice_rolled] == True:
            delay = 30
            image_count = len(S.dice_images[dice_type][dice_rolled])
            image_id = 0
            images = S.dice_images[dice_type][dice_rolled].copy()
            for i in range(0, image_count-1):
                img = pg.transform.scale(images[i], (S.SCREEN_WIDTH * 0.4, S.SCREEN_HEIGHT * 0.4))
                images[i] = img
            start_time = pg.time.get_ticks()
            screen_copy = screen.copy()
            while True:
                clear_screen = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.SRCALPHA)
                clear_screen.blit(images[image_id], pos)
                if pg.time.get_ticks() - start_time >= delay:
                    image_id += 1
                    start_time = pg.time.get_ticks()
                    if image_id >= image_count-1:
                        for i in range(0, 4):
                            time.sleep(0.1)
                        return
                screen.blit(screen_copy, (0, 0))
                screen.blit(clear_screen, (0, 0))
                pg.display.flip()
                clock.tick(60)
        else:
            for i in range(0, 100):
                display_text(screen, dice_type + " rolled: " + str(dice_rolled), 20, pos, case="C")
                pg.display.flip()
                clock.tick(60)

    elif isinstance(dice_rolled, list):
        """multiple dice rolls"""
        all_checks_passed = all(S.dice_images["Finished"].get(dice_type) != None and S.dice_images["Finished"][dice_type].get(str(dice_roll)) == True for dice_roll in dice_rolled)
        if all_checks_passed:
            delay = 30
            image_count = []
            image_id = []
            images = []
            finished = []
            new_pos = []
            orientation = {
                0: ((S.SCREEN_WIDTH * 0), (S.SCREEN_HEIGHT * 0)),
                1: ((S.SCREEN_WIDTH * 0.2), (S.SCREEN_HEIGHT * 0)),
                2: ((S.SCREEN_WIDTH * 0), (S.SCREEN_HEIGHT * 0.2)),
                3: ((S.SCREEN_WIDTH * 0.2), (S.SCREEN_HEIGHT * 0.2)),
                4: ((S.SCREEN_WIDTH * 0.4), (S.SCREEN_HEIGHT * 0)),
                5: ((S.SCREEN_WIDTH * 0), (S.SCREEN_HEIGHT * 0.4)),
                6: ((S.SCREEN_WIDTH * 0.4), (S.SCREEN_HEIGHT * 0.4)),
                           }
            for i in range(0, len(dice_rolled)):
                image_count.append(len(S.dice_images[dice_type][str(dice_rolled[i])]))
                image_id.append(0)
                finished.append(False)
                new_pos.append((pos[0] + orientation[i][0], pos[1] + orientation[i][1]))
                images.append(S.dice_images[dice_type][str(dice_rolled[i])].copy())
                for ii in range(0, image_count[i]-1):
                    img = pg.transform.scale(images[i][ii], (S.SCREEN_WIDTH * 0.4, S.SCREEN_HEIGHT * 0.4))
                    images[i][ii] = img
            start_time = pg.time.get_ticks()
            screen_copy = screen.copy()

            while True:
                clear_screen = pg.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.SRCALPHA)
                for i in range(0, len(dice_rolled)):
                    if image_id[i] >= len(images[i])-1:
                        image_id[i] = len(images[i])-2

                    clear_screen.blit(images[i][image_id[i]], new_pos[i])
                if pg.time.get_ticks() - start_time >= delay:
                    for i in range(0, len(dice_rolled)):
                        image_id[i] += 1
                    start_time = pg.time.get_ticks()
                    for i in range(0, len(dice_rolled)):
                        if image_id[i] >= image_count[i]-1:
                            finished[i] = True

                screen.blit(screen_copy, (0, 0))
                screen.blit(clear_screen, (0, 0))
                pg.display.flip()
                clock.tick(60)
                if all(done == True for done in finished):
                    for i in range(0, 9):
                        time.sleep(0.1)
                    return
        else:
            for i in range(0, 100):
                display_text(screen, dice_type + " rolled: " + str(dice_rolled), 20, pos, case="C")
                pg.display.flip()
                clock.tick(60)
    else:
        print_debug("unrecognised dice type, must be str or list", debug="ERROR")


def rename_images_in_folder(folder_path):
    import os
    import glob
    # Check if the folder exists
    if not os.path.isdir(folder_path):
        print_debug(f"The folder '{folder_path}' does not exist.", debug="ERROR")
        return

    # Get the folder name
    folder_name = folder_path.split("/")[-1]

    # Get all image files in the folder (assuming common image extensions)
    image_files = glob.glob(os.path.join(folder_path, '*.*'))

    # # Filter image files to include only common image formats (you can add more if needed)
    image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    # # Check if there are any image files in the folder
    if not image_files:
        print_debug(f"No image files found in the folder '{folder_path}'.", debug="ERROR")
        return
    print_debug(image_files, debug="INFO")
    num = -1
    # # Rename each image file

    for image_path in image_files:
        num += 1
        folders = image_path.split("/")
        print_debug(folders, debug="INFO")
        new_path = ""
        for i in range(0, len(folders)-1):
            new_path += folders[i] + "/"
        new_path += folder_name + "/"
        file = folders[-1].split("\\")[1]
        try:
            number = str(num) + ".png"
            new_path += folder_name + "_" + number
            os.rename(image_path, new_path)
        except IndexError:
            print_debug("INDEX ERROR", debug="ERROR")
        # print_debug(new_path)

# def fix_files(folder_path):
#     import os
#     import glob
#     # Check if the folder exists
#     if not os.path.isdir(folder_path):
#         print_debug(f"The folder '{folder_path}' does not exist.")
#         return
#
#     # Get the folder name
#     folder_name = folder_path.split("/")[-1]
#
#     # Get all image files in the folder (assuming common image extensions)
#     image_files = glob.glob(os.path.join(folder_path, '*.*'))
#
#     # # Filter image files to include only common image formats (you can add more if needed)
#     image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
#
#     # # Check if there are any image files in the folder
#     if not image_files:
#         print_debug(f"No image files found in the folder '{folder_path}'.")
#         return
#     sorted_files = natural_sort(image_files)
#
#     num = -1
#     # # Rename each image file
#
#     for image_path in sorted_files:
#         num += 1
#         folders = image_path.split("/")
#         new_path = ""
#         for i in range(0, len(folders)-1):
#             new_path += folders[i] + "/"
#         new_path += folder_name + "/"
#         file = folders[-1].split("\\")[1]
#         try:
#             number = str(num) + ".png"
#             new_path += folder_name + "_" + number
#             os.rename(image_path, new_path)
#         except IndexError:
#             print_debug("INDEX ERROR")


def natural_sort(filenames):
    # Helper function to extract the numeric part of a filename
    def extract_numbers(filename):
        # Split the filename by non-digit characters and convert the numeric parts to integers
        number_part = ''.join(c if c.isdigit() else ' ' for c in filename)
        return list(map(int, number_part.split()))

    # Sort filenames based on the numeric parts
    return sorted(filenames, key=extract_numbers)

def update_items_db(char):
    V.character_dict[V.char_name] = char.copy()
    sql = "UPDATE `characters` SET `Items`='%s' where `Name`='%s'" % (char["Items"], V.char_name)
    Write_to_DataBase(sql)

def update_gold_db(char):
    sql = "UPDATE `characters` SET `Gold`='%s' where `Name`='%s'" % (char["Gold"], V.char_name)
    Write_to_DataBase(sql)


def display_nat_20_or_1(screen, critical_fail, critical_success):
    if S.Seisure and critical_fail:
        for i in range(0, 10):
            screen.fill("Black")
            display_text(screen, "CRITICAL FAIL", 50, (S.SCREEN_WIDTH / 2, S.SCREEN_HEIGHT / 2), color="White",case="C")
            pg.display.flip()
            time.sleep(0.1)
            screen.fill("white")
            display_text(screen, "CRITICAL FAIL!!!", 50, (S.SCREEN_WIDTH / 2, S.SCREEN_HEIGHT / 2), color="black", case="C")
            pg.display.flip()
            time.sleep(0.1)
        critical_fail = False
    elif S.Seisure and critical_success:
        for i in range(0, 2):
            screen.fill("Gold")
            display_text(screen, "NAT 20!!!", 50, (S.SCREEN_WIDTH / 2, S.SCREEN_HEIGHT / 2), color="Purple", case="C")
            pg.display.flip()
            time.sleep(0.5)
            screen.fill("Purple")
            display_text(screen, "NAT 20!!!", 50, (S.SCREEN_WIDTH / 2, S.SCREEN_HEIGHT / 2), color="Gold", case="C")
            pg.display.flip()
            time.sleep(0.5)
        critical_success = False
    return critical_fail, critical_success

def display_notice(screen, notice, pos):
    if notice != []:
        display_text(screen, notice[0], 20, pos, color="red")
        notice[1] -= 1
        if notice[1] <= 0:
            notice = []
    return notice


def reset_spellSlots(SR_or_LR):
    """Adds spell slots based on class"""
    if SR_or_LR != "SR":
        V.spell_slots = {}
        classes = []
        classes.append(V.character_dict[V.char_name]["Class"].split(", "))
        if V.character_dict[V.char_name].get("SubClass") != None:
            classes.append(V.character_dict[V.char_name]["SubClass"].split(","))
        position = lambda x, t: 0 if x == t[0] else 1 if x == t[-1] else None
        for i in range(0, len(classes)):
            for char_class in classes[i]:
                level = V.character_dict[V.char_name]["Level"].split(",")[position(char_class, classes[i])]
                if V.Available_spells_data.get(char_class) != None:
                    slots = V.Available_spells_data[char_class][int(level)][3]
                    if slots != "":
                        for slot in slots.split(","):
                            type, amount = slot.split(":")
                            if V.spell_slots.get(type) == None:
                                V.spell_slots[type] = 0
                            V.spell_slots[type] += int(amount)

    for feature, values in S.Class_features.items():
        if values['Action_Type'] == "Spell_Slot" and values.get("Class") != None and values["Class"] in V.character_dict[V.char_name]["Class"]:
            if "reset" in values and SR_or_LR == values["reset"] or SR_or_LR == "LR":
                """If reset matches the rest or its a long rest"""
                if values["Spell_slot"][0] == "COMMAND":
                    if values["Spell_slot"][1] == "Char":
                        variable = V.character_dict[V.char_name]
                    elif values["Spell_slot"][1] == "MODIFIER":
                        variable = V.score_modifiers
                    else:
                        print_debug("MASTER I DONT GET IT, THE FIRST VARIABLE ISNT CHARACTER I NEED HELP IN Functions->reset_spellSlots", values["Spell_slot"][1], debug="ERROR")

                    if len(values["Spell_slot"]) == 6:
                        index = variable[values["Spell_slot"][2]].split(", ").index(values["Spell_slot"][3])
                        value = variable[values["Spell_slot"][4]].split(",")[index]
                        if "+" in values["Spell_slot"][5]:
                            value = int(value) + int(values["Spell_slot"][5].split("+")[1])
                        elif "/" in values["Spell_slot"][5]:
                            value = int(value) / int(values["Spell_slot"][5].split("/")[1])
                            value = math.floor(value)
                    else:
                        value = int(variable[values["Spell_slot"][2]])
                        if len(values["Spell_slot"]) == 5:
                            add_or_subtract = values["Spell_slot"][3]
                            amount = values["Spell_slot"][4]
                            if add_or_subtract == "+":
                                value += int(amount)
                            else:
                                value -= int(amount)
                    V.spell_slots[feature] = value
                elif values["Spell_slot"][0] == "ADD":
                    if values["Spell_slot"][1] == "Proficiency Bonus":
                        V.spell_slots[feature] = V.Proficiecy_bonus
                    else:
                        V.spell_slots[feature] = int(values["Spell_slot"][1])
                else:
                    slots = values["Spell_slot"].split(":")
                    index = V.character_dict[V.char_name]["Class"].split(", ").index(slots[0])
                    level = V.character_dict[V.char_name]["Level"].split(",")[index]
                    V.spell_slots[feature] = int(level) + int(slots[1].split("+")[1])
        if values["Action_Type"] == "Changed_Spell_Slot" and values.get("Class") != None and values["Class"] in V.character_dict[V.char_name]["Class"]:
            if "ADD" in S.Class_features[feature]["Change"][0]:
                amount = 1
                if feature == "Blood Maledict" and "Curse Specialist" in V.character_dict[V.char_name]["Code"]:
                    amount += 1

                if feature not in V.spell_slots:
                    V.spell_slots[feature] = amount
        if values['Action_Type'] in ["Spell_Slot"] and values.get("Race") != None and values["Race"] in V.character_dict[V.char_name]["Race"]:
            if "reset" in values and SR_or_LR == values["reset"] or SR_or_LR == "LR":
                """If reset matches the rest or its a long rest"""
                if values["Spell_slot"][0] == "COMMAND":
                    if values["Spell_slot"][1] == "Char":
                        variable = V.character_dict[V.char_name]
                    elif values["Spell_slot"][1] == "MODIFIER":
                        variable = V.score_modifiers
                    else:
                        print_debug(
                            "MASTER I DONT GET IT, THE FIRST VARIABLE ISNT CHARACTER I NEED HELP IN Functions->reset_spellSlots",
                            values["Spell_slot"][1], debug="ERROR")

                    if len(values["Spell_slot"]) == 6:
                        index = variable[values["Spell_slot"][2]].split(", ").index(values["Spell_slot"][3])
                        value = variable[values["Spell_slot"][4]].split(",")[index]
                        if "+" in values["Spell_slot"][5]:
                            value = int(value) + int(values["Spell_slot"][5].split("+")[1])
                        elif "/" in values["Spell_slot"][5]:
                            value = int(value) / int(values["Spell_slot"][5].split("/")[1])
                            value = math.floor(value)
                    else:
                        value = int(variable[values["Spell_slot"][2]])
                        if len(values["Spell_slot"]) == 5:
                            """["COMMAND", "MODIFIER", "CON", "+", "1"]"""
                            add_or_subtract = values["Spell_slot"][3]
                            amount = values["Spell_slot"][4]
                            if add_or_subtract == "+":
                                value += int(amount)
                            else:
                                value -= int(amount)
                        else:
                            print_debug("Probbly doesnt work", value, "Error")
                    V.spell_slots[feature] = value
                elif values["Spell_slot"][0] == "ADD":
                    if values["Spell_slot"][1] == "Proficiency Bonus":
                        V.spell_slots[feature] = V.Proficiecy_bonus
                    else:
                        V.spell_slots[feature] = int(values["Spell_slot"][1])
                else:
                    slots = values["Spell_slot"].split(":")
                    index = V.character_dict[V.char_name]["Class"].split(", ").index(slots[0])
                    level = V.character_dict[V.char_name]["Level"].split(",")[index]
                    V.spell_slots[feature] = int(level) + int(slots[1].split("+")[1])
    if V.Rites != {}:
        for rite in V.Rites:
            V.Rites[rite] = ""



def remove_spell_slot(spell_slot_lv):
    slots = V.spell_slots
    slot_level = level_to_name(spell_slot_lv)
    if slots.get(slot_level) != None:
        if slots[slot_level] != 1:
            slots[slot_level] -= 1
        else:
            del slots[slot_level]
        return True
    else:
        return False

def level_to_name(level):
    dictionary = {
        "1": "1st",
        "2": "2nd",
        "3": "3rd",
    }
    if level.isdigit():
        if dictionary.get(level) != None:
            return dictionary[level]
        else:
            return str(level) + "th"
    else:
        return level

def DEATH(screen, clock):
    """
    Displays multiple instances of the word "DEATH" at random positions and angles,
    gradually increasing the number of words on the screen, with decreasing intervals
    between the appearance of each new word.

    Parameters:
    - screen: The Pygame screen object where the animation will be displayed.
    - clock: The Pygame clock object to control the frame rate.
    """
    # Set colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    # Define the text
    text = "DEATH"
    max_words = 1000

    # List to hold the word data
    words = []

    # Set the initial interval time (in milliseconds) and the minimum interval
    time_interval = 100  # Start with 3 seconds
    min_interval = 1  # Minimum interval (0.1 seconds)

    # Time tracking
    last_time_added = pg.time.get_ticks()  # Time when the last word was added
    current_time = last_time_added

    # Game loop
    running = True
    while running:
        # Handle events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        # Fill the screen with black
        screen.fill(BLACK)
        # Check if enough time has passed to add a new word
        current_time = pg.time.get_ticks()
        if current_time - last_time_added >= time_interval and len(words) < max_words:
            # Randomly choose the size, position, and angle for the new word
            word_data = {
                'text': text,
                'size': random.randint(30, 100),  # Random size
                'x': random.randint(0, screen.get_width()),  # Random x position
                'y': random.randint(0, screen.get_height()),  # Random y position
                'angle': random.randint(0, 360)  # Random angle
            }
            words.append(word_data)

            # Update the last time a word was added
            last_time_added = current_time

            # Decrease the interval, but don't go below the minimum interval
            time_interval = max(min_interval, time_interval - 10)  # Decrease by 10ms after each word

        # Draw all words on the screen
        for word_data in words:
            # Create a font with the size of the word
            font = pg.font.SysFont("Arial", word_data['size'])
            # Render the text
            text_surface = font.render(word_data['text'], True, WHITE)
            # Rotate the text to the specified angle
            rotated_text = pg.transform.rotate(text_surface, word_data['angle'])
            # Get the rect of the text for positioning
            text_rect = rotated_text.get_rect(center=(word_data['x'], word_data['y']))
            # Draw the rotated text
            screen.blit(rotated_text, text_rect)

        # Update the screen
        pg.display.flip()

        # Cap the frame rate (60 FPS)
        clock.tick(60)

def check_if_choise_was_already_made(choise_name):
    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)
    if char_config_data.get("Choises") == None:
        return False
    else:
        if char_config_data["Choises"].get(choise_name) == None:
            return False
        else:
            return char_config_data["Choises"][choise_name]
def save_choise_json(choise_name, result):
    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)
    if char_config_data.get("Choises") == None:
        char_config_data["Choises"] = {}
    if char_config_data["Choises"].get(choise_name) == None:
        char_config_data["Choises"][choise_name] = result
    create_char_JSON(V.char_name, char_config_data)

def create_char_JSON(char_name, data):
    json_output = json.dumps(data, indent=4)
    # Define the filename using char_name, adding .json extension
    filename = f"{S.local_path}/Created_Players/{char_name}_config.json"

    # Write the JSON output to the file
    with open(filename, "w") as file:
        file.write(json_output)

def get_equiped_weapons():
    weapon_list = ["Unarmed Strike", "Improvised Attack"]
    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)
    if char_config_data.get("Equiped Items") != None:
        for key, value in char_config_data["Equiped Items"].items():
            if key in ["Weapons", "Magic Weapon"] and value != "":
                if "," in value:
                    items = value.split(",")
                    weapon_list += items
                else:
                    weapon_list.append(value)
    return weapon_list

def get_equiped_armor():
    """Gets equiped ermor list, excludes shields"""
    armor_list = []
    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)
    if char_config_data.get("Equiped Items") != None:
        for key, value in char_config_data["Equiped Items"].items():
            if key in ["Armour", "Magic Armour"] and value != "":
                if "," in value:
                    items = value.split(",")
                    armor_list += items
                else:
                    armor_list.append(value)
    return armor_list

def save_equiped_items(equiped_items_dict):
    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)
    if char_config_data.get("Equiped Items") == None:
        char_config_data["Equiped Items"] = {}
    for type, name in equiped_items_dict.items():
        if char_config_data["Equiped Items"].get(type) == None:
            char_config_data["Equiped Items"][type] = ""
        char_config_data["Equiped Items"][type] = name
    create_char_JSON(V.char_name, char_config_data)


def print_debug(text, variable=None, debug="info"):
    RESET = "\033[0m"
    INFO_COLOR = "\033[32m"  # Green
    WARNING_COLOR = "\033[33m"  # Yellow
    ERROR_COLOR = "\033[31m"  # Red
    DEBUG_COLOR = "\033[34m"  # Blue

    color = {
        "info": INFO_COLOR,
        "error": ERROR_COLOR,
        "warning": WARNING_COLOR,
        "debug": DEBUG_COLOR
    }
    if variable:
        print(f"{color[debug.lower()]}[{debug.upper()}] {text}: {variable}{RESET}")
    else:
        print(f"{color[debug.lower()]}[{debug.upper()}] {text}{RESET}")

def add_to_roll_history(dtwenty, rolled_sum, case):
    time = datetime.datetime.now()
    V.Roll_history.append([str(time.hour) + ":" + str(time.minute) + ":" + str(time.second), case, str(dtwenty), str(rolled_sum)])
    if len(V.Roll_history) > 10:
        V.Roll_history.pop(0)

def save_text_to_json(text):
    with open(S.local_path + '/Created_Players/' + V.char_name + '_config.json', 'r') as file:
        char_config_data = json.load(file)
    if char_config_data.get("Notes") == None:
        char_config_data["Notes"] = ""
    char_config_data["Notes"] = text
    create_char_JSON(V.char_name, char_config_data)



