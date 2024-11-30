import cv2
import numpy as np
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES

# Глобальные переменные
image = None

# Цветовые диапазоны (BGR)
color_ranges = {
    "red": [(0, 0, 100), (100, 100, 255)],
    "green": [(0, 100, 0), (100, 255, 100)],
    "blue": [(100, 0, 0), (255, 100, 100)],
    "yellow": [(0, 150, 150), (100, 255, 255)],
    "white": [(200, 200, 200), (255, 255, 255)],
    "orange": [(0, 50, 150), (100, 150, 255)]
}


# Определение цвета на основе среднего значения
def determine_color(mean_color):
    for color_name, (lower, upper) in color_ranges.items():
        if all(lower[i] <= mean_color[i] <= upper[i] for i in range(3)):
            return color_name
    return "unknown"


# Распознавание квадратов и цветов
def detect_colors():
    global image

    if image is None:
        print("Пожалуйста, загрузите изображение!")
        return

    # Преобразование в оттенки серого и сглаживание
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Выделение контуров
    _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_colors = []
    output_image = image.copy()

    for contour in contours:
        # Аппроксимация контура
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)

        # Проверка, является ли контур квадратом
        if len(approx) == 4 and cv2.contourArea(contour) > 500:
            # Получаем прямоугольник, охватывающий квадрат
            x, y, w, h = cv2.boundingRect(approx)
            roi = image[y:y+h, x:x+w]

            # Вычисление среднего цвета в контуре
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(mask, [approx], -1, 255, -1)  # Создаём маску для контуров
            mean_color = cv2.mean(image, mask=mask)[:3]
            mean_color = tuple(map(int, mean_color))

            # Определение цвета
            color_name = determine_color(mean_color)
            detected_colors.append(color_name)

            # Отображение квадрата и его цвета
            cv2.rectangle(output_image, (x, y), (x+w, y+h), (0, 0, 0), 2)
            cv2.putText(output_image, color_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    # Отображение результата
    cv2.imshow("Detected Colors", output_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print("Найденные цвета:", detected_colors)


# Функция для обработки перетаскивания изображения
def drop_image(event):
    global image
    file_path = event.data.strip().strip('{').strip('}')
    image = cv2.imread(file_path)
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return

    # Автоматическое распознавание после загрузки
    detect_colors()


# Создание GUI с помощью TkinterDnD
root = TkinterDnD.Tk()
root.title("Распознавание цветов кубика Рубика")
root.geometry("300x300")

# Инструкция для пользователя
label_instruction = tk.Label(root, text="Перетащите изображение кубика Рубика", font=("Arial", 14), wraplength=250, justify="center")
label_instruction.pack(pady=20)

# Добавление функциональности для перетаскивания
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop_image)

# Запуск основного цикла Tkinter
root.mainloop()

# Уничтожение всех окон OpenCV
cv2.destroyAllWindows()
