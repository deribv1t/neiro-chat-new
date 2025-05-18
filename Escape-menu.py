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
    if event.delta > 0:
        new_volume = min(current + 0.02, 1.0)
    else:
        new_volume = max(current - 0.02, 0.0)
    slider.set(new_volume)
    update_volume(volume_label,new_volume)


def update_rate(speed_label,value):
    rate = float(value)
    engine.setProperty('rate', rate)
    speed_label.config(text=f"Скорость: {round(rate/200,2)}x")

def on_mousewheel_rate(slider,speed_label,event):
    current = slider.get()
    if event.delta > 0:
        new_rate = min(current + 5, 500)
    else:
        new_rate = max(current - 5, 1)
    slider.set(new_rate)
    update_rate(speed_label,new_rate)


def show_settings():
    global count
    count += 1
    if count > 1:
        return
    
    settings_window = Toplevel(root)
    settings_window.title("Настройки")
    settings_window.geometry("400x300")
    settings_window.resizable(False, False)
    settings_window.protocol("WM_DELETE_WINDOW",partial(settings_close,settings_window))
    settings_window.grab_set()
    settings_window.transient(root)
    center_window(settings_window)
    
    notebook = ttk.Notebook(settings_window)
    
    audio_frame = ttk.Frame(notebook)
    notebook.add(audio_frame, text="Аудио")


    volume_label = ttk.Label(audio_frame,
                            text=f"Громкость: {int(current_volume*100)}%", 
                            font=('Arial', 13)
                            )
    volume_label.pack()

    volume_slider = ttk.Scale(audio_frame, 
                            from_=0, 
                            to=1, 
                            orient="horizontal",
                            command=partial(update_volume,volume_label)
                            )
    volume_slider.set(current_volume)
    volume_slider.pack(fill="x")

    volume_slider.bind("<MouseWheel>", partial(on_mousewheel_volume,volume_slider,volume_label))

    speed_label = ttk.Label(audio_frame, 
                            text=f"Скорость: {int(current_rate)}x", 
                            font=('Arial', 13)
                        )
    speed_label.pack()

    speed_slider = ttk.Scale(audio_frame, 
                            from_=1, 
                            to=500, 
                            orient="horizontal",
                            command=partial(update_rate,speed_label)
                            )
    speed_slider.set(current_rate)
    speed_slider.pack(fill="x")
    
    speed_slider.bind("<MouseWheel>", partial(on_mousewheel_rate,speed_slider,speed_label))



    model_frame = ttk.Frame(notebook)
    notebook.add(model_frame, text="Модель")
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
    ttk.Button(btn_frame, text="Отмена", command=partial(settings_close,settings_window)).pack(side="right", padx=5)

def settings_close(window,event=None):
    global count
    window.destroy()
    count -= 1

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


root = Tk()
root.title("Голосовой ассистент")
root.geometry("800x600")

engine = pyttsx3.init()
current_volume = engine.getProperty('volume')
current_rate = engine.getProperty('rate')

root.bind("<Escape>", on_escape)
count = 0

ttk.Button(root, text="Проверить звук",
          command=lambda: [engine.say("Тест громкости")]
          ).pack(pady=10)

ttk.Button(root, text="Проверить звук",
          command=lambda: [engine.say("Тест громкости"), engine.runAndWait()]
          ).pack(pady=10)

# Основной интерфейс
ttk.Label(root, text="Голосовой ассистент", font=("Arial", 16)).pack(pady=20)
ttk.Button(root, text="Открыть настройки (Escape)", command=show_settings).pack()

root.mainloop()