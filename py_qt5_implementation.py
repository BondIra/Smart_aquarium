import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap, QPainter, QTransform
from PyQt5.QtCore import Qt, QTimer, QSize

aquarium_width = 800
aquarium_height = 800

class Fish:
    def __init__(self, age, speed, size, fish_type):
        self.age = age
        self.speed = speed
        self.size = size
        self.fish_type = fish_type
        self.direction = random.choice(['up', 'down', 'left', 'right', 'upleft', 'upright', 'downleft', 'downright'])
        self.image_index = 0
        self.images = {
            'type1': [QPixmap('type1_fish1.png'), QPixmap('type1_fish2.png'), QPixmap('type1_fish3.png')],
            'type2': [QPixmap('type2_fish1.png'), QPixmap('type2_fish2.png'), QPixmap('type2_fish3.png')],
            'type3': [QPixmap('type3_fish1.png'), QPixmap('type3_fish2.png'), QPixmap('type3_fish3.png')],
            'type4': [QPixmap('type4_fish1.png'), QPixmap('type4_fish2.png'), QPixmap('type4_fish3.png')]
            # Добавьте изображения для остальных типов рыб
        }
        self.x = random.randint(0, aquarium_width - self.size)
        self.y = random.randint(0, aquarium_height - self.size)

    def move(self):
        if self.direction == 'up':
            self.y -= self.speed
            if self.y < 0:
                self.direction = 'down'
        elif self.direction == 'down':
            self.y += self.speed
            if self.y > aquarium_height - self.size:
                self.direction = 'up'
        elif self.direction == 'left':
            self.x -= self.speed
            if self.x < 0:
                self.direction = 'right'
        elif self.direction == 'right':
            self.x += self.speed
            if self.x > aquarium_width - self.size:
                self.direction = 'left'
        elif self.direction == 'upleft':  # Добавляем диагональные направления
            self.x -= self.speed
            self.y -= self.speed
            if self.x < 0 or self.y < 0:
                self.direction = 'downright'
        elif self.direction == 'upright':
            self.x += self.speed
            self.y -= self.speed
            if self.x > aquarium_width - self.size or self.y < 0:
                self.direction = 'downleft'
        elif self.direction == 'downleft':
            self.x -= self.speed
            self.y += self.speed
            if self.x < 0 or self.y > aquarium_height - self.size:
                self.direction = 'upright'
        elif self.direction == 'downright':
            self.x += self.speed
            self.y += self.speed
            if self.x > aquarium_width - self.size or self.y > aquarium_height - self.size:
                self.direction = 'upleft'

    def change_direction(self):
        self.direction = random.choice(['up', 'down', 'left', 'right', 'upleft', 'upright', 'downleft', 'downright'])  # Добавляем диагональные направления

    def update_image(self):
        self.image_index = (self.image_index + 1) % len(self.images[self.fish_type])


    def draw(self, painter):
        images = self.images[self.fish_type]
        image = images[self.image_index]
        if self.direction in ['down', 'up']:
            if self.direction == 'up':
                angle = -20
            else:
                angle = 20
            rotated_image = image.transformed(QTransform().rotate(angle))
            scaled_image = rotated_image.scaled(int(self.size * 1.15), int(self.size * 1.15))
            painter.drawPixmap(self.x, self.y, scaled_image)
        elif self.direction == 'down':
            if self.direction == 'up':
                angle = 20
            else:
                angle = -20
            rotated_image = image.transformed(QTransform().rotate(angle))
            scaled_image = rotated_image.scaled(self.size, self.size)
            painter.drawPixmap(self.x, self.y, scaled_image)
        else:
            if self.direction == 'left':
                mirrored_image = image.transformed(QTransform().scale(-1, 1))
                scaled_image = mirrored_image.scaled(self.size, self.size)
                painter.drawPixmap(self.x, self.y, scaled_image)
            elif self.direction == 'right':
                scaled_image = image.scaled(self.size, self.size)
                painter.drawPixmap(self.x, self.y, scaled_image)
            elif self.direction in ['upright', 'downright']:
                if self.direction == 'upright':
                    angle = -20
                else:
                    angle = 20
                rotated_image = image.transformed(QTransform().rotate(angle))
                mirrored_image = rotated_image.transformed(QTransform().scale(-1, 1))
                scaled_image = mirrored_image.scaled(int(self.size * 1.15), int(self.size * 1.15))
                painter.drawPixmap(self.x, self.y, scaled_image)
            else:
                if self.direction == 'upright':
                    angle = -20
                elif self.direction == 'downright':
                    angle = 20
                else:
                    angle = 0
                rotated_image = image.transformed(QTransform().rotate(angle))
                mirrored_image = rotated_image.transformed(QTransform().scale(-1, 1))
                scaled_image = mirrored_image.scaled(self.size, self.size)
                painter.drawPixmap(self.x, self.y, scaled_image)


class Aquarium(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Аквариум')
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: white;")
        self.fish_list = []
        self.create_fish()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fish)
        self.timer.start(200)  # Увеличение интервала для замедления рыбок

    def create_fish(self):
        for _ in range(10):
            age = random.randint(1, 100)
            speed = 1
            size = age // 5 + 150
            fish_type = random.choice(['type1', 'type2', 'type3', 'type4'])  # Выбираем случайный тип рыбы
            fish = Fish(age, speed, size, fish_type)
            self.fish_list.append(fish)


    def update_fish(self):
        for fish in self.fish_list:
            fish.move()
            fish.update_image()
            if random.random() < 0.01:  # Change direction randomly
                fish.change_direction()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        for fish in self.fish_list:
            fish.draw(painter)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    aquarium = Aquarium()
    aquarium.show()
    sys.exit(app.exec_())
