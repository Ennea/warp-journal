import logging
import sys

from pathlib import Path
from typing import NoReturn


def panic(message) -> NoReturn:
    logging.error(message)
    show_error_dialog(message)
    logging.info('Quitting')
    sys.exit(1)


def show_error_dialog(message):
    try:
        import tkinter
        from tkinter import ttk
    except ImportError:
        return

    root = tkinter.Tk()
    root.title('Warp Journal')
    root.minsize(300, 0)
    root.resizable(False, False)
    root.iconphoto(False, tkinter.PhotoImage(file=Path(sys.path[0]) / 'icon.png'))

    frame = ttk.Frame(root, padding=10)
    frame.pack()
    ttk.Label(frame, text=message).pack()
    ttk.Frame(frame, height=5).pack()
    ttk.Button(frame, text='Okay', command=root.destroy).pack()

    # center the window
    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry('+{}+{}'.format(int(screen_width / 2 - window_width / 2), int(screen_height / 2 - window_height / 2)))

    root.mainloop()
