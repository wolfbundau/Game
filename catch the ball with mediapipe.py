import pygame  #thư viện pygame, hỗ trợ các chức năng game
import mediapipe as mp #thư viện hỗ trợ phát hiện chuyển động tay
import cv2  # trích xuất camera
import sys  
import random   

pygame.mixer.init()

# Nhạc nền
pygame.mixer.music.load("music_background.mp3")
pygame.mixer.music.play(-1)  # Phát lặp vô hạn
pygame.mixer.music.set_volume(0.2)

lose_sound = pygame.mixer.Sound("lose_music.mp3")
lose_sound.set_volume(0.5)

funny_sound = pygame.mixer.Sound("score10.mp3")
funny_sound.set_volume(0.7)

funny_effect = pygame.mixer.Sound("funnyeffect1.mp3")
funny_effect.set_volume(0.7)
# Âm thanh hiệu ứng
catch_sound = pygame.mixer.Sound("catching_sound.wav")
catch_sound.set_volume(0.7)

# Khởi tạo Mediapipe 
mp_hands = mp.solutions.hands #nhận diện cử chỉ tay
hands = mp_hands.Hands() #phát hiện chuyển và trả về tọa độ bàn tay
mp_drawing = mp.solutions.drawing_utils #vẽ các khớp bàn tay

def draw_hand_landmarks(frame, results):
    """Hàm vẽ các điểm landmark và khung bàn tay lên khung hình."""
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,  # Vẽ các kết nối giữa các điểm
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),  # Màu và kích thước điểm
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)  # Màu và kích thước đường nối
            )
# Thiết lập pygame
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game Hứng Bóng")

# Màu sắc và phông chữ
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT = pygame.font.SysFont("Noto Sans", 60)

# Tải và điều chỉnh kích thước hình ảnh
background_image = pygame.image.load("background.png")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

special_ball_image = pygame.image.load("fireball.webp")
special_ball_image = pygame.transform.scale(special_ball_image, (40 , 40))

ball_image = pygame.image.load("ball.png")
ball_image = pygame.transform.scale(ball_image, (40, 40))  # Điều chỉnh kích thước bóng (ví dụ 40x40 pixels)
ball_radius = ball_image.get_width() // 2

basket_image = pygame.image.load("basket.png")
basket_image = pygame.transform.scale(basket_image, (100, 100))  # Điều chỉnh kích thước chậu/rổ 
basket_width = basket_image.get_width()
basket_height = basket_image.get_height()

health_ball_image = pygame.image.load("healthball.webp")
health_ball_image = pygame.transform.scale(health_ball_image, (40, 40))


# Thông số trò chơi
ball_speed = 5
score = 0
game_active = False
health = 3
# Thông số cho nhiều quả bóng
num_balls =random.randint(3, 5)  # Số lượng bóng
balls = []  # Danh sách lưu trữ thông tin các quả bóng

# Biến để kiểm soát thời gian thêm bóng
last_ball_time = 0
ball_spawn_interval = random.randrange(2000, 3000 , 500)  # Khoảng thời gian (ms) để thêm bóng mới

# Vị trí khởi tạo 

basket_x = screen_width // 2 - basket_width // 2
basket_y = screen_height - 100

### HEALTH BALL
# Bóng Health
health_ball = {"x": 0, "y": 0, "active": False}  # Quả bóng health
health_ball_radius = 10
health_ball_speed = 5

# Màn hình hướng dẫn
def guide_screen():
    running = True
    while running:
        screen.blit(background_image, (0, 0))
        
        # Tiêu đề
        title_text = FONT.render("How to Play", True, RED)
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 4))
        
        # Hướng dẫn chi tiết
        instructions = [
            "1. Use your hand gestures to move the basket.",
            "2. Catch as many balls as you can.",
            "3. Avoid missing balls to maintain your health.",
            "4. Special balls grant temporary power-ups.",
            "5. Health balls restore your health.",
            "Press ESC to return to main menu."
        ]
        
        for i, line in enumerate(instructions):
            instruction_text = FONT.render(line, True, BLACK)
            screen.blit(instruction_text, (screen_width // 2 - instruction_text.get_width() // 2, screen_height // 3 + i * 40))
        
        pygame.display.flip()
        
        # Xử lý sự kiện quay lại menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False


# Hàm tạo bóng health
def spawn_health_ball():
    global health_ball
    health_ball["x"] = random.randint(health_ball_radius, screen_width - health_ball_radius)
    health_ball["y"] = 0
    health_ball["active"] = True

# Cập nhật bóng health
def update_health_ball():
    global health_ball, health

    if health_ball["active"]:
        health_ball["y"] += health_ball_speed

        # Kiểm tra va chạm với rổ
        if basket_y <= health_ball["y"] + health_ball_radius <= basket_y + basket_height and \
           basket_x <= health_ball["x"] <= basket_x + basket_width:
            health_ball["active"] = False
            health_ball["y"] = 0
            health = min(health + 1, 3)  # Tăng máu (tối đa là 3)

        # Nếu bóng rơi khỏi màn hình mà không được bắt
        if health_ball["y"] > screen_height:
            health_ball["active"] = False

# Gọi bóng health ngẫu nhiên
def random_spawn_health_ball():
    if not health_ball["active"] and random.random() < 0.01:  # Xác suất xuất hiện
        spawn_health_ball()

### SPECIAL BALL
# Thông số cho bóng đặc biệt
special_ball = {"x": 0, "y": 0, "active": False}  # Quả bóng đặc biệt
special_ball_radius = 20
special_effect_duration = 5000  # 5 giây
special_ball_speed = 5
basket_original_width = basket_width  # Lưu kích thước gốc của rổ
special_effect_start_time = None  # Thời điểm bắt đầu hiệu ứng
basket_original_image= basket_image
# Hàm tạo bóng đặc biệt
def spawn_special_ball():
    global special_ball
    special_ball["x"] = random.randint(special_ball_radius, screen_width - special_ball_radius)
    special_ball["y"] = 0
    special_ball["active"] = True
# Cập nhật bóng đặc biệt
def update_special_ball():
    global special_ball, basket_width, special_effect_start_time, basket_image

    if special_ball["active"]:
        special_ball["y"] += special_ball_speed

        # Kiểm tra va chạm với rổ
        if basket_y <= special_ball["y"] + special_ball_radius <= basket_y + basket_height and \
           basket_x <= special_ball["x"] <= basket_x + basket_width:
            special_ball["active"] = False
            special_ball["y"] = 0
            basket_width = basket_original_width * 3
            special_effect_start_time = pygame.time.get_ticks()
            basket_image = pygame.transform.scale(basket_image, (300, 100))
        # Nếu bóng rơi khỏi màn hình mà không được bắt
        if special_ball["y"] > screen_height:
            special_ball["active"] = False

    # Kiểm tra nếu hết thời gian hiệu ứng
    if special_effect_start_time and pygame.time.get_ticks() - special_effect_start_time > special_effect_duration:
        basket_image = basket_original_image
        basket_width = basket_original_width
        special_effect_start_time = None

# Gọi bóng đặc biệt ngẫu nhiên
def random_spawn_special_ball():
    if not special_ball["active"] and random.random() < 0.01:  # Xác suất trên mỗi frame
        spawn_special_ball()


# Màn hình chính với nút bắt đầu
def main_screen():
    while True:
        screen.blit(background_image, (0, 0))
        
        # Hiển thị tiêu đề và lựa chọn
        title_text = FONT.render("Catch the Ball", True, BLACK)
        play_text = FONT.render("Click anywhere to Start Game", True, RED)
        guide_text = FONT.render("Press 2 for How to Play", True, BLACK)
        
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 4))
        screen.blit(play_text, (screen_width // 2 - play_text.get_width() // 2, screen_height // 2))
        screen.blit(guide_text, (screen_width // 2 - guide_text.get_width() // 2, screen_height // 2 + 50))
        
        pygame.display.flip()
        
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Nhấn chuột bắt đầu game
                return "start"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_2:  # Nhấn phím 2 để xem hướng dẫn
                    return "guide"

#Màn hình chiến thắng
def victory_screen():
    screen.blit(background_image, (0, 0))  # Hiển thị nền
    victory_text = FONT.render("YOU WIN!", True, BLACK)
    score_text = FONT.render(f"Your Score: {score}", True, BLACK)
    reset_text = FONT.render("Click to Restart", True, BLACK)

    # Hiển thị thông điệp
    screen.blit(victory_text, (screen_width // 2 - victory_text.get_width() // 2, screen_height // 3))
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 2))
    screen.blit(reset_text, (screen_width // 2 - reset_text.get_width() // 2, screen_height // 2 + 50))

    pygame.display.flip()

    # Chờ người chơi nhấn chuột để khởi động lại
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                reset_game()
                waiting = False

#màn hình game over
def game_over_screen():
    global game_active

    screen.blit(background_image, (0, 0))  # Hiển thị nền
    game_over_text = FONT.render("GAME OVER", 60, RED)
    score_text = FONT.render(f"Your Score: {score}", True, BLACK)
    reset_text = FONT.render("Click to Restart", True, BLACK)

    # Vẽ các thông điệp
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 3))
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 2))
    screen.blit(reset_text, (screen_width // 2 - reset_text.get_width() // 2, screen_height // 2 + 50))

    pygame.display.flip()

    # Chờ người chơi nhấn chuột để khởi động lại
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Nhấn chuột để khởi động lại
                reset_game()
                waiting = False
# Xử lý chuyển động bóng
def update_ball():
    global balls, score, game_active, last_ball_time, ball_speed, health
    current_time = pygame.time.get_ticks()
    # Thêm bóng mới sau mỗi khoảng thời gian
    if current_time - last_ball_time > ball_spawn_interval:
        if len(balls) < num_balls:  # Giới hạn số bóng trên màn hình
            balls.append({
                "x": random.randint(ball_radius, screen_width - ball_radius),
                "y": 0
            })
        last_ball_time = current_time
    for ball in balls:
        ball["y"]+=ball_speed
        
    # Kiểm tra va chạm với rổ
        if basket_y <= ball["y"] + ball_radius <= basket_y + basket_height and \
           basket_x <= ball["x"] <= basket_x + basket_width:
           balls.remove(ball)  # Xóa bóng đã hứng được
           score += 1
           catch_sound.play()
           ball_speed+=0.5
       
        if ball["y"] > screen_height :
            balls.remove(ball)
            if health>0:
                health -= 1
            if health<=0:
                if score>=20:
                   funny_effect.play()
                   game_active = False
                   victory_screen()  
                else:
                   game_active = False
                   lose_sound.play()
                   game_over_screen()
            if score == 10:
                funny_sound.play()
          
# Vòng lặp chính của game
def game_loop():
    global game_active, basket_x, basket_y, score, health

    cap = cv2.VideoCapture(0)
    clock = pygame.time.Clock()
    
    while True:
        if not game_active:
            action = main_screen()
            if action == "start":
                game_active = True
                reset_game()  # Khởi tạo lại trò chơi
            elif action == "guide":
                guide_screen()  # Chuyển đến màn hình hướng dẫn
        else:
            # Vòng lặp trò chơi chính
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    cap.release()
                    sys.exit()

        # Đọc hình ảnh từ camera
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Điều khiển rổ bằng cử chỉ tay

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmark = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                basket_x = int(landmark.x * screen_width) - basket_width // 2
                
            draw_hand_landmarks(frame, results)    

        # Hiển thị camera lên màn hình trong trò chơi
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(cv2.transpose(frame_rgb))
        frame_surface = pygame.transform.scale(frame_surface, (200, 150))  # Thu nhỏ khung camera
        screen.blit(background_image, (0, 0))  # Hiển thị background
        screen.blit(frame_surface, (600,0 ))   # Hiển thị camera

        # Cập nhật vị trí bóng
        update_ball()
        update_special_ball()
        random_spawn_special_ball()
        update_health_ball()
        random_spawn_health_ball()
        # Vẽ bóng và rổ
        for ball in balls:
           screen.blit(ball_image, (ball["x"] - ball_radius, ball["y"] - ball_radius))

        if special_ball["active"]:
            screen.blit(special_ball_image, (special_ball["x"] - special_ball_radius, special_ball["y"] - special_ball_radius))
      
        if health_ball["active"]:
            screen.blit(health_ball_image, (health_ball["x"] - health_ball_radius, health_ball["y"] - health_ball_radius))
        
        screen.blit(basket_image, (basket_x, basket_y))

        # Vẽ điểm số
        score_text = FONT.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, screen_height - 40))
        
        #vẽ health
        health_text = FONT.render(f"Health: {health}",True, RED)
        screen.blit(health_text, (screen_width - 200, screen_height - 40))
        # Cập nhật màn hình
        pygame.display.flip()
        clock.tick(60)

# Reset lại trò chơi
def reset_game():
    global balls, last_ball_time, score, ball_speed, health
    balls = []  # Xóa toàn bộ danh sách bóng
    last_ball_time = pygame.time.get_ticks()  # Đặt lại thời gian
    score = 0
    ball_speed = 5
    health = 3
    
    special_ball = special_ball = {"x": 0, "y": 0, "active": False}
    

# Chạy game
if __name__ == "__main__":
    game_loop()
