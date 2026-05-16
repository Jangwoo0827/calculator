import pygame
import sys

# 초기화
pygame.init()

# 화면 설정
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mega-Map Engine")

clock = pygame.time.Clock()
FPS = 60

# 색상
DARK_GRAY = (30, 30, 30)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
GREEN = (50, 200, 100)
RED = (255, 100, 100)

TILE_SIZE = 20

# 1. 플레이어 클래스
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 플레이어 크기 20x20 수정
        self.image = pygame.Surface((20, 20)) 
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 물리 수치
        self.change_x = 0
        self.change_y = 0
        self.speed = 7           
        self.gravity = 0.9       
        self.jump_power = -20    
        self.on_ground = False
        
        # 벽타기 변수
        self.on_wall_left = False
        self.on_wall_right = False
        self.wall_slide_speed = 3   
        
        self.wall_jump_timer = 0    
        # 벽 프레임 6 수정
        self.wall_jump_lock_frames = 6  
        
        self.map_total_height = 720

    def update(self, platforms, hazards):
        self.calc_grav()
        
        if self.wall_jump_timer > 0:
            self.wall_jump_timer -= 1
        
        # X축 이동 및 충돌
        self.rect.x += self.change_x
        self.on_wall_left = False
        self.on_wall_right = False
        
        block_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
                if not self.on_ground and pygame.key.get_pressed()[pygame.K_RIGHT] and self.wall_jump_timer == 0:
                    self.on_wall_right = True
            elif self.change_x < 0:
                self.rect.left = block.rect.right
                if not self.on_ground and pygame.key.get_pressed()[pygame.K_LEFT] and self.wall_jump_timer == 0:
                    self.on_wall_left = True

        # Y축 이동 및 충돌
        self.rect.y += self.change_y
        block_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        self.on_ground = False
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
                self.change_y = 0
                self.on_ground = True
                self.wall_jump_timer = 0 
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
                self.change_y = 0

        # 위험 지역 충돌 -> 리스폰
        if pygame.sprite.spritecollide(self, hazards, False):
            self.respawn()

    def calc_grav(self):
        if self.change_y == 0: self.change_y = 1
        else: self.change_y += self.gravity
            
        if (self.on_wall_left or self.on_wall_right) and self.change_y > self.wall_slide_speed:
            self.change_y = self.wall_slide_speed

    def jump(self):
        if self.on_ground:
            self.change_y = self.jump_power
            self.on_ground = False
        elif self.on_wall_right:
            self.change_y = self.jump_power - 2  
            self.change_x = -self.speed * 1.5   
            self.wall_jump_timer = self.wall_jump_lock_frames 
            self.on_wall_right = False
        elif self.on_wall_left:
            self.change_y = self.jump_power - 2  
            self.change_x = self.speed * 1.5    
            self.wall_jump_timer = self.wall_jump_lock_frames 
            self.on_wall_left = False

    def respawn(self):
        self.rect.x = 60
        self.rect.y = self.map_total_height - 140
        self.change_x = 0
        self.change_y = 0
        self.wall_jump_timer = 0

    def go_left(self):
        if self.wall_jump_timer == 0: self.change_x = -self.speed
    def go_right(self):
        if self.wall_jump_timer == 0: self.change_x = self.speed
    def stop(self):
        if self.wall_jump_timer == 0: self.change_x = 0


# 2. 타일 클래스
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, size, color):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# 3. 그림판 이미지 분석 함수
def load_map_from_image(filename):
    platforms = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    try:
        map_image = pygame.image.load(filename).convert()
    except pygame.error:
        print(f"\n[오류] '{filename}' 파일이 없습니다.")
        pygame.quit()
        sys.exit()

    img_width, img_height = map_image.get_size()
    print(f"[맵 로딩 성공] 대형 월드 크기: {img_width} x {img_height}")

    for y in range(0, img_height, TILE_SIZE):
        for x in range(0, img_width, TILE_SIZE):
            color = map_image.get_at((x, y))
            r, g, b = color[0], color[1], color[2]
            
            if r < 50 and g < 50 and b < 50: 
                tile = Tile(x, y, TILE_SIZE, GREEN)
                platforms.add(tile)
                all_sprites.add(tile)
            elif r > 200 and g < 50 and b < 50: 
                tile = Tile(x, y, TILE_SIZE, RED)
                hazards.add(tile)
                all_sprites.add(tile)

    return all_sprites, platforms, hazards, img_width, img_height


def main():
    # map2.png 수정
    all_sprites, platforms, hazards, map_total_width, map_total_height = load_map_from_image("map2.png")

    player = Player(60, map_total_height - 140)
    player.map_total_height = map_total_height 
    all_sprites.add(player)

    world_canvas = pygame.Surface((map_total_width, map_total_height))
    view_full_map = False

    running = True
    while running:
        keys = pygame.key.get_pressed()
        if player.wall_jump_timer == 0:
            if keys[pygame.K_LEFT]: player.go_left()
            elif keys[pygame.K_RIGHT]: player.go_right()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: player.go_left()
                elif event.key == pygame.K_RIGHT: player.go_right()
                elif event.key == pygame.K_SPACE: player.jump()
                elif event.key == pygame.K_ESCAPE:
                    view_full_map = not view_full_map
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0: player.stop()
                elif event.key == pygame.K_RIGHT and player.change_x > 0: player.stop()

        player.update(platforms, hazards)

        if player.rect.top > map_total_height:
            player.respawn()

        # 그리기
        if not view_full_map:
            room_x = player.rect.centerx // SCREEN_WIDTH
            room_y = player.rect.centery // SCREEN_HEIGHT
            camera_x = room_x * SCREEN_WIDTH
            camera_y = room_y * SCREEN_HEIGHT

            screen.fill(DARK_GRAY)
            for sprite in all_sprites:
                screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y - camera_y))
        else:
            world_canvas.fill(DARK_GRAY)
            for sprite in all_sprites:
                world_canvas.blit(sprite.image, (sprite.rect.x, sprite.rect.y))
            
            # 비율 유지 계산 수정
            ratio_w = SCREEN_WIDTH / map_total_width
            ratio_h = SCREEN_HEIGHT / map_total_height
            scale_ratio = min(ratio_w, ratio_h)
            
            new_w = int(map_total_width * scale_ratio)
            new_h = int(map_total_height * scale_ratio)
            
            scaled_canvas = pygame.transform.smoothscale(world_canvas, (new_w, new_h))
            
            center_x = (SCREEN_WIDTH - new_w) // 2
            center_y = (SCREEN_HEIGHT - new_h) // 2
            
            screen.fill(BLACK)
            screen.blit(scaled_canvas, (center_x, center_y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()