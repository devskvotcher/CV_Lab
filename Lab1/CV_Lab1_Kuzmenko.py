import cv2
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES

drawing = False
x_start, y_start, x_end, y_end = -1, -1, -1, -1
image = None
modified_image = None
rectangle_drawn = False
window_name = "Modified Image"

def update(val):
    global image, modified_image, x_start, y_start, x_end, y_end, rectangle_drawn

    if image is None or not rectangle_drawn or x_start == -1 or y_start == -1 or x_end == -1 or y_end == -1:
        return

    x_start_, x_end_ = sorted([x_start, x_end])
    y_start_, y_end_ = sorted([y_start, y_end])

    if x_start_ >= x_end_ or y_start_ >= y_end_:
        return

    alpha = val / 100.0
    region = image[y_start_:y_end_, x_start_:x_end_]
    if region.size == 0:
        return

    gray_half = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    gray_half_bgr = cv2.cvtColor(gray_half, cv2.COLOR_GRAY2BGR)
    modified_image = image.copy()
    blended_half = cv2.addWeighted(region, 1 - alpha, gray_half_bgr, alpha, 0)
    modified_image[y_start_:y_end_, x_start_:x_end_] = blended_half
    cv2.rectangle(modified_image, (x_start_, y_start_), (x_end_, y_end_), (0, 255, 0), 2)
    cv2.imshow(window_name, modified_image)

def draw_rectangle(event, x, y, flags, param):
    global x_start, y_start, x_end, y_end, drawing, rectangle_drawn, image

    if image is None:
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x_start, y_start = x, y
        rectangle_drawn = False

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            temp_image = image.copy()
            cv2.rectangle(temp_image, (x_start, y_start), (x, y), (0, 255, 0), 2)
            cv2.imshow(window_name, temp_image)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x_end, y_end = x, y
        rectangle_drawn = True
        update(cv2.getTrackbarPos('Strength', window_name))

def drop_image(event):
    global image, modified_image, rectangle_drawn
    file_path = event.data.strip().strip('{').strip('}')
    image = cv2.imread(file_path)
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return

    modified_image = image.copy()
    rectangle_drawn = False
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    cv2.setMouseCallback(window_name, draw_rectangle)
    cv2.createTrackbar('Strength', window_name, 0, 100, update)
    cv2.imshow(window_name, image)

root = TkinterDnD.Tk()
root.title("Загрузите изображение")
root.geometry("300x400")
label_instruction = tk.Label(root, text="Загрузите изображение", font=("Arial", 14), wraplength=250, justify="center")
label_instruction.pack(pady=20)
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop_image)
root.mainloop()
cv2.destroyAllWindows()
