import pygame
import random

# Game settings
WIDTH, HEIGHT = 800, 600
ROAD_WIDTH = WIDTH // 2
LANE_WIDTH = ROAD_WIDTH // 3
CAR_WIDTH, CAR_HEIGHT = 40, 80
FPS = 60

# Colors
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)


class PlayerCar(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((CAR_WIDTH, CAR_HEIGHT))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        # Keep the car on the road
        left_bound = (WIDTH - ROAD_WIDTH) // 2
        right_bound = left_bound + ROAD_WIDTH - CAR_WIDTH
        self.rect.x = max(left_bound, min(self.rect.x, right_bound))


class EnemyCar(pygame.sprite.Sprite):
    def __init__(self, lane, y):
        super().__init__()
        self.image = pygame.Surface((CAR_WIDTH, CAR_HEIGHT))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        lane_x = (WIDTH - ROAD_WIDTH) // 2 + lane * LANE_WIDTH + LANE_WIDTH // 2
        self.rect.center = (lane_x, y)
        self.speed = 6

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Road:
    def __init__(self):
        self.offset = 0
        self.line_height = 40
        self.speed = 6

    def draw(self, surface):
        center = WIDTH // 2
        left_edge = center - ROAD_WIDTH // 2
        pygame.draw.rect(surface, GREY, (left_edge, 0, ROAD_WIDTH, HEIGHT))
        # Lane lines
        for i in range(HEIGHT // self.line_height + 2):
            y = (i * self.line_height * 2 + self.offset) % (self.line_height * 4)
            for lane in range(1, 3):
                x = left_edge + lane * LANE_WIDTH
                pygame.draw.rect(surface, WHITE, (x - 2, y, 4, self.line_height))

    def update(self):
        self.offset += self.speed


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True

    player = PlayerCar(WIDTH // 2, HEIGHT - 100)
    all_sprites = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    road = Road()
    score = 0
    font = pygame.font.SysFont(None, 36)

    enemy_event = pygame.USEREVENT + 1
    pygame.time.set_timer(enemy_event, 1200)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == enemy_event:
                lane = random.randrange(0, 3)
                enemy = EnemyCar(lane, -CAR_HEIGHT)
                all_sprites.add(enemy)
                enemies.add(enemy)

        keys = pygame.key.get_pressed()
        player.update(keys)
        road.update()
        enemies.update()

        if pygame.sprite.spritecollideany(player, enemies):
            running = False

        score += 1
        screen.fill((0, 0, 0))
        road.draw(screen)
        all_sprites.draw(screen)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
