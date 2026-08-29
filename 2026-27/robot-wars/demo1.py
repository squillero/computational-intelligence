import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Moving Squares"


class MovingSquares(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

        # Red square position and speed
        self.red_x = 200
        self.red_y = 300
        self.red_change_x = 4
        self.red_change_y = 3
        self.red_size = 50

        # Blue square position and speed
        self.blue_x = 600
        self.blue_y = 300
        self.blue_change_x = -3
        self.blue_change_y = -5
        self.blue_size = 50

    def on_draw(self):
        self.clear()

        # Draw red square using Arcade 3.x API
        arcade.draw_rect_filled(
            arcade.rect.XYWH(self.red_x, self.red_y, self.red_size, self.red_size), arcade.color.RED
        )

        # Draw blue square using Arcade 3.x API
        arcade.draw_rect_filled(
            arcade.rect.XYWH(self.blue_x, self.blue_y, self.blue_size, self.blue_size),
            arcade.color.BLUE,
        )

    def on_update(self, delta_time):
        # Update red square position
        self.red_x += self.red_change_x
        self.red_y += self.red_change_y

        # Bounce red square off the screen boundaries
        half_red = self.red_size / 2
        if self.red_x - half_red <= 0 or self.red_x + half_red >= SCREEN_WIDTH:
            self.red_change_x *= -1
        if self.red_y - half_red <= 0 or self.red_y + half_red >= SCREEN_HEIGHT:
            self.red_change_y *= -1

        # Update blue square position
        self.blue_x += self.blue_change_x
        self.blue_y += self.blue_change_y

        # Bounce blue square off the screen boundaries
        half_blue = self.blue_size / 2
        if self.blue_x - half_blue <= 0 or self.blue_x + half_blue >= SCREEN_WIDTH:
            self.blue_change_x *= -1
        if self.blue_y - half_blue <= 0 or self.blue_y + half_blue >= SCREEN_HEIGHT:
            self.blue_change_y *= -1


def main():
    window = MovingSquares(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
