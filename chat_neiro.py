from tkinter import *
from tkinter import ttk
from tkinter import font
from functools import partial
from llama_cpp import Llama
import threading
import pyttsx3
import os

def change_action(event=None):
    if btn["text"] == '✅':
        textEntry(event)
        return
    
    txt = entry.get("1.0", "end-1c")
    txt = txt[0:-1]
    if txt == '':
        entry.delete("1.0", "end")
        
def update_scrollregion(event):
    scroll_track(event)
    bbox = canvas.bbox("all")
    canvas.configure(scrollregion=(bbox[0], bbox[1], bbox[2], bbox[3] + 20))
    canvas.itemconfig(canvas.find_withtag("all"), width=event.width)
    update_scroll()

def scroll_track(event=None):
    global user_scrolled_up
    if canvas.yview()[1] <= 0.99:
        user_scrolled_up = True
    else:
        user_scrolled_up = False

def update_scroll():
    global user_scrolled_up
    if not user_scrolled_up:
        canvas.yview_moveto(1)
        
def copy_text(label,event=None):
    root.clipboard_clear()
    root.clipboard_append(label["text"])
    root.update()

def show_menu(label,event):
    menu = Menu(root, tearoff=0)
    menu.add_command(label="Копировать", command=partial(copy_text,label))
    menu.add_command(label="Изменить", command=partial(replace_text,label))
    menu.post(event.x_root, event.y_root)

def show_menu_spec(label,event):
    menu = Menu(root, tearoff=0)
    menu.add_command(label="Копировать", command=partial(copy_text,label))
    menu.add_command(label="Озвучить", command=lambda:threading.Thread(target=sound, args=(label,)).start())
    menu.post(event.x_root, event.y_root)

def sound(label):
    engine = pyttsx3.init()
    voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0"
    engine.setProperty('voice', voice_id)

    engine.setProperty('rate', 180)
    engine.setProperty('volume', 0.9)
    engine.setProperty('pitch', 200)

    engine.say(label["text"])
    engine.runAndWait()

def replace_label(label,event=None):
    text = entry.get("1.0", "end-1c")
    label["text"] = text
    entry.delete("1.0", END)

    root.unbind("<Return>")
    root.bind("<Return>",change_action)
    btn.config(text='✅',
            command=textEntry
            )
    

def replace_text(label,event=None):
    global generate
    if generate:
        return
    
    copy_text(label)
    text = root.clipboard_get()
    entry.delete("1.0", END)
    entry.insert("1.0",text)

    root.bind('<Return>',partial(replace_label,label))
    btn.config(text='✎',
            command=partial(replace_label,label)
            )

def insert_newline(event):
    entry.insert("insert", "\n")
    return "break"

def updatesize(event=None):
    style.configure("TLabel",
                    wraplength=root.winfo_width()*0.8
                )

def stop_generating():
    global stop_generation
    stop_generation = True

def return_neiro(text):
    global llm
    global messages
    global stop_generation
    global generate

    generate = True
    messages.append({"role":"user",
                    "content":text
                    })
    
    stream = llm.create_chat_completion(
    messages,
    stream=True
    )

    btn.config(text='◼',
               command=stop_generating
            )
    
    frame = ttk.Frame(inner_frame)
    label = ttk.Label(frame,text="""""",background='#2b5378',justify="left",font=('Open Sans',12))

    frame.pack(fill=X,pady=8,anchor='sw')
    label.pack(side=BOTTOM,anchor='sw')

    for chunk in stream:
        if stop_generation:
            break
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:
            html = delta["content"]
            label["text"] += html

            if '```' in label["text"]:
                if ('```py' in label["text"]):
                    label["text"] = label["text"].replace('```python\n','')
                    label["font"] = ('Consolas',11)

                elif ('```css' in label["text"]):
                    label["text"] = label["text"].replace('```css\n','')
                    label["font"] = ('Consolas',11)

                elif ('```pascal' in label["text"]):
                    label["text"] = label["text"].replace('```pascal\n','')
                    label["font"] = ('Consolas',11)

                elif ('```javascript' in label["text"]):
                    label["text"] = label["text"].replace('```javascript\n','')
                    label["font"] = ('Consolas',11)

                elif ('```cpp' in label["text"]):
                    label["text"] = label["text"].replace('```cpp\n','')
                    label["font"] = ('Consolas',11)

                elif('```php' in label["text"]):
                    label["text"] = label["text"].replace('```php\n','')
                    label["font"] = ('Consolas',11)

                
    label["text"] = label["text"].replace('\n```\n','')
    label.bind("<Button-3>", partial(show_menu_spec,label))

    if stop_generation:
        messages.append({"role":"assistent", 
                        "content":""
                        })
    else:
        messages.append({"role":"assistent", 
                        "content":label["text"]
                        })
        
    stop_generation = False
    generate = False
    btn.config(text='✅',
                command=textEntry
                )

def message(pos,txt):
    global user_scrolled_up
    if txt == '' or txt ==' ':
        return
    
    frame = ttk.Frame(inner_frame)
    label = ttk.Label(frame,text=txt,style="TLabel",compound="center")

    label.bind("<Button-3>", partial(show_menu,label))

    frame.pack(fill=X,pady=8,anchor=pos)
    label.pack(side=BOTTOM,anchor=pos)

    user_scrolled_up = False
    update_scroll()

def textEntry(event=None):
    txt = entry.get("1.0", "end-1c")
    if event != None:
        txt = txt[0:-1]
        if txt == '':
            entry.delete("1.0", "end")
            return
    
    entry.delete("1.0", "end")
    entry["height"] = 1
    message('se',txt)
    thread = threading.Thread(target=return_neiro, args=(txt,))
    thread.start()
    return


root = Tk()
root.geometry("900x700")
root.config(bg='#072b3d')
root.minsize(200, 400)
root.title("Chat")

root.bind('<Return>',change_action)
root.bind('<Configure>',updatesize)
root.bind("<Control-Return>", insert_newline)

user_scrolled_up = False


filepath = os.path.join(os.path.dirname(__file__), "Model/gemma-3-1b-it-Q8_0.gguf")
llm = Llama(
    model_path=filepath,
    n_ctx=2048,
    n_threads=8,
    verbose=False,
    temperature=0.7
    )

messages = [
    {"role": "system", 
    "content": "Ты помощник разработчика, пиши код аккуратно без комментариев,без функций, думай на русском языке,\
    отвечай без кода если тебя не просили написать код"}
    ]
stop_generation = False


style = ttk.Style()

style.configure("TLabel",
                foreground="white",
                font=('Open Sans',12),
                background='#8f4bb0',
                padding=8,
                border=0,
                wraplength=720)

style.configure("TFrame",
                background='#072b3d')

style.configure("Bottom.TFrame",
                background='#17212B')
# style.configure("TButton",background='#000000',foreground="white",font=('Open Sans',13),border=4)

canvas = Canvas(root,
                bg='#072b3d',
                borderwidth=0,
                highlightthickness=0,
                width=900
                )

scrollbar = ttk.Scrollbar(canvas, orient="vertical", command=canvas.yview)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(fill="both",expand=True)

inner_frame = ttk.Frame(canvas)

canvas.create_window((0, 0), window=inner_frame, anchor="nw", width=canvas.winfo_width())

inner_frame.bind("<Configure>", update_scrollregion)
canvas.bind("<Configure>", update_scrollregion)

def handle_mousewheel(event):
    if event.widget == entry:
        entry.yview_scroll(int(-event.delta/60), "units")
    else:
        canvas.yview_scroll(int(-event.delta/60), "units")

root.bind_all("<MouseWheel>", handle_mousewheel)

bot_frame = ttk.Frame(root,
                      style="Bottom.TFrame"
                    )
bot_frame.pack(side=BOTTOM,fill=X)

btn = Button(bot_frame,
            text='✅', 
            command=textEntry,
            background='#17212B',
            activebackground='#17212B',
            activeforeground="#27a7e7",
            foreground="white",
            font=('Open Sans',14), 
            height=1,
            width=5,
            border=0,
            relief=FLAT)

btn.pack(padx=(0,30),pady=(5,5),side=RIGHT)

entry = Text(
    bot_frame,
    font=('Open Sans',12),
    height=1,
    wrap=WORD,       
    padx=5,     
    pady=5,
    background='#17212B',
    foreground="white",
    insertbackground='white',
    spacing1=10,
    spacing2=10,
    border=0
)

def adjust_height(event):
    txt = entry.get("1.0", "end-1c")
    lines = txt.count('\n') + 1
    font_obj = font.Font(font=entry.cget("font"))

    width_px = entry.winfo_width()
    for line in txt.split('\n'):
        line_width = font_obj.measure(line)
        if line_width > width_px:
            lines += int(line_width / width_px)
        
    new_height = max(1, min(lines, 12))
    if entry.cget("height") != new_height:
        entry.config(height=new_height)
        
    entry.see(INSERT)
    
scroll_text = ttk.Scrollbar(entry, orient="vertical", command=entry.yview)
entry.configure(yscrollcommand=scroll_text.set)

entry.bind('<Configure>',updatesize)
entry.bind('<Configure>',adjust_height)
entry.bind('<KeyRelease>', adjust_height)
entry.pack(fill=X,expand=True,side=LEFT,padx=(5,0),pady=(5,5))


"""------------------------------------------------------------------------------------------------------"""
#Escape manu





updatesize()
root.mainloop()