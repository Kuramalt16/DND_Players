import pygame as pg, os, Settings as S, Functions as F, main

def check_text_pass(text_dict):
    for name, (text, rect) in text_dict.items():
        if text == "Bubble":
        # if text == "1":
            return "Laura"
        elif text == "6467":
        # elif text == "2":
            return "Simonas"
        elif text == "Dalbajobs":
        # elif text == "3":
            return "Rokas"
        elif text == "eguitex":
        # elif text == "3":
            return "Rita"
        elif text == "123":
        # elif text == "3":
            return "Admin"
    return None

S.local_path = os.getcwd()
# F.rename_images_in_folder(S.local_path + "/Images/Background/Roling_Dice/D4/1")  #at the end of the path last folder doesn't need /
# F.fix_files(S.local_path + "/Images/Background/Roling_Dice/D20/20")

pg.init()  # initializes all game modules
screen = pg.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pg.RESIZABLE)  # sets screen mode
pg.display.set_caption('A Game')
screen.fill('white')
pg.display.flip()
clock = pg.time.Clock()
x = S.SCREEN_WIDTH / 3
y = S.SCREEN_HEIGHT / 3
selected_entry = -1
running = True
timer = 10
timer2 = 0
pressed = ""
text_dict = {"Pass": ["", 0]}
entry = []
if os.path.exists("v.txt"):
    with open("v.txt", "r", encoding="utf-8") as f:
        content = f.read()
        content = content.replace("\n", "")
        if content != S.VERSION:
            if int(content) < 10:
                S.VERSION = "1.00" + content
            elif int(content) < 100:
                S.VERSION = "1.0" + content
            elif int(content) < 1000:
                S.VERSION = "1." + content
            else:
                print("IDK WHAT VERSION", S.VERSION, content)


else:
    S.VERSION = "1"
    with open("v.txt", "w", encoding="utf-8") as f:
        f.write(S.VERSION)
    S.VERSION = "1.001"
while running:
    F.add_image_to_screen(screen, "background", (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), "Background")
    entr = F.add_entry_to_list((x + S.SCREEN_WIDTH / 3, y + 8, 200, 30), "password", screen, "Enter Password", 30, (x, y))
    F.display_text(screen, "Version: " + S.VERSION, 20, (0, S.SCREEN_HEIGHT * 0.95))
    if entr not in entry:
        entry.append(entr)
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
            for i in range(0, len(entry)):
                if entry[i].collidepoint(pos):
                    selected_entry = i
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            pos = pg.mouse.get_pos()
            if selected_entry != -1 and not entry[selected_entry].collidepoint(pos):
                selected_entry = -1
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                pressed = "ENTER"
            else:
                pressed = ""
        elif event.type == pg.TEXTINPUT and selected_entry != -1:
            property = list(text_dict.keys())[selected_entry]
            text_dict[property][0] += event.text
        if keys[pg.K_BACKSPACE] and selected_entry != -1 and not keys[pg.K_LCTRL]:
            property = list(text_dict.keys())[selected_entry]
            text_dict[property][0] = text_dict[property][0][:-1]
        elif keys[pg.K_BACKSPACE] and selected_entry != -1 and keys[pg.K_LCTRL]:
            property = list(text_dict.keys())[selected_entry]
            text_dict[property][0] = ""

    F.update_text(text_dict, entry, screen, True)

    char_name = check_text_pass(text_dict)

    if char_name != None and timer2 == 0:
        timer2 = 255


    if selected_entry != -1:
        F.flash_marker(selected_entry, entry, screen, timer, text_dict)

    if timer2 != 0 and pressed == "ENTER" and char_name != None:
        timer2 -= 10
        alpha = 255 - timer2
        F.display_text(screen, "Hello " + char_name, 30, (x, y + S.SCREEN_HEIGHT / 3), "black", "TL", alpha)
    elif pressed == "ENTER" and char_name == None:
        F.display_text(screen, "Incorrect Password", 30, (x, y + S.SCREEN_HEIGHT / 3), "black", "TL")

    if timer2 < 0:
        running = False
        F.print_debug("Passwword, Correct", debug="INFO")
        main.Start(char_name, screen, clock)
    pg.display.flip()
    clock.tick(60)
    timer = F.reset_timer(timer)
pg.quit()


