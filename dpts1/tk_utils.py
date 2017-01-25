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


def entry_prompt(prompt, default='', window_title=None, wrap=10, callback_template=None, root=None):
    # http://www.python-course.eu/tkinter_entry_widgets.php
    # callback_template takes (root, labelvar) and returns a lambda callback
    if root is None:
        root = tk.Tk()
    if window_title:
        root.wm_title(window_title)
    # wrap text
    prompt = prompt.split()
    row = 0
    while len(prompt) > 0:
        line = ' '.join(prompt[:wrap])
        labelvar = tk.StringVar()
        tk.Label(root, textvariable=labelvar, justify=tk.LEFT).grid(row=row)
        labelvar.set(line)
        row += 1
        del prompt[:wrap]
    
    global_handler_id = [None]
    if callback_template:
        # callback is only called once, if you want to repeatedly call it,
        # re-register within itself by 'nonlocal root; root.after(...)'
        # http://stackoverflow.com/questions/25753632/tkinter-how-to-use-after-method
        handler_id = root.after(2000, callback_template(root, labelvar, global_handler_id))
        global_handler_id[0] = handler_id

    def destroy():
        if global_handler_id[0]:
            # must cancel the specific 'after' handler
            root.after_cancel(global_handler_id[0])
        root.destroy()

    entered_text = None
    
    # action trigger when Enter key pressed on Entry text field
    def enter_key_pressed(event):
        nonlocal entered_text
        entered_text = event.widget.get()
        print('ENTER key pressed:', entered_text)
        destroy()
        
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
        destroy()

    # kwarg: sticky=tk.W to move the button to left
    tk.Button(root, text='OK', command=ok_button_pressed).grid(row=row, column=0)
    tk.Button(root, text='Cancel', command=destroy).grid(row=row, column=1, pady=15)
    root.mainloop()
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
