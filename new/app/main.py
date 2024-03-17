import sys
import random
import os
import psycopg2
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QDialog, QSlider, QComboBox, QRadioButton, QWidget, QProgressBar
from PyQt5.QtGui import QPixmap, QPainter, QTransform, QFont, QFontDatabase
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QApplication, QWidget, QProgressBar, QVBoxLayout, QStatusBar
from PyQt5.QtWidgets import QProgressBar, QStyleOptionProgressBar, QStyle
import copy
from datetime import timedelta
from PyQt5.QtGui import QPainter, QColor
import time
import matplotlib.pyplot as plt
import threading

# from datetime import datetime



scale = 1.8

aquarium_width = int(1020*scale)
aquarium_height = int(640*scale)

global_shift_x = int(60*scale)
global_shift_y = int(130*scale)

fish_images = None

fish_table = []

fish_list = []

aquarium_volume = 100

heater_switch = True

filter_switch = True

feeder_amount = 50000

led_switch = True

# show_red_circle = True


connection_params = {
    'dbname': 'fish3',
    'user': 'postgres',
    'password': '1',
    'host': 'localhost',
    'port': '5432'
}

global_time = None
led_auto_switch = True

# Функция, которая будет работать в отдельном потоке и обновлять глобальную переменную
def update_global_time():
    global global_time, led_auto_switch, led_switch
    while True:
        # Получаем текущее время
        current_time_str = time.strftime("%H:%M:%S", time.localtime())
        current_time = time.localtime()
        # Обновляем глобальную переменную
        global_time = [current_time, current_time_str]
        current_hour = current_time.tm_hour
        if led_auto_switch:
            if 7 <= current_hour < 21:
                led_switch = True
            else:
                led_switch = False
    
        # Ждем 1 секунду перед обновлением
        time.sleep(1)

# Запускаем функцию в отдельном потоке
update_thread = threading.Thread(target=update_global_time)
update_thread.daemon = True  # Устанавливаем поток в демонский режим, чтобы он завершался при завершении основной программы
update_thread.start()

def write_current_time_to_file(file_path):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(file_path, 'w') as file:
        file.write(current_time)

def read_time_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            time_string = file.readline().strip()
            if time_string:
                return datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M')
            else:
                # Если строка пуста, записываем в файл текущее время и возвращаем его
                write_current_time_to_file(file_path)
                return datetime.datetime.now()
    except FileNotFoundError:
        # Если файл не существует, записываем в него текущее время и возвращаем его
        write_current_time_to_file(file_path)
        return datetime.datetime.now()


feeder_update_date = read_time_from_file("cache/feeder_date.txt")

filter_update_date = read_time_from_file("cache/filter_date.txt")


def write_to_file(file_path, number):
    try:
        with open(file_path, 'w') as file:
            file.write(str(number))  # Записываем число в файл как строку
            print(f"Number {number} has been written to the file.")
    except Exception as e:
        print(f"Error occurred while writing to file: {e}")

def read_from_file(file_path, default_value=0):
    try:
        with open(file_path, 'r') as file:
            content = file.read().strip()  # Читаем содержимое файла и удаляем лишние пробелы
            if content:
                return int(content)  # Если файл не пустой, возвращаем прочитанное число
            else:
                print("File is empty.")
                write_to_file(file_path, default_value)  # Если файл пустой, записываем значение по умолчанию
                return default_value  # и возвращаем его
    except FileNotFoundError:
        print("File not found. Creating a new file.")
        write_to_file(file_path, default_value)  # Если файл отсутствует, создаем новый и записываем в него значение по умолчанию
        return default_value
    except Exception as e:
        print(f"Error occurred while reading from file: {e}")
        return default_value


heater_temp_path = "cache/heater_temp.txt"

heater_temp = read_from_file(heater_temp_path, 21)



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
        self.y = random.randint(shift_y, aquarium_height - self.size+int(60*scale))

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
        self.light_image = QPixmap(os.path.join(resource_dir,'Light_on.png'))

        self.click_sound = QSound(os.path.join(resource_dir,"click.wav"))  # Указываем путь к звуковому файлу


        global fish_images

        # fish_images с обновленными путями к изображениям
        fish_images = {
            'type1': [QPixmap(os.path.join(resource_dir, 'type1_fish1.png')), QPixmap(os.path.join(resource_dir, 'type1_fish2.png')), QPixmap(os.path.join(resource_dir, 'type1_fish3.png')), QPixmap(os.path.join(resource_dir, 'type1_fish2.png')), QPixmap(os.path.join(resource_dir, 'type1_fish1.png')), QPixmap(os.path.join(resource_dir, 'type1_fish4.png')), QPixmap(os.path.join(resource_dir, 'type1_fish5.png')), QPixmap(os.path.join(resource_dir, 'type1_fish4.png'))],
            'type2': [QPixmap(os.path.join(resource_dir, 'type2_fish1.png')), QPixmap(os.path.join(resource_dir, 'type2_fish2.png')), QPixmap(os.path.join(resource_dir, 'type2_fish3.png')), QPixmap(os.path.join(resource_dir, 'type2_fish2.png')), QPixmap(os.path.join(resource_dir, 'type2_fish1.png')), QPixmap(os.path.join(resource_dir, 'type2_fish4.png')), QPixmap(os.path.join(resource_dir, 'type2_fish5.png')), QPixmap(os.path.join(resource_dir, 'type2_fish4.png'))],
            'type3': [QPixmap(os.path.join(resource_dir, 'type3_fish1.png')), QPixmap(os.path.join(resource_dir, 'type3_fish2.png')), QPixmap(os.path.join(resource_dir, 'type3_fish3.png')), QPixmap(os.path.join(resource_dir, 'type3_fish2.png')), QPixmap(os.path.join(resource_dir, 'type3_fish1.png')), QPixmap(os.path.join(resource_dir, 'type3_fish4.png')), QPixmap(os.path.join(resource_dir, 'type3_fish5.png')), QPixmap(os.path.join(resource_dir, 'type3_fish4.png'))],
            'type4': [QPixmap(os.path.join(resource_dir, 'type4_fish1.png')), QPixmap(os.path.join(resource_dir, 'type4_fish2.png')), QPixmap(os.path.join(resource_dir, 'type4_fish3.png')), QPixmap(os.path.join(resource_dir, 'type4_fish2.png')), QPixmap(os.path.join(resource_dir, 'type4_fish1.png')), QPixmap(os.path.join(resource_dir, 'type4_fish4.png')), QPixmap(os.path.join(resource_dir, 'type4_fish5.png')), QPixmap(os.path.join(resource_dir, 'type4_fish4.png'))]
        }

        # Инициализация стилей кнопок
        self.button_style3 = ("QPushButton { background-color: red; color: white; font-size: 16pt; }"
                        "QPushButton:hover { background-color: lightblue; }"
                        "QPushButton:checked { background-color: red; }")
        self.button_style4 = ("QPushButton { background-color: grey; color: white; font-size: 16pt; }"
                        "QPushButton:hover { background-color: lightblue; }"
                        "QPushButton:checked { background-color: grey; }")
        self.button_style5 = ("QPushButton { background-color: blue; color: white; font-size: 16pt; }"
                        "QPushButton:hover { background-color: lightblue; }"
                        "QPushButton:checked { background-color: blue; }")


        self.fish_list = []
        self.create_fish()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fish)
        self.timer.start(220)  # Увеличение интервала для замедления рыбок
        self.all_buttons(1170, 500)
        self.buttons_light(1140, 100)
        


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
        
        button_style1 = ("QPushButton { background-color: orange; color: white; font-size: 20pt; }"
                    "QPushButton:hover { background-color: lightblue; }"
                    "QPushButton:pressed { background-color: darkblue; }")

        button_style2 = ("QPushButton { background-color: blue; color: white; font-size: 20pt; }"
                    "QPushButton:hover { background-color: lightblue; }"
                    "QPushButton:pressed { background-color: darkblue; }")
        
        self.button = QPushButton('Add Fish', self)
        self.button.setGeometry(int(x*scale), int(y*scale), int(160*scale), int(60*scale))
        self.button.setStyleSheet(button_style)
        self.button.setFont(self.font)
        self.button.clicked.connect(self.button_clicked_open_add_window)

        self.button1 = QPushButton('Service', self)
        self.button1.setGeometry(int(x*scale), int((y+100)*scale), int(160*scale), int(60*scale))
        self.button1.setStyleSheet(button_style1)
        self.button1.setFont(self.font)
        self.button1.clicked.connect(self.button_clicked_open_service_window)

        self.button2 = QPushButton('Statistics', self)
        self.button2.setGeometry(int(x*scale), int((y+200)*scale), int(160*scale), int(60*scale))
        self.button2.setStyleSheet(button_style2)
        self.button2.setFont(self.font)
        self.button2.clicked.connect(self.button_clicked_open_stats_window)

    def buttons_light(self, x, y):
        self.button3 = QPushButton('ON', self)
        self.button3.setGeometry(int((x)*scale), int(y*scale), int(70*scale), int(50*scale))
        self.button3.setStyleSheet(self.button_style3)
        self.button3.setCheckable(True)
        self.button3.clicked.connect(self.button_clicked_on)

        self.button4 = QPushButton('OFF', self)
        self.button4.setGeometry(int(x*scale+70*scale), int((y+0)*scale), int(70*scale), int(50*scale))
        self.button4.setStyleSheet(self.button_style4)
        self.button4.setCheckable(True)
        self.button4.clicked.connect(self.button_clicked_off)

        self.button5 = QPushButton('AUTO', self)
        self.button5.setGeometry(int(x*scale + 140*scale), int((y+0)*scale), int(70*scale), int(50*scale))
        self.button5.setStyleSheet(self.button_style5)
        self.button5.setCheckable(True)
        self.button5.clicked.connect(self.button_clicked_auto)

        self.button_clicked_auto_action()

    def button_clicked_on(self):
        self.click_sound.play()
        global led_auto_switch
        self.button3.setChecked(True)
        self.button4.setChecked(False)
        self.button5.setChecked(False)
        global led_switch
        led_switch = True
        if led_auto_switch:
            led_auto_switch = False
        

    def button_clicked_off(self):
        global led_auto_switch
        self.click_sound.play()
        self.button3.setChecked(False)
        self.button4.setChecked(True)
        self.button5.setChecked(False)
        global led_switch
        led_switch = False
        if led_auto_switch:
            led_auto_switch = False


    def button_clicked_auto(self):
        self.click_sound.play()
        self.button_clicked_auto_action()

    def button_clicked_auto_action(self):
        global led_auto_switch
        self.button3.setChecked(False)
        self.button4.setChecked(False)
        self.button5.setChecked(True)
        if not led_auto_switch:
            led_auto_switch = True
        

    def update_button_styles(self):
        # Сначала применяем оригинальные стили
        self.button3.setStyleSheet(self.button_style3)
        self.button4.setStyleSheet(self.button_style4)
        self.button5.setStyleSheet(self.button_style5)
        # Затем добавляем стили для нажатых кнопок
        if self.button3.isChecked():
            self.button3.setStyleSheet(self.button3.styleSheet() + "QPushButton { background-color: red; }")
        elif self.button4.isChecked():
            self.button4.setStyleSheet(self.button4.styleSheet() + "QPushButton { background-color: grey; }")
        elif self.button5.isChecked():
            self.button5.setStyleSheet(self.button5.styleSheet() + "QPushButton { background-color: blue; }")



    # Функция, вызываемая при нажатии на кнопку
    def button_clicked_open_stats_window(self):
        # print("Кнопка была нажата!")
        self.click_sound.play()
        stats_window = StatsWindow()
        stats_window.exec_()

    def button_clicked_open_add_window(self):
        # print("Кнопка была нажата!")
        self.click_sound.play()
        second_window = SecondWindow()
        second_window.exec_()
        

    def button_clicked_open_service_window(self):
        # print("Кнопка была нажата!")
        self.click_sound.play()
        service_window = ServiceWindow()
        service_window.exec_()


    # def create_fish1(self):
    #     for _ in range(10):
    #         age = random.randint(1, 100)
    #         speed = 1
    #         size = int((age // 5 + 75)*scale)
    #         fish_type = random.choice(['type1', 'type2', 'type3', 'type4'])  # Выбираем случайный тип рыбы


    #         fish = Fish(age, speed, size, fish_type)
    #         self.fish_list.append(fish)


    def create_fish(self):
        global fish_table, fish_list
        for el in fish_table:

            age = self.calc_age(el[1], el[3])
            speed = 1
            size = self.fish_size(age)
            fish_type = self.fish_type(el[4])

            fish = Fish(age, speed, size, fish_type)
            fish_list.append(fish)

    def fish_size(self, age):
        return int((age // 5 + 75)*scale)
    
    @staticmethod
    def calc_age(date_added, age_in_months_at_addition):
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
        global fish_list
        for fish in fish_list:
            fish.move()
            fish.update_image()
            if random.random() < 0.01:  # Change direction randomly
                fish.change_direction()
        self.update()


    def paintEvent(self, event):
        global fish_list, filter_switch, heater_switch, led_switch
        painter = QPainter(self)
        painter.drawPixmap(int(-130*scale), int(-80*scale), int(1400*scale), int(1000*scale), self.aquarium_image)

        if led_switch:
            painter.drawPixmap(int(-130*scale), int(-80*scale), int(1400*scale), int(1000*scale), self.light_image)

        if filter_switch:
            painter.setBrush(QColor('red'))
            painter.drawEllipse(int(1039*scale), int(189*scale), int(13*scale), int(13*scale))

        if heater_switch:
            painter.setBrush(QColor('red'))
            painter.drawEllipse(int(66*scale), int(150*scale), int(8*scale), int(8*scale))
            

        for fish in fish_list:
            fish.draw(painter)

class SecondWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Fish")
        self.setFixedSize(int(500*scale), int(350*scale))  # Установка фиксированного размера окна
        self.label = QLabel("Это второе окно", self)
        self.label.move(int(25*scale), int(25*scale))  # Установка позиции для метки

        self.click_sound = QSound("resources/click.wav")  # Указываем путь к звуковому файлу
        self.age = 15
        self.sex = 'M'
        self.type = "Cory catfish"
        self.create_combo_box(50, 50)  # Добавление выпадающего списка
        self.age_slider(50, 100)
        self.add_radio_buttons(280, 50)
        self.button_add(50, 200)
        self.button_clean(300, 300)
    
    def button_add_clicked(self):
        # print("Кнопка была нажата!")
        global aquarium_volume, fish_list
        if len(fish_list) < aquarium_volume/2:
            self.click_sound.play()
            global connection_params, fish_table
            my_db = db(connection_params)

            my_db.add_fish(self.type, self.sex, self.age)
            current_time = datetime.datetime.now().replace(microsecond=0)  # убираем миллисекунды
            temp_fish = (self.sex, current_time, 0, self.age, self.type)  
            # ВНИМАНИЕ 0 Это не ПРАВДА
            fish_table.append(temp_fish)
            speed = 1
            fish_type= self.fish_type_keys(self.type)
            fish = Fish(self.age, speed, self.fish_size(self.age), fish_type)
            fish_list.append(fish)
        else:
            print("no more space")

    def fish_size(self, age):
        return int((age // 5 + 75)*scale)
    
    def fish_type_keys(self, a_type):
        keys = ['Cory catfish', 'Guppy', 'Neon Tetra', 'Platies']
        values = ['type1', 'type2', 'type3', 'type4']
        my_dict = dict(zip(keys, values))
        return my_dict[a_type]


    def button_clean_clicked(self):
        # print("Кнопка была нажата!")
        if True :
            global connection_params, fish_list, fish_table
            self.click_sound.play()

            my_db = db(connection_params)
            my_db.delete_all_fish()
            fish_list = []
            fish_table = []

            


    def button_clean(self, x, y):

        button_style = ("QPushButton { background-color: blue; color: white; font-size: 12pt; }"
                    "QPushButton:hover { background-color: lightblue; }"
                    "QPushButton:pressed { background-color: darkblue; }")
        
        self.button1 = QPushButton('Clean All', self)
        self.button1.setGeometry(int(x*scale), int(y*scale), int(80*scale), int(30*scale))
        self.button1.setStyleSheet(button_style)
        # self.button1.setFont(self.font)
        self.button1.clicked.connect(self.button_clean_clicked)


    def button_add(self, x, y):

        button_style = ("QPushButton { background-color: green; color: white; font-size: 20pt; }"
                    "QPushButton:hover { background-color: lightblue; }"
                    "QPushButton:pressed { background-color: darkblue; }")
        
        self.button = QPushButton('Add Fish', self)
        self.button.setGeometry(int(x*scale), int(y*scale), int(120*scale), int(50*scale))
        self.button.setStyleSheet(button_style)
        # self.button.setFont(self.font)
        self.button.clicked.connect(self.button_add_clicked)



    def age_slider(self, x, y):
        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Horizontal)  # Устанавливаем горизонтальную ориентацию
        self.slider.setFixedSize(int(400*scale), int(25*scale))  # Устанавливаем размеры слайдера
        self.slider.move(int(x*scale), int(y*scale))  # Устанавливаем позицию для слайдера
        self.slider.setMinimum(0)  # Устанавливаем минимальное значение
        self.slider.setMaximum(60)  # Устанавливаем максимальное значение
        self.slider.setValue(15)  # Устанавливаем начальное значение
        self.slider.setTickInterval(10)  # Устанавливаем интервал меток
        self.slider.valueChanged.connect(self.update_slider_action)  # Подключаем обновление метки к изменению значения слайдера

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
        self.slider_label = QLabel('15', self)
        self.slider_label.move(int((x + 400 + 10)*scale), int(y*scale))  # Устанавливаем позицию метки

    def update_slider_action(self, value):
        self.age << value
        self.slider_label.setText(str(value))  # Обновляем значение метки при изменении значения слайдера


    def create_combo_box(self, x, y):
        self.combo_box = QComboBox(self)
        self.combo_box.setFixedSize(int(200*scale), int(30*scale))
        self.combo_box.setStyleSheet("font-size: 14pt;")  # Установка размера шрифта 14pt

        self.combo_box.addItems(["Cory catfish", "Guppy", "Neon Tetra", "Platies"])
        self.combo_box.move(int(x*scale), int(y*scale))
        self.combo_box.activated.connect(self.get_type)

    def get_type(self, index):
        selected_option = self.combo_box.itemText(index)
        self.type = selected_option
        print("Selected option:", selected_option)

    def add_radio_buttons(self, x, y):

        self.radio_male = QRadioButton('Male', self)
        self.radio_female = QRadioButton('Female', self)
        self.radio_male.move(int(x*scale), int(y*scale))
        self.radio_female.move(int((x+100)*scale), int(y*scale))
        self.radio_male.setChecked(True)  # Устанавливаем "Male" по умолчанию
        # Увеличиваем размер радиокнопок
        self.radio_male.setStyleSheet("QRadioButton { font-size: 40px; }")
        self.radio_female.setStyleSheet("QRadioButton { font-size: 40px; }")

         # Подключаем слоты для сигналов toggled радиокнопок
        self.radio_male.toggled.connect(self.on_male_toggled)
        self.radio_female.toggled.connect(self.on_female_toggled)

        # # Устанавливаем размер круглого кржочка
        # self.radio_male.setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; }")
        # self.radio_female.setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; }")

    def on_male_toggled(self, checked):
        if checked:
            self.sex = "M"
            print("Selected gender: Male")

    def on_female_toggled(self, checked):
        if checked:
            self.sex = "F"
            print("Selected gender: Female")

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
            # print(all_fish)
            return all_fish
        except:
            print('Can`t establish connection to database')

    def add_fish(self, type_of_fish, sex, age):

        try:
            # пытаемся подключиться к базе данных
            conn = psycopg2.connect(**self.connection_params)
            cursor = conn.cursor()

            # SQL-запрос для добавления новой строки
            insert_query = "INSERT INTO allfish (type_of_fish, sex, age, date_entered) VALUES (%s, %s, %s, %s)"  # замените column1, column2 и column3 на реальные названия столбцов

            current_time = datetime.datetime.now().replace(microsecond=0)  # убираем миллисекунды
        
            # данные для новой строки
            new_data = (type_of_fish, sex, age ,current_time)  # замените value1, value2 и value3 на реальные значения

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

    def delete_all_fish(self):
        try:
            conn = psycopg2.connect(**self.connection_params)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM allfish')
            conn.commit()  # Не забудьте подтвердить изменения с помощью commit()
            cursor.close()
            conn.close()
            print('All fish deleted successfully.')
        except psycopg2.Error as e:
            print('Error deleting fish:', e)

class ServiceWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aquarium maintaince")
        self.setFixedSize(int(600*scale), int(320*scale))  # Установка фиксированного размера окна
        # self.label = QLabel("Это второе окно", self)
        # self.label.move(int(25*scale), int(25*scale))  # Установка позиции для метки

        self.click_sound = QSound("resources/click.wav")  # Указываем путь к звуковому файлу
        a = Fider()
        self.left = int(a.food_left())
        self.add_filter()
        self.add_feeder()
        self.add_heater()

    def add_filter(self):
        label = QLabel("Filter", self)
        label.move(int(25*scale), int(25*scale))  # Установка позиции для метки
        label_font = QFont("Arial", 16)  # Создаем экземпляр QFont с указанным шрифтом и размером
        label.setFont(label_font)  # Устанавливаем шрифт для метки
        
        a = Fider()
        b = a.filter_status()
        global progress_bar_filter
        progress_bar_filter = ProgressBar(self, int(200*scale), int(25*scale), 0, 100, 0 )
        progress_bar_filter.move(int(110*scale), int(25*scale))  
        progress_bar_filter.set_progress_for_filter(b)

        self.button_clean_filter(int(350), int(23))

        self.button_switch_filter(475, 23)
        

    def add_feeder(self):
        
        label = QLabel("Feeder", self)
        label.move(int(25*scale), int(100*scale))  # Установка позиции для метки
        label_font = QFont("Arial", 16)  # Создаем экземпляр QFont с указанным шрифтом и размером
        label.setFont(label_font)  # Устанавливаем шрифт для метки
        
        global progress_bar_feeder
        progress_bar_feeder= ProgressBar(self, int(200*scale), int(25*scale), 0, 100, 0 )
        progress_bar_feeder.move(int(110*scale), int(100*scale))  
        progress_bar_feeder.set_progress_for_feeder(self.left)

        self.button_topup_feeder(int(350), int(98))
        self.button_refresh_feeder(int(475), int(98))

    def add_heater(self):
        global heater_temp
        self.temp = heater_temp
        label = QLabel("Heater", self)
        label.move(int(25*scale), int(180*scale))  # Установка позиции для метки
        label_font = QFont("Arial", 16)  # Создаем экземпляр QFont с указанным шрифтом и размером
        label.setFont(label_font)  # Устанавливаем шрифт для метки
        
        self.progress_bar_heater = ProgressBar(self, int(200*scale), int(25*scale), 0, 40, self.temp )
        self.progress_bar_heater.move(int(110*scale), int(180*scale))  
        
        self.progress_bar_heater.set_progress_for_heater(self.temp)

        self.button_switch_heater(475, 178)
        
        self.temp_slider(50, 250, self.temp)

        self.button_set_temp(int(350), int(178))


    def button_clean_filter(self, x, y):

        button_style = ("QPushButton { background-color: blue; color: white; font-size: 15pt; }"
                    "QPushButton:hover { background-color: lightblue; }"
                    "QPushButton:pressed { background-color: darkblue; }")
        
        button = QPushButton('Clean', self)
        button.setGeometry(int(x*scale), int(y*scale), int(90*scale), int(30*scale))
        button.setStyleSheet(button_style)
        # self.button.setFont(self.font)
        button.clicked.connect(self.button_clean_filter_clicked)

    def button_clean_filter_clicked(self):
        global filter_update_date, progress_bar_filter
        self.click_sound.play()
        write_current_time_to_file("cache/filter_date.txt")
        filter_update_date = datetime.datetime.now().replace(microsecond=0)
        a = Fider()
        b = a.filter_status()
        progress_bar_filter.set_progress_for_filter(b)


    def button_topup_feeder(self, x, y):

        button_style = ("QPushButton { background-color: green; color: white; font-size: 15pt; }"
                    "QPushButton:hover { background-color: lightblue; }"
                    "QPushButton:pressed { background-color: darkblue; }")
        
        button = QPushButton('Top Up', self)
        button.setGeometry(int(x*scale), int(y*scale), int(90*scale), int(30*scale))
        button.setStyleSheet(button_style)
        # self.button.setFont(self.font)
        button.clicked.connect(self.button_topup_feeder_clicked)

    def button_topup_feeder_clicked(self):
        global feeder_update_date
        self.click_sound.play()
        write_current_time_to_file("cache/feeder_date.txt")
        feeder_update_date = datetime.datetime.now().replace(microsecond=0)
        self.button_refresh_feeder_clicked()
        global progress_bar_feeder
        
        a = Fider()
        b = a.food_left()
        progress_bar_feeder.set_progress_for_feeder(int(b))

        

    def button_refresh_feeder(self, x, y):

        button_style = ("QPushButton { background-color: blue; color: white; font-size: 15pt; }"
                    "QPushButton:hover { background-color: lightblue; }"
                    "QPushButton:pressed { background-color: darkblue; }")
        
        button = QPushButton('Refresh', self)
        button.setGeometry(int(x*scale), int(y*scale), int(90*scale), int(30*scale))
        button.setStyleSheet(button_style)
        # self.button.setFont(self.font)
        button.clicked.connect(self.button_refresh_feeder_clicked)

    def button_refresh_feeder_clicked(self):
        global progress_bar_feeder
        self.click_sound.play()
        a = Fider()
        b = a.food_left()
        progress_bar_feeder.set_progress_for_feeder(int(b))
        # print(b)



    def button_switch_heater(self, x, y):
        global heater_switch
        self.button_style_off = ("QPushButton { background-color: grey; color: white; font-size: 15pt; }"
                            "QPushButton:hover { background-color: lightblue; }"
                            "QPushButton:pressed { background-color: darkblue; }")
        self.button_style_on = ("QPushButton { background-color: red; color: white; font-size: 15pt; }"
                            "QPushButton:hover { background-color: lightblue; }"
                            "QPushButton:pressed { background-color: darkblue; }")
        
        self.button = QPushButton('ON/OFF', self)
        self.button.setGeometry(int(x*scale), int(y*scale), int(90*scale), int(30*scale))
        self.button.clicked.connect(self.button_switch_heater_clicked)

        # Устанавливаем начальный стиль кнопки в зависимости от значения heater_switch
        if heater_switch == True:
            self.button.setStyleSheet(self.button_style_on)
        else:
            self.button.setStyleSheet(self.button_style_off)

    def button_switch_heater_clicked(self):
        global heater_switch
        self.click_sound.play()

        heater_switch = self.switch_off_on(heater_switch)
        # print(heater_switch)

        # После изменения состояния переменной heater_switch меняем стиль кнопки
        if heater_switch == True:
            self.button.setStyleSheet(self.button_style_on)
        else:
            self.button.setStyleSheet(self.button_style_off)

    def switch_off_on(self, a_value):
        return not a_value  # Просто инвертируем значение
    
    def temp_slider(self, x, y, temp):
        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Horizontal)  # Устанавливаем горизонтальную ориентацию
        self.slider.setFixedSize(int(500*scale), int(25*scale))  # Устанавливаем размеры слайдера
        self.slider.move(int(x*scale), int(y*scale))  # Устанавливаем позицию для слайдера
        self.slider.setMinimum(8)  # Устанавливаем минимальное значение
        self.slider.setMaximum(34)  # Устанавливаем максимальное значение
        self.slider.setValue(temp)  # Устанавливаем начальное значение
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(2)  # Устанавливаем интервал меток
        self.slider.setPageStep(2)
        
        self.slider.valueChanged.connect(self.update_slider_action)  # Подключаем обновление метки к изменению значения слайдера

        self.slider.setStyleSheet("QSlider::groove:horizontal {"
                          "    height: 30px;"  # Устанавливаем высоту бара
                          "    border-radius: 5px;"  # Устанавливаем скругление углов
                          "    background: #cce6ff;"  # Устанавливаем цвет бара
                          "}"
                          "QSlider::handle:horizontal {"
                          "    background: #ffd633;"  # Устанавливаем цвет ползунка
                          "    border: 2px solid #555;"  # Устанавливаем обводку ползунка
                          "    width: 60px;"  # Устанавливаем ширину ползунка
                          "    margin: -5px 0px;"  # Устанавливаем отступы
                          "    border-radius: 25px;"  # Устанавливаем скругление углов ползунка
                          "}"
                          )
        # Создание метки для отображения текущего значения слайдера
        self.slider_label = QLabel(str(temp), self)
        self.slider_label.move(int((x + 500 + 10)*scale), int(y*scale))  # Устанавливаем позицию метки

    def update_slider_action(self, value):
        self.temp = value
        self.slider_label.setText(str(value))  # Обновляем значение метки при изменении значения слайдера


    def button_set_temp(self, x, y):

        button_style = ("QPushButton { background-color: green; color: white; font-size: 15pt; }"
                    "QPushButton:hover { background-color: lightblue; }"
                    "QPushButton:pressed { background-color: darkblue; }")
        
        button = QPushButton('Set temp', self)
        button.setGeometry(int(x*scale), int(y*scale), int(90*scale), int(30*scale))
        button.setStyleSheet(button_style)
        # self.button.setFont(self.font)
        button.clicked.connect(self.button_set_temp_clicked)


    def button_set_temp_clicked(self):
        self.click_sound.play()
        global heater_temp_path, heater_temp
        if heater_temp < self.temp:
            while heater_temp < self.temp:
                heater_temp += 1
                # print(heater_temp)
                self.progress_bar_heater.set_progress_for_heater(heater_temp)
                time.sleep(0.5)
        elif heater_temp > self.temp:
            while heater_temp > self.temp:
                heater_temp -= 1
                # print(heater_temp)
                self.progress_bar_heater.set_progress_for_heater(heater_temp)
                time.sleep(0.5)
        else:
            heater_temp = self.temp

        write_to_file(heater_temp_path, self.temp)
        
        # print(self.temp)

    def button_switch_filter(self, x, y):
        global filter_switch
        self.button1_style_off = ("QPushButton { background-color: grey; color: white; font-size: 15pt; }"
                            "QPushButton:hover { background-color: lightblue; }"
                            "QPushButton:pressed { background-color: darkblue; }")
        self.button1_style_on = ("QPushButton { background-color: red; color: white; font-size: 15pt; }"
                            "QPushButton:hover { background-color: lightblue; }"
                            "QPushButton:pressed { background-color: darkblue; }")
        
        self.button1 = QPushButton('ON/OFF', self)
        self.button1.setGeometry(int(x*scale), int(y*scale), int(90*scale), int(30*scale))
        self.button1.clicked.connect(self.button_switch_filter_clicked)

        # Устанавливаем начальный стиль кнопки в зависимости от значения filter_switch
        if filter_switch == True:
            self.button1.setStyleSheet(self.button1_style_on)
        else:
            self.button1.setStyleSheet(self.button1_style_off)

    def button_switch_filter_clicked(self):
        global filter_switch
        self.click_sound.play()

        filter_switch = self.switch_off_on(filter_switch)
        # print(filter_switch)

        # После изменения состояния переменной filter_switch меняем стиль кнопки
        if filter_switch == True:
            self.button1.setStyleSheet(self.button1_style_on)
        else:
            self.button1.setStyleSheet(self.button1_style_off)



class StatsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stats and analitics")
        self.setFixedSize(int(800*scale), int(600*scale))
        self.setStyleSheet("background-color: white;")  # Устанавливаем белый фон для окна
        self.click_sound = QSound("resources/click.wav")

        # Создание данных для графиков
        labels = ['A', 'B', 'C', 'D']
        values = [30, 40, 20, 10]

        self.pie_chart(labels, values)
        self.line_chart(labels, values)
        self.bar_chart(labels, values)

        self.add_sll_plots()
        

    def add_sll_plots(self):

        # Добавляем изображения графиков в окно
        pie_chart_label = QLabel(self)
        pie_chart_label.setGeometry(int(50*scale), int(50*scale), int(300*scale), int(300*scale))  # Позиция и размеры изображения
        pie_chart_label.setPixmap(QPixmap('cache/plots/pie_chart.png'))

        line_chart_label = QLabel(self)
        line_chart_label.setGeometry(int(300*scale), int(50*scale), int(300*scale), int(300*scale))
        line_chart_label.setPixmap(QPixmap('cache/plots/line_chart.png'))

        bar_chart_label = QLabel(self)
        bar_chart_label.setGeometry(int(500*scale), int(50*scale), int(300*scale), int(300*scale))  # Позиция и размеры изображения
        bar_chart_label.setPixmap(QPixmap('cache/plots/bar_chart.png'))


    def pie_chart(self, labels, values):
        # Круговая диаграмма
        plt.figure(figsize=(3, 3))
        plt.pie(values, labels=labels, autopct='%1.1f%%')
        plt.title('Pie Chart')
        plt.axis('equal')  # Чтобы круг был кругом, а не эллипсом
        plt.savefig('cache/plots/pie_chart.png')  # Сохраняем график в файл
        plt.close()

    def line_chart(self, labels, values):
        # Линейная диаграмма
        plt.figure(figsize=(3, 3))
        plt.plot(labels, values, marker='o')
        plt.title('Line Chart')
        plt.xlabel('Labels')
        plt.ylabel('Values')
        plt.grid(True)
        plt.savefig('cache/plots/line_chart.png')
        plt.close()

    def bar_chart(self, labels, values):
         # Столбчатая диаграмма
        plt.figure(figsize=(6, 4))
        plt.bar(labels, values, color='skyblue')
        plt.title('Bar Chart')
        plt.xlabel('Labels')
        plt.ylabel('Values')
        plt.grid(axis='y')
        plt.savefig('cache/plots/bar_chart.png')  # Сохраняем график в файл
        plt.close()


class ProgressBar(QWidget):
    def __init__(self, parent, x, y, min, max, set):
        super().__init__(parent)
        self.x = x
        self.y = y
        self.min = min
        self.max = max
        self.set = set
        self.initUI()

    def initUI(self):
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(0, 0, self.x, self.y)  # Учитываем размеры родительского объекта
        self.progress_bar.setMinimum(self.min)
        self.progress_bar.setMaximum(self.max)
        self.progress_bar.setValue(self.set)
        

        # self.setWindowTitle('Пример прогресс-бара')
        # self.setGeometry(100, 100, self.parent_width - 200, 100)  # Устанавливаем размеры виджета ProgressBar
    
    def set_progress_for_filter(self, value):
        self.progress_bar.setValue(value)
        if value > 85:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    text-align: center;  /* Центрирование текста */
                    font-size: 35px;  /* Размер шрифта */
                    color: black;  /* Цвет текста */
                    font-weight: bold;  /* Жирный текст */
                }
                QProgressBar::chunk {
                    background-color: #cc0000;
                    width: 10px;
                    margin: 1px;
                }
            """)
        elif value > 70:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    text-align: center;  /* Центрирование текста */
                    font-size: 35px;  /* Размер шрифта */
                    color: black;  /* Цвет текста */
                    font-weight: bold;  /* Жирный текст */
                }
                QProgressBar::chunk {
                    background-color: #ffa31a;
                    width: 10px;
                    margin: 1px;
                }
            """)
        else:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    text-align: center;  /* Центрирование текста */
                    font-size: 35px;  /* Размер шрифта */
                    color: black;  /* Цвет текста */
                    font-weight: bold;  /* Жирный текст */
                }
                QProgressBar::chunk {
                    background-color: green;
                    width: 10px;
                    margin: 1px;
                }
            """)

    def set_progress_for_feeder(self, value):
        self.progress_bar.setValue(value)
        if value < 20:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    text-align: center;  /* Центрирование текста */
                    font-size: 35px;  /* Размер шрифта */
                    color: black;  /* Цвет текста */
                    font-weight: bold;  /* Жирный текст */
                }
                QProgressBar::chunk {
                    background-color: #cc0000;
                    width: 10px;
                    margin: 1px;
                }
            """)
        elif value < 40:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    text-align: center;  /* Центрирование текста */
                    font-size: 35px;  /* Размер шрифта */
                    color: black;  /* Цвет текста */
                    font-weight: bold;  /* Жирный текст */
                }
                QProgressBar::chunk {
                    background-color: #ffa31a;
                    width: 10px;
                    margin: 1px;
                }
            """)
        else:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    text-align: center;  /* Центрирование текста */
                    font-size: 35px;  /* Размер шрифта */
                    color: black;  /* Цвет текста */
                    font-weight: bold;  /* Жирный текст */
                }
                QProgressBar::chunk {
                    background-color: green;
                    width: 10px;
                    margin: 1px;
                }
            """)

    def set_progress_for_heater(self, value):
        self.progress_bar.setValue(value)
        if value > 30:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    text-align: center;  /* Центрирование текста */
                    font-size: 35px;  /* Размер шрифта */
                    color: black;  /* Цвет текста */
                    font-weight: bold;  /* Жирный текст */
                }
                QProgressBar::chunk {
                    background-color: #cc0000;
                    width: 10px;
                    margin: 1px;
                }
            """)
        elif value > 18:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    text-align: center;  /* Центрирование текста */
                    font-size: 35px;  /* Размер шрифта */
                    color: black;  /* Цвет текста */
                    font-weight: bold;  /* Жирный текст */
                }
                QProgressBar::chunk {
                    background-color: #ffa31a;
                    width: 10px;
                    margin: 1px;
                }
            """)
        else:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    text-align: center;  /* Центрирование текста */
                    font-size: 35px;  /* Размер шрифта */
                    color: black;  /* Цвет текста */
                    font-weight: bold;  /* Жирный текст */
                }
                QProgressBar::chunk {
                    background-color: blue;
                    width: 10px;
                    margin: 1px;
                }
            """)

        # Заменяем значок процента на значок градуса Цельсия
        self.progress_bar.setFormat("%v°C")

class Fider:
    def __init__(self):
        self.type = {
            'Cory catfish': 200,
            'Guppy': 250,
            'Neon Tetra': 230,
            'Platies': 300
        } 
        # global feeder_update_date
        self.amount = 0
        # self.topup_date = datetime.datetime(2024, 3, 13, 20, 5, 50)
        # now = datetime.datetime.now()
        # self.topup_date = now - timedelta(days=2)
        # self.topup_date  = feeder_update_date

    def fish_portion(self, a_fish):
        age = Aquarium.calc_age(a_fish[1], a_fish[3])
        default_portion = self.type[a_fish[4]]

        return default_portion + (age-50)*1.1

    def calc_full_portion(self, option):
        global fish_table, feeder_update_date, filter_update_date
        if option == 0:
            update_date = feeder_update_date
        else:
            update_date = filter_update_date

        fish_table_safe = copy.deepcopy(fish_table)
        for a_fish in fish_table_safe:
            days = self.fish_time_since(update_date, a_fish[1])
            portion = self.fish_portion(a_fish)
            self.amount = self.amount + portion*days
        
        return self.amount
    
    def food_left(self):
        global feeder_amount
        p = self.calc_full_portion(0)
        left = feeder_amount-p
        
        return self.calculate_percentage(left, feeder_amount)
    
    def filter_status(self):
        global feeder_amount
        p = self.calc_full_portion(1)
        left = feeder_amount-p
        
        return int((100 - self.calculate_percentage(left, feeder_amount))*0.7)

    def calculate_percentage(self, part, whole):
        return (part / whole) * 100


    def fish_time_since(self, topup_date, fish_add_date):
        now = datetime.datetime.now()
        # Разница между текущей датой и датой внесения рыбы
        fish_age = now - fish_add_date

        # Разница между текущей датой и датой последней дозаправки
        topup_age = now - topup_date

        # Если рыба была добавлена позже, то используем это значение
        if fish_age > topup_age:
            days_since = fish_age.days
        else:
            days_since = topup_age.days

        return days_since







def main():
    global fish_table, connection_params
    my_db = db(connection_params)
    fish_table = my_db.get_fish()
    # print(len(fish_table))

    app = QApplication(sys.argv)
    aquarium = Aquarium()
    aquarium.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
