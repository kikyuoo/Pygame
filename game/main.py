import pygame
import random
import sys
import os

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ловец кубиков")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Загрузка изображений
try:
    platform_img = pygame.image.load(os.path.join('assets', 'platform.png')).convert_alpha()
    platform_img = pygame.transform.scale(platform_img, (100, 20))
    heart_img = pygame.image.load(os.path.join('assets', 'heart.png')).convert_alpha()
    heart_img = pygame.transform.scale(heart_img, (30, 30))
except:
    # Если изображений нет, создаем простые фигуры
    platform_img = pygame.Surface((100, 20), pygame.SRCALPHA)
    pygame.draw.rect(platform_img, WHITE, (0, 0, 100, 20), border_radius=5)
    heart_img = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.polygon(heart_img, RED, [(15, 0), (0, 30), (30, 30)])

# Игровые параметры
platform_width = 100
platform_height = 20
platform_speed = 10
platform = pygame.Rect(WIDTH // 2 - platform_width // 2, HEIGHT - 50, platform_width, platform_height)

cube_size = 30
cubes = []
special_cubes = []
score = 0
hp = 3  # Количество жизней
font = pygame.font.SysFont('Arial', 36)

# Эффекты
speed_boost = False
boost_time = 0
wide_platform = False
wide_time = 0

clock = pygame.time.Clock()

def create_cube():
    x = random.randint(0, WIDTH - cube_size)
    cube_type = random.choices(["normal", "special", "hp"], weights=[0.7, 0.2, 0.1])[0]
    
    if cube_type == "normal":
        color = BLUE
        cubes.append({"rect": pygame.Rect(x, 0, cube_size, cube_size), "color": color, "type": "normal"})
    elif cube_type == "hp":
        color = PURPLE
        cubes.append({"rect": pygame.Rect(x, 0, cube_size, cube_size), "color": color, "type": "hp"})
    else:
        color = random.choice([RED, GREEN, YELLOW])
        effect = random.choice(["speed", "wide", "points"])
        special_cubes.append({"rect": pygame.Rect(x, 0, cube_size, cube_size), "color": color, "type": "special", "effect": effect})

def draw_platform():
    current_width = platform_width * 2 if wide_platform else platform_width
    current_img = pygame.transform.scale(platform_img, (current_width, platform_height))
    screen.blit(current_img, (platform.x, platform.y))

def apply_effect(effect):
    global speed_boost, boost_time, wide_platform, wide_time, score, hp
    
    if effect == "speed":
        speed_boost = True
        boost_time = pygame.time.get_ticks() + 5000
    elif effect == "wide":
        wide_platform = True
        wide_time = pygame.time.get_ticks() + 7000
    elif effect == "points":
        score += 50

def check_effects():
    global speed_boost, wide_platform
    
    current_time = pygame.time.get_ticks()
    
    if speed_boost and current_time > boost_time:
        speed_boost = False
    if wide_platform and current_time > wide_time:
        wide_platform = False

def draw_hearts():
    for i in range(hp):
        screen.blit(heart_img, (10 + i * 35, 50))

# Основной игровой цикл
spawn_timer = 0
running = True

while running:
    current_time = pygame.time.get_ticks()
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Управление платформой
    keys = pygame.key.get_pressed()
    speed = platform_speed * 2 if speed_boost else platform_speed
    if keys[pygame.K_LEFT] and platform.x > 0:
        platform.x -= speed
    if keys[pygame.K_RIGHT] and platform.x < WIDTH - (platform_width * 2 if wide_platform else platform_width):
        platform.x += speed
    
    # Создание кубиков
    if current_time - spawn_timer > 800:  # Каждые 0.8 секунды
        create_cube()
        spawn_timer = current_time
    
    # Движение кубиков
    for cube in cubes[:]:
        cube["rect"].y += 5
        
        current_platform = pygame.Rect(platform.x, platform.y, 
                                    platform_width * 2 if wide_platform else platform_width, 
                                    platform_height)
        
        if cube["rect"].colliderect(current_platform):
            if cube["type"] == "hp":
                hp = min(5, hp + 1)  # Максимум 5 жизней
            else:
                score += 10
            cubes.remove(cube)
        elif cube["rect"].y > HEIGHT:
            if cube["type"] == "normal":
                hp -= 1
                if hp <= 0:
                    running = False
            cubes.remove(cube)
    
    for cube in special_cubes[:]:
        cube["rect"].y += 5
        current_platform = pygame.Rect(platform.x, platform.y, 
                                     platform_width * 2 if wide_platform else platform_width, 
                                     platform_height)
        if cube["rect"].colliderect(current_platform):
            apply_effect(cube["effect"])
            special_cubes.remove(cube)
        elif cube["rect"].y > HEIGHT:
            special_cubes.remove(cube)
    
    # Проверка эффектов
    check_effects()
    
    # Отрисовка
    screen.fill(BLACK)
    
    # Рисуем кубики
    for cube in cubes:
        if cube["type"] == "hp":
            screen.blit(heart_img, cube["rect"])
        else:
            pygame.draw.rect(screen, cube["color"], cube["rect"])
    
    for cube in special_cubes:
        pygame.draw.rect(screen, cube["color"], cube["rect"])
        if cube["effect"] == "speed":
            pygame.draw.circle(screen, WHITE, (cube["rect"].x + cube_size // 2, cube["rect"].y + cube_size // 2), 5)
        elif cube["effect"] == "wide":
            pygame.draw.line(screen, WHITE, (cube["rect"].x + 5, cube["rect"].y + cube_size // 2), 
                            (cube["rect"].x + cube_size - 5, cube["rect"].y + cube_size // 2), 3)
        elif cube["effect"] == "points":
            pygame.draw.rect(screen, WHITE, (cube["rect"].x + 10, cube["rect"].y + 10, 10, 10))
    
    draw_platform()
    draw_hearts()
    
    # Отображение счета
    score_text = font.render(f"Счет: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Отображение активных эффектов
    effects_text = []
    if speed_boost:
        effects_text.append("Ускорение")
    if wide_platform:
        effects_text.append("Широкая платформа")
    
    if effects_text:
        effects_display = font.render(" | ".join(effects_text), True, YELLOW)
        screen.blit(effects_display, (WIDTH // 2 - effects_display.get_width() // 2, 10))
    
    pygame.display.flip()
    clock.tick(60)

# Экран окончания игры
screen.fill(BLACK)
game_over_text = font.render(f"Игра окончена! Счет: {score}", True, WHITE)
screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
pygame.display.flip()
pygame.time.wait(3000)

pygame.quit()
sys.exit()
