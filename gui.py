import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from downloader import download_video, get_available_formats  # Импортируем функции из downloader.py


# Функция для вставки текста из буфера обмена
def paste_text(event=None):
    try:
        # Получаем содержимое из буфера обмена
        clipboard = root.clipboard_get()
        url_entry.insert('insert', clipboard)
    except tk.TclError:
        pass  # Игнорируем ошибку, если буфер обмена пуст или недоступен


# Обработчик нажатий клавиш
def handle_keypress(event):
    # Проверяем, была ли нажата клавиша Ctrl и в какой раскладке
    if event.state & 0x0004:  # Ctrl is pressed
        if event.keysym in ('v', 'м'):  # 'м' для русской раскладки
            paste_text()
            return 'break'  # Предотвращаем дальнейшую обработку события
        if event.keycode == 86:  # Для английской раскладки
            event.widget.event_generate('<<Paste>>')
            return 'break'


# Функция для обновления прогресса
def update_progress(d):
    if d['status'] == 'downloading':
        percentage = float(d['_percent_str'].strip().replace('%', ''))
        progress_var.set(percentage)
        progress_bar.update()  # Обновляем прогресс-бар


# Функция для вывода логов в текстовое поле
def log_callback(log_msg):
    # Выводим все сообщения, кроме процентов
    if 'percent' not in log_msg:
        log_text.insert(tk.END, log_msg + "\n")
        log_text.see(tk.END)  # Прокручиваем вниз


# Функция для обновления выпадающего списка доступных форматов
def update_format_options(url):
    global available_formats
    available_formats = get_available_formats(url)

    valid_formats = []

    for fmt in available_formats:
        filesize = fmt.get('filesize', None)
        acodec = fmt.get('acodec', None)  # Получаем кодек аудио
        height = fmt.get('height', None)  # Получаем разрешение
        print(fmt)  # Выводим всю информацию о формате

        # Убедимся, что файл имеет аудиодорожку, размер файла не равен None, и разрешение доступно
        if acodec is not None and acodec != 'none' and filesize is not None and height is not None:
            try:
                # Преобразуем filesize в число, если это строка
                filesize = float(filesize)
                valid_formats.append(fmt)
            except ValueError:
                # Если преобразование не удалось, пропускаем формат
                continue

    format_combobox['values'] = [
        f"{fmt['format_id']} - {fmt['height']}p - {fmt['ext']} - "
        f"Filesize: {filesize / (1024 ** 2):.2f} MB" if 'filesize' in fmt else "N/A"
        for fmt in valid_formats
    ]


# Функция для запуска загрузки видео и открытия второго окна с прогресс-баром
def start_download(url, download_path, format_id):
    # Закрываем первое окно
    root.destroy()

    # Создаем второе окно для отображения прогресса и логов
    progress_window = tk.Tk()
    progress_window.title("Скачивание видео")

    # Прогресс-бар
    global progress_var, progress_bar, log_text
    progress_var = tk.DoubleVar()

    # Прогресс-бар
    progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
    progress_bar.pack(pady=10, padx=5, fill=tk.X)

    # Поле для логов
    log_text = tk.Text(progress_window, height=10, state=tk.NORMAL)
    log_text.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)

    # Запускаем скачивание видео с выбранным форматом
    result = download_video(url, download_path, format_id, update_progress, log_callback)

    # Выводим результат в лог
    log_text.insert(tk.END, result + "\n")
    log_text.see(tk.END)

    # Запуск основного цикла второго окна
    progress_window.mainloop()


# Функция для выбора каталога и передачи данных для скачивания
def on_download_button_click():
    url = url_entry.get()
    download_path = filedialog.askdirectory()

    if not url:
        messagebox.showerror("Ошибка", "Введите URL видео!")
        return

    if not download_path:
        messagebox.showerror("Ошибка", "Выберите каталог для сохранения!")
        return

    # Получаем выбранный формат
    selected_format = format_combobox.get()
    if not selected_format:
        messagebox.showerror("Ошибка", "Выберите формат для скачивания!")
        return

    format_id = selected_format.split(' - ')[0]  # Получаем ID формата

    # Открываем окно с прогрессом и логами
    start_download(url, download_path, format_id)


# Функция для загрузки форматов видео
def load_formats():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Ошибка", "Введите URL видео!")
        return

    update_format_options(url)


# Создаем первое окно для ввода URL
root = tk.Tk()
root.title("YouTube Видео Загрузчик")

# Метка для ввода URL
url_label = tk.Label(root, text="Введите URL видео:")
url_label.pack(pady=5)

# Поле ввода URL с отступами 5px
url_frame = tk.Frame(root, padx=5, pady=5)  # Добавляем отступы с помощью Frame
url_frame.pack(fill=tk.X)

url_entry = tk.Entry(url_frame, width=50)
url_entry.pack(fill=tk.X)

# Привязка обработчика для нажатий клавиш
url_entry.bind('<Key>', handle_keypress)

# Кнопка для загрузки форматов видео
load_formats_button = tk.Button(root, text="Загрузить форматы", command=load_formats)
load_formats_button.pack(pady=10)

# Выпадающий список для выбора формата
format_combobox = ttk.Combobox(root, state="readonly")
format_combobox.pack(pady=10, padx=5, fill=tk.X)

# Кнопка для скачивания видео
download_button = tk.Button(root, text="Скачать видео", command=on_download_button_click)
download_button.pack(pady=20)

# Запуск основного цикла программы
root.mainloop()
