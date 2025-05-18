from tkinter import *
from tkinter import ttk
from functools import partial
import pyttsx3


def update_volume(volume_label,value):
    volume = float(value)
    engine.setProperty('volume', volume)
    volume_label.config(text=f"Громкость: {int(volume*100)}%")

def on_mousewheel_volume(slider,volume_label,event):
    current = slider.get()
    if event.delta > 0:  # Прокрутка вверх
        new_value = min(current + 0.02, 1.0)
    else:  # Прокрутка вниз
        new_value = max(current - 0.02, 0.0)
    slider.set(new_value)
    update_volume(volume_label,new_value)


def update_rate(speed_label,value):
    rate = int(value)
    engine.setProperty('rate', rate)
    speed_label.config(text=f"Скорость: {int(rate*100)}%")

def on_mousewheel_rate(slider,speed_label,event):
    current = slider.get()
    if event.delta > 0:  # Прокрутка вверх
        new_value = min(current + 0.02, 1.0)
    else:  # Прокрутка вниз
        new_value = max(current - 0.02, 0.0)
    slider.set(new_value)
    update_volume(speed_label,new_value)


def show_settings():
    settings_window = Toplevel(root)
    settings_window.title("Настройки")
    settings_window.geometry("400x300")
    settings_window.resizable(False, False)
    
    # Делаем окно модальным и центрируем
    settings_window.grab_set()
    settings_window.transient(root)
    center_window(settings_window)
    
    # Создаем вкладки
    notebook = ttk.Notebook(settings_window)
    
    # Вкладка аудио
    audio_frame = ttk.Frame(notebook)
    notebook.add(audio_frame, text="Аудио")
    
    # Громкость
    ttk.Label(audio_frame, text="Громкость:").pack(pady=(10, 0))
    volume_slider = ttk.Scale(audio_frame, 
                            from_=0, 
                            to=1, 
                            orient="horizontal")
    volume_slider.set(0.9)  # Значение по умолчанию
    volume_slider.pack(fill="x")
    volume_label = ttk.Label(audio_frame, 
                            text=f"Громкость: {int(current_volume*100)}%", 
                            font=('Arial', 12)
                            )
    volume_label.pack(pady=10)
    volume_slider.bind("<MouseWheel>", partial(on_mousewheel_volume,volume_slider,volume_label))


    speed_slider = ttk.Scale(audio_frame, 
                            from_=1, 
                            to=500, 
                            orient="horizontal",
                            command=partial(update_rate,volume_slider))
    
    speed_slider.set(180)
    speed_slider.pack(pady=5, padx=10, fill="x")
    speed_label = ttk.Label(audio_frame, 
                            text=f"Скорость: {int(current_rate*100)}%", 
                            font=('Arial', 12)
                            )
    speed_label.pack(pady=10)

    speed_slider.bind("<MouseWheel>", partial(on_mousewheel_rate,volume_slider,speed_label))
    # Вкладка модели
    model_frame = ttk.Frame(notebook)
    notebook.add(model_frame, text="Модель")
    
    # Выбор модели
    ttk.Label(model_frame, text="Модель нейросети:").pack(pady=(10, 0))
    models = ["GPT-4", "GPT-3.5", "Claude 3", "Llama 3", "Mixtral"]
    model_combobox = ttk.Combobox(model_frame, values=models, state="readonly")
    model_combobox.current(0)  # Выбираем первую модель по умолчанию
    model_combobox.pack(pady=5, padx=10, fill="x")
    
    notebook.pack(expand=True, fill="both", padx=5, pady=5)
    
    # Кнопки
    btn_frame = ttk.Frame(settings_window)
    btn_frame.pack(fill="x", padx=5, pady=5)
    
    ttk.Button(btn_frame, text="Сохранить", 
              command=lambda: save_settings(volume_slider.get(), 
                                            speed_slider.get(), 
                                            model_combobox.get()
                                        )
            ).pack(side="right", padx=5)
    ttk.Button(btn_frame, text="Отмена", command=settings_window.destroy).pack(side="right", padx=5)

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"+{x}+{y}")

def save_settings(volume, speed, model):
    print(f"Сохранены настройки: Громкость={volume}%, Скорость={speed}x, Модель={model}")
    root.focus_set()

def on_escape(event):
    show_settings()

# Создаем главное окно
root = Tk()
root.title("Голосовой ассистент")
root.geometry("800x600")

engine = pyttsx3.init()
current_volume = engine.getProperty('volume')
current_rate = engine.getProperty('rate')
root.bind("<Escape>", on_escape)

ttk.Button(root, text="Проверить звук",
          command=lambda: [engine.say("Тест громкости"), engine.runAndWait()]
          ).pack(pady=10)
# Основной интерфейс
ttk.Label(root, text="Голосовой ассистент", font=("Arial", 16)).pack(pady=20)
ttk.Button(root, text="Открыть настройки (Escape)", command=show_settings).pack()

root.mainloop()