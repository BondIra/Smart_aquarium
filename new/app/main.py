import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QPainter, QTransform
from PyQt5.QtCore import Qt, QTimer, QSize, QRect
from PyQt5.QtGui import QFontDatabase
import os
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel, QPushButton
from PyQt5.QtWidgets import QComboBox, QRadioButton
import psycopg2
from psycopg2 import extras
from datetime import datetime
import datetime


scale = 1.8

aquarium_width = int(1020*scale)
aquarium_height = int(640*scale)

global_shift_x = int(60*scale)
global_shift_y = int(130*scale)

fish_images = 0

fish_table = 0

connection_params = {
    'dbname': 'fish3',
    'user': 'postgres',
    'password': '1',
    'host': 'localhost',
    'port': '5432'
}

class Fish:
    def __init__(self, age, speed, size, fish_type, shift_x=global_shift_x, shift_y=global_shift_y):
        self.age = age
        self.speed = speed
        self.size = size
        self.fish_type = fish_type
        self.direction = random.choice(['up', 'down', 'left', 'right', 'upleft', 'upright', 'downleft', 'downright'])
        self.image_index = 0
        self.shift_x = int(shift_x*scale)  # Сдвиг по оси X
        self.shift_y = int(shift_y*scale)  # Сдвиг по оси Y
        self.images = fish_images
        # инициализируют начальное положение рыбы в аквариуме
        self.x = random.randint(shift_x, aquarium_width - self.size)
        self.y = random.randint(shift_y, aquarium_height - self.size+int(50*scale))

    def move(self):
        if self.direction == 'up':
            self.y -= self.speed
            if self.y < self.shift_y:
                self.direction = 'down'
                self.y = self.shift_y
        elif self.direction == 'down':
            self.y += self.speed
            if self.y > aquarium_height - self.size - self.shift_y:
                self.direction = 'up'
                self.y = aquarium_height - self.size - self.shift_y
        elif self.direction == 'left':
            self.x -= self.speed
            if self.x < self.shift_x:
                self.direction = 'right'
                self.x = self.shift_x
        elif self.direction == 'right':
            self.x += self.speed
            if self.x > aquarium_width - self.size - self.shift_x:
                self.direction = 'left'
                self.x = aquarium_width - self.size - self.shift_x
        elif self.direction == 'upleft':
            self.x -= self.speed
            self.y -= self.speed
            if self.x < self.shift_x or self.y < self.shift_y:
                if self.x < self.shift_x:
                    self.x = self.shift_x
                if self.y < self.shift_y:
                    self.y = self.shift_y
                self.direction = 'downright'
        elif self.direction == 'upright':
            self.x += self.speed
            self.y -= self.speed
            if self.x > aquarium_width - self.size - self.shift_x or self.y < self.shift_y:
                if self.x > aquarium_width - self.size - self.shift_x:
                    self.x = aquarium_width - self.size - self.shift_x
                if self.y < self.shift_y:
                    self.y = self.shift_y
                self.direction = 'downleft'
        elif self.direction == 'downleft':
            self.x -= self.speed
            self.y += self.speed
            if self.x < self.shift_x or self.y > aquarium_height - self.size - self.shift_y:
                if self.x < self.shift_x:
                    self.x = self.shift_x
                if self.y > aquarium_height - self.size - self.shift_y:
                    self.y = aquarium_height - self.size - self.shift_y
                self.direction = 'upright'
        elif self.direction == 'downright':
            self.x += self.speed
            self.y += self.speed
            if self.x > aquarium_width - self.size - self.shift_x or self.y > aquarium_height - self.size - self.shift_y:
                if self.x > aquarium_width - self.size - self.shift_x:
                    self.x = aquarium_width - self.size - self.shift_x
                if self.y > aquarium_height - self.size - self.shift_y:
                    self.y = aquarium_height - self.size - self.shift_y
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
        self.setGeometry(int(100*scale), int(100*scale), int(1400*scale), int(850*scale))
        self.setStyleSheet("background-color: white;")

        # Получаем путь к папке с ресурсами
        resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')

        self.aquarium_image = QPixmap(os.path.join(resource_dir,'Full.png'))

        self.click_sound = QSound(os.path.join(resource_dir,"click.wav"))  # Указываем путь к звуковому файлу


        global fish_images

        

        # fish_images с обновленными путями к изображениям
        fish_images = {
            'type1': [QPixmap(os.path.join(resource_dir, 'type1_fish1.png')), QPixmap(os.path.join(resource_dir, 'type1_fish2.png')), QPixmap(os.path.join(resource_dir, 'type1_fish3.png')), QPixmap(os.path.join(resource_dir, 'type1_fish2.png')), QPixmap(os.path.join(resource_dir, 'type1_fish1.png')), QPixmap(os.path.join(resource_dir, 'type1_fish4.png')), QPixmap(os.path.join(resource_dir, 'type1_fish5.png')), QPixmap(os.path.join(resource_dir, 'type1_fish4.png'))],
            'type2': [QPixmap(os.path.join(resource_dir, 'type2_fish1.png')), QPixmap(os.path.join(resource_dir, 'type2_fish2.png')), QPixmap(os.path.join(resource_dir, 'type2_fish3.png')), QPixmap(os.path.join(resource_dir, 'type2_fish2.png')), QPixmap(os.path.join(resource_dir, 'type2_fish1.png')), QPixmap(os.path.join(resource_dir, 'type2_fish4.png')), QPixmap(os.path.join(resource_dir, 'type2_fish5.png')), QPixmap(os.path.join(resource_dir, 'type2_fish4.png'))],
            'type3': [QPixmap(os.path.join(resource_dir, 'type3_fish1.png')), QPixmap(os.path.join(resource_dir, 'type3_fish2.png')), QPixmap(os.path.join(resource_dir, 'type3_fish3.png')), QPixmap(os.path.join(resource_dir, 'type3_fish2.png')), QPixmap(os.path.join(resource_dir, 'type3_fish1.png')), QPixmap(os.path.join(resource_dir, 'type3_fish4.png')), QPixmap(os.path.join(resource_dir, 'type3_fish5.png')), QPixmap(os.path.join(resource_dir, 'type3_fish4.png'))],
            'type4': [QPixmap(os.path.join(resource_dir, 'type4_fish1.png')), QPixmap(os.path.join(resource_dir, 'type4_fish2.png')), QPixmap(os.path.join(resource_dir, 'type4_fish3.png')), QPixmap(os.path.join(resource_dir, 'type4_fish2.png')), QPixmap(os.path.join(resource_dir, 'type4_fish1.png')), QPixmap(os.path.join(resource_dir, 'type4_fish4.png')), QPixmap(os.path.join(resource_dir, 'type4_fish5.png')), QPixmap(os.path.join(resource_dir, 'type4_fish4.png'))]
        }

        self.fish_list = []
        self.create_fish()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fish)
        self.timer.start(220)  # Увеличение интервала для замедления рыбок
        self.all_buttons(1150, 50)
        


    def set_font(self):
        if os.path.isfile("resources/LoveDays.ttf"):
            font_id = QFontDatabase.addApplicationFont("resources/LoveDays.ttf")
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            print("Файл шрифта не найден.")

        self.font = QFont(font_family)  # Создаем экземпляр класса QFont с указанным именем семейства шрифтов


    def all_buttons(self, x, y):

        self.set_font()

        button_style = ("QPushButton { background-color: green; color: white; font-size: 20pt; }"
                    "QPushButton:hover { background-color: lightblue; }"
                    "QPushButton:pressed { background-color: darkblue; }")
        
        button_style1 = ("QPushButton { background-color: blue; color: white; font-size: 20pt; }"
                    "QPushButton:hover { background-color: lightblue; }"
                    "QPushButton:pressed { background-color: darkblue; }")

        self.button = QPushButton('Add Fish', self)
        self.button.setGeometry(int(x*scale), int(y*scale), int(160*scale), int(60*scale))
        self.button.setStyleSheet(button_style)
        self.button.setFont(self.font)
        self.button.clicked.connect(self.button_clicked_open_window)

        self.button1 = QPushButton('Button2', self)
        self.button1.setGeometry(int(x*scale), int((y+100)*scale), int(160*scale), int(60*scale))
        self.button1.setStyleSheet(button_style1)
        self.button1.setFont(self.font)
        self.button1.clicked.connect(self.button_clicked)

        self.button2 = QPushButton('Button3', self)
        self.button2.setGeometry(int(x*scale), int((y+200)*scale), int(160*scale), int(60*scale))
        self.button2.setStyleSheet(button_style1)
        self.button2.setFont(self.font)
        self.button2.clicked.connect(self.button_clicked)


    # Функция, вызываемая при нажатии на кнопку
    def button_clicked(self):
        print("Кнопка была нажата!")
        self.click_sound.play()

    def button_clicked_open_window(self):
        print("Кнопка была нажата!")
        self.click_sound.play()
        second_window = SecondWindow()
        second_window.exec_()


    def create_fish1(self):
        for _ in range(10):
            age = random.randint(1, 100)
            speed = 1
            size = int((age // 5 + 75)*scale)
            fish_type = random.choice(['type1', 'type2', 'type3', 'type4'])  # Выбираем случайный тип рыбы


            fish = Fish(age, speed, size, fish_type)
            self.fish_list.append(fish)


    def create_fish(self):
        global fish_table
        for el in fish_table:

            age = self.calc_age(el[1], el[3])
            speed = 1
            size = self.fish_size(age)
            fish_type = self.fish_type(el[4])

            fish = Fish(age, speed, size, fish_type)
            self.fish_list.append(fish)

    def fish_size(self, age):
        return int((age // 5 + 75)*scale)
    
    def calc_age(self, date_added, age_in_months_at_addition):
        # Получаем сегодняшнюю дату
        today = datetime.date.today()

        # Рассчитываем разницу между сегодняшней датой и датой добавления
        age_delta = today - date_added.date()

        # Преобразуем полученное количество дней в месяцы
        age_in_months = age_delta.days // 30

        # Добавляем возраст рыбы на момент добавления
        age_in_months += age_in_months_at_addition

        return age_in_months

    
    def fish_type(self, a_type):
        keys = ['Cory catfish', 'Guppy', 'Neon Tetra', 'Platies']
        values = ['type1', 'type2', 'type3', 'type4']
        my_dict = dict(zip(keys, values))
        return my_dict[a_type]

    def update_fish(self):
        for fish in self.fish_list:
            fish.move()
            fish.update_image()
            if random.random() < 0.01:  # Change direction randomly
                fish.change_direction()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.drawPixmap(int(-130*scale), int(-80*scale), int(1400*scale), int(1000*scale), self.aquarium_image)

        for fish in self.fish_list:
            fish.draw(painter)

class SecondWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Fish")
        self.setFixedSize(int(500*scale), int(350*scale))  # Установка фиксированного размера окна
        self.label = QLabel("Это второе окно", self)
        self.label.move(int(25*scale), int(25*scale))  # Установка позиции для метки

        self.click_sound = QSound("resources/click.wav")  # Указываем путь к звуковому файлу
    
        self.create_combo_box(50, 50)  # Добавление выпадающего списка
        self.age_slider(50, 100)
        self.add_radio_buttons(280, 50)
        self.button_add(50, 200)
        self.button_clean(300, 300)
    
    def button_clicked(self):
        print("Кнопка была нажата!")
        self.click_sound.play()


    def button_clean(self, x, y):

        button_style = ("QPushButton { background-color: blue; color: white; font-size: 12pt; }"
                    "QPushButton:hover { background-color: lightblue; }"
                    "QPushButton:pressed { background-color: darkblue; }")
        
        self.button1 = QPushButton('Clean All', self)
        self.button1.setGeometry(int(x*scale), int(y*scale), int(80*scale), int(30*scale))
        self.button1.setStyleSheet(button_style)
        # self.button1.setFont(self.font)
        # self.button1.clicked.connect(self.button_clicked)


    def button_add(self, x, y):

        button_style = ("QPushButton { background-color: green; color: white; font-size: 20pt; }"
                    "QPushButton:hover { background-color: lightblue; }"
                    "QPushButton:pressed { background-color: darkblue; }")
        
        self.button = QPushButton('Add Fish', self)
        self.button.setGeometry(int(x*scale), int(y*scale), int(120*scale), int(50*scale))
        self.button.setStyleSheet(button_style)
        # self.button.setFont(self.font)
        self.button.clicked.connect(self.button_clicked)



    def age_slider(self, x, y):
        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Horizontal)  # Устанавливаем горизонтальную ориентацию
        self.slider.setFixedSize(int(400*scale), int(25*scale))  # Устанавливаем размеры слайдера
        self.slider.move(int(x*scale), int(y*scale))  # Устанавливаем позицию для слайдера
        self.slider.setMinimum(0)  # Устанавливаем минимальное значение
        self.slider.setMaximum(60)  # Устанавливаем максимальное значение
        self.slider.setValue(15)  # Устанавливаем начальное значение
        self.slider.setTickInterval(10)  # Устанавливаем интервал меток
        self.slider.valueChanged.connect(self.update_slider_label)  # Подключаем обновление метки к изменению значения слайдера

        self.slider.setStyleSheet("QSlider::groove:horizontal {"
                          "    height: 20px;"  # Устанавливаем высоту бара
                          "    border-radius: 5px;"  # Устанавливаем скругление углов
                          "    background: white;"  # Устанавливаем цвет бара
                          "}"
                          "QSlider::handle:horizontal {"
                          "    background: green;"  # Устанавливаем цвет ползунка
                          "    border: 2px solid #555;"  # Устанавливаем обводку ползунка
                          "    width: 40px;"  # Устанавливаем ширину ползунка
                          "    margin: -5px 0px;"  # Устанавливаем отступы
                          "    border-radius: 10px;"  # Устанавливаем скругление углов ползунка
                          "}"
                          )
        # Создание метки для отображения текущего значения слайдера
        self.slider_label = QLabel('50', self)
        self.slider_label.move(int((x + 400 + 10)*scale), int(y*scale))  # Устанавливаем позицию метки

    def update_slider_label(self, value):
        self.slider_label.setText(str(value))  # Обновляем значение метки при изменении значения слайдера


    def create_combo_box(self, x, y):
        self.combo_box = QComboBox(self)
        self.combo_box.setFixedSize(int(200*scale), int(30*scale))
        self.combo_box.setStyleSheet("font-size: 14pt;")  # Установка размера шрифта 14pt

        self.combo_box.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        self.combo_box.move(int(x*scale), int(y*scale))

    def add_radio_buttons(self, x, y):

        self.radio_male = QRadioButton('Male', self)
        self.radio_female = QRadioButton('Female', self)
        self.radio_male.move(int(x*scale), int(y*scale))
        self.radio_female.move(int((x+100)*scale), int(y*scale))
        self.radio_male.setChecked(True)  # Устанавливаем "Male" по умолчанию
        # Увеличиваем размер радиокнопок
        self.radio_male.setStyleSheet("QRadioButton { font-size: 40px; }")
        self.radio_female.setStyleSheet("QRadioButton { font-size: 40px; }")

        # # Устанавливаем размер круглого кржочка
        # self.radio_male.setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; }")
        # self.radio_female.setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; }")

class db:
    def __init__(self, connection_params):
        self.connection_params = connection_params

    def get_fish(self):
        # 
        try:
            conn = psycopg2.connect(**self.connection_params)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM allfish')
            all_fish = cursor.fetchall()
            cursor.close()
            conn.close()
            print(all_fish)
            return all_fish
        except:
            print('Can`t establish connection to database')

    def add_fish(self, a , b):

        try:
            # пытаемся подключиться к базе данных
            conn = psycopg2.connect(dbname='fish3', user='postgres', password='1', host='localhost', port='5432')
            cursor = conn.cursor()

            # SQL-запрос для добавления новой строки
            insert_query = "INSERT INTO allfish (type_of_fish, sex, age, date_entered) VALUES (%s, %s, %s, %s)"  # замените column1, column2 и column3 на реальные названия столбцов

            current_time = datetime.now().replace(microsecond=0)  # убираем миллисекунды
        
            # данные для новой строки
            new_data = ('Neon Tetra', 'F', 100 ,current_time)  # замените value1, value2 и value3 на реальные значения

            # выполнение запроса
            cursor.execute(insert_query, new_data)

            # подтверждаем транзакцию
            conn.commit()

            # закрываем курсор и соединение
            cursor.close()
            conn.close()

            print("Запись успешно добавлена!")

        except psycopg2.Error as e:
            # в случае ошибки выводим сообщение
            print('Ошибка при добавлении записи в базу данных:', e)


def main():
    global fish_table, connection_params
    my_db = db(connection_params)
    fish_table = my_db.get_fish()
    print(len(fish_table))

    app = QApplication(sys.argv)
    aquarium = Aquarium()
    aquarium.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
