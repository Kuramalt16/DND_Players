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
        # text = text.encode('utf-8').decode('utf-8')
        text = text.replace("'", "'")
        text = text.replace('â€™', "'")
        text = text.replace('ā€™', "'")
        text = text.replace('â€“', "-")
        text = text.replace('ā€“', "-")
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
        filepath = None
        if os.path.exists(S.local_path + "/" + case + "/" + name + ".png") and name.lower() + ".png" != "con.png":
            filepath = S.local_path + "/" + case + "/" + name + ".png"
        elif os.path.exists(S.local_path + "/" + case + "/" + name + ".jpg") and name.lower() + ".jpg" != "con.jpg":
            filepath = S.local_path + "/" + case + "/" + name + ".jpg"
        elif case != "Images/Players":
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
    host = '192.168.0.135'
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
                "LevelUp": int(value[10])
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


def save_data(data, table, case=None):
    """
    Insert a new entry into the database, or update if the entry already exists.

    :param table_name: The name of the table to insert/update the row
    :param data: A dictionary containing column names as keys and the values to insert
    :param db_config: A dictionary with database connection details (host, user, password, database)
    """
    db_dict = {
        "characters": ["Name", "Race", "Class", "Lv", "Hp", "Language", "Ability_Scores", "Gold", "Items", "Extra"],
        "campaign": ["Name", "Number_of_players", "First", "Second", "Third", "Fourth", "Fifth", "Sixth"]
    }
    local_dict = {
        "characters": ["Name", "Race", "Class", "Level", "Health", "Languages", "Ability_Scores", "Gold", "Items", "Extra"],
        "campaign": ["Name", "Player Count", "Player Num 1", "Player Num 2", "Player Num 3", "Player Num 4", "Player Num 5", "Player Num 6"]

    }
    remove_list = []
    for i in range(0, len(local_dict[table])):
        if data.get(local_dict[table][i]) == None:
            remove_list.append(i)

    for i in reversed(remove_list):  # Iterate backwards to avoid index shifting
        local_dict[table].pop(i)
        db_dict[table].pop(i)


    if case == None:
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
            local_dict[table].remove("Ability_Scores")
            db_dict[table].remove("Ability_Scores")
            sql = "UPDATE `{}` SET {} WHERE `Name` = '{}'".format(
                table,
                ', '.join(
                    [f"`{db_dict[table][i]}` = '{data[local_dict[table][i]][0]}'" for i in range(len(db_dict[table]))]),
                # Set column=value pairs
                str(data[local_dict[table][0]][0])  # Where Name matches the value
            )
            print_debug(sql, debug="INFO")
            Write_to_DataBase(sql)
    else:
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

def display_spell_slots(screen, slot_to_display):
    plus_minus_slot_rects = {}
    if V.spell_slots != {}:

        x = S.SCREEN_WIDTH * 0.95
        w = S.SCREEN_WIDTH * 0.05
        h = S.SCREEN_WIDTH * 0.05
        x_step = S.SCREEN_WIDTH * 0.06
        y = S.SCREEN_HEIGHT * 0.32
        y_step = S.SCREEN_HEIGHT * 0.03
        diferent_slot_count = 0
        for slot, amount in V.max_spell_slots.items():
            diferent_slot_count += 1
            if slot in ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th"] and V.SECRETS.get(V.char_name) != None and V.SECRETS[V.char_name]["Spells"] == 1:
                continue
            elif V.SECRETS.get(V.char_name) != None and V.SECRETS[V.char_name]["Features"] == 1:
                continue
            display_text(screen, slot, 15, (x-S.SCREEN_WIDTH * 0.02, y-S.SCREEN_HEIGHT * 0.02), rotate=90)
            r = add_image_to_screen(screen, slot, (x, y + y_step, w, h), "background")
            display_text(screen, str(V.spell_slots[slot]) + "/" + str(amount), 15, (r.x + r.w * 0.5, r.y + r.h * 0.8))
            plus_r = pg.Rect(r.x, r.y, r.w * 0.5, r.h)
            minus_r = pg.Rect(r.x + r.w * 0.5, r.y, r.w * 0.5, r.h)
            if slot_to_display == (slot, "Plus"):
                pg.draw.rect(screen, "green", plus_r)
                display_text(screen, "+", 15, (plus_r.x + plus_r.w * 0.5, plus_r.y + plus_r.h * 0.5), case="C")

            if slot_to_display == (slot, "Minus"):
                pg.draw.rect(screen, "red", minus_r)
                display_text(screen, "-", 15, (minus_r.x + minus_r.w * 0.5, minus_r.y + minus_r.h * 0.5), case="C")

            plus_minus_slot_rects[slot] = {}
            plus_minus_slot_rects[slot]["Plus"] = plus_r
            plus_minus_slot_rects[slot]["Minus"] = minus_r
            if r == None:
                add_image_to_screen(screen, "1st", (x, y + y_step, w, h), "background")
            x -= x_step
            if diferent_slot_count == 3:
                diferent_slot_count = 0
                x = S.SCREEN_WIDTH * 0.95
                y += y_step*3
    return plus_minus_slot_rects

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
    if item_name == "Spellcasting_Focus":
        return
    item_list.remove(item_name)
    char["Items"] = ",".join(item_list)
    update_items_db(char)
    if item_name not in char["Items"]:
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

def Roll_3d_dice(screen, clock, dice_type, dice_rolled, pos=None):
    if pos == None:
        pos = (S.SCREEN_WIDTH * 0.25, S.SCREEN_HEIGHT * 0.25)
    if isinstance(dice_rolled, str):
        """singular dice roll"""
        if S.dice_images["Finished"].get(dice_type) != None and S.dice_images["Finished"][dice_type].get(dice_rolled) != None and S.dice_images["Finished"][dice_type][dice_rolled] == True:
            delay = 30
            image_count = len(S.dice_images[dice_type][dice_rolled])
            image_id = 0
            images = S.dice_images[dice_type][dice_rolled].copy()
            # for i in range(0, image_count-1):
            #     img = pg.transform.scale(images[i], (S.SCREEN_WIDTH * 0.4, S.SCREEN_HEIGHT * 0.4))
            #     images[i] = img
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
        V.max_spell_slots = {}
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
                            if V.max_spell_slots.get(type) == None:
                                V.max_spell_slots[type] = 0
                            V.spell_slots[type] += int(amount)
                            V.max_spell_slots[type] += int(amount)

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
                    V.max_spell_slots[feature] = value
                elif values["Spell_slot"][0] == "ADD":
                    if values["Spell_slot"][1] == "Proficiency Bonus":
                        V.spell_slots[feature] = V.Proficiecy_bonus
                        V.max_spell_slots[feature] = V.Proficiecy_bonus
                    else:
                        V.spell_slots[feature] = int(values["Spell_slot"][1])
                        V.max_spell_slots[feature] = int(values["Spell_slot"][1])
                else:
                    slots = values["Spell_slot"].split(":")
                    index = V.character_dict[V.char_name]["Class"].split(", ").index(slots[0])
                    level = V.character_dict[V.char_name]["Level"].split(",")[index]
                    V.spell_slots[feature] = int(level) + int(slots[1].split("+")[1])
                    V.max_spell_slots[feature] = int(level) + int(slots[1].split("+")[1])
        if values["Action_Type"] == "Changed_Spell_Slot" and values.get("Class") != None and values["Class"] in V.character_dict[V.char_name]["Class"]:
            if "ADD" in S.Class_features[feature]["Change"][0]:
                amount = 1
                if feature == "Blood Maledict" and "Curse Specialist" in V.character_dict[V.char_name]["Code"]:
                    amount += 1

                if feature not in V.spell_slots:
                    V.spell_slots[feature] = amount
                    V.max_spell_slots[feature] = amount
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
                    V.max_spell_slots[feature] = value
                elif values["Spell_slot"][0] == "ADD":
                    if values["Spell_slot"][1] == "Proficiency Bonus":
                        V.spell_slots[feature] = V.Proficiecy_bonus
                        V.max_spell_slots[feature] = V.Proficiecy_bonus
                    else:
                        V.spell_slots[feature] = int(values["Spell_slot"][1])
                        V.max_spell_slots[feature] = int(values["Spell_slot"][1])
                else:
                    slots = values["Spell_slot"].split(":")
                    index = V.character_dict[V.char_name]["Class"].split(", ").index(slots[0])
                    level = V.character_dict[V.char_name]["Level"].split(",")[index]
                    V.spell_slots[feature] = int(level) + int(slots[1].split("+")[1])
                    V.max_spell_slots[feature] = int(level) + int(slots[1].split("+")[1])
    if V.Rites != {}:
        for rite in V.Rites:
            V.Rites[rite] = ""



def remove_spell_slot(spell_slot_lv):
    slots = V.spell_slots
    slot_level = level_to_name(spell_slot_lv)
    if slots.get(slot_level) != None and slots[slot_level] != 0:
        if slots[slot_level] != 1:
            slots[slot_level] -= 1
        else:
            # del slots[slot_level]
            slots[slot_level] = 0
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

def get_ammo_count(weapon_list):
    ammo_count = {}
    for weapon in weapon_list:
        if V.item_dict[weapon].get("Extra") != None and V.item_dict[weapon].get("Properties") != None:
            if "Ammunition" in V.item_dict[weapon]["Properties"] and weapon in V.character_dict[V.char_name]["Items"]:
                items = V.character_dict[V.char_name]["Items"].split(",")
                ammo_count[weapon] = items.count(weapon)
                if items[0] == "":
                    V.character_dict[V.char_name]["Items"] = ",".join(items[1:])
    return ammo_count

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


def get_mob_actions():
    for mob in V.mob_dict:
        if mob in ["Azrael", "Lilit"]:
            continue
        print_results = False
        abilities = V.mob_dict[mob]["Abilities"].split(", ")
        actions = V.mob_dict[mob]["Actions"].split(", ")
        V.mob_dict[mob]["Real_Abilities"] = {}
        V.mob_dict[mob]["Real_Actions"] = {}
        ability_score = V.mob_dict[mob]["Ability Score"].split(",")
        mob_name = mob.replace("Ochre Jelly", "jelly").replace("Rock Gnome Recluse", "gnome").replace("Giant Rat",
                                                                                                      "rat").replace(
            "Vine Blight", "blight").replace("Anchorite of Talos", "anchorite").replace("Dire Wolf", "wolf").replace(
            "Young White Dragon", "dragon").replace("Young Red Dragon", "dragon").replace("Vampire Spawn",
                                                                                          "vampire").replace(
            "Brown Bear", "bear").lower()

        mob_modifyers = {
            "STR": (int(ability_score[0]) - 10) // 2,
            "DEX": (int(ability_score[1]) - 10) // 2,
            "CON": (int(ability_score[2]) - 10) // 2,
            "INT": (int(ability_score[3]) - 10) // 2,
            "WIS": (int(ability_score[4]) - 10) // 2,
            "CHA": (int(ability_score[5]) - 10) // 2,
        }
        if print_results: print(mob)
        prof_bonus = 2
        if mob in ["Vampire Spawn", "Wraith", "Young White Dragon"]:
            prof_bonus = 3
        elif mob in ["Young Red Dragon"]:
            prof_bonus = 4

        if abilities != [""]:
            for ability in abilities:
                text = ""
                if ability in ["Aggressive"]:
                    text += "As a bonus action, "

                if ability in ["Shapechanger"]:
                    if mob == "Mimic":
                        into_ = "an object"
                    elif mob == "Anchorite of Talos":
                        into_ = "a boar"
                    text = f"The {mob_name} can use its action to polymorph into {into_} or back into its true form. Its statistics are the same in each form. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies."
                elif ability in ["Grappler"]:
                    text = f"The {mob_name} has advantage on attack rolls against any creature grappled by it."
                elif ability in ["Adhesive (object)"]:
                    text = f"The {mob_name} adheres to anything that touches it. A Huge or smaller creature adhered to the {mob_name} is also grappled by it (escape DC 13). Ability checks made to escape this grapple have disadvantage."
                elif ability in ["False Appearance (object)", "False Appearance"]:
                    if mob == "Mimic":
                        from_ = "an ordinary object"
                    elif mob == "Vine Blight":
                        from_ = "a tangle of vines"
                    text = f"While the {mob_name} remains motionless, it is indistinguishable from {from_}."
                elif ability in ["Tail Spike Regrowth"]:
                    text = f"The {mob_name} has twenty-four tail spikes. Used spikes regrow when the {mob_name} finishes a long rest."
                elif ability in ["Amorphous"]:
                    text = f"The {mob_name} can move through a space as narrow as 1 inch wide without squeezing."
                elif ability in ["Spider Climb"]:
                    text = f"The {mob_name} can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check."
                elif ability in ["Gnome Cunning"]:
                    text = f"The {mob_name} has advantage on Intelligence, Wisdom, and Charisma saving throws against magic."
                elif ability in ["Spellcasting"]:
                    text = f"The {mob_name} is a 2nd-level spellcaster. Its spellcasting ability is Intelligence (spell save DC 12, +4 to hit with spell attacks). It has the following wizard spells prepared: Cantrips (at will): mage hand, prestidigitation, ray of frost 1st level (3 slots): detect magic, mage armor, magic missile, shield"
                elif ability in ["Aggressive"]:
                    text += f"the {mob_name} can move up to its speed toward a hostile creature that it can see."
                elif ability in ["Charge"]:
                    if mob == "Cow":
                        damage = "7 (2d6) piercing"
                    elif mob == "Boar":
                        damage = "3 (1d6) slashing"
                    text += f"If the {mob_name} moves at least 20 feet straight toward a target and then hits it with an attack on the same turn, the target takes an extra {damage} damage. If the target is a creature, it must succeed on a DC 11 Strength saving throw or be knocked prone."

                elif ability in ["Pack Tactics"]:
                    text += f"The {mob_name} has advantage on an attack roll against a creature if at least one of the {mob_name}'s allies is within 5 feet of the creature and the ally isn't incapacitated."
                elif ability in ["Innate Spellcasting"]:
                    text += f"The {mob_name}'s innate spellcasting ability is Wisdom (spell save DC 12). It can innately cast the following spells, requiring no material components: 3/day: thunderwave (2d8 damage) 1/day each: augury, bless, lightning bolt (8d6 damage), revivify"
                elif ability in ["Relentless"]:
                    text += f"(Recharges after a Short or Long Rest). If the {mob_name} takes 7 damage or less that would reduce it to 0 hit points, it is reduced to 1 hit point instead."

                elif ability in ["Reabsorbing Skin"]:
                    text += f"If a creature touches the {mob_name} or hits it with a melee attack while within 5 feet of it, the {mob_name} deals 3(1d6) acid damage to that creature and regains hit points equal to half the damage dealt."
                elif ability in ["Gliding"]:
                    text += f"It takes a successful DC 16 Wisdom (Perception) check to hear the {mob_name} move."
                elif ability in ["Small Creature"]:
                    text += f"The {mob_name} Armour Class increases to 16 when target is at least 60 ft. away."
                elif ability in ["Silent Flight"]:
                    text += f"The {mob_name} makes no sound when flying."
                elif ability in ["Keen Hearing and Sight", "Keen Smell", "Keen Hearing", "Keen Hearing and Smell",
                                 "Keen Sight and Smell"]:
                    text += f"The {mob_name} has advantage on Wisdom (Perception) checks that rely on"
                    text += ability.lower().replace("and", "or").replace("keen", "") + "."
                elif ability in ["Hidden"]:
                    text += f"The {mob_name} has Advantage on Dexterity (Stealth) checks when remaining motionless."
                elif ability in ["Ice Walk"]:
                    text += f"The {mob_name} can move across and climb icy surfaces without needing to make an ability check. Additionally, difficult terrain composed of ice or snow doesn't cost it extra movement."
                elif ability in ["Nimble Escape"]:
                    text += f"The {mob_name} can take the Disengage or Hide action as a bonus action on each of its turns."
                elif ability in ["Stench"]:
                    text += f"Any creature that starts its turn within 5 feet of the {mob_name} must succeed on a DC 10 Constitution saving throw or be poisoned until the start of its next turn. On a successful saving throw, the creature is immune to the {mob_name}'s Stench for 24 hours."
                elif ability in ["Turning Defiance"]:
                    text += f"The {mob_name} and any ghouls within 30 feet of it have advantage on saving throws against effects that turn undead."
                elif ability in ["Detect Life"]:
                    text += f"The banshee can magically sense the presence of creatures up to 5 miles away that aren’t undead or constructs. She knows the general direction they’re in but not their exact locations."
                elif ability in ["Incorporeal Movement"]:
                    text += f"The {mob_name} can move through other creatures and objects as if they were difficult terrain. It takes 5 (1d10) force damage if it ends its turn inside an object."
                elif ability in ["Regeneration"]:
                    text += f"The vampire regains 10 hit points at the start of its turn if it has at least 1 hit point and isn't in sunlight or running water. If the vampire takes radiant damage or damage from holy water, this trait doesn't function at the start of the vampire's next turn."
                elif ability in ["Vampire Weaknesses"]:
                    text += f"The vampire has the following flaws: Forbiddance. The vampire can't enter a residence without an invitation from one of the occupants. Harmed by Running Water. The vampire takes 20 acid damage when it ends its turn in running water. Stake to the Heart. The vampire is destroyed if a piercing weapon made of wood is driven into its heart while it is incapacitated in its resting place. Sunlight Hypersensitivity. The vampire takes 20 radiant damage when it starts its turn in sunlight. While in sunlight, it has disadvantage on attack rolls and ability checks."
                elif ability in ["Sunlight Sensitivity"]:
                    text += f"While in sunlight, the wraith has disadvantage on attack rolls, as well as on Wisdom (Perception) checks that rely on sight."
                elif ability in ["Ethereal Sight"]:
                    text += f"The ghost can see 60 feet into the Ethereal Plane when it is on the Material Plane, and vice versa."
                elif ability in ["Undead Fortitude"]:
                    text += f"If damage reduces the zombie to 0 hit points, it must make a Constitution saving throw with a DC of 5 + the damage taken, unless the damage is radiant or from a critical hit. On a success, the zombie drops to 1 hit point instead."
                elif ability in ["Reckless"]:
                    text += f"The orc can choose to gain advantage on all melee weaopn attacks during its turn, but in return all attack rolls against it also have advantage untill the start of its next turn."
                elif ability in ["Ice"]:
                    text += f""

                if V.mob_dict[mob]["Real_Abilities"].get(ability) == None:
                    V.mob_dict[mob]["Real_Abilities"][ability] = {"Text": "",
                                                                  "Can_Damage": False,
                                                                  "Damage": "",
                                                                  "Hit_mod": "",
                                                                  }
                V.mob_dict[mob]["Real_Abilities"][ability]["Text"] = text

                if print_results: print(ability.replace("object", "Object Form Only") + ".",
                                        V.mob_dict[mob]["Real_Abilities"][ability]["Text"])

        if actions != [""]:
            for action in actions:
                can_damage = False
                damage_saved = ""
                Hit_mod = ""
                text = ""
                attack_type = ""
                extra_to_hit = "0"
                reach = ""
                target_count = ""
                damage = ""
                damage_type = ""
                extra_type = ""
                extra_damage = ""
                extra_text = "."
                if action in ["Bite", "Pseudopod", "Claw", "Greatclub", "Club", "Greataxe", "Claws", "Gore", "Hooves",
                              "Longsword", "Shortsword", "Constrict", "Clawed Gauntlet", "Tusk", "Pseudobeak", "Talons",
                              "Beak", "Horns", "Scimitar", "Slam", "Greatsword", "Fist", "Life Drain",
                              "Withering Touch"]:
                    attack_type = "Melee Weapon Attack: "
                    can_damage = True
                elif action in ["Tail Spike", "Heavy Crossbow", "Shortbow", "Rock"]:
                    attack_type = "Ranged Weapon Attack: "
                    can_damage = True
                elif action in ["Javelin"]:
                    attack_type = "Melee or Ranged Weapon Attack: "
                    can_damage = True
                elif action in ["Ray of Frost"]:
                    attack_type = "Ranged Spell Attack: "
                    can_damage = True
                elif action in ["Corrupting Touch"]:
                    attack_type = "Melee Spell Attack: "
                    can_damage = True

                if action in ["Bite", "Pseudopod", "Claw", "Tail Spike", "Greatclub", "Javelin", "Club", "Greataxe",
                              "Claws", "Gore", "Longsword", "Shortsword", "Constrict", "Clawed Gauntlet", "Tusk",
                              "Fist", "Rock", "Hooves", "Greatsword", "Shortbow", "Slam", "Scimitar", "Pseudobeak",
                              "Talons", "Beak", "Horns", "Corrupting Touch", "Life Drain"]:
                    if mob_modifyers["STR"] > mob_modifyers["DEX"]:
                        extra_to_hit = f"+{str(mob_modifyers['STR'] + prof_bonus)} to hit,"
                    else:
                        if mob_modifyers["DEX"] > mob_modifyers["CON"]:
                            extra_to_hit = f"+{str(mob_modifyers['DEX'] + prof_bonus)} to hit,"
                        else:
                            extra_to_hit = f"+{str(mob_modifyers['CON'] + prof_bonus)} to hit,"

                    if action == "Bite" and mob == "Ghast":
                        extra_to_hit = f"+{mob_modifyers['STR']} to hit,"

                elif action in ["Ray of Frost"]:
                    extra_to_hit = f"+{str(mob_modifyers['INT'] + prof_bonus)} to hit,"
                elif action in ["Heavy Crossbow"]:
                    extra_to_hit = f"+{str(mob_modifyers['DEX'] + prof_bonus)} to hit,"
                elif action in ["Withering Touch"]:
                    extra_to_hit = f"+{str(mob_modifyers['CHA'] + prof_bonus)} to hit,"
                Hit_mod = extra_to_hit

                if action in ["Bite", "Pseudopod", "Claw", "Greatclub", "Javelin", "Club", "Claws", "Greataxe", "Gore",
                              "Longsword", "Shortsword", "Clawed Gauntlet", "Tusk", "Talons", "Beak", "Horns", "Hooves",
                              "Scimitar", "Corrupting Touch", "Life Drain", "Withering Touch", "Slam", "Greatsword",
                              "Fist"]:
                    reach = " reach 5 ft"
                elif action in ["Constrict", "Pseudobeak"]:
                    reach = " reach 10 ft"
                elif action in ["Tail Spike"]:
                    reach = " range 100/200 ft"
                elif action in ["Heavy Crossbow"]:
                    reach = " range 100/400 ft"
                elif action in ["Ray of Frost"]:
                    reach = " range 60 ft"
                elif action in ["Shortbow"]:
                    reach = " range 80/320 ft"
                elif action in ["Rock"]:
                    reach = " range 25/50 ft"

                if action == "Bite" and mob in ["Young Red Dragon", "Young White Dragon"]:
                    reach = " reach 10 ft"

                if action in ["Javelin"]:
                    reach += f". or range 30/120 ft"
                reach += ".,"

                if action in ["Bite", "Pseudopod", "Claw", "Tail Spike", "Greatclub", "Javelin", "Club", "Claws",
                              "Ray of Frost", "Greataxe", "Gore", "Longsword", "Shortsword", "Heavy Crossbow",
                              "Constrict", "Clawed Gauntlet", "Tusk", "Pseudobeak", "Talons", "Beak", "Horns",
                              "Scimitar", "Corrupting Touch", "Life Drain", "Withering Touch", "Slam", "Fist",
                              "Shortbow", "Rock"]:
                    target_count = " one target."
                elif action in ["Hooves"]:
                    target_count = " one prone target."
                elif action in ["Greatsword"]:
                    target_count = " two seperate targets."

                if action in ["Bite"] and mob == "Vampire Spawn":
                    target_count = " one willing creature, or a creature that is grappled by the vampire, incapacitated, or restrained."

                if action in ["Bite", "Pseudopod", "Tail Spike", "Greatclub", "Javelin", "Claws", "Club", "Greataxe",
                              "Ray of Frost", "Claw", "Gore", "Longsword", "Shortsword", "Heavy Crossbow", "Constrict",
                              "Clawed Gauntlet", "Tusk", "Pseudobeak", "Talons", "Beak", "Horns", "Scimitar",
                              "Corrupting Touch", "Life Drain", "Withering Touch", "Slam", "Greatsword", "Fist",
                              "Hooves", "Shortbow", "Rock"]:
                    die = "1d8"
                    if mob_modifyers["STR"] > mob_modifyers["DEX"]:
                        mod = mob_modifyers['STR']
                    else:
                        mod = mob_modifyers['DEX']
                    if mob in ["Rock Gnome Recluse"]:
                        mod = 0
                    if action in ["Heavy Crossbow"]:
                        mod = mob_modifyers['DEX']
                    if action in ["Withering Touch"]:
                        mod = mob_modifyers['CHA']

                    extra = 0
                    if (mob, action) in [("Young Red Dragon", "Bite"), ("Young White Dragon", "Bite")] or mob in []:
                        die = "2d10"
                    elif (mob, action) in [("Orc", "Greataxe")] or mob in []:
                        die = "1d12"
                    elif (mob, action) in [("Veteran", "Heavy Crossbow"), ("Owlbear", "Beak"),
                                           ("Red Dragon Wyrmling", "Bite")] or mob in []:
                        die = "1d10"
                    elif (mob, action) in [("Wraith", "Life Drain")] or mob in []:
                        die = "4d8"
                    elif (mob, action) in [("Ogre", "Greatclub"), ("Owlbear", "Claws"), ("Ghast", "Bite")] or mob in []:
                        die = "2d8"
                    elif (mob, action) in [("Ghost", "Withering Touch")] or mob in []:
                        die = "4d6"
                    elif (mob, action) in [("Banshee", "Corrupting Touch")] or mob in []:
                        die = "3d6"
                    elif (mob, action) in [("Ogre", "Javelin"), ("Ankheg", "Bite"), ("Dire Wolf", "Bite"),
                                           ("Young Red Dragon", "Claw"), ("Young White Dragon", "Claw"),
                                           ("Ghast", "Claws"), ("Half Orc", "Greatsword"),
                                           ("Brown Bear", "Claws")] or mob in ["Ochre Jelly", "Vine Blight"]:
                        die = "2d6"
                    elif (mob, action) in [("Manticore", "Claw"), ("Orc", "Javelin"), ("Veteran", "Shortsword"),
                                           ("Anchorite of Talos", "Tusk"), ("Boar", "Tusk"), ("Stag", "Horns"),
                                           ("Vampire Spawn", "Bite")] or mob in ["Cow", "Goblin", "Skeleton", "Zombie",
                                                                                 "Ape"]:
                        die = "1d6"
                    elif (mob, action) in [("Harpy", "Claws"), ("Wolf", "Bite"), ("Stag", "Hooves"),
                                           ("Vampire Spawn", "Claws")] or mob in ["Pony"]:
                        die = "2d4"
                    elif (mob, action) in [("Harpy", "Club"), ("Anchorite of Talos", "Clawed Gauntlet"),
                                           ("Gooze", "Pseudobeak")] or mob in ["Giant Rat", "Commoner", "Fox", "Rabbit",
                                                                               "Owl"]:
                        die = "1d4"

                    if mob in ["Ochre Jelly", "Ogre", "Harpy", "Vine Blight", "Ankheg", "Wolf", "Dire Wolf",
                               "Young Red Dragon", "Young White Dragon", "Ghast", "Banshee", "Vampire Spawn", "Ghost",
                               "Half Orc"]:
                        if mob == "Harpy" and action == "Club" or mob == "Vampire Spawn" and action == "Bite":
                            extra = 0
                        else:
                            extra = 1
                    average_roll = (int(die.split("d")[1]) * int(die.split("d")[0])) // 2 + mod + extra
                    damage = f" Hit: {average_roll} ({die}"
                    if mod != 0:
                        damage += f" + {mod}"
                    damage += ")"
                    damage_saved = damage

                if action in ["Bite", "Tail Spike", "Javelin", "Gore", "Shortsword", "Heavy Crossbow", "Beak", "Horns",
                              "Shortbow"]:
                    damage_type = " piercing damage"
                elif action in ["Pseudopod", "Greatclub", "Club", "Constrict", "Pseudobeak", "Hooves", "Slam", "Fist",
                                "Rock"]:
                    damage_type = " bludgeoning damage"
                elif action in ["Claw", "Claws", "Greataxe", "Longsword", "Clawed Gauntlet", "Tusk", "Talons",
                                "Scimitar", "Greatsword"]:
                    damage_type = " slashing damage"
                elif action in ["Ray of Frost"]:
                    damage_type = " cold damage"
                elif action in ["Corrupting Touch", "Life Drain", "Withering Touch"]:
                    damage_type = " necrotic damage"

                if action in ["Bite", "Pseudobeak"]:
                    extra_type = " acid damage"
                    if mob in ["Young Red Dragon", "Red Dragon Wyrmling"]:
                        extra_type = " fire damage"
                    elif mob in ["Young White Dragon"]:
                        extra_type = " cold damage"
                    elif mob in ["Vampire Spawn"]:
                        extra_type = " necrotic damage"

                    if mob in ["Vampire Spawn"]:
                        extra_damage = " plus 7 (2d6)"
                    elif mob in ["Mimic", "Young White Dragon"]:
                        extra_damage = " plus 4 (1d8)"
                    elif mob in ["Ankheg", "Gooze", "Young Red Dragon", "Red Dragon Wyrmling"]:
                        extra_damage = " plus 3 (1d6)"
                    damage_saved += extra_damage
                    if extra_damage == "":
                        extra_type = ""

                if action in ["Pseudopod"]:
                    if mob in ["Mimic"]:
                        extra_text = f". If the {mob_name} is in object form, the target is subjected to its Adhesive trait."
                    elif mob in ["Ochre Jelly"]:
                        extra_text = f" plus 3 (1d6) acid damage."
                elif action in ["Multiattack"]:
                    reach = ""
                    amount = "three"
                    if mob in ["Harpy", "Veteran", "Owlbear", "Brown Bear", "Ape", "Vampire Spawn"]:
                        amount = "two"

                    if mob in ["Harpy", "Owlbear", "Vampire Spawn", "Brown Bear"]:
                        """Only two named attacks"""
                        if mob == "Harpy":
                            attacks = ["one", "claws", "one", "club"]
                        elif mob == "Owlbear":
                            attacks = ["one", "beak", "one", "claws"]
                        elif mob in ["Vampire Spawn", "Brown Bear"]:
                            attacks = ["one", "bite", "one", "claws"]
                        extra_text = f"The {mob_name} makes {amount} attacks: {attacks[0]} with its {attacks[1]} and {attacks[2]} with its {attacks[3]}"
                        if mob == "Vampire Spawn":
                            extra_text += " or two with its claws"
                    elif mob in ["Veteran", "Gooze", "Ape"]:
                        """Only one named attack"""
                        attacks = "longsword"
                        if mob == "Gooze":
                            attacks = "pseudobeak"
                        elif mob == "Ape":
                            attacks = "fist"
                        extra_text = f"The {mob_name} makes {amount} {attacks} attacks"
                        if mob == "Veteran":
                            extra_text += ". If it has a shortsword drawn, it can also make a shortsword attack"

                    elif mob in ["Manticore", "Young Red Dragon", "Young White Dragon"]:
                        if mob == "Manticore":
                            attacks = ["one", "bite", "two", "claws"]
                        elif "Dragon" in mob:
                            attacks = ["one", "bite", "two", "claws"]
                        extra_text = f"The {mob_name} makes {amount} attacks: {attacks[0]} with its {attacks[1]} and {attacks[2]} with its {attacks[3]}"
                        if "Manticore" in mob:
                            extra_text += " or three with its tail spikes"
                    extra_text += "."

                elif action in ["R:Split"]:
                    reach = ""
                    extra_text = f"When a jelly that is Medium or larger is subjected to lightning or slashing damage, it splits into two new jellies if it has at least 10 hit points. Each new jelly has hit points equal to half the original jelly's, rounded down. New jellies are one size smaller than the original jelly."
                elif action in ["Luring Song"]:
                    reach = ""
                    extra_text = f"The harpy sings a magical melody. Every humanoid and giant within 300 feet of the harpy that can hear the song must succeed on a DC 11 Wisdom saving throw or be charmed until the song ends. The harpy must take a bonus action on its subsequent turns to continue singing. It can stop singing at any time. The song ends if the harpy is incapacitated. While charmed by the harpy, a target is incapacitated and ignores the songs of other harpies. If the charmed target is more than 5 feet away from the harpy, the target must move on its turn toward the harpy by the most direct route, trying to get within 5 feet. It doesn't avoid opportunity attacks, but before moving into damaging terrain, such as lava or a pit, and whenever it takes damage from a source other than the harpy, the target can repeat the saving throw. A charmed target can also repeat the saving throw at the end of each of its turns. If the saving throw is successful, the effect ends on it. A target that successfully saves is immune to this harpy's song for the next 24 hours."
                elif action in ["Magic Missile"]:
                    reach = ""
                    extra_text = f"The gnome creates three magical darts. Each dart hits a creature the gnome chooses within 120 feet of it and deals 3 (1d4 + 1) force damage."
                elif action in ["Ray of Frost"]:
                    extra_text = f", and the target's speed is reduced by 10 feet until the start of the gnome's next turn."
                elif action in ["Longsword"]:
                    extra_text = f", or 8 (1d10 + 3) slashing damage if used with two hands."
                elif action in ["Constrict"]:
                    extra_text = f", and a Large or smaller target is grappled (escape DC 12). Until this grapple ends, the target is restrained, and the blight can't constrict another target."
                elif action in ["Entangling Plants"]:
                    reach = ""
                    extra_text = f"(Recharge 5–6). Grasping roots and vines sprout in a 15-foot radius centered on the blight, withering away after 1 minute. For the duration, that area is difficult terrain for nonplant creatures. In addition, each creature of the blight's choice in that area when the plants appear must succeed on a DC 12 Strength saving throw or become restrained. A creature can use its action to make a DC 12 Strength check, freeing itself or another entangled creature within reach on a success."
                elif action in ["Acid Spray"]:
                    reach = ""
                    extra_text = f"(Recharge 6). The ankheg spits acid in a line that is 30 feet long and 5 feet wide, provided that it has no creature grappled. Each creature in that line must make a DC 13 Dexterity saving throw, taking 10 (3d6) acid damage on a failed save, or half as much damage on a successful one."
                elif action in ["Bite"]:
                    if mob == "Ankheg":
                        extra_text = ". If the target is a Large or smaller creature, it is grappled (escape DC 13). Until this grapple ends, the ankheg can bite only the grappled creature and has advantage on attack rolls to do so."
                    elif mob in ["Wolf", "Dire Wolf"]:
                        dc = "11"
                        if mob == "Dire Wolf": dc = "13"
                        extra_text = f". If the target is a creature, it must succeed on a DC {dc} Strength saving throw or be knocked prone."
                    elif mob in ["Vampire Spawn"]:
                        extra_text = f". The target's hit point maximum is reduced by an amount equal to the necrotic damage taken, and the vampire regains hit points equal to that amount. The reduction lasts until the target finishes a long rest. The target dies if this effect reduces its hit point maximum to 0."
                elif action in ["Pseudobeak"]:
                    extra_text += f" The {mob_name} regains hit points equal to half the acid damage dealt."
                elif action in ["Bubbling Hiss"]:
                    reach = ""
                    extra_text = f"The gooze ferociously hisses and exhales acidic bubbles in a 15-foot cone. Each creature in that area must make a DC 14 Dexterity saving throw, taking 21 (6d6) acidic damage on a failed save, or half as much damage on a successful one. A creature taking 10 or more acidic damage in this way is also frightened untill the end of its next turn."
                elif action in ["Slug Hug"]:
                    reach = ""
                    extra_text = f"The hug slug reaches out toward a creature within 5 feet of it while emitting squeaking, croaking and grunting sounds. The creature must succeed on a DC 7 Wisdom saving throw, or use its reaction to grapple the hug slug. The creature can choose to fail the saving throw. A creature grappling the hug slug gains 3 (1d6) temporary hit points at the start of each of its turns. When the grapple ends, the creature must succeed on a DC 12 Consititution saving throw or be poisoned for 1 minute. The creature must repeat the saving throw ath the end of each of its turns, taking 3 (1d6) poison damage on a failure or ending the poison on itself on a success."
                elif action in ["Fire Breath", "Cold Breath"]:
                    reach = ""
                    size = "30"
                    if "Wyrmling" in mob:
                        size = "15"
                    if "Fire" in action:
                        save = "17 Dexterity"
                        dmg = "56 (16d6)"
                        if "Wyrmling" in mob:
                            save = "13 Dexterity"
                            dmg = "24 (7d6)"
                    elif "Cold" in action:
                        save = "15 Constitution"
                        dmg = "45 (10d8)"
                    extra_text = f"(Recharge 5–6). The dragon exhales {action.split(' ')[0].lower()} in a {size}-foot cone. Each creature in that area must make a DC {save} saving throw, taking {dmg} {action.split(' ')[0].lower()} damage on a failed save, or half as much damage on a successful one."
                elif action in ["Claws"]:
                    if mob == "Ghast":
                        extra_text = f". If the target is a creature other than an undead, it must succeed on a DC 10 Constitution saving throw or be paralyzed for 1 minute. The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success."
                    if mob == "Vampire Spawn":
                        extra_text = f". Instead of dealing damage, the vampire can grapple the target (escape DC 13)."
                elif action in ["Horrifying Visage"]:
                    reach = ""
                    if mob == "Banshee":
                        extra2 = "with disadvantage if the banshee is within line of sight, "
                        extra = ""
                        extra3 = ""
                    if mob == "Ghost":
                        extra = "If the save fails by 5 or more, the target also ages 1d4 × 10 years. "
                        extra2 = ""
                        extra3 = " The aging effect can be reversed with a greater restoration spell, but only within 24 hours of it occurring."
                    extra_text = f"Each non-undead creature within 60 feet of the {mob_name} that can see it must succeed on a DC 13 Wisdom saving throw or be frightened for 1 minute. {extra}A frightened target can repeat the saving throw at the end of each of its turns, {extra2}ending the effect on itself on a success. If a target's saving throw is successful or the effect ends for it, the target is immune to the {mob_name}'s Horrifying Visage for the next 24 hours.{extra3}"
                elif action in ["Wail"]:
                    reach = ""
                    extra_text = f"(1/Day). The banshee releases a mournful wail, provided that she isn’t in sunlight. This wail has no effect on constructs and undead. All other creatures within 30 feet of her that can hear her must make a DC 13 Constitution saving throw. On a failure, a creature drops to 0 hit points. On a success, a creature takes 10 (3d6) psychic damage."
                elif action in ["Create Specter"]:
                    reach = ""
                    extra_text = f"The wraith targets a humanoid within 10 feet of it that has been dead for no longer than 1 minute and died violently. The target's spirit rises as a specter in the space of its corpse or in the nearest unoccupied space. The specter is under the wraith's control. The wraith can have no more than seven specters under its control at one time."
                elif action in ["Life Drain"]:
                    extra_text = f". The target must succeed on a DC 14 Constitution saving throw or its hit point maximum is reduced by an amount equal to the damage taken. This reduction lasts until the target finishes a long rest. The target dies if this effect reduces its hit point maximum to 0."
                elif action in ["Etherealness"]:
                    reach = ""
                    extra_text = f"The ghost enters the Ethereal Plane from the Material Plane, or vice versa. It is visible on the Material Plane while it is in the Border Ethereal, and vice versa, yet it can't affect or be affected by anything on the other plane."
                elif action in ["Possession"]:
                    reach = ""
                    extra_text = f"(Recharge 6). One humanoid that the ghost can see within 5 feet of it must succeed on a DC 13 Charisma saving throw or be possessed by the ghost; the ghost then disappears, and the target is incapacitated and loses control of its body. The ghost now controls the body but doesn't deprive the target of awareness. The ghost can't be targeted by any attack, spell, or other effect, except ones that turn undead, and it retains its alignment, Intelligence, Wisdom, Charisma, and immunity to being charmed and frightened. It otherwise uses the possessed target's statistics, but doesn't gain access to the target's knowledge, class features, or proficiencies. The possession lasts until the body drops to 0 hit points, the ghost ends it as a bonus action, or the ghost is turned or forced out by an effect like the dispel evil and good spell. When the possession ends, the ghost reappears in an unoccupied space within 5 feet of the body. The target is immune to this ghost's Possession for 24 hours after succeeding on the saving throw or after the possession ends."

                text = f"{attack_type}{extra_to_hit}{reach}{target_count}{damage}{damage_type}{extra_damage}{extra_type}{extra_text}"
                if V.mob_dict[mob]["Real_Actions"].get(action) == None:
                    V.mob_dict[mob]["Real_Actions"][action] = {"Text": "",
                                                               "Can_Damage": False,
                                                               "Damage": "",
                                                               "Hit_mod": "",
                                                               }
                V.mob_dict[mob]["Real_Actions"][action]["Text"] = text
                V.mob_dict[mob]["Real_Actions"][action]["Can_Damage"] = can_damage
                V.mob_dict[mob]["Real_Actions"][action]["Damage"] = damage_saved
                V.mob_dict[mob]["Real_Actions"][action]["Hit_mod"] = Hit_mod
                if print_results: print(action.replace("R:", "") + ".", V.mob_dict[mob]["Real_Actions"][action]["Text"])

