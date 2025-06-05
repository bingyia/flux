import random
import time
from pathlib import Path
from PIL import Image, ImageDraw

WIDTH = 800
HEIGHT = 600


def draw_wave(draw: ImageDraw.Draw, amplitude: int, color: tuple) -> None:
    """Draw a simple wave across the canvas."""
    points = []
    for x in range(0, WIDTH + 1, 10):
        y = HEIGHT // 2 + int(amplitude * random.uniform(0.8, 1.2) * random.choice([-1, 1]) * (random.random()))
        points.append((x, y))
    draw.line(points, fill=color, width=3)


def draw_surfboard(draw: ImageDraw.Draw, x: int, y: int, color: tuple) -> None:
    board_width = 120
    board_height = 20
    draw.ellipse([x, y - board_height // 2, x + board_width, y + board_height // 2], fill=color)


def generate_surf_image() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), (135, 206, 235))  # sky blue background
    draw = ImageDraw.Draw(img)

    # ocean
    draw.rectangle([0, HEIGHT // 2, WIDTH, HEIGHT], fill=(0, 105, 148))

    # waves
    for _ in range(5):
        amp = random.randint(10, 30)
        color = (255, 255, 255)
        draw_wave(draw, amp, color)

    # surfboard
    board_x = random.randint(100, WIDTH - 150)
    board_y = HEIGHT // 2 + random.randint(-20, 20)
    color = tuple(random.randint(0, 255) for _ in range(3))
    draw_surfboard(draw, board_x, board_y, color)

    return img


def main() -> None:
    img = generate_surf_image()
    ts = int(time.time())
    path = Path(f"surf_{ts}.png")
    img.save(path)
    try:
        img.show()
    except Exception:
        pass
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
