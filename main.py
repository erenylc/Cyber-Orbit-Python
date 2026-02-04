"""
Modern Space Shooter Game - Professional Architecture
2026 Standards - Class-Based Design
"""

import os
import random
import math
import pygame
from pygame import Vector2
from enum import Enum

# ==================== GLOBAL CONSTANTS ====================
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# ==================== CONSTANTS ====================
class Config:
    WINDOW_WIDTH = WINDOW_WIDTH
    WINDOW_HEIGHT = WINDOW_HEIGHT
    FPS = 60
    
    # Player
    PLAYER_WIDTH = 56
    PLAYER_HEIGHT = 112
    PLAYER_ACCELERATION = 0.8
    PLAYER_FRICTION = 0.95
    PLAYER_MAX_SPEED = 25.0
    MAX_ROTATION = 15
    ROTATION_LERP_SPEED = 0.15
    
    # Meteor
    MAX_METEORS_ON_SCREEN = 12
    SPAWN_INTERVAL_BASE = 1500  # ms
    SPAWN_INTERVAL_MIN = 300
    TARGETED_METEOR_CHANCE = 0.3  # 30% tracking meteors
    
    # Bullet
    BULLET_SPEED = 10
    BULLET_WIDTH = 4
    BULLET_HEIGHT = 12
    
    # Coin
    COIN_DROP_CHANCE = 0.3
    
    # Colors - Cyberpunk Neon Palette
    BACKGROUND_COLOR = (0, 0, 0)  # Deep black #000000
    MENU_BG_COLOR = (0, 0, 0)  # Deep black
    TEXT_COLOR = (0, 240, 255)  # Neon Cyan
    GOLD_COLOR = (255, 215, 0)  # Keep gold for coins
    NEON_PINK = (255, 0, 255)  # Electric Pink #FF00FF
    NEON_BLUE = (0, 240, 255)  # Neon Mavi #00F0FF
    NEON_CYAN = (0, 255, 255)  # Bright Cyan
    NEON_PURPLE = (188, 0, 255)  # Cyber Mor #BC00FF
    CYBERPUNK_BG = (0, 0, 0)  # Deep black
    CYBERPUNK_DARK = (0, 0, 0)  # Deep black
    NEON_ORANGE = (255, 100, 0)  # Brighter orange


class MeteorSize(Enum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2


METEOR_CONFIGS = {
    MeteorSize.SMALL: {"size": 32, "speed_mult": 1.5, "score": 3, "color": (120, 120, 120)},  # Gray
    MeteorSize.MEDIUM: {"size": 48, "speed_mult": 1.0, "score": 5, "color": (100, 100, 100)},  # Dark gray
    MeteorSize.LARGE: {"size": 64, "speed_mult": 0.6, "score": 10, "color": (80, 80, 80)}  # Darker gray
}


class Language(Enum):
    TURKISH = "tr"
    ENGLISH = "en"


TRANSLATIONS = {
    Language.TURKISH: {
        "shop": "MAĞAZA",
        "score": "Skor",
        "points": "Puan",
        "last_score": "Son Skor",
        "new_record": "YENİ REKOR!",
        "high_score": "En Yüksek Skor",
        "press_enter": "Başlamak için Enter'a bas",
        "back": "GERİ",
        "shield": "Kalkan",
        "magnet": "Mıknatıs",
        "speed": "Hız",
        "purchased": "SATIN ALINDI",
        "gold": "Altın",
        "game_over": "OYUN BİTTİ",
        "retry": "TEKRAR OYNA",
        "shopping": "ALIŞVERİŞ",
        "settings": "AYARLAR",
        "volume": "Ses",
        "language": "Dil",
        "turkish": "Türkçe",
        "english": "English",
        "increase_volume": "+",
        "decrease_volume": "-",
        "triple_shot": "Üçlü Ateş",
        "continue_game": "Oyuna Devam Et",
        "paused": "DURAKLATILDI"
    },
    Language.ENGLISH: {
        "shop": "SHOP",
        "score": "Score",
        "points": "Points",
        "last_score": "Last Score",
        "new_record": "NEW RECORD!",
        "high_score": "High Score",
        "press_enter": "Press Enter to start",
        "back": "BACK",
        "shield": "Shield",
        "magnet": "Magnet",
        "speed": "Speed",
        "purchased": "PURCHASED",
        "gold": "Gold",
        "game_over": "GAME OVER",
        "retry": "RETRY",
        "shopping": "SHOPPING",
        "settings": "SETTINGS",
        "volume": "Volume",
        "language": "Language",
        "turkish": "Türkçe",
        "english": "English",
        "increase_volume": "+",
        "decrease_volume": "-",
        "triple_shot": "Triple Shot",
        "continue_game": "Continue Game",
        "paused": "PAUSED"
    }
}


# ==================== UTILITY CLASSES ====================
class ScreenShake:
    def __init__(self):
        self.intensity = 0.0
        self.x = 0.0
        self.y = 0.0
    
    def add_shake(self, amount):
        self.intensity += amount
    
    def update(self, dt):
        if self.intensity > 0:
            self.x = random.uniform(-self.intensity, self.intensity)
            self.y = random.uniform(-self.intensity, self.intensity)
            self.intensity *= 0.9
            if self.intensity < 0.1:
                self.intensity = 0
                self.x = 0
                self.y = 0
        else:
            self.x = 0
            self.y = 0
    
    def get_offset(self):
        return (int(self.x), int(self.y))


class ParallaxBackground:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.layers = []
        self._create_layers()
    
    def _create_layers(self):
        for layer_idx in range(3):
            layer_stars = []
            star_count = 80 if layer_idx == 0 else (40 if layer_idx == 1 else 20)
            for _ in range(star_count):
                layer_stars.append({
                    "x": random.randint(0, self.width - 1),
                    "y": random.randint(0, self.height - 1),
                    "speed": (0.3 + layer_idx * 0.2) * (1.0 + layer_idx * 0.5),
                    "size": max(1, 3 - layer_idx),
                    "brightness": 200 - layer_idx * 50
                })
            self.layers.append(layer_stars)
    
    def update(self, dt):
        for layer in self.layers:
            for star in layer:
                star["y"] += star["speed"] * dt * 60
                if star["y"] > self.height:
                    star["y"] = 0
                    star["x"] = random.randint(0, self.width - 1)
    
    def draw(self, surface):
        for layer_idx, layer in enumerate(self.layers):
            for star in layer:
                brightness = star["brightness"]
                if layer_idx == 0:
                    color = (brightness, brightness, 255)
                elif layer_idx == 1:
                    color = (brightness, brightness, brightness)
                else:
                    color = (brightness // 2, brightness // 2, brightness // 2)
                pygame.draw.circle(
                    surface,
                    color,
                    (int(star["x"]), int(star["y"])),
                    star["size"]
                )


# ==================== GAME OBJECTS ====================
class Particle:
    def __init__(self, x, y, vx, vy, color, life=0.8, size=None):
        """Particle for explosion effects with enhanced visuals"""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size or random.randint(3, 8)
    
    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += 50 * dt  # Gravity
        self.life -= dt
    
    def is_alive(self):
        return self.life > 0
    
    def draw(self, surface, offset=(0, 0)):
        """Draw particle with glow effect and smooth fade"""
        alpha = int(255 * (self.life / self.max_life))
        
        # Glow effect for particles
        glow_size = self.size + 2
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        glow_alpha = int(alpha * 0.4)
        glow_color = (*self.color, glow_alpha)
        pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
        surface.blit(glow_surf, (int(self.x - glow_size + offset[0]), int(self.y - glow_size + offset[1])))
        
        # Main particle
        color_with_alpha = (*self.color, alpha)
        particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, color_with_alpha, (self.size, self.size), self.size)
        surface.blit(particle_surf, (int(self.x - self.size + offset[0]), int(self.y - self.size + offset[1])))


class Coin:
    def __init__(self, x, y, value=1, is_score=False):
        # Boyut puanın değerine göre değişir
        if is_score:
            if value == 3:
                size = 28  # 3 puan - büyük
            elif value == 2:
                size = 22  # 2 puan - orta
            else:  # 1 puan
                size = 16  # 1 puan - küçük
        else:
            size = 20  # Altın - normal boyut
        
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = (x, y)
        self.value = value
        self.is_score = is_score  # True = puan, False = altın
        
        # Puanlar için hareket yok (sadece aşağı düşer), Altınlar için random hareket
        if is_score:
            self.vx = 0  # Puanlar yatay hareket etmez
            self.vy = 3.0  # Puanlar sadece aşağı düşer (başlangıç hızı artırıldı)
        else:
            self.vx = random.uniform(-2.0, 2.0)  # Altınlar sağa-sola hareket eder
            self.vy = random.uniform(-2.0, 2.0)
        
        self.spawn_time = pygame.time.get_ticks()
        self.sparkle = 0.0
    
    def update(self, dt, player_pos=None, magnet_active=False):
        age = (pygame.time.get_ticks() - self.spawn_time) / 1000.0
        
        # Puanlar için farklı hareket - sadece aşağı düşer (sağ-sol sallanma yok)
        if self.is_score:
            # Mıknatıs aktifse puanları rokete çek
            if magnet_active and player_pos:
                dx = player_pos[0] - self.rect.centerx
                dy = player_pos[1] - self.rect.centery
                distance = math.sqrt(dx**2 + dy**2)
                if distance > 0:
                    magnet_force = 5.0 / max(distance / 100, 1.0)  # Puanlar için daha güçlü çekim
                    self.rect.centerx += (dx / distance) * magnet_force * dt * 60
                    self.rect.centery += (dy / distance) * magnet_force * dt * 60
            else:
                # Puanlar: Sadece aşağı düşer, yerçekimi etkisi
                self.vy += 0.3 * dt * 60  # Yerçekimi ivmesi
                self.rect.centerx += self.vx * dt * 60
                self.rect.centery += self.vy * dt * 60
                self.vx *= 0.98  # Hafif yatay yavaşlama
        else:
            # Altınlar: Sallanarak hareket eder (eski davranış)
            swing_amount = math.sin(age * 3) * 2.0
            
            if magnet_active and player_pos:
                dx = player_pos[0] - self.rect.centerx
                dy = player_pos[1] - self.rect.centery
                distance = math.sqrt(dx**2 + dy**2)
                if distance > 0:
                    magnet_force = 3.0 / max(distance / 100, 1.0)
                    self.rect.centerx += (dx / distance) * magnet_force * dt * 60
                    self.rect.centery += (dy / distance) * magnet_force * dt * 60
                else:
                    self.rect.centerx += swing_amount * dt * 60
                    self.rect.centerx += self.vx * dt * 60
                    self.rect.centery += self.vy * dt * 60
                    self.vx *= 0.95
                    self.vy *= 0.95
            else:
                self.rect.centerx += swing_amount * dt * 60
                self.rect.centerx += self.vx * dt * 60
                self.rect.centery += self.vy * dt * 60
                self.vx *= 0.95
                self.vy *= 0.95
        
        self.sparkle = (math.sin(age * 8) + 1) / 2
    
    def draw(self, surface, offset=(0, 0)):
        coin_size = self.rect.width // 2
        glow_size = int(coin_size * (1.0 + self.sparkle * 0.5))
        glow_alpha = int(150 * self.sparkle)
        
        # Farklı renk: Altın için sarı, Puan için değere göre farklı renkler
        if self.is_score:
            # Puan renkleri value'ya göre
            if self.value == 3:
                main_color = (200, 100, 255)  # Mor - 3 puan
                inner_color = (230, 180, 255)
            elif self.value == 2:
                main_color = (100, 200, 255)  # Mavi - 2 puan
                inner_color = (180, 230, 255)
            else:  # 1 puan
                main_color = (255, 220, 100)  # Sarı - 1 puan
                inner_color = (255, 240, 180)
        else:
            main_color = Config.GOLD_COLOR  # Sarı - altın
            inner_color = (255, 255, 200)
        
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (main_color[0], main_color[1], main_color[2], glow_alpha),
                          (glow_size, glow_size), glow_size)
        surface.blit(glow_surf, (self.rect.centerx - glow_size + offset[0], self.rect.centery - glow_size + offset[1]))
        
        pygame.draw.circle(surface, main_color,
                          (self.rect.centerx + offset[0], self.rect.centery + offset[1]), coin_size)
        pygame.draw.circle(surface, inner_color,
                          (self.rect.centerx + offset[0], self.rect.centery + offset[1]), coin_size - 2)
        
        value_font = pygame.font.SysFont("consolas", 12, bold=True)
        value_text = value_font.render(str(self.value), True, (0, 0, 0))
        value_rect = value_text.get_rect(center=(self.rect.centerx + offset[0], self.rect.centery + offset[1]))
        surface.blit(value_text, value_rect)


class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - Config.BULLET_WIDTH // 2, y, Config.BULLET_WIDTH, Config.BULLET_HEIGHT)
    
    def update(self, dt):
        self.rect.y -= Config.BULLET_SPEED * dt * 60
    
    def is_off_screen(self):
        return self.rect.y < -Config.BULLET_HEIGHT
    
    def draw(self, surface, offset=(0, 0)):
        glow_surf = pygame.Surface((self.rect.width + 6, self.rect.height + 6), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (Config.NEON_CYAN[0], Config.NEON_CYAN[1], Config.NEON_CYAN[2], 100),
                           glow_surf.get_rect())
        surface.blit(glow_surf, (self.rect.x - 3 + offset[0], self.rect.y - 3 + offset[1]))
        pygame.draw.ellipse(surface, Config.NEON_CYAN,
                          (self.rect.x + offset[0], self.rect.y + offset[1], self.rect.width, self.rect.height))


class Meteor:
    def __init__(self, x, y, size_type, target_pos=None):
        config = METEOR_CONFIGS[size_type]
        self.size_type = size_type
        self.rect = pygame.Rect(x, y, config["size"], config["size"])
        self.score_value = config["score"]
        self.color = config["color"]
        
        # Health system based on size
        if size_type == MeteorSize.LARGE:
            self.health = 4  # Büyük: 4 vuruş
            self.max_health = 4
        elif size_type == MeteorSize.MEDIUM:
            self.health = 2  # Orta: 2 vuruş
            self.max_health = 2
        else:  # SMALL
            self.health = 1  # Küçük: 1 vuruş
            self.max_health = 1
        
        base_speed = (2.5 + random.uniform(0, 1.5)) * config["speed_mult"]
        
        if target_pos and random.random() < Config.TARGETED_METEOR_CHANCE:
            target_vector = Vector2(target_pos[0] - x, target_pos[1] - y)
            if target_vector.length() > 0:
                target_vector.normalize_ip()
                self.velocity_x = target_vector.x * base_speed
                self.velocity_y = target_vector.y * base_speed
            else:
                self.velocity_x = random.uniform(-1.0, 1.0) * base_speed * 0.3
                self.velocity_y = base_speed
        else:
            self.velocity_x = random.uniform(-1.0, 1.0) * base_speed * 0.3
            self.velocity_y = base_speed
    
    def update(self, dt):
        self.rect.x += self.velocity_x * dt * 60
        self.rect.y += self.velocity_y * dt * 60
    
    def is_off_screen(self):
        return self.rect.y > Config.WINDOW_HEIGHT + self.rect.height
    
    def draw(self, surface, offset=(0, 0)):
        """Draw meteor with realistic gray stone texture and shading"""
        center = (self.rect.centerx + offset[0], self.rect.centery + offset[1])
        radius = self.rect.width // 2
        
        # Realistic gray stone colors with shading
        base_color = self.color  # Already gray (120, 100, 80)
        highlight = tuple(min(255, c + 50) for c in base_color)  # Lighter gray highlight
        shadow = tuple(max(0, c - 40) for c in base_color)  # Darker gray shadow
        mid_tone = tuple((c + base_color[0]) // 2 for c in base_color)  # Mid-tone gray
        
        # Anti-aliased drawing with smooth edges
        # Subtle glow (not neon, realistic)
        glow_surf = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*base_color, 80), (radius + 2, radius + 2), radius + 2)
        surface.blit(glow_surf, (center[0] - radius - 2, center[1] - radius - 2))
        
        # Main meteor body (gray stone)
        pygame.draw.circle(surface, base_color, center, radius)
        
        # Shadow for depth (realistic stone shadow)
        shadow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (*shadow, 200), (radius, radius), radius - 1)
        surface.blit(shadow_surf, (center[0] - radius + 2, center[1] - radius + 2))
        
        # Realistic highlights for 3D stone effect
        pygame.draw.circle(surface, highlight, (center[0] - radius // 3, center[1] - radius // 4), radius // 3)
        pygame.draw.circle(surface, shadow, (center[0] - radius // 3 - 1, center[1] - radius // 4 + 1), radius // 4)
        pygame.draw.circle(surface, highlight, (center[0] + radius // 4, center[1] + radius // 6), radius // 4)
        pygame.draw.circle(surface, mid_tone, (center[0] + radius // 5, center[1] - radius // 3), radius // 5)
        
        # Additional stone texture details
        pygame.draw.circle(surface, shadow, (center[0] - radius // 2, center[1] + radius // 3), radius // 6)
        pygame.draw.circle(surface, highlight, (center[0] + radius // 3, center[1] - radius // 2), radius // 7)


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, Config.PLAYER_WIDTH, Config.PLAYER_HEIGHT)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.rotation = 0.0
        self.target_rotation = 0.0
        self.image = None
        self.flame_image = None
        self.original_flame_width = None
        self.original_flame_height = None
        self._load_images()
    
    def _load_images(self):
        try:
            if os.path.exists("newrocket.png"):
                self.image = pygame.image.load("newrocket.png").convert_alpha()
                self.image = pygame.transform.smoothscale(self.image, (Config.PLAYER_WIDTH, Config.PLAYER_HEIGHT))
        except:
            self.image = None
        
        try:
            # Load flame image (alev.png)
            if os.path.exists("alev.png"):
                self.flame_image = pygame.image.load("alev.png").convert_alpha()
                # Store original dimensions for dynamic scaling
                self.original_flame_width = self.flame_image.get_width()
                self.original_flame_height = self.flame_image.get_height()
            else:
                self.flame_image = None
                self.original_flame_width = None
                self.original_flame_height = None
        except Exception as e:
            self.flame_image = None
            self.original_flame_width = None
            self.original_flame_height = None
    
    def update(self, dt, keys, speed_multiplier=1.0):
        acceleration_x = 0.0
        acceleration_y = 0.0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            acceleration_x -= Config.PLAYER_ACCELERATION
            self.target_rotation = -Config.MAX_ROTATION
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            acceleration_x += Config.PLAYER_ACCELERATION
            self.target_rotation = Config.MAX_ROTATION
        else:
            self.target_rotation = 0.0
        
        self.rotation += (self.target_rotation - self.rotation) * Config.ROTATION_LERP_SPEED * dt * 60
        self.rotation = max(-Config.MAX_ROTATION, min(Config.MAX_ROTATION, self.rotation))
        
        current_acceleration = Config.PLAYER_ACCELERATION * speed_multiplier
        current_max_speed = Config.PLAYER_MAX_SPEED * speed_multiplier
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            acceleration_y -= current_acceleration * 1.5
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            acceleration_y += current_acceleration
        
        self.velocity_x += acceleration_x * dt * 60
        self.velocity_y += acceleration_y * dt * 60
        
        self.velocity_x *= Config.PLAYER_FRICTION
        self.velocity_y *= Config.PLAYER_FRICTION
        
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if speed > current_max_speed:
            self.velocity_x = (self.velocity_x / speed) * current_max_speed
            self.velocity_y = (self.velocity_y / speed) * current_max_speed
        
        self.rect.x += self.velocity_x * dt * 60
        self.rect.y += self.velocity_y * dt * 60
        
        self.rect.x = max(0, min(self.rect.x, Config.WINDOW_WIDTH - Config.PLAYER_WIDTH))
        self.rect.y = max(0, min(self.rect.y, Config.WINDOW_HEIGHT - Config.PLAYER_HEIGHT))
    
    def get_speed(self):
        return math.sqrt(self.velocity_x**2 + self.velocity_y**2)
    
    def shoot(self, weapon_level):
        bullets = []
        if weapon_level == 1:
            # Tek atış - ortada
            bullets.append(Bullet(self.rect.centerx, self.rect.top))
        elif weapon_level == 2:
            # Çift atış - sağ ve sol
            bullets.append(Bullet(self.rect.centerx - 15, self.rect.top))
            bullets.append(Bullet(self.rect.centerx + 15, self.rect.top))
        elif weapon_level >= 3:
            # Üçlü atış - orta, sağ ve sol (3 mermi aynı anda)
            bullets.append(Bullet(self.rect.centerx, self.rect.top))  # Ortada
            bullets.append(Bullet(self.rect.centerx - 20, self.rect.top))  # Solda
            bullets.append(Bullet(self.rect.centerx + 20, self.rect.top))  # Sağda
        return bullets
    
    def draw(self, surface, offset=(0, 0), keys=None, speed_multiplier=1.0):
        draw_x = self.rect.x + offset[0]
        draw_y = self.rect.y + offset[1]
        
        # Calculate rocket position and rotation ONCE for smooth rendering
        rocket_center = (self.rect.centerx + offset[0], self.rect.centery + offset[1])
        rocket_bottom = (self.rect.centerx + offset[0], self.rect.bottom + offset[1])
        
        # Rocket (drawn FIRST to get correct positioning for flame)
        rotated_rocket = None
        rocket_rect = None
        
        if self.image is not None:
            if abs(self.rotation) > 0.1:
                # Rotate rocket image
                rotated_rocket = pygame.transform.rotate(self.image, -self.rotation)
                # Get rect centered on rocket center (prevents diagonal drift)
                rocket_rect = rotated_rocket.get_rect(center=rocket_center)
            else:
                rotated_rocket = self.image
                rocket_rect = self.image.get_rect(topleft=(draw_x, draw_y))
        
        # Flame - draw BEFORE rocket (behind), pinned to rocket's bottom
        if keys and self.flame_image is not None and rotated_rocket is not None:
            is_accelerating = keys[pygame.K_UP] or keys[pygame.K_w]
            speed = self.get_speed()
            current_max_speed = Config.PLAYER_MAX_SPEED * speed_multiplier
            
            # Calculate flame size based on acceleration
            if is_accelerating:
                speed_ratio = min(speed / current_max_speed, 1.0)
                flame_alpha = int(180 + (speed_ratio * 75))
                flame_height_multiplier = 0.4 + (speed_ratio * 2.1)
                flame_width_multiplier = 0.5 + (speed_ratio * 0.5)
            else:
                flame_alpha = 0
                flame_height_multiplier = 0
                flame_width_multiplier = 0
            
            if flame_alpha > 0:
                # Calculate flame size
                target_base_width = int(Config.PLAYER_WIDTH * 0.7)
                target_base_height = int(Config.PLAYER_HEIGHT * 0.8)
                base_flame_width = max(int(target_base_width * flame_width_multiplier), Config.PLAYER_WIDTH // 4)
                base_flame_height = max(int(target_base_height * flame_height_multiplier), Config.PLAYER_HEIGHT // 5)
                
                # Scale flame
                scaled_flame = pygame.transform.smoothscale(self.flame_image, (base_flame_width, base_flame_height))
                
                # Remove black background FIRST
                scaled_flame = scaled_flame.convert_alpha()
                scaled_flame.set_colorkey((0, 0, 0))
                
                # Apply transparency
                scaled_flame.set_alpha(flame_alpha)
                
                # Rotate flame WITH rocket (same angle)
                if abs(self.rotation) > 0.1:
                    scaled_flame = pygame.transform.rotate(scaled_flame, -self.rotation)
                
                # Pin flame to rocket's bottom center (midbottom)
                flame_rect = scaled_flame.get_rect()
                flame_rect.midtop = rocket_rect.midbottom
                
                # Draw flame FIRST (behind rocket)
                surface.blit(scaled_flame, flame_rect)
        
        # Draw rocket AFTER flame (on top)
        if rotated_rocket is not None and rocket_rect is not None:
            surface.blit(rotated_rocket, rocket_rect)
        else:
            # Fallback drawing
            pygame.draw.rect(surface, (210, 210, 255), (draw_x, draw_y, self.rect.width, self.rect.height), border_radius=self.rect.width // 2)


# ==================== MAIN GAME CLASS ====================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT),
                                              pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.state = "menu"  # menu, playing, paused, shop, settings
        self.shop_section = "main"  # main, weapons
        self.language = Language.TURKISH
        self.volume = 0.5  # Volume level (0.0 to 1.0)
        
        # Game objects
        self.player = None
        self.meteors = []
        self.bullets = []
        self.coins = []
        self.particles = []
        self.screen_shake = ScreenShake()
        self.background = ParallaxBackground(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        
        # Game stats
        self.current_score = 0.0
        self.total_gold = 0
        self.high_score = 0.0
        self.last_run_score = 0
        self.is_new_record = False
        
        # Shop items
        self.weapon_level = 1
        self.has_shield = False
        self.has_magnet = False
        self.speed_boost_level = 0
        self.shield_active = False
        self.shield_timer = 0.0
        
        # Spawn system (dt-based for smooth continuous flow)
        self.spawn_timer = 0.0  # Time accumulator for dt-based spawning
        self.game_time = 0.0
        self.base_spawn_interval = 1.2  # Base spawn interval in seconds (smooth continuous flow)
        
        # Button states (for realistic button interactions)
        self.pressed_buttons = {}  # Track which buttons are currently pressed
        self.button_scales = {}  # Track button scales for LERP animation
        self.button_glow_intensities = {}  # Track glow intensities for LERP
        
        # Bloom effect surface
        self.bloom_surface = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
        
        # Fade effect for menu transitions (disabled for instant transitions)
        self.fade_alpha = 0
        self.fade_direction = 0  # 0 = none, 1 = fade in, -1 = fade out
        self.fade_speed = 20.0  # Much faster fade
        
        # Sounds
        self.hit_sound = None
        self.start_sound = None
        self._load_sounds()
        
        # Language flag images
        self.turk_flag_image = None
        self.eng_flag_image = None
        self.settings_icon_image = None
        self._load_flag_images()
        self._load_settings_icon()
        
        # Initialize menu meteors for background effect
        for _ in range(4):
            self._spawn_menu_meteor()
    
    def _load_sounds(self):
        try:
            if os.path.exists("hit.wav"):
                self.hit_sound = pygame.mixer.Sound("hit.wav")
        except:
            pass
        try:
            if os.path.exists("start.wav"):
                self.start_sound = pygame.mixer.Sound("start.wav")
        except:
            pass
        try:
            if os.path.exists("music.mp3") or os.path.exists("music.ogg"):
                music_file = "music.mp3" if os.path.exists("music.mp3") else "music.ogg"
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1)
        except:
            pass
    
    def _load_flag_images(self):
        """Load flag images for language selection"""
        flag_size = 40  # Bayrak boyutu
        
        # Türk bayrağı - yeni görsel
        turk_flag_paths = [
            "turk_bayragi.png",
            r"C:\Users\Eren\.cursor\projects\c-Users-Eren-Desktop-proje-yap-m\assets\c__Users_Eren_AppData_Roaming_Cursor_User_workspaceStorage_22ea1cbefb422ba0484b2555f2307e4a_images_images-7d34a241-0627-49bb-b7dd-47d3b7aca5d9.png"
        ]
        for path in turk_flag_paths:
            try:
                if os.path.exists(path):
                    self.turk_flag_image = pygame.image.load(path).convert_alpha()
                    self.turk_flag_image = pygame.transform.smoothscale(self.turk_flag_image, (flag_size, flag_size))
                    break
            except:
                continue
        
        # İngilizce bayrağı
        eng_flag_paths = [
            "ingilizce_bayragi.png",
            r"C:\Users\Eren\.cursor\projects\c-Users-Eren-Desktop-proje-yap-m\assets\c__Users_Eren_AppData_Roaming_Cursor_User_workspaceStorage_22ea1cbefb422ba0484b2555f2307e4a_images_download-6be46051-ada2-4875-a00c-703f062ebaf7.png"
        ]
        for path in eng_flag_paths:
            try:
                if os.path.exists(path):
                    self.eng_flag_image = pygame.image.load(path).convert_alpha()
                    self.eng_flag_image = pygame.transform.smoothscale(self.eng_flag_image, (flag_size, flag_size))
                    break
            except:
                continue
    
    def _load_settings_icon(self):
        """Load settings icon image"""
        icon_size = 60  # Icon size for top-left corner
        
        try:
            if os.path.exists("settings.png"):
                self.settings_icon_image = pygame.image.load("settings.png").convert_alpha()
                self.settings_icon_image = pygame.transform.smoothscale(self.settings_icon_image, (icon_size, icon_size))
        except:
            self.settings_icon_image = None
    
    def t(self, key):
        return TRANSLATIONS[self.language].get(key, key)
    
    def _clamp_mouse_pos(self, pos):
        """Clamp mouse position to screen bounds to prevent crashes"""
        x, y = pos
        x = max(0, min(x, Config.WINDOW_WIDTH - 1))
        y = max(0, min(y, Config.WINDOW_HEIGHT - 1))
        return (x, y)
    
    def _get_safe_mouse_pos(self):
        """Get mouse position safely clamped to screen bounds"""
        try:
            pos = pygame.mouse.get_pos()
            return self._clamp_mouse_pos(pos)
        except:
            return (Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2)
    
    def start_game(self):
        self.state = "playing"
        self.game_time = 0.0
        self.current_score = 0.0
        self.player = Player(Config.WINDOW_WIDTH // 2 - Config.PLAYER_WIDTH // 2,
                            Config.WINDOW_HEIGHT - Config.PLAYER_HEIGHT - 50)
        self.meteors.clear()
        self.bullets.clear()
        self.coins.clear()
        self.particles.clear()
        self.spawn_timer = 0.0  # Reset spawn timer
        self.screen_shake.intensity = 0.0
        
        # Shield kontrolü - satın alındıysa aktif
        if self.has_shield:
            self.shield_active = True
            self.shield_timer = 10.0
        
        # Mıknatıs satın alındıysa aktif (çarpışınca yok olur)
        # Hız ve silah da satın alındıysa aktif (oyun boyunca kullanılır)
        
        if self.start_sound:
            self.start_sound.play()
        
        # Initial meteors
        for _ in range(3):
            self._spawn_meteor()
    
    def _spawn_meteor(self):
        if len(self.meteors) >= Config.MAX_METEORS_ON_SCREEN:
            return
        
        size_type = random.choice(list(MeteorSize))
        meteor_size = METEOR_CONFIGS[size_type]["size"]
        x = random.randint(0, Config.WINDOW_WIDTH - meteor_size)
        y = random.randint(-meteor_size * 3, -meteor_size)
        
        target_pos = None
        if self.player:
            target_pos = (self.player.rect.centerx, self.player.rect.centery)
        
        meteor = Meteor(x, y, size_type, target_pos)
        self.meteors.append(meteor)
    
    def _spawn_menu_meteor(self):
        """Spawn meteors for menu background effect (non-targeting, slower)"""
        if len(self.meteors) >= 8:  # Limit for menu
            return
        
        size_type = random.choice(list(MeteorSize))
        meteor_size = METEOR_CONFIGS[size_type]["size"]
        x = random.randint(0, Config.WINDOW_WIDTH - meteor_size)
        y = random.randint(-meteor_size * 3, -meteor_size)
        
        # No targeting for menu meteors - just random movement
        meteor = Meteor(x, y, size_type, None)
        # Slow down meteors for menu background effect
        meteor.velocity_x *= 0.5
        meteor.velocity_y *= 0.5
        self.meteors.append(meteor)
    
    def _update_spawn_system(self, dt):
        """Update meteor spawn system using dt for smooth continuous flow (no pauses)"""
        if len(self.meteors) >= Config.MAX_METEORS_ON_SCREEN:
            return
        
        # Calculate dynamic spawn interval based on game time (gradually decreases)
        reduction_factor = max(0.5, 1.0 - (self.game_time / 120.0))  # Gets faster over 2 minutes
        current_spawn_interval = self.base_spawn_interval * reduction_factor
        current_spawn_interval = max(0.5, current_spawn_interval)  # Minimum 0.5 seconds
        
        # Accumulate time using dt (frame-independent)
        self.spawn_timer += dt
        
        # Spawn when timer reaches interval
        if self.spawn_timer >= current_spawn_interval:
            spawn_count = 1
            # Increase spawn count as game progresses
            if self.game_time > 15:
                spawn_count = random.randint(1, 2)
            if self.game_time > 45:
                spawn_count = random.randint(1, 3)
            
            available_slots = Config.MAX_METEORS_ON_SCREEN - len(self.meteors)
            spawn_count = min(spawn_count, available_slots)
            
            for _ in range(spawn_count):
                self._spawn_meteor()
            
            # Reset timer (keep remainder for smooth flow)
            self.spawn_timer = 0.0
    
    def _create_explosion(self, x, y, meteor_type, is_large=False):
        """Create particle explosion with enhanced visual effects"""
        particle_count = 15 if meteor_type == MeteorSize.LARGE else 10 if meteor_type == MeteorSize.MEDIUM else 6
        if is_large:
            particle_count = max(particle_count, 12)
        
        # Enhanced particle colors with neon tints
        particle_colors = [
            (180, 100, 220),  # Purple debris
            (200, 60, 240),   # Bright purple
            (255, 150, 0),    # Orange sparks
            (255, 200, 100),  # Bright orange
            (150, 150, 200),  # Blue-gray debris
            (100, 100, 150)   # Dark debris
        ]
        
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.5, 7.0)  # Slightly faster particles
            color = random.choice(particle_colors)
            # Vary particle size
            size = random.randint(3, 8) if meteor_type == MeteorSize.LARGE else random.randint(2, 6)
            self.particles.append(Particle(x, y, math.cos(angle) * speed, math.sin(angle) * speed, color, size=size))
        
        # Enhanced screen shake based on meteor size
        shake_amount = 4.0 if meteor_type == MeteorSize.LARGE else 2.5 if meteor_type == MeteorSize.MEDIUM else 1.5
        if is_large:
            shake_amount = max(shake_amount, 3.0)
        self.screen_shake.add_shake(shake_amount)
    
    def _spawn_coins(self, x, y):
        if random.random() < Config.COIN_DROP_CHANCE:
            coin_count = random.randint(1, 3)
            for _ in range(coin_count):
                angle = random.uniform(0, 2 * math.pi)
                spread_distance = random.uniform(30, 60)
                coin_x = x + math.cos(angle) * spread_distance
                coin_y = y + math.sin(angle) * spread_distance
                self.coins.append(Coin(coin_x, coin_y, random.choice([1, 1, 1, 2, 3]), is_score=False))
    
    def _spawn_score_drops(self, x, y, size_type):
        """Spawn score pickups based on meteor size"""
        if size_type == MeteorSize.SMALL:
            # Küçük: %20 şansla 1 puan
            if random.random() < 0.2:
                self.coins.append(Coin(x, y, 1, is_score=True))
        elif size_type == MeteorSize.MEDIUM:
            # Orta: random 0, 1, veya 2 puan
            score_value = random.choice([0, 1, 2])
            if score_value > 0:
                self.coins.append(Coin(x, y, score_value, is_score=True))
        else:  # LARGE
            # Büyük: Her zaman 2 veya 3 puan
            score_value = random.choice([2, 3])
            self.coins.append(Coin(x, y, score_value, is_score=True))
    
    def update_playing(self, dt, keys):
        self.game_time += dt
        
        # Spawn system (dt-based for smooth continuous flow)
        self._update_spawn_system(dt)
        
        # Screen shake
        self.screen_shake.update(dt)
        
        # Background
        self.background.update(dt)
        
        # Player
        speed_multiplier = 1.0 + (self.speed_boost_level * 0.3)
        self.player.update(dt, keys, speed_multiplier)
        
        speed = self.player.get_speed()
        self.current_score += speed * dt * 0.1
        
        if int(self.current_score) > self.high_score:
            self.is_new_record = True
        else:
            self.is_new_record = False
        
        # Bullets
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                continue
            
            for meteor in self.meteors[:]:
                if bullet.rect.colliderect(meteor.rect):
                    self.bullets.remove(bullet)
                    
                    # Reduce meteor health
                    meteor.health -= 1
                    
                    # Only destroy if health reaches 0
                    if meteor.health <= 0:
                        meteor_pos = meteor.rect.center
                        self._create_explosion(meteor_pos[0], meteor_pos[1], meteor.size_type)
                        self._spawn_coins(meteor_pos[0], meteor_pos[1])  # Altın düşür
                        self._spawn_score_drops(meteor_pos[0], meteor_pos[1], meteor.size_type)  # Puan düşür
                        self.meteors.remove(meteor)
                    else:
                        # Hit effect but not destroyed - create small particle effect
                        meteor_pos = meteor.rect.center
                        for _ in range(3):
                            angle = random.uniform(0, math.pi * 2)
                            speed = random.uniform(1, 3)
                            self.particles.append(
                                Particle(meteor_pos[0], meteor_pos[1],
                                       math.cos(angle) * speed, math.sin(angle) * speed,
                                       (255, 255, 255), life=0.3, size=2)
                            )
                    break
        
        # Meteors
        for meteor in self.meteors[:]:
            meteor.update(dt)
            if meteor.is_off_screen():
                self.meteors.remove(meteor)
        
        # Space destroy
        if keys[pygame.K_SPACE]:
            destroy_radius = 150
            for meteor in self.meteors[:]:
                distance = math.sqrt(
                    (meteor.rect.centerx - self.player.rect.centerx)**2 +
                    (meteor.rect.centery - self.player.rect.centery)**2
                )
                if distance < destroy_radius:
                    meteor_pos = meteor.rect.center
                    self.current_score += meteor.score_value
                    self._create_explosion(meteor_pos[0], meteor_pos[1], meteor.size_type, is_large=True)
                    self._spawn_coins(meteor_pos[0], meteor_pos[1])
                    self.meteors.remove(meteor)
        
        # Shield
        if self.has_shield and self.shield_active:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False
        
        # Collisions
        for meteor in self.meteors[:]:
            if self.player.rect.colliderect(meteor.rect):
                # Önce kalkan kontrol et
                if self.has_shield and self.shield_active:
                    self.shield_active = False
                    self.shield_timer = 0.0
                    self._create_explosion(meteor.rect.centerx, meteor.rect.centery, meteor.size_type)
                    self.meteors.remove(meteor)
                # Kalkan yoksa mıknatıs kontrol et
                elif self.has_magnet:
                    self.has_magnet = False  # Mıknatıs bir çarpışmayı engelleyip yok olur
                    self._create_explosion(meteor.rect.centerx, meteor.rect.centery, meteor.size_type)
                    self.meteors.remove(meteor)
                # İkisi de yoksa oyun biter
                else:
                    self.screen_shake.add_shake(5.0)
                    if self.hit_sound:
                        self.hit_sound.play()
                    self.last_run_score = int(self.current_score)
                    self.total_gold += int(self.current_score) // 2
                    if self.current_score > self.high_score:
                        self.high_score = self.current_score
                    
                    # Tüm tek kullanımlık öğeleri sıfırla (her oyun için ayrı satın alınmalı)
                    self.has_shield = False
                    self.has_magnet = False
                    self.speed_boost_level = 0
                    self.weapon_level = 1
                    
                    # Ensure shop_section exists before switching to shop
                    if not hasattr(self, 'shop_section'):
                        self.shop_section = "main"
                    self.state = "shop"
                    self.shop_section = "main"
                    break
        
        # Coins
        player_pos = (self.player.rect.centerx, self.player.rect.centery)
        for coin in self.coins[:]:
            coin.update(dt, player_pos, self.has_magnet)
            if coin.rect.y > Config.WINDOW_HEIGHT or coin.rect.x < -50 or coin.rect.x > Config.WINDOW_WIDTH + 50:
                self.coins.remove(coin)
            elif self.player.rect.colliderect(coin.rect):
                if coin.is_score:
                    # Puan toplama
                    self.current_score += coin.value
                else:
                    # Altın toplama
                    self.total_gold += coin.value
                self.coins.remove(coin)
        
        # Particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)
    
    def draw_playing(self, surface, keys):
        # Background
        surface.fill(Config.BACKGROUND_COLOR)
        self.background.draw(surface)
        
        offset = self.screen_shake.get_offset()
        
        # Bloom surface for neon effects
        self.bloom_surface.fill((0, 0, 0, 0))
        
        # Particles
        for particle in self.particles:
            particle.draw(surface, offset)
        
        # Coins
        for coin in self.coins:
            coin.draw(surface, offset)
        
        # Meteors
        for meteor in self.meteors:
            meteor.draw(surface, offset)
        
        # Bullets with bloom
        for bullet in self.bullets:
            bullet.draw(surface, offset)
            # Bloom effect for bullets
            glow_rect = pygame.Rect(bullet.rect.x + offset[0] - 5, bullet.rect.y + offset[1] - 5,
                                   bullet.rect.width + 10, bullet.rect.height + 10)
            pygame.draw.ellipse(self.bloom_surface, 
                              (Config.NEON_CYAN[0], Config.NEON_CYAN[1], Config.NEON_CYAN[2], 100),
                              glow_rect)
        
        # Shield with bloom (Mavi şeffaf çember)
        if self.has_shield and self.shield_active:
            shield_radius = max(Config.PLAYER_WIDTH, Config.PLAYER_HEIGHT) // 2 + 15
            shield_alpha = int(120 + 80 * math.sin(pygame.time.get_ticks() / 150.0))
            shield_color = (100, 150, 255)  # Mavi renk
            
            # Kalkan çemberi
            shield_surf = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (shield_color[0], shield_color[1], shield_color[2], shield_alpha),
                             (shield_radius, shield_radius), shield_radius, width=4)
            surface.blit(shield_surf, (self.player.rect.centerx - shield_radius + offset[0],
                                     self.player.rect.centery - shield_radius + offset[1]))
            
            # İç çember (daha şeffaf)
            inner_surf = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(inner_surf, (shield_color[0], shield_color[1], shield_color[2], shield_alpha // 3),
                             (shield_radius, shield_radius), shield_radius - 2)
            surface.blit(inner_surf, (self.player.rect.centerx - shield_radius + offset[0],
                                     self.player.rect.centery - shield_radius + offset[1]))
            
            # Bloom for shield
            bloom_shield_surf = pygame.Surface((shield_radius * 2 + 20, shield_radius * 2 + 20), pygame.SRCALPHA)
            pygame.draw.circle(bloom_shield_surf, 
                             (shield_color[0], shield_color[1], shield_color[2], 60),
                             (shield_radius + 10, shield_radius + 10), shield_radius + 10)
            self.bloom_surface.blit(bloom_shield_surf, 
                                   (self.player.rect.centerx - shield_radius - 10 + offset[0],
                                    self.player.rect.centery - shield_radius - 10 + offset[1]))
        
        # Magnet with bloom (Mor/Yeşil şeffaf çember)
        if self.has_magnet:
            magnet_radius = max(Config.PLAYER_WIDTH, Config.PLAYER_HEIGHT) // 2 + 18
            magnet_alpha = int(100 + 70 * math.sin(pygame.time.get_ticks() / 200.0))
            magnet_color = (150, 100, 255)  # Mor renk (mıknatıs için)
            
            # Mıknatıs çemberi
            magnet_surf = pygame.Surface((magnet_radius * 2, magnet_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(magnet_surf, (magnet_color[0], magnet_color[1], magnet_color[2], magnet_alpha),
                             (magnet_radius, magnet_radius), magnet_radius, width=3)
            surface.blit(magnet_surf, (self.player.rect.centerx - magnet_radius + offset[0],
                                     self.player.rect.centery - magnet_radius + offset[1]))
            
            # İç çember (daha şeffaf)
            inner_magnet_surf = pygame.Surface((magnet_radius * 2, magnet_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(inner_magnet_surf, (magnet_color[0], magnet_color[1], magnet_color[2], magnet_alpha // 4),
                             (magnet_radius, magnet_radius), magnet_radius - 2)
            surface.blit(inner_magnet_surf, (self.player.rect.centerx - magnet_radius + offset[0],
                                     self.player.rect.centery - magnet_radius + offset[1]))
            
            # Bloom for magnet
            bloom_magnet_surf = pygame.Surface((magnet_radius * 2 + 20, magnet_radius * 2 + 20), pygame.SRCALPHA)
            pygame.draw.circle(bloom_magnet_surf, 
                             (magnet_color[0], magnet_color[1], magnet_color[2], 50),
                             (magnet_radius + 10, magnet_radius + 10), magnet_radius + 10)
            self.bloom_surface.blit(bloom_magnet_surf, 
                                   (self.player.rect.centerx - magnet_radius - 10 + offset[0],
                                    self.player.rect.centery - magnet_radius - 10 + offset[1]))
        
        # Player
        self.player.draw(surface, offset, keys, 1.0 + (self.speed_boost_level * 0.3))
        
        # Apply bloom effect (blend mode)
        surface.blit(self.bloom_surface, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # UI with glow
        score_color = Config.GOLD_COLOR if self.is_new_record else Config.TEXT_COLOR
        font = pygame.font.SysFont("consolas", 32, bold=True)
        score_text = font.render(f"{self.t('score')}: {int(self.current_score)}", True, score_color)
        # Glow effect for score
        glow_score = font.render(f"{self.t('score')}: {int(self.current_score)}", True, 
                               (int(score_color[0] * 0.3), int(score_color[1] * 0.3), int(score_color[2] * 0.3)))
        surface.blit(glow_score, (17, 17))
        surface.blit(score_text, (15, 15))
        
        gold_text = font.render(f"{self.t('points')}: {int(self.total_gold)}", True, Config.GOLD_COLOR)
        glow_gold = font.render(f"{self.t('points')}: {int(self.total_gold)}", True,
                              (int(Config.GOLD_COLOR[0] * 0.3), int(Config.GOLD_COLOR[1] * 0.3), int(Config.GOLD_COLOR[2] * 0.3)))
        surface.blit(glow_gold, (17, 57))
        surface.blit(gold_text, (15, 55))
    
    def draw_menu(self, surface):
        # Space background with flowing stars (same as in game)
        surface.fill(Config.BACKGROUND_COLOR)  # Deep black
        self.background.draw(surface)  # Draw parallax starfield
        
        # Draw flowing meteors in background
        for meteor in self.meteors:
            meteor.draw(surface)
        
        # Title - Clean cyan style (no pink/magenta)
        title_font = pygame.font.SysFont("consolas", 110, bold=True)
        title_text = "INFINITE ORBIT"
        
        title_center = (Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2 - 80)
        
        # Glow effect (cyan only)
        glow_surf = title_font.render(title_text, True, (0, 180, 220))
        glow_surf.set_alpha(120)
        for offset in range(4, 0, -1):
            glow_rect = glow_surf.get_rect(center=(title_center[0], title_center[1]))
            glow_rect.inflate_ip(offset * 2, offset * 2)
            surface.blit(glow_surf, glow_rect)
        
        # Main cyan text - bright and clean
        title_surf = title_font.render(title_text, True, (0, 255, 255))
        title_rect = title_surf.get_rect(center=title_center)
        surface.blit(title_surf, title_rect)
        
        # Subtitle - "BAŞLAMAK İÇİN TIKLA" / "CLICK TO START"
        subtitle_font = pygame.font.SysFont("consolas", 32, bold=True)
        subtitle_text = "BAŞLAMAK İÇİN TIKLA" if self.language == Language.TURKISH else "CLICK TO START"
        subtitle_surf = subtitle_font.render(subtitle_text, True, (150, 220, 255))
        subtitle_rect = subtitle_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2 + 50))
        surface.blit(subtitle_surf, subtitle_rect)
        
        # High score
        if self.high_score > 0:
            hs_font = pygame.font.SysFont("consolas", 28, bold=True)
            hs_text = f"{self.t('high_score')}: {int(self.high_score)}"
            hs_surf = hs_font.render(hs_text, True, (255, 200, 100))
            hs_rect = hs_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2 + 160))
            surface.blit(hs_surf, hs_rect)
        
        # Language button
        self._draw_language_button(surface)
        
        # Settings icon (top-left corner)
        self._draw_menu_settings_icon(surface)
    
    def _draw_menu_settings_icon(self, surface):
        """Draw settings icon in top-left corner of menu"""
        icon_size = 60
        icon_x = 20
        icon_y = 20
        icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
        
        try:
            mouse_pos = self._get_safe_mouse_pos()
        except:
            mouse_pos = (Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2)
        
        is_hovered = icon_rect.collidepoint(mouse_pos)
        
        # Draw icon background (hover effect)
        if is_hovered:
            # Brighter glow on hover
            glow_surf = pygame.Surface((icon_size + 10, icon_size + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (Config.NEON_CYAN[0], Config.NEON_CYAN[1], Config.NEON_CYAN[2], 150),
                           glow_surf.get_rect(), border_radius=10)
            surface.blit(glow_surf, (icon_x - 5, icon_y - 5))
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        
        # Draw icon image or fallback
        if self.settings_icon_image:
            surface.blit(self.settings_icon_image, icon_rect.topleft)
        else:
            # Fallback: draw simple gear icon
            pygame.draw.circle(surface, (100, 100, 150), icon_rect.center, icon_size // 2)
            pygame.draw.circle(surface, (150, 150, 200), icon_rect.center, icon_size // 3)
        
        # Border
        if is_hovered:
            pygame.draw.rect(surface, Config.NEON_CYAN, icon_rect, width=3, border_radius=10)
        else:
            pygame.draw.rect(surface, (100, 100, 150), icon_rect, width=2, border_radius=10)
    
    def draw_paused(self, surface):
        """Draw pause menu overlay on top of game"""
        # Draw the game in background (frozen)
        if self.player:
            keys = pygame.key.get_pressed()
            self.draw_playing(surface, keys)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark overlay
        surface.blit(overlay, (0, 0))
        
        # Pause panel (taller for settings button)
        panel_width = 400
        panel_height = 320
        panel_x = Config.WINDOW_WIDTH // 2 - panel_width // 2
        panel_y = Config.WINDOW_HEIGHT // 2 - panel_height // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Panel background
        pygame.draw.rect(surface, (50, 50, 70), panel_rect, border_radius=20)
        pygame.draw.rect(surface, (100, 100, 150), panel_rect, width=3, border_radius=20)
        
        # Paused title
        title_font = pygame.font.SysFont("consolas", 48, bold=True)
        title_text = self.t("paused")
        title_surf = title_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(panel_rect.centerx, panel_rect.y + 50))
        surface.blit(title_surf, title_rect)
        
        try:
            mouse_pos = self._get_safe_mouse_pos()
        except:
            mouse_pos = (Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2)
        
        # Continue button
        continue_button_width = 300
        continue_button_height = 60
        continue_button_rect = pygame.Rect(panel_rect.centerx - continue_button_width // 2,
                                          panel_rect.y + 120,
                                          continue_button_width, continue_button_height)
        continue_hover = continue_button_rect.collidepoint(mouse_pos)
        
        if continue_hover:
            continue_color = (100, 200, 100)  # Brighter green
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            continue_color = (80, 180, 80)  # Normal green
        
        # Draw continue button
        pygame.draw.rect(surface, continue_color, continue_button_rect, border_radius=15)
        pygame.draw.rect(surface, (50, 150, 50), continue_button_rect, width=3, border_radius=15)
        
        # Continue button text
        continue_font = pygame.font.SysFont("consolas", 28, bold=True)
        continue_text = self.t("continue_game")
        continue_text_surf = continue_font.render(continue_text, True, (255, 255, 255))
        continue_text_rect = continue_text_surf.get_rect(center=continue_button_rect.center)
        # Black outline for visibility
        outline_continue = continue_font.render(continue_text, True, (0, 0, 0))
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    surface.blit(outline_continue, (continue_text_rect.x + dx, continue_text_rect.y + dy))
        surface.blit(continue_text_surf, continue_text_rect)
        
        # Settings button
        settings_button_width = 300
        settings_button_height = 60
        settings_button_rect = pygame.Rect(panel_rect.centerx - settings_button_width // 2,
                                          panel_rect.y + 200,
                                          settings_button_width, settings_button_height)
        settings_hover = settings_button_rect.collidepoint(mouse_pos)
        
        if settings_hover:
            settings_color = (255, 165, 0)  # Brighter orange
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            settings_color = (255, 140, 0)  # Normal orange
        
        # Draw settings button
        pygame.draw.rect(surface, settings_color, settings_button_rect, border_radius=15)
        pygame.draw.rect(surface, (200, 100, 0), settings_button_rect, width=3, border_radius=15)
        
        # Settings button text
        settings_font = pygame.font.SysFont("consolas", 28, bold=True)
        settings_text = self.t("settings")
        settings_text_surf = settings_font.render(settings_text, True, (255, 255, 255))
        settings_text_rect = settings_text_surf.get_rect(center=settings_button_rect.center)
        # Black outline for visibility
        outline_settings = settings_font.render(settings_text, True, (0, 0, 0))
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    surface.blit(outline_settings, (settings_text_rect.x + dx, settings_text_rect.y + dy))
        surface.blit(settings_text_surf, settings_text_rect)
    
    def _draw_language_button(self, surface):
        """Draw language selection buttons with flag images and text"""
        flag_size = 40
        spacing = 10
        start_x = 15
        start_y = Config.WINDOW_HEIGHT - 70
        
        try:
            mouse_pos = self._get_safe_mouse_pos()
        except:
            mouse_pos = (Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2)
        
        # Türk bayrağı
        turk_rect = pygame.Rect(start_x, start_y, flag_size, flag_size)
        is_hovered_turk = turk_rect.collidepoint(mouse_pos)
        
        if self.turk_flag_image:
            surface.blit(self.turk_flag_image, turk_rect.topleft)
        else:
            # Fallback: çizim
            pygame.draw.rect(surface, (227, 10, 23), turk_rect)
            pygame.draw.circle(surface, (255, 255, 255), turk_rect.center, flag_size // 3)
            pygame.draw.circle(surface, (227, 10, 23), turk_rect.center, flag_size // 4)
        
        if is_hovered_turk:
            pygame.draw.rect(surface, Config.NEON_CYAN, turk_rect, width=2)
        
        # TUR yazısı
        turk_text_font = pygame.font.SysFont("consolas", 14, bold=True)
        turk_text_color = Config.NEON_CYAN if self.language == Language.TURKISH else Config.TEXT_COLOR
        turk_text = turk_text_font.render("TUR", True, turk_text_color)
        turk_text_rect = turk_text.get_rect(center=(turk_rect.centerx, turk_rect.bottom + 12))
        surface.blit(turk_text, turk_text_rect)
        
        # İngilizce bayrağı
        eng_rect = pygame.Rect(start_x + flag_size + spacing, start_y, flag_size, flag_size)
        is_hovered_eng = eng_rect.collidepoint(mouse_pos)
        
        if self.eng_flag_image:
            surface.blit(self.eng_flag_image, eng_rect.topleft)
        else:
            # Fallback: çizim
            pygame.draw.rect(surface, (0, 35, 149), eng_rect)
            pygame.draw.line(surface, (255, 255, 255), eng_rect.topleft, eng_rect.bottomright, 3)
            pygame.draw.line(surface, (255, 255, 255), eng_rect.topright, eng_rect.bottomleft, 3)
        
        if is_hovered_eng:
            pygame.draw.rect(surface, Config.NEON_CYAN, eng_rect, width=2)
        
        # ENG yazısı
        eng_text_font = pygame.font.SysFont("consolas", 14, bold=True)
        eng_text_color = Config.NEON_CYAN if self.language == Language.ENGLISH else Config.TEXT_COLOR
        eng_text = eng_text_font.render("ENG", True, eng_text_color)
        eng_text_rect = eng_text.get_rect(center=(eng_rect.centerx, eng_rect.bottom + 12))
        surface.blit(eng_text, eng_text_rect)
    
    def draw_shop(self, surface):
        """Draw death screen with space background (flowing stars like in game)"""
        try:
            # Space background - same as in game (flowing stars)
            surface.fill(Config.BACKGROUND_COLOR)  # Deep black
            self.background.draw(surface)  # Draw parallax starfield
            
            # Title "GAME OVER" or "OYUN BİTTİ"
            title_font = pygame.font.SysFont("consolas", 72, bold=True)
            title_text = self.t("game_over")
            title_color = (255, 255, 255)  # White
            title_outline_color = (50, 50, 50)  # Dark gray outline
            
            # Draw outline (shadow effect)
            for dx in [-3, -2, -1, 1, 2, 3]:
                for dy in [-3, -2, -1, 1, 2, 3]:
                    title_surf = title_font.render(title_text, True, title_outline_color)
                    title_rect = title_surf.get_rect(center=(Config.WINDOW_WIDTH // 2 + dx, 120 + dy))
                    surface.blit(title_surf, title_rect)
            
            # Draw main title
            title_surf = title_font.render(title_text, True, title_color)
            title_rect = title_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 120))
            surface.blit(title_surf, title_rect)
            
            # Score display
            score_font = pygame.font.SysFont("consolas", 36, bold=True)
            score_text = f"{self.t('score')}: {int(self.last_run_score)}"
            score_surf = score_font.render(score_text, True, (255, 255, 0))  # Yellow
            score_rect = score_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 200))
            surface.blit(score_surf, score_rect)
            
            if self.last_run_score == int(self.high_score) and self.last_run_score > 0:
                record_font = pygame.font.SysFont("consolas", 28, bold=True)
                record_text = self.t("new_record")
                record_surf = record_font.render(record_text, True, (255, 200, 0))  # Gold
                record_rect = record_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 240))
                surface.blit(record_surf, record_rect)
            
            # Three rounded square buttons (like in the image)
            button_size = 120
            button_spacing = 40
            buttons_y = Config.WINDOW_HEIGHT // 2 + 50
            total_width = 3 * button_size + 2 * button_spacing
            buttons_start_x = Config.WINDOW_WIDTH // 2 - total_width // 2
            
            try:
                mouse_pos = self._get_safe_mouse_pos()
            except:
                mouse_pos = (Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2)
            
            # Shopping Cart Button (left) - Orange-yellow
            cart_button_rect = pygame.Rect(buttons_start_x, buttons_y, button_size, button_size)
            cart_color = (255, 165, 0)  # Orange
            cart_hover = cart_button_rect.collidepoint(mouse_pos)
            if cart_hover:
                cart_color = (255, 200, 0)  # Brighter orange
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            
            # Draw button with 3D effect
            pygame.draw.rect(surface, cart_color, cart_button_rect, border_radius=15)
            pygame.draw.rect(surface, (200, 120, 0), cart_button_rect, width=3, border_radius=15)
            # Highlight
            highlight_rect = pygame.Rect(cart_button_rect.x + 5, cart_button_rect.y + 5, 
                                        cart_button_rect.width - 10, 20)
            pygame.draw.rect(surface, (255, 220, 100), highlight_rect, border_radius=8)
            
            # Shopping cart text - "MAĞAZA"
            cart_text_font = pygame.font.SysFont("consolas", 28, bold=True)
            cart_text = cart_text_font.render("MAĞAZA", True, (255, 255, 255))
            cart_text_rect = cart_text.get_rect(center=cart_button_rect.center)
            # Black outline for better visibility
            outline_cart = cart_text_font.render("MAĞAZA", True, (0, 0, 0))
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        surface.blit(outline_cart, (cart_text_rect.x + dx, cart_text_rect.y + dy))
            surface.blit(cart_text, cart_text_rect)
            
            # Play/Retry Button (center) - Red
            play_button_rect = pygame.Rect(buttons_start_x + button_size + button_spacing, buttons_y, 
                                          button_size, button_size)
            play_color = (255, 0, 0)  # Red
            play_hover = play_button_rect.collidepoint(mouse_pos)
            if play_hover:
                play_color = (255, 50, 50)  # Brighter red
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            
            pygame.draw.rect(surface, play_color, play_button_rect, border_radius=15)
            pygame.draw.rect(surface, (180, 0, 0), play_button_rect, width=3, border_radius=15)
            highlight_rect = pygame.Rect(play_button_rect.x + 5, play_button_rect.y + 5,
                                       play_button_rect.width - 10, 20)
            pygame.draw.rect(surface, (255, 100, 100), highlight_rect, border_radius=8)
            
            # Play icon (triangle) - keep for visual
            play_icon_size = 50
            play_triangle = [
                (play_button_rect.centerx - play_icon_size // 2, play_button_rect.centery - play_icon_size // 2),
                (play_button_rect.centerx - play_icon_size // 2, play_button_rect.centery + play_icon_size // 2),
                (play_button_rect.centerx + play_icon_size // 2, play_button_rect.centery)
            ]
            pygame.draw.polygon(surface, (255, 255, 255), play_triangle)
            
            # Settings Button (right) - Orange-yellow
            settings_button_rect = pygame.Rect(buttons_start_x + 2 * (button_size + button_spacing), 
                                               buttons_y, button_size, button_size)
            settings_color = (255, 165, 0)  # Orange
            settings_hover = settings_button_rect.collidepoint(mouse_pos)
            if settings_hover:
                settings_color = (255, 200, 0)  # Brighter orange
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            
            pygame.draw.rect(surface, settings_color, settings_button_rect, border_radius=15)
            pygame.draw.rect(surface, (200, 120, 0), settings_button_rect, width=3, border_radius=15)
            highlight_rect = pygame.Rect(settings_button_rect.x + 5, settings_button_rect.y + 5,
                                       settings_button_rect.width - 10, 20)
            pygame.draw.rect(surface, (255, 220, 100), highlight_rect, border_radius=8)
            
            # Settings text - "AYARLAR"
            settings_text_font = pygame.font.SysFont("consolas", 26, bold=True)
            settings_text = settings_text_font.render("AYARLAR", True, (255, 255, 255))
            settings_text_rect = settings_text.get_rect(center=settings_button_rect.center)
            # Black outline for better visibility
            outline_settings = settings_text_font.render("AYARLAR", True, (0, 0, 0))
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        surface.blit(outline_settings, (settings_text_rect.x + dx, settings_text_rect.y + dy))
            surface.blit(settings_text, settings_text_rect)
            
            # Button labels - only for center button (Retry/Play)
            label_font = pygame.font.SysFont("consolas", 20, bold=True)
            label_y = buttons_y + button_size + 15
            
            # Only retry label (center button)
            retry_label = label_font.render("TEKRAR BAŞLA", True, (255, 255, 255))
            retry_label_rect = retry_label.get_rect(center=(play_button_rect.centerx, label_y))
            # Black outline
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        outline_surf = label_font.render("TEKRAR BAŞLA", True, (0, 0, 0))
                        surface.blit(outline_surf, (retry_label_rect.x + dx, retry_label_rect.y + dy))
            surface.blit(retry_label, retry_label_rect)
            
            # Back button (ana ekrana dön) - sadece ana ölüm ekranında göster
            if self.shop_section == "main":
                back_button_width = 200
                back_button_height = 50
                back_button_y = label_y + 50
                back_button_rect = pygame.Rect(Config.WINDOW_WIDTH // 2 - back_button_width // 2,
                                               back_button_y, back_button_width, back_button_height)
                back_hover = back_button_rect.collidepoint(mouse_pos)
                if back_hover:
                    back_color = (150, 150, 200)  # Brighter on hover
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    back_color = (100, 100, 150)  # Normal
                
                # Draw back button
                pygame.draw.rect(surface, back_color, back_button_rect, border_radius=10)
                pygame.draw.rect(surface, (70, 70, 100), back_button_rect, width=3, border_radius=10)
                
                # Back button text
                back_font = pygame.font.SysFont("consolas", 24, bold=True)
                back_text = f"◄ {self.t('back')}"
                back_text_surf = back_font.render(back_text, True, (255, 255, 255))
                back_text_rect = back_text_surf.get_rect(center=back_button_rect.center)
                # Black outline for visibility
                outline_back = back_font.render(back_text, True, (0, 0, 0))
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            surface.blit(outline_back, (back_text_rect.x + dx, back_text_rect.y + dy))
                surface.blit(back_text_surf, back_text_rect)
            
            # Draw shop/equipment menu if shopping cart was clicked (overlay on death screen)
            if self.shop_section == "weapons" and self.state == "shop":
                self._draw_equipment_menu(surface)
            
            # Draw settings menu if settings button was clicked (overlay on death screen)
            if self.state == "settings":
                self._draw_settings_menu(surface)
            
        except Exception as e:
            # Fallback: Draw simple error message
            try:
                error_font = pygame.font.SysFont("consolas", 24, bold=True)
                error_text = error_font.render("Error - Press ESC to continue", True, (255, 0, 0))
                error_rect = error_text.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2))
                surface.blit(error_text, error_rect)
            except:
                pass
    
    def _draw_modern_button(self, surface, rect, text, icon="", base_color=Config.NEON_BLUE, 
                           is_hovered=False, is_pressed=False, button_id=""):
        """Draw modern glassmorphism button with LERP animations"""
        # LERP animation for smooth transitions
        target_scale = 1.0
        target_glow = 0.6
        
        if is_pressed:
            target_scale = 0.9  # 10% smaller when pressed
            target_glow = 0.8
        elif is_hovered:
            target_scale = 1.05  # 5% larger when hovered
            target_glow = 1.2
        
        # Smooth LERP interpolation
        if button_id not in self.button_scales:
            self.button_scales[button_id] = 1.0
        if button_id not in self.button_glow_intensities:
            self.button_glow_intensities[button_id] = 0.6
        
        # LERP speed (adjust for smoothness - frame-independent)
        lerp_speed = 0.2  # Smooth but responsive
        self.button_scales[button_id] += (target_scale - self.button_scales[button_id]) * lerp_speed
        self.button_glow_intensities[button_id] += (target_glow - self.button_glow_intensities[button_id]) * lerp_speed
        
        scale = self.button_scales[button_id]
        glow_intensity_base = self.button_glow_intensities[button_id]
        
        # Scaled rect
        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)
        scaled_rect = pygame.Rect(
            rect.centerx - scaled_width // 2,
            rect.centery - scaled_height // 2,
            scaled_width,
            scaled_height
        )
        
        # Border radius
        border_radius = min(scaled_rect.width, scaled_rect.height) // 2 if scaled_rect.width == scaled_rect.height else 15
        
        # Color based on state with LERP smooth transitions
        glow_intensity = glow_intensity_base
        
        if is_pressed:
            button_color = tuple(max(0, c - 40) for c in base_color)  # Darker when pressed
            border_color = tuple(max(0, c - 20) for c in base_color)
        elif is_hovered:
            # Hover: %20 brighter with neon glow (never disappears)
            button_color = tuple(min(255, int(c * 1.2)) for c in base_color)  # 20% brighter
            border_color = tuple(min(255, int(c * 1.3)) for c in base_color)  # 30% brighter border
        else:
            button_color = base_color
            border_color = tuple(min(255, c + 20) for c in base_color)
        
        # Enhanced Neon Glow effect
        glow_layers = 3
        for i in range(glow_layers):
            glow_size = 30 + (i * 10)
            glow_surf = pygame.Surface((scaled_rect.width + glow_size * 2, scaled_rect.height + glow_size * 2), pygame.SRCALPHA)
            glow_alpha = int((150 - i * 30) * glow_intensity)
            glow_color = (int(border_color[0] * glow_intensity), int(border_color[1] * glow_intensity),
                         int(border_color[2] * glow_intensity), glow_alpha)
            pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=border_radius + glow_size // 2)
            surface.blit(glow_surf, (scaled_rect.x - glow_size, scaled_rect.y - glow_size))
        
        # Modern glassmorphism button background (always visible, never disappears)
        button_surf = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
        if is_hovered:
            button_alpha = 240  # Very visible when hovered (bright)
            button_surf.fill((int(button_color[0] * 0.3), int(button_color[1] * 0.3), int(button_color[2] * 0.3), button_alpha))
        else:
            button_alpha = 200  # Visible when normal
            button_surf.fill((button_color[0] // 5, button_color[1] // 5, button_color[2] // 5, button_alpha))
        surface.blit(button_surf, scaled_rect)
        
        # Enhanced Neon border with glow
        border_width = 5 if is_hovered else 3
        # Inner glow
        inner_glow = pygame.Surface((scaled_rect.width - 4, scaled_rect.height - 4), pygame.SRCALPHA)
        inner_glow_rect = pygame.Rect(2, 2, scaled_rect.width - 4, scaled_rect.height - 4)
        pygame.draw.rect(inner_glow, (border_color[0], border_color[1], border_color[2], 100), 
                        inner_glow.get_rect(), border_radius=border_radius - 2)
        surface.blit(inner_glow, (scaled_rect.x + 2, scaled_rect.y + 2))
        # Main border
        pygame.draw.rect(surface, border_color, scaled_rect, width=border_width, border_radius=border_radius)
        
        # Highlight effect
        if is_hovered and not is_pressed:
            highlight = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (255, 255, 255, 60), highlight.get_rect(), border_radius=border_radius)
            surface.blit(highlight, scaled_rect.topleft)
        
        # Text and icon
        if icon:
            icon_font = pygame.font.SysFont("consolas", int(28 * scale), bold=True)
            icon_surf = icon_font.render(icon, True, (255, 255, 255))
            icon_rect = icon_surf.get_rect(center=(scaled_rect.centerx, scaled_rect.centery - 8))
            surface.blit(icon_surf, icon_rect)
        
        if text:
            text_font = pygame.font.SysFont("consolas", int(20 * scale), bold=True)
            text_surf = text_font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(scaled_rect.centerx, scaled_rect.centery + (12 if icon else 0)))
            # Glow text
            glow_text = text_font.render(text, True, (int(border_color[0] * 0.3), int(border_color[1] * 0.3), int(border_color[2] * 0.3)))
            surface.blit(glow_text, (text_rect.x + 1, text_rect.y + 1))
            surface.blit(text_surf, text_rect)
    
    def _draw_main_shop(self, surface, content_rect, start_y):
        """Draw main shop with modern glassmorphism buttons"""
        try:
            mouse_pos = self._get_safe_mouse_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]
        except:
            mouse_pos = (Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2)
            mouse_pressed = False
        
        hovered_button = None
        
        # Circular buttons row
        button_size = 80
        button_spacing = 20
        buttons_start_y = start_y + 100
        total_buttons_width = 3 * button_size + 2 * button_spacing
        buttons_start_x = content_rect.centerx - total_buttons_width // 2
        
        circular_buttons = [
            ("weapons", "⚔", self.t("shop"), Config.NEON_CYAN),
            ("stats", "📊", "Stats", Config.NEON_BLUE),
            ("help", "?", "Help", Config.NEON_PURPLE)
        ]
        
        for idx, (button_id, icon, label, color) in enumerate(circular_buttons):
            try:
                button_x = buttons_start_x + idx * (button_size + button_spacing)
                button_rect = pygame.Rect(button_x, buttons_start_y, button_size, button_size)
                is_hovered = button_rect.collidepoint(mouse_pos)
                is_pressed = is_hovered and mouse_pressed and button_id not in self.pressed_buttons
                
                if is_hovered:
                    hovered_button = button_id
                
                if is_pressed:
                    self.pressed_buttons[button_id] = True
                elif button_id in self.pressed_buttons and not mouse_pressed:
                    del self.pressed_buttons[button_id]
                
                # Draw modern button
                self._draw_modern_button(surface, button_rect, label, icon, color, is_hovered, is_pressed, button_id)
            except:
                pass  # Silently ignore button drawing errors
        
        # Set cursor based on hover state
        try:
            if hovered_button:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        except:
            pass  # Silently ignore cursor errors
        
        # Pill-shaped buttons
        try:
            pill_button_width = 200  # Modern, elegant size
            pill_button_height = 45
            pill_buttons_start_y = buttons_start_y + button_size + 80
            
            # "Weapons" button
            weapons_button_rect = pygame.Rect(content_rect.centerx - pill_button_width // 2,
                                             pill_buttons_start_y, pill_button_width, pill_button_height)
            is_hovered_weapons = weapons_button_rect.collidepoint(mouse_pos)
            is_pressed_weapons = is_hovered_weapons and mouse_pressed and "weapons_pill" not in self.pressed_buttons
            
            if is_pressed_weapons:
                self.pressed_buttons["weapons_pill"] = True
            elif "weapons_pill" in self.pressed_buttons and not mouse_pressed:
                del self.pressed_buttons["weapons_pill"]
            
            self._draw_modern_button(surface, weapons_button_rect, f"⚔ {self.t('shop')}", "", 
                                    Config.NEON_CYAN, is_hovered_weapons, is_pressed_weapons, "weapons_pill")
        except:
            pass  # Silently ignore pill button errors
        
        # "Back" button
        back_button_rect = pygame.Rect(content_rect.centerx - pill_button_width // 2,
                                       pill_buttons_start_y + pill_button_height + 20,
                                       pill_button_width, pill_button_height)
        try:
            is_hovered_back = back_button_rect.collidepoint(mouse_pos)
            is_pressed_back = is_hovered_back and mouse_pressed and "back_pill" not in self.pressed_buttons
            
            if is_pressed_back:
                self.pressed_buttons["back_pill"] = True
            elif "back_pill" in self.pressed_buttons and not mouse_pressed:
                del self.pressed_buttons["back_pill"]
            
            self._draw_modern_button(surface, back_button_rect, f"◄ {self.t('back')}", "", 
                                    (220, 50, 50), is_hovered_back, is_pressed_back, "back_pill")
        except:
            pass  # Silently ignore back button errors
        
        # Enter prompt
        enter_font = pygame.font.SysFont("consolas", 20, bold=True)
        enter_text = self.t("press_enter")
        enter_surf = enter_font.render(enter_text, True, Config.NEON_CYAN)
        enter_rect = enter_surf.get_rect(center=(content_rect.centerx, content_rect.bottom - 30))
        surface.blit(enter_surf, enter_rect)
    
    def _draw_weapons_shop(self, surface, content_rect, start_y):
        """Draw weapons shop with simple, clean buttons (no excessive glow effects)"""
        try:
            mouse_pos = self._get_safe_mouse_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]
        except:
            mouse_pos = (Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2)
            mouse_pressed = False
        
        hovered_button = None
        
        # Item buttons (circular) - simple design
        item_button_size = 90
        item_spacing = 30
        items_start_y = start_y + 50
        total_items_width = 4 * item_button_size + 3 * item_spacing
        items_start_x = content_rect.centerx - total_items_width // 2
        
        items = [
            ("shield", "S", self.t("shield"), 100, self.has_shield),
            ("magnet", "M", self.t("magnet"), 80, self.has_magnet),
            ("speed", "SP", f"{self.t('speed')} +{self.speed_boost_level + 1}" if self.speed_boost_level < 3 else f"{self.t('speed')} MAX", 50, self.speed_boost_level >= 3),
            ("triple", "3X", self.t("triple_shot"), 150, self.weapon_level >= 3)
        ]
        
        for idx, (item_id, icon, item_name, cost, is_owned) in enumerate(items):
            button_x = items_start_x + idx * (item_button_size + item_spacing)
            item_rect = pygame.Rect(button_x, items_start_y, item_button_size, item_button_size)
            is_hovered = item_rect.collidepoint(mouse_pos)
            can_afford = self.total_gold >= cost
            
            if is_hovered and can_afford:
                hovered_button = item_id
            
            # Simple button drawing - NO excessive glow effects
            if is_owned:
                button_color = (100, 200, 100)  # Light green
                border_color = (50, 150, 50)
            elif not can_afford:
                button_color = (100, 100, 100)  # Gray
                border_color = (70, 70, 70)
            else:
                button_color = (150, 150, 200)  # Light blue-gray
                border_color = (100, 100, 150)
            
            # Hover effect - slightly brighter
            if is_hovered and can_afford and not is_owned:
                button_color = tuple(min(255, c + 30) for c in button_color)
                border_color = tuple(min(255, c + 30) for c in border_color)
            
            # Draw simple circular button (NO glow layers)
            pygame.draw.circle(surface, button_color, item_rect.center, item_button_size // 2)
            pygame.draw.circle(surface, border_color, item_rect.center, item_button_size // 2, width=3)
            
            # Icon text (always visible)
            icon_font = pygame.font.SysFont("consolas", 36, bold=True)
            icon_color = (255, 255, 255) if can_afford or is_owned else (150, 150, 150)
            icon_surf = icon_font.render(icon, True, icon_color)
            icon_rect = icon_surf.get_rect(center=item_rect.center)
            # Text outline for visibility
            outline_surf = icon_font.render(icon, True, (0, 0, 0))
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        surface.blit(outline_surf, (icon_rect.x + dx, icon_rect.y + dy))
            surface.blit(icon_surf, icon_rect)
            
            # Label and cost below (ALWAYS visible with outline)
            label_font = pygame.font.SysFont("consolas", 16, bold=True)
            label_color = (0, 0, 0)  # Black text for visibility on light background
            label_surf = label_font.render(item_name, True, label_color)
            label_rect = label_surf.get_rect(center=(item_rect.centerx, item_rect.bottom + 18))
            # White outline for visibility
            outline_label = label_font.render(item_name, True, (255, 255, 255))
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        surface.blit(outline_label, (label_rect.x + dx, label_rect.y + dy))
            surface.blit(label_surf, label_rect)
            
            if not is_owned:
                cost_font = pygame.font.SysFont("consolas", 14, bold=True)
                cost_text = f"{cost} {self.t('points')}"
                cost_color = (200, 150, 0) if can_afford else (120, 120, 120)  # Gold or gray
                cost_surf = cost_font.render(cost_text, True, cost_color)
                cost_rect = cost_surf.get_rect(center=(item_rect.centerx, item_rect.bottom + 36))
                # White outline for visibility
                outline_cost = cost_font.render(cost_text, True, (255, 255, 255))
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            surface.blit(outline_cost, (cost_rect.x + dx, cost_rect.y + dy))
                surface.blit(cost_surf, cost_rect)
            else:
                owned_font = pygame.font.SysFont("consolas", 14, bold=True)
                owned_color = (0, 150, 0)  # Dark green
                owned_surf = owned_font.render(self.t("purchased"), True, owned_color)
                owned_rect = owned_surf.get_rect(center=(item_rect.centerx, item_rect.bottom + 36))
                # White outline for visibility
                outline_owned = owned_font.render(self.t("purchased"), True, (255, 255, 255))
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            surface.blit(outline_owned, (owned_rect.x + dx, owned_rect.y + dy))
                surface.blit(owned_surf, owned_rect)
        
        # Back button - simple design
        pill_button_width = 200
        pill_button_height = 45
        back_button_rect = pygame.Rect(content_rect.centerx - pill_button_width // 2,
                                       items_start_y + item_button_size + 80,
                                       pill_button_width, pill_button_height)
        is_hovered_back = back_button_rect.collidepoint(mouse_pos)
        
        if is_hovered_back:
            hovered_button = "back_weapons"
            back_color = (220, 80, 80)  # Brighter red on hover
        else:
            back_color = (200, 50, 50)  # Normal red
        
        # Simple back button (NO glow effects)
        pygame.draw.rect(surface, back_color, back_button_rect, border_radius=10)
        pygame.draw.rect(surface, (150, 0, 0), back_button_rect, width=3, border_radius=10)
        
        # Back button text (always visible)
        back_font = pygame.font.SysFont("consolas", 22, bold=True)
        back_text = f"◄ {self.t('back')}"
        back_text_surf = back_font.render(back_text, True, (255, 255, 255))
        back_text_rect = back_text_surf.get_rect(center=back_button_rect.center)
        # Black outline for visibility
        outline_back = back_font.render(back_text, True, (0, 0, 0))
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    surface.blit(outline_back, (back_text_rect.x + dx, back_text_rect.y + dy))
        surface.blit(back_text_surf, back_text_rect)
        
        # Set cursor based on hover state
        try:
            if hovered_button:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        except:
            pass  # Silently ignore cursor errors
        
        # Enter prompt removed - mouse click only
    
    def _draw_settings_menu(self, surface):
        """Draw settings menu overlay with volume and language controls"""
        # Semi-transparent overlay
        overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Settings panel (increased height to fit all buttons)
        panel_width = 500
        panel_height = 500
        panel_x = Config.WINDOW_WIDTH // 2 - panel_width // 2
        panel_y = Config.WINDOW_HEIGHT // 2 - panel_height // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Bright, childish panel background
        pygame.draw.rect(surface, (255, 255, 200), panel_rect, border_radius=20)
        pygame.draw.rect(surface, (200, 200, 100), panel_rect, width=4, border_radius=20)
        
        # Title
        title_font = pygame.font.SysFont("consolas", 48, bold=True)
        title_text = self.t("settings")
        title_surf = title_font.render(title_text, True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(panel_rect.centerx, panel_rect.y + 40))
        surface.blit(title_surf, title_rect)
        
        try:
            mouse_pos = self._get_safe_mouse_pos()
        except:
            mouse_pos = (Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2)
        
        # Volume section (moved up)
        volume_y = panel_rect.y + 100
        volume_label_font = pygame.font.SysFont("consolas", 28, bold=True)
        volume_label = volume_label_font.render(f"{self.t('volume')}: {int(self.volume * 100)}%", True, (0, 0, 0))
        volume_label_rect = volume_label.get_rect(center=(panel_rect.centerx, volume_y))
        surface.blit(volume_label, volume_label_rect)
        
        # Volume buttons
        vol_button_size = 60
        vol_button_y = volume_y + 50
        vol_decrease_x = panel_rect.centerx - 80
        vol_increase_x = panel_rect.centerx + 80
        
        # Decrease button
        vol_dec_rect = pygame.Rect(vol_decrease_x - vol_button_size // 2, vol_button_y - vol_button_size // 2,
                                   vol_button_size, vol_button_size)
        vol_dec_hover = vol_dec_rect.collidepoint(mouse_pos)
        vol_dec_color = (255, 100, 100) if vol_dec_hover else (255, 150, 150)
        pygame.draw.rect(surface, vol_dec_color, vol_dec_rect, border_radius=10)
        pygame.draw.rect(surface, (200, 0, 0), vol_dec_rect, width=3, border_radius=10)
        dec_font = pygame.font.SysFont("consolas", 40, bold=True)
        dec_text = dec_font.render(self.t("decrease_volume"), True, (255, 255, 255))
        dec_rect = dec_text.get_rect(center=vol_dec_rect.center)
        surface.blit(dec_text, dec_rect)
        
        # Increase button
        vol_inc_rect = pygame.Rect(vol_increase_x - vol_button_size // 2, vol_button_y - vol_button_size // 2,
                                   vol_button_size, vol_button_size)
        vol_inc_hover = vol_inc_rect.collidepoint(mouse_pos)
        vol_inc_color = (100, 255, 100) if vol_inc_hover else (150, 255, 150)
        pygame.draw.rect(surface, vol_inc_color, vol_inc_rect, border_radius=10)
        pygame.draw.rect(surface, (0, 200, 0), vol_inc_rect, width=3, border_radius=10)
        inc_font = pygame.font.SysFont("consolas", 40, bold=True)
        inc_text = inc_font.render(self.t("increase_volume"), True, (255, 255, 255))
        inc_rect = inc_text.get_rect(center=vol_inc_rect.center)
        surface.blit(inc_text, inc_rect)
        
        # Language section (moved up)
        lang_y = volume_y + 120
        lang_label_font = pygame.font.SysFont("consolas", 28, bold=True)
        lang_label = lang_label_font.render(self.t("language"), True, (0, 0, 0))
        lang_label_rect = lang_label.get_rect(center=(panel_rect.centerx, lang_y))
        surface.blit(lang_label, lang_label_rect)
        
        # Language buttons
        lang_button_width = 180
        lang_button_height = 50
        lang_button_y = lang_y + 40
        lang_turk_x = panel_rect.centerx - 100
        lang_eng_x = panel_rect.centerx + 100
        
        # Turkish button
        lang_turk_rect = pygame.Rect(lang_turk_x - lang_button_width // 2, lang_button_y - lang_button_height // 2,
                                     lang_button_width, lang_button_height)
        lang_turk_hover = lang_turk_rect.collidepoint(mouse_pos)
        lang_turk_color = (200, 200, 255) if lang_turk_hover else (180, 180, 255)
        if self.language == Language.TURKISH:
            lang_turk_color = (150, 150, 255)
        pygame.draw.rect(surface, lang_turk_color, lang_turk_rect, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 200), lang_turk_rect, width=3, border_radius=10)
        turk_font = pygame.font.SysFont("consolas", 24, bold=True)
        turk_text = turk_font.render(self.t("turkish"), True, (0, 0, 0))
        turk_rect = turk_text.get_rect(center=lang_turk_rect.center)
        surface.blit(turk_text, turk_rect)
        
        # English button
        lang_eng_rect = pygame.Rect(lang_eng_x - lang_button_width // 2, lang_button_y - lang_button_height // 2,
                                    lang_button_width, lang_button_height)
        lang_eng_hover = lang_eng_rect.collidepoint(mouse_pos)
        lang_eng_color = (200, 200, 255) if lang_eng_hover else (180, 180, 255)
        if self.language == Language.ENGLISH:
            lang_eng_color = (150, 150, 255)
        pygame.draw.rect(surface, lang_eng_color, lang_eng_rect, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 200), lang_eng_rect, width=3, border_radius=10)
        eng_font = pygame.font.SysFont("consolas", 24, bold=True)
        eng_text = eng_font.render(self.t("english"), True, (0, 0, 0))
        eng_rect = eng_text.get_rect(center=lang_eng_rect.center)
        surface.blit(eng_text, eng_rect)
        
        # Back button (Geri - moved up)
        back_button_width = 150
        back_button_height = 45
        back_button_rect = pygame.Rect(panel_rect.centerx - back_button_width // 2,
                                       panel_rect.bottom - 110,
                                       back_button_width, back_button_height)
        back_hover = back_button_rect.collidepoint(mouse_pos)
        back_color = (200, 255, 200) if back_hover else (150, 255, 150)
        pygame.draw.rect(surface, back_color, back_button_rect, border_radius=10)
        pygame.draw.rect(surface, (0, 200, 0), back_button_rect, width=3, border_radius=10)
        back_font = pygame.font.SysFont("consolas", 22, bold=True)
        back_text = back_font.render(self.t("back"), True, (0, 0, 0))
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        surface.blit(back_text, back_text_rect)
        
        # Quit button (Oyundan Çık - at the bottom)
        quit_button_width = 200
        quit_button_height = 45
        quit_button_rect = pygame.Rect(panel_rect.centerx - quit_button_width // 2,
                                       panel_rect.bottom - 50,
                                       quit_button_width, quit_button_height)
        quit_hover = quit_button_rect.collidepoint(mouse_pos)
        quit_color = (255, 100, 100) if quit_hover else (255, 150, 150)
        pygame.draw.rect(surface, quit_color, quit_button_rect, border_radius=10)
        pygame.draw.rect(surface, (200, 0, 0), quit_button_rect, width=3, border_radius=10)
        quit_font = pygame.font.SysFont("consolas", 22, bold=True)
        quit_text_str = "OYUNDAN ÇIK" if self.language == Language.TURKISH else "QUIT GAME"
        quit_text = quit_font.render(quit_text_str, True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)
        surface.blit(quit_text, quit_text_rect)
    
    def _draw_equipment_menu(self, surface):
        """Draw equipment/shop menu overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Equipment panel
        panel_width = 700
        panel_height = 500
        panel_x = Config.WINDOW_WIDTH // 2 - panel_width // 2
        panel_y = Config.WINDOW_HEIGHT // 2 - panel_height // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Bright, childish panel background
        pygame.draw.rect(surface, (255, 255, 200), panel_rect, border_radius=20)
        pygame.draw.rect(surface, (200, 200, 100), panel_rect, width=4, border_radius=20)
        
        # Title
        title_font = pygame.font.SysFont("consolas", 48, bold=True)
        title_text = self.t("shopping")
        title_surf = title_font.render(title_text, True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(panel_rect.centerx, panel_rect.y + 40))
        surface.blit(title_surf, title_rect)
        
        # Gold display
        gold_font = pygame.font.SysFont("consolas", 32, bold=True)
        gold_text = f"{self.t('points')}: {int(self.total_gold)}"
        gold_surf = gold_font.render(gold_text, True, (255, 215, 0))
        gold_rect = gold_surf.get_rect(center=(panel_rect.centerx, panel_rect.y + 90))
        surface.blit(gold_surf, gold_rect)
        
        # Draw equipment items using existing weapons shop function
        content_rect = pygame.Rect(panel_x + 20, panel_y + 120, panel_width - 40, panel_height - 180)
        content_start_y = content_rect.top + 20
        self._draw_weapons_shop(surface, content_rect, content_start_y)
    
    def _draw_shop_item_button(self, surface, rect, text, cost, can_afford, is_hovered, is_owned):
        t = pygame.time.get_ticks() / 1000.0
        glow = (math.sin(t * 4) + 1) / 2
        
        if is_owned:
            button_color = (Config.NEON_CYAN[0] // 6, Config.NEON_CYAN[1] // 6, Config.NEON_CYAN[2] // 6)
            border_color = Config.NEON_CYAN
            text_color = Config.NEON_CYAN
            glow_intensity = 0.6
        elif is_hovered and can_afford:
            button_color = (Config.NEON_PINK[0] // 4, Config.NEON_PINK[1] // 4, Config.NEON_PINK[2] // 4)
            border_color = Config.NEON_PINK
            text_color = Config.NEON_PINK
            glow_intensity = 1.0
        elif can_afford:
            button_color = (Config.CYBERPUNK_DARK[0], Config.CYBERPUNK_DARK[1], Config.CYBERPUNK_DARK[2])
            border_color = Config.NEON_BLUE
            text_color = Config.NEON_CYAN
            glow_intensity = 0.5 + glow * 0.3
        else:
            button_color = (Config.CYBERPUNK_DARK[0] // 2, Config.CYBERPUNK_DARK[1] // 2, Config.CYBERPUNK_DARK[2] // 2)
            border_color = (100, 100, 100)
            text_color = (150, 150, 150)
            glow_intensity = 0.2
        
        glow_surface = pygame.Surface((rect.width + 25, rect.height + 25), pygame.SRCALPHA)
        glow_alpha = int(140 * glow_intensity)
        glow_color = (int(border_color[0] * glow_intensity), int(border_color[1] * glow_intensity),
                     int(border_color[2] * glow_intensity), glow_alpha)
        pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=20)
        surface.blit(glow_surface, (rect.x - 12, rect.y - 12))
        
        pygame.draw.rect(surface, button_color, rect, border_radius=18)
        pygame.draw.rect(surface, border_color, rect, width=3, border_radius=18)
        
        if is_hovered and can_afford:
            highlight = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (255, 255, 255, 50), highlight.get_rect(), border_radius=18)
            surface.blit(highlight, rect.topleft)
        
        button_font = pygame.font.SysFont("consolas", 22, bold=True)
        button_text = button_font.render(text, True, text_color)
        button_text_rect = button_text.get_rect(center=(rect.centerx, rect.centery - 10))
        glow_text = button_font.render(text, True, (text_color[0] // 3, text_color[1] // 3, text_color[2] // 3))
        surface.blit(glow_text, (button_text_rect.x + 1, button_text_rect.y + 1))
        surface.blit(button_text, button_text_rect)
        
        if cost > 0 and not is_owned:
            cost_font = pygame.font.SysFont("consolas", 18, bold=True)
            cost_text = cost_font.render(f"{cost} {self.t('points')}", True,
                                       Config.GOLD_COLOR if can_afford else (100, 100, 100))
            cost_text_rect = cost_text.get_rect(center=(rect.centerx, rect.centery + 15))
            surface.blit(cost_text, cost_text_rect)
        elif is_owned:
            owned_font = pygame.font.SysFont("consolas", 16, bold=True)
            owned_text = owned_font.render(self.t("purchased"), True, Config.NEON_CYAN)
            owned_text_rect = owned_text.get_rect(center=(rect.centerx, rect.centery + 15))
            surface.blit(owned_text, owned_text_rect)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    # Toggle fullscreen
                    pass  # Fullscreen toggle can be added here
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER or event.key == pygame.K_SPACE:
                    if self.state == "menu":
                        self.start_game()
                    elif self.state == "shop":
                        # Ölüm ekranında Enter veya Space'e basınca oyunu yeniden başlat
                        self.start_game()
                elif event.key == pygame.K_ESCAPE:
                    if self.state == "settings":
                        # Settings'ten geri dön
                        if self.player:  # Oyun aktifse pause'a dön
                            self.state = "paused"
                        elif self.last_run_score > 0:  # Ölüm ekranından ayarlara girdiyse
                            self.state = "shop"
                        else:  # Menu'den ayarlara girdiyse
                            self.state = "menu"
                    elif self.state == "shop":
                        if self.shop_section == "weapons":
                            self.shop_section = "main"
                        else:
                            self.state = "menu"  # Ana ekrana dön (oyunu kapatma)
                    elif self.state == "playing":
                        self.state = "paused"  # Oyunu duraklat
                    elif self.state == "paused":
                        self.state = "playing"  # ESC ile de devam edebilir
            
            if event.type == pygame.KEYDOWN and self.state == "playing":
                if event.key == pygame.K_SPACE:
                    new_bullets = self.player.shoot(self.weapon_level)
                    self.bullets.extend(new_bullets)
            
            # Only process mouse clicks (not drags)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                try:
                    mouse_pos = self._clamp_mouse_pos(event.pos)
                    
                    flag_size = 40
                    spacing = 10
                    start_x = 15
                    start_y = Config.WINDOW_HEIGHT - 70
                    
                    # Türk bayrağı tıklama
                    turk_rect = pygame.Rect(start_x, start_y, flag_size, flag_size)
                    if turk_rect.collidepoint(mouse_pos):
                        self.language = Language.TURKISH
                        continue
                    
                    # İngilizce bayrağı tıklama
                    eng_rect = pygame.Rect(start_x + flag_size + spacing, start_y, flag_size, flag_size)
                    if eng_rect.collidepoint(mouse_pos):
                        self.language = Language.ENGLISH
                        continue
                    
                    # Menu state - ayarlar ikonu veya genel tıklama
                    if self.state == "menu":
                        # Ayarlar ikonu kontrolü
                        icon_size = 60
                        icon_x = 20
                        icon_y = 20
                        icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
                        
                        # Dil butonları kontrolü
                        flag_clicked = turk_rect.collidepoint(mouse_pos) or eng_rect.collidepoint(mouse_pos)
                        
                        if icon_rect.collidepoint(mouse_pos):
                            self.state = "settings"
                            continue
                        elif not flag_clicked:
                            # Ekranın herhangi bir yerine tıklanınca oyunu başlat
                            self.start_game()
                            continue
                    
                    if self.state == "paused":
                        # Pause menu button clicks
                        try:
                            panel_width = 400
                            panel_height = 320
                            panel_x = Config.WINDOW_WIDTH // 2 - panel_width // 2
                            panel_y = Config.WINDOW_HEIGHT // 2 - panel_height // 2
                            
                            # Continue button
                            continue_button_width = 300
                            continue_button_height = 60
                            continue_button_rect = pygame.Rect(panel_x + panel_width // 2 - continue_button_width // 2,
                                                              panel_y + 120,
                                                              continue_button_width, continue_button_height)
                            if continue_button_rect.collidepoint(mouse_pos):
                                self.state = "playing"  # Oyuna devam et
                            
                            # Settings button
                            settings_button_width = 300
                            settings_button_height = 60
                            settings_button_rect = pygame.Rect(panel_x + panel_width // 2 - settings_button_width // 2,
                                                              panel_y + 200,
                                                              settings_button_width, settings_button_height)
                            if settings_button_rect.collidepoint(mouse_pos):
                                self.state = "settings"  # Ayarlar menüsüne git
                        except:
                            pass
                    
                    elif self.state == "settings":
                        # Settings menu button clicks
                        try:
                            panel_width = 500
                            panel_height = 500
                            panel_x = Config.WINDOW_WIDTH // 2 - panel_width // 2
                            panel_y = Config.WINDOW_HEIGHT // 2 - panel_height // 2
                            
                            # Volume decrease button
                            vol_button_size = 60
                            volume_y = panel_y + 100
                            vol_button_y = volume_y + 50
                            vol_decrease_x = Config.WINDOW_WIDTH // 2 - 80
                            vol_dec_rect = pygame.Rect(vol_decrease_x - vol_button_size // 2, vol_button_y - vol_button_size // 2,
                                                       vol_button_size, vol_button_size)
                            if vol_dec_rect.collidepoint(mouse_pos):
                                self.volume = max(0.0, self.volume - 0.1)
                                pygame.mixer.music.set_volume(self.volume)
                                if self.hit_sound:
                                    self.hit_sound.set_volume(self.volume)
                                if self.start_sound:
                                    self.start_sound.set_volume(self.volume)
                            
                            # Volume increase button
                            vol_increase_x = Config.WINDOW_WIDTH // 2 + 80
                            vol_inc_rect = pygame.Rect(vol_increase_x - vol_button_size // 2, vol_button_y - vol_button_size // 2,
                                                       vol_button_size, vol_button_size)
                            if vol_inc_rect.collidepoint(mouse_pos):
                                self.volume = min(1.0, self.volume + 0.1)
                                pygame.mixer.music.set_volume(self.volume)
                                if self.hit_sound:
                                    self.hit_sound.set_volume(self.volume)
                                if self.start_sound:
                                    self.start_sound.set_volume(self.volume)
                            
                            # Language buttons
                            lang_button_width = 180
                            lang_button_height = 50
                            lang_y = volume_y + 120
                            lang_button_y = lang_y + 40
                            lang_turk_x = Config.WINDOW_WIDTH // 2 - 100
                            lang_eng_x = Config.WINDOW_WIDTH // 2 + 100
                            
                            lang_turk_rect = pygame.Rect(lang_turk_x - lang_button_width // 2, lang_button_y - lang_button_height // 2,
                                                          lang_button_width, lang_button_height)
                            if lang_turk_rect.collidepoint(mouse_pos):
                                self.language = Language.TURKISH
                            
                            lang_eng_rect = pygame.Rect(lang_eng_x - lang_button_width // 2, lang_button_y - lang_button_height // 2,
                                                         lang_button_width, lang_button_height)
                            if lang_eng_rect.collidepoint(mouse_pos):
                                self.language = Language.ENGLISH
                            
                            # Back button (Geri - moved up)
                            back_button_width = 150
                            back_button_height = 45
                            back_button_rect = pygame.Rect(Config.WINDOW_WIDTH // 2 - back_button_width // 2,
                                                           panel_y + panel_height - 110,
                                                           back_button_width, back_button_height)
                            if back_button_rect.collidepoint(mouse_pos):
                                # Doğru ekrana geri dön
                                if self.player:  # Oyun oynarken ayarlara girdiyse
                                    self.state = "paused"
                                elif self.last_run_score > 0:  # Ölüm ekranından ayarlara girdiyse
                                    self.state = "shop"
                                else:  # Menu'den ayarlara girdiyse
                                    self.state = "menu"
                            
                            # Quit button (Oyundan Çık - at the bottom)
                            quit_button_width = 200
                            quit_button_height = 45
                            quit_button_rect = pygame.Rect(Config.WINDOW_WIDTH // 2 - quit_button_width // 2,
                                                           panel_y + panel_height - 50,
                                                           quit_button_width, quit_button_height)
                            if quit_button_rect.collidepoint(mouse_pos):
                                self.running = False  # Oyunu kapat
                        except:
                            pass
                    
                    elif self.state == "shop":
                        # Death screen button clicks
                        try:
                            button_size = 120
                            button_spacing = 40
                            buttons_y = Config.WINDOW_HEIGHT // 2 + 50
                            total_width = 3 * button_size + 2 * button_spacing
                            buttons_start_x = Config.WINDOW_WIDTH // 2 - total_width // 2
                            
                            # Shopping cart button (left)
                            cart_button_rect = pygame.Rect(buttons_start_x, buttons_y, button_size, button_size)
                            if cart_button_rect.collidepoint(mouse_pos):
                                self.shop_section = "weapons"
                            
                            # Play/Retry button (center)
                            play_button_rect = pygame.Rect(buttons_start_x + button_size + button_spacing, buttons_y,
                                                          button_size, button_size)
                            if play_button_rect.collidepoint(mouse_pos):
                                self.start_game()
                            
                            # Settings button (right)
                            settings_button_rect = pygame.Rect(buttons_start_x + 2 * (button_size + button_spacing),
                                                               buttons_y, button_size, button_size)
                            if settings_button_rect.collidepoint(mouse_pos):
                                self.state = "settings"
                            
                            # Back button (ana ekrana dön) - sadece ana ölüm ekranında
                            if self.shop_section == "main":
                                label_y = buttons_y + button_size + 15
                                back_button_width = 200
                                back_button_height = 50
                                back_button_y = label_y + 50
                                back_button_rect = pygame.Rect(Config.WINDOW_WIDTH // 2 - back_button_width // 2,
                                                               back_button_y, back_button_width, back_button_height)
                                if back_button_rect.collidepoint(mouse_pos):
                                    self.state = "menu"  # Ana ekrana dön
                            
                            # Equipment menu clicks (if open)
                            if self.shop_section == "weapons":
                                try:
                                    # Calculate panel and content rects (same as drawing)
                                    panel_width = 700
                                    panel_height = 500
                                    panel_x = Config.WINDOW_WIDTH // 2 - panel_width // 2
                                    panel_y = Config.WINDOW_HEIGHT // 2 - panel_height // 2
                                    content_rect = pygame.Rect(panel_x + 20, panel_y + 120, panel_width - 40, panel_height - 180)
                                    content_start_y = content_rect.top + 20
                                    
                                    # Check circular item buttons
                                    item_button_size = 90
                                    item_spacing = 25
                                    items_start_y = content_start_y + 100
                                    total_items_width = 4 * item_button_size + 3 * item_spacing
                                    items_start_x = content_rect.centerx - total_items_width // 2
                                    
                                    # Shield
                                    shield_rect = pygame.Rect(items_start_x, items_start_y, item_button_size, item_button_size)
                                    if shield_rect.collidepoint(mouse_pos) and not self.has_shield and self.total_gold >= 300:
                                        self.total_gold -= 300
                                        self.has_shield = True
                                    
                                    # Magnet (tek kullanımlık - her tura özel)
                                    magnet_rect = pygame.Rect(items_start_x + item_button_size + item_spacing, items_start_y,
                                                              item_button_size, item_button_size)
                                    if magnet_rect.collidepoint(mouse_pos) and not self.has_magnet and self.total_gold >= 80:
                                        self.total_gold -= 80
                                        self.has_magnet = True
                                    
                                    # Speed Boost
                                    speed_rect = pygame.Rect(items_start_x + 2 * (item_button_size + item_spacing),
                                                            items_start_y, item_button_size, item_button_size)
                                    if speed_rect.collidepoint(mouse_pos) and self.speed_boost_level < 3 and self.total_gold >= 150:
                                        self.total_gold -= 150
                                        self.speed_boost_level += 1
                                    
                                    # Triple Shot
                                    triple_rect = pygame.Rect(items_start_x + 3 * (item_button_size + item_spacing),
                                                              items_start_y, item_button_size, item_button_size)
                                    if triple_rect.collidepoint(mouse_pos) and self.weapon_level < 3 and self.total_gold >= 500:
                                        self.total_gold -= 500
                                        self.weapon_level = 3
                                    
                                    # Back button - ana ekrana dön
                                    pill_button_width = 200
                                    pill_button_height = 45
                                    back_button_rect = pygame.Rect(content_rect.centerx - pill_button_width // 2,
                                                                   items_start_y + item_button_size + 100,
                                                                   pill_button_width, pill_button_height)
                                    if back_button_rect.collidepoint(mouse_pos):
                                        self.state = "menu"  # Ana ekrana dön
                                        self.shop_section = "main"
                                except:
                                    pass
                            
                        except Exception as e:
                            # Silently handle any shop state errors
                            pass
                except Exception as e:
                    # Silently handle any mouse event errors to prevent game crash
                    pass
    
    def run(self):
        while self.running:
            dt = self.clock.tick(Config.FPS) / 1000.0
            keys = pygame.key.get_pressed()
            
            self.handle_events()
            
            # Fade effect disabled - instant transitions
            # (Keeping fade code but not using it to avoid kararma effect)
            self.fade_alpha = 0
            self.fade_direction = 0
            
            # Update background for flowing stars (in all states)
            if self.state == "playing":
                self.update_playing(dt, keys)
            elif self.state == "menu":
                # Update background animation and meteors for menu screen
                self.background.update(dt)
                # Update meteors for flowing effect
                for meteor in self.meteors[:]:
                    meteor.update(dt)
                    if meteor.is_off_screen():
                        self.meteors.remove(meteor)
                # Spawn meteors occasionally for menu background effect
                if len(self.meteors) < 5:  # Keep a few meteors flowing
                    if random.random() < 0.02:  # Small chance each frame
                        self._spawn_menu_meteor()
            elif self.state == "shop":
                # Update background animation for flowing stars effect
                self.background.update(dt)
            elif self.state == "settings":
                # Update background animation for flowing stars effect
                self.background.update(dt)
                # Menu'den ayarlara girdiyse meteors da güncelle
                if not self.player and self.last_run_score == 0:
                    # Menu'den ayarlara girdiyse meteors güncelle
                    for meteor in self.meteors[:]:
                        meteor.update(dt)
                        if meteor.is_off_screen():
                            self.meteors.remove(meteor)
                    # Spawn meteors occasionally for menu background effect
                    if len(self.meteors) < 5:
                        if random.random() < 0.02:
                            self._spawn_menu_meteor()
            
            # Draw
            if self.state == "menu":
                self.draw_menu(self.screen)
            elif self.state == "playing":
                self.draw_playing(self.screen, keys)
            elif self.state == "paused":
                self.draw_paused(self.screen)
            elif self.state == "settings":
                # Settings overlay - draw correct background first
                if self.player:  # Oyun oynarken ayarlara girdiyse
                    self.draw_paused(self.screen)
                elif self.last_run_score > 0:  # Ölüm ekranından ayarlara girdiyse
                    self.draw_shop(self.screen)
                else:  # Menu'den ayarlara girdiyse
                    self.draw_menu(self.screen)
                self._draw_settings_menu(self.screen)
            elif self.state == "shop":
                try:
                    self.draw_shop(self.screen)
                except Exception as e:
                    # If shop drawing fails, return to menu instead of crashing
                    self.state = "menu"
                    if not hasattr(self, 'shop_section'):
                        self.shop_section = "main"
            
            # Apply fade overlay
            if self.fade_alpha > 0:
                fade_surf = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
                fade_surf.fill((0, 0, 0, int(self.fade_alpha)))
                self.screen.blit(fade_surf, (0, 0))
            
            pygame.display.flip()
        
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
