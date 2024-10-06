import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from downloader import download_video, get_available_formats  # Импортируем функции из downloader.py

# Функция для вставки текста из буфера обмена
def paste_text(event=None):
    try:
        clipboard = root.clipboard_get()
        url_entry.insert('insert', clipboard)
    except tk.TclError:
        pass  # Игнорируем ошибку, если буфер обмена пуст или недоступен

# Обработчик нажатий клавиш
def handle_keypress(event):
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
    if 'percent' not in log_msg:
        log_text.insert(tk.END, log_msg + "\n")
        log_text.see(tk.END)  # Прокручиваем вниз

# Функция для обновления выпадающих списков доступных форматов
def update_format_options(url):
    global available_formats
    available_formats = get_available_formats(url)

    video_formats = []
    audio_formats = []

    for fmt in available_formats:
        format_id = fmt.get('format_id', '')
        ext = fmt.get('ext', '')
        resolution = fmt.get('resolution', '')
        height = fmt.get('height', '')
        vcodec = fmt.get('vcodec', '')
        acodec = fmt.get('acodec', '')
        filesize_str = fmt.get('filesize', None)
        if filesize_str is not None:
            try:
                filesize = int(float(filesize_str))  # Преобразуем строку в float, затем в int
            except ValueError:
                filesize = None  # Если не удалось преобразовать, ставим None
        else:
            filesize = None

        # Преобразуем filesize в MB
        if filesize:
            filesize_mb = filesize / (1024 ** 2)
            filesize_str = f"{filesize_mb:.2f} MB"
        else:
            filesize_str = "N/A"

        if vcodec != 'none' and acodec == 'none' and filesize_str != "N/A":
            # Это видео без аудио
            video_formats.append({
                'format_id': format_id,
                'description': f"{height}p - {vcodec} - {ext} - {filesize_str}"
            })
        elif vcodec == 'none' and acodec != 'none' and filesize_str != "N/A":
            # Это только аудио
            audio_formats.append({
                'format_id': format_id,
                'description': f"{acodec.upper()} - {ext} - {filesize_str}"
            })
        # Пропускаем форматы, где есть и видео и аудио, или где нет ни того ни другого

    # Обновляем выпадающие списки
    video_combobox['values'] = [vf['description'] for vf in video_formats]
    audio_combobox['values'] = [af['description'] for af in audio_formats]

    # Сохраняем списки форматов для последующего использования
    video_combobox.video_formats = video_formats
    audio_combobox.audio_formats = audio_formats

# Функция для запуска загрузки видео и отображения прогресса и логов
def start_download(url, download_path, video_format_id, audio_format_id):
    # Запускаем скачивание видео с выбранным форматом
    result = download_video(url, download_path, video_format_id, audio_format_id, update_progress, log_callback)

    # Выводим результат в лог
    log_text.insert(tk.END, result + "\n")
    log_text.see(tk.END)

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

    selected_video = video_combobox.get()
    selected_audio = audio_combobox.get()

    if not selected_video:
        messagebox.showerror("Ошибка", "Выберите качество видео!")
        return

    if not selected_audio:
        messagebox.showerror("Ошибка", "Выберите качество звука!")
        return

    # Получаем format_id из выбранных опций
    video_format_id = selected_video.split(' - ')[0]
    audio_format_id = selected_audio.split(' - ')[0]

    # Обновляем прогресс бар и текст логов
    start_download(url, download_path, video_format_id, audio_format_id)

# Функция для загрузки форматов видео
def load_formats():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Ошибка", "Введите URL видео!")
        return

    update_format_options(url)

# Функция для отображения контекстного меню
def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)  # Показываем меню в позиции курсора

# Создаем основное окно
root = tk.Tk()
root.title("YouTube Видео Загрузчик")

# Метка для ввода URL
url_label = tk.Label(root, text="Введите URL видео:")
url_label.pack(pady=5)

# Поле ввода URL
url_frame = tk.Frame(root, padx=5, pady=5)
url_frame.pack(fill=tk.X)

url_entry = tk.Entry(url_frame, width=50)
url_entry.pack(fill=tk.X)

# Привязка обработчика для нажатий клавиш
url_entry.bind('<Key>', handle_keypress)

# Создаем контекстное меню
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Вставить ссылку", command=paste_text)  # Добавляем пункт "Вставить ссылку"

# Привязываем контекстное меню к полю ввода URL
url_entry.bind("<Button-3>", show_context_menu)  # Правая кнопка мыши

# Кнопка для загрузки форматов видео
load_formats_button = tk.Button(root, text="Загрузить форматы", command=load_formats)
load_formats_button.pack(pady=10)

# Фрейм для размещения двух Combobox на одной строке
formats_frame = tk.Frame(root)
formats_frame.pack(pady=10, padx=5, fill=tk.X)

# Метка и Combobox для выбора качества видео
video_label = tk.Label(formats_frame, text="Качество видео:")
video_label.pack(side=tk.LEFT, padx=(0, 5))

video_combobox = ttk.Combobox(formats_frame, state="readonly", width=37)
video_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

# Метка и Combobox для выбора качества звука
audio_label = tk.Label(formats_frame, text="Качество звука:")
audio_label.pack(side=tk.LEFT, padx=(0, 5))

audio_combobox = ttk.Combobox(formats_frame, state="readonly", width=23)
audio_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Прогресс-бар
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=10, padx=5, fill=tk.X)

# Поле для логов
log_text = tk.Text(root, height=10, state=tk.NORMAL)
log_text.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)

# Кнопка для скачивания видео
download_button = tk.Button(root, text="Скачать видео", command=on_download_button_click)
download_button.pack(pady=20)

# Запуск основного цикла программы
root.mainloop()
