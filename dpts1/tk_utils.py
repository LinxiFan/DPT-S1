"""
Tkinter utils for interactive prompt
"""
import tkinter as tk
from tkinter import messagebox

def get_root(center=True):
    # return Tkinter root panel that always stays on the front
    # http://stackoverflow.com/questions/3375227/how-to-give-tkinter-file-dialog-focus
    # WARNING: doesn't work well 
    root = tk.Tk()
    # Make it almost invisible - no decorations, 0 size, top left corner.
    root.overrideredirect(True)
    if center:
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        w, h = w // 2, h // 2
    else:
        w, h = 0, 0
    root.geometry('0x0+{}+{}'.format(w, h))
    # Show window again and lift it to top so it can get focus,
    # otherwise dialogs will end up behind the terminal.
    root.deiconify()
    root.lift()
    root.focus_force()
    return root


def entry_prompt(prompt, default='', wrap=10, root=None):
    # http://www.python-course.eu/tkinter_entry_widgets.php
    if root is None:
        root = tk.Tk()
    # wrap text
    prompt = prompt.split()
    row = 0
    while len(prompt) > 0:
        line = ' '.join(prompt[:wrap])
        tk.Label(root, text=line, justify=tk.LEFT).grid(row=row)
        row += 1
        del prompt[:wrap]
    
    entered_text = None
    
    # action trigger when Enter key pressed on Entry text field
    def enter_key_pressed(event):
        nonlocal entered_text
        entered_text = event.widget.get()
        print('ENTER key pressed:', entered_text)
        root.destroy()
        
    entry = tk.Entry(root)
    entry.insert(0, default)
    entry.bind('<Return>', enter_key_pressed)
    entry.grid(row=row)
    row += 1
    
    def ok_button_pressed():
        nonlocal entered_text
        entered_text = entry.get()
        print('OK button pressed:', entered_text)
        entry.delete(0, tk.END) # unnecessary
        root.destroy()

    # kwarg: sticky=tk.W to move the button to left
    tk.Button(root, text='OK', command=ok_button_pressed).grid(row=row, column=0)
    tk.Button(root, text='Cancel', command=root.destroy).grid(row=row, column=1, pady=15)
    tk.mainloop()
    return entered_text


def yesno_prompt(prompt, title='', root=None):
    if root is None:
        root = tk.Tk()
    elif root == 'corner':
        root = get_root(center=False)
    elif root == 'center':
        root = get_root(center=True)
    
    return messagebox.askyesno(title, prompt, parent=root)
    

if __name__ == '__main__':
    PROMPT = 'this is a very looooong text ' * 8
    ans = entry_prompt(PROMPT, default='hello there!')
    print(ans)
    ans = yesno_prompt(PROMPT, title='YesNo1', root='corner')
    print(ans)
    ans = yesno_prompt(PROMPT, title='YesNo2', root='center')
    print(ans)