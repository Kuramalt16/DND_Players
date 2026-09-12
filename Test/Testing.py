import pygame
import colorsys


def draw_spell_slots():

    pygame.init()


    def create_spell_slot(filename, color, pattern, pixel_size=3):
        """
        Create a pixel-art ball and save it as a PNG.

        filename   - Output filename, e.g. "fireball.png"
        color      - Base RGB color, e.g. (255, 80, 30)
        pattern    - List of strings describing the ball
        pixel_size - Size of each "pixel"
        """

        height = len(pattern)
        width = len(pattern[0])

        # Create shading colors from the base color
        lighter = tuple(min(255, int(c * 1.25)) for c in color)
        darker = tuple(max(0, int(c * 0.65)) for c in color)

        surface = pygame.Surface(
            (width * pixel_size, height * pixel_size),
            pygame.SRCALPHA
        )

        lighter = tuple(min(255, int(c * 1.45)) for c in color)
        super_light = tuple(min(255, int(c * 2)) for c in color)
        darker = tuple(max(0, int(c * 0.65)) for c in color)

        for y, row in enumerate(pattern):
            for x, pixel in enumerate(row):
                if pixel == "X":
                    pixel_color = color
                elif pixel == "Y":
                    pixel_color = lighter
                elif pixel == "Z":
                    pixel_color = darker
                elif pixel == "W":
                    pixel_color = super_light
                else:
                    continue

                pygame.draw.rect(
                    surface,
                    pixel_color,
                    (
                        x * pixel_size,
                        y * pixel_size,
                        pixel_size,
                        pixel_size
                    )
                )


        pygame.image.save(surface, filename)


    # --------------------------------------------------
    # EXAMPLE
    # --------------------------------------------------

    ball_pattern = [
        "   YYY   ",
        "  WWYXX  ",
        " YWYXXXX ",
        " YYXXXXZ ",
        " YXXXXZZ ",
        "  XXXZZ  ",
        "   ZZZ   ",
    ]


    # create_spell_slot(
    #     "fireball.png",
    #     (255, 60, 20),
    #     ball_pattern,
    #     pixel_size=3
    # )


    for i in range(20):
        hue = i / 20
        color = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.8, 1.0))

        create_spell_slot(
            f"spell_{i:02}.png",
            color,
            ball_pattern,
            pixel_size=3
        )
    pygame.quit()