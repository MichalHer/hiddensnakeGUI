import tkinter as tk
from tkinter import *
from tkinter import Tk, ttk, IntVar, StringVar, messagebox
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfile

from hiddensnakegui.encryption_algorithms import DESEncrypterCBC
from hiddensnakegui.hiding_algorithms import LSBHider
from hiddensnakegui.utils import exit

from hiddensnake.carrier_files import WavFile, PngFile
from hiddensnake.abstract_classes import AbstractFile
from hiddensnake import HiddenSnake

from pathlib import Path
import os
import threading
import time
from functools import partial

WAITING_STRINGS = [
    "    Please wait    ",
    "  . Please wait .  ",
    " .. Please wait .. ",
    "... Please wait ...",
]

done = False

class App(Tk):

    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)
        # component_classes
        self.carrier_files_classes = {
            ".wav":WavFile,
            ".png":PngFile
        }
        self.hiding_algorithm = LSBHider()
        self.encryption_algorithm = DESEncrypterCBC()
        
        # global variables
        self.content_radio_value = IntVar(self, value=0)
        self.hidden_file_path = StringVar(self)
        self.displayed_hint = StringVar(master=self, value="")
        
        # main window settings
        self.title("HiddenSnake")
        self.geometry("500x400")
        
        self.grid()
        self.columnconfigure(0,weight=50)
        self.columnconfigure(1,weight=1)
        self.rowconfigure(100,weight=50)

        # app menu
        self.menubar = tk.Menu(self)
        self.settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.about_menu = tk.Menu(self.menubar, tearoff=0)
        self.config(menu=self.menubar)
        self.menubar.add_cascade(label="HiddenSnake", menu=self.settings_menu)
        self.menubar.add_cascade(label="About", menu=self.about_menu)

        self.settings_menu.add_command(label="Settings", command=self.show_app_config_window)
        self.settings_menu.add_command(label="Exit", command=partial(exit, top_pointer=self))

        # window controls
        self.carrier_label = ttk.Label(self, text="Carrier files", justify='left').grid(column=0, row=0, sticky="we", padx=5)

        self.carrier_list = ttk.Treeview(self, column=("File path",), show='headings', height=5)
        self.carrier_list.column("# 1")
        self.carrier_list.heading("# 1", text="File path")
        self.carrier_list.grid(column=0, row=1, sticky='swe', rowspan=2, padx=5)

        self.add_carrier_btn = ttk.Button(self, text="Add", command=self.add_carrier_file).grid(column=1,row=1)
        self.add_carrier_btn = ttk.Button(self, text="Remove", command=self.remove_selected_carrier_file).grid(column=1,row=2)

        self.content_label = ttk.Label(self, text="Hidden content", justify='left').grid(column=0, row=3, sticky="we", padx=5)
        
        self.file_radio = ttk.Radiobutton(self, text="file", value=0, variable=self.content_radio_value).grid(padx=5, column=0, row=4, sticky="w")
        self.message_radio = ttk.Radiobutton(self, text="message", value=1, variable=self.content_radio_value).grid(padx=5, column=0, row=5, sticky="w")
        
        self.content_path = ttk.Entry(self, textvariable=self.hidden_file_path, ).grid(column=0, row=6, sticky='wes', padx=5)
        self.add_carrier_btn = ttk.Button(self, text="Find", command=self.select_hidden_file).grid(column=1,row=6)

        # bottom frame
        self.test_frame = ttk.Frame(self, padding=50)
        self.test_frame.grid(column=0, columnspan=2, row=100, sticky='s')
        self.test_frame.rev_btn = ttk.Button(self.test_frame, text="Reveal", command=self.reveal).grid(column=0,row=0)
        self.test_frame.hid_btn = ttk.Button(self.test_frame, text="Hide", command=self.hide).grid(column=1,row=0)

        self.text = ttk.Label(self, textvariable=self.displayed_hint, justify='center').grid(column=0, row=100, sticky='s', columnspan=2)

    def add_carrier_file(self):
        filetypes = []
        for __, parser in self.carrier_files_classes.items():
            filetypes.append(("",f"*{parser.get_file_extension()}"))
        filename = askopenfilename(filetypes=filetypes)
        self.carrier_list.insert('', 'end', text=filename, values=(filename,))

    def remove_selected_carrier_file(self):
        selected = self.carrier_list.focus()
        self.carrier_list.delete(selected)

    def select_hidden_file(self):
        if self.content_radio_value.get() == 1:
            mb = messagebox.Message()
            mb.show(title="Type message", message="Just type a message here.")
        else:
            self.hidden_file_path.set(askopenfilename(filetypes=(("any",'*.*'),)))

    def get_hidden_snake(self) -> HiddenSnake:
        # setting up the encrypter
        self.encryption_algorithm.display_password_request()

        # initializing hidden snake
        hs = HiddenSnake()
        hs.register_hider(self.hiding_algorithm)
        hs.register_encrypter(self.encryption_algorithm)

        return hs
    
    def get_carrier(self, path):
        carrier_file = self.carrier_files_classes[Path(path).suffix]()
        carrier_file.from_file(path)
        return carrier_file
    
    def show_please_wait(self):
        thread = threading.Thread(target=self.wait)
        thread.start()
        
    def wait(self):
        global done
        while not done:
            for t in WAITING_STRINGS:
                self.displayed_hint.set(t)
                time.sleep(0.5)
        self.displayed_hint.set("")
        done=False

    def hide(self):
        # getting hiddensnake
        hs = self.get_hidden_snake()
        t = threading.Thread(target=self.run_hiding, args=(hs,))
        t.start()
        self.show_please_wait()
    
    def run_hiding(self, hs):
        # hidden content registering
        if self.content_radio_value.get() == 1:
            hidden_content = self.hidden_file_path.get()
            hidden_content = bytearray(hidden_content, encoding='utf-8')
            file_ext = "plaintext"
        else:
            file_path = self.hidden_file_path.get()
            with open(file_path, 'rb') as file:
                hidden_content = bytearray(file.read())
                file_ext = Path(file_path).suffix

        hs.register_hidden_bytes(hidden_content, file_ext)

        # registering carrier files
        for x in self.carrier_list.get_children():
            item = self.carrier_list.item(x)
            carrier_file_path = item.get('values')[0]
            hs.register_carrier_file(self.get_carrier(carrier_file_path))

        target_folder = askdirectory()

        if hs.can_hide(file_ext):
            files = hs.hide()
            for i, f in enumerate(files):
                f.save_file(os.path.join(target_folder, f'file_with_hidden_message_{i}{f.get_file_extension()}'))
            mb = messagebox.Message()
            mb.show(title="Steganograms created", message="Steganograms created.")

        else:
            mb = messagebox.Message()
            mb.show(title="Carrier files capacity", message="Carrier files capacity is too low.")
        
        global done
        done = True
        

    def reveal(self):
        # print("getting hiddensnake")
        hs = self.get_hidden_snake()
        t = threading.Thread(target=self.run_reveal, args=(hs,))
        t.start()
        self.show_please_wait()

    def run_reveal(self, hs):
        # print("registering carrier files")
        for x in self.carrier_list.get_children():
            item = self.carrier_list.item(x)
            carrier_file_path = item.get('values')[0]
            hs.register_carrier_file(self.get_carrier(carrier_file_path))

        # print("Revealing content")
        global done
        try:
            revealed_bytes, file_ext = hs.reveal()
        except:
            done = True
            mb = messagebox.Message()
            mb.show(title="Revealing error", message="Wrong password or no content.", icon=messagebox.ERROR)
            return
        
        done = True

        # print("Saving/Displaying")
        if file_ext[0] == ".":
            file = asksaveasfile(filetypes=(("",file_ext),("any","*.*")), mode='wb', defaultextension=file_ext)
            if file is None:
                return
            file.write(revealed_bytes)
            file.close()
        else:
            mb = messagebox.Message()
            mb.show(title="Revealed message", message=f'"{revealed_bytes.decode()}"')
    
    def show_app_config_window(self):
        acw = AppConfigWindow(self)
        acw.geometry("800x600")
        acw.title("Settings")

class AppConfigWindow(tk.Toplevel):
    def __init__(self, master: Misc | None = None) -> None:
        super().__init__(master)
        self.master = master
        self.grid()
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=5)
        self.rowconfigure(0,weight=100)
        
        self.tree_menu = ttk.Treeview(self)

        components_pos = self.tree_menu.insert('', tk.END, text="components", iid="comp", open=True)
        self.tree_menu.insert(components_pos, tk.END, text="hiding algorithms", iid="ha", tags=('component'))
        self.tree_menu.insert(components_pos, tk.END, text="encryption algorithms", iid="ea", tags=('component'))
        self.tree_menu.insert(components_pos, tk.END, text="carrier file parsers", iid="cf", tags=('component'))

        self.tree_menu.tag_bind("component", "<<TreeviewSelect>>", self.change_frame)
        self.tree_menu.grid(column=0,row=0, sticky="wnes", padx=5)

        self.settings_frame = self.get_file_parsers_frame()
        self.settings_frame.grid(column=1, row=0, sticky="wnes", padx=5)

    def change_frame(self, event):
        selection = self.tree_menu.selection()
        match selection[0]:
            case 'ha': self.settings_frame = self.get_hiding_algorithms_frame().grid(column=1, row=0, sticky="wnes", padx=5)
            case 'ea': self.settings_frame = self.get_encryption_algorithms_frame().grid(column=1, row=0, sticky="wnes", padx=5)
            case 'cf': self.settings_frame = self.get_file_parsers_frame().grid(column=1, row=0, sticky="wnes", padx=5)

    def get_hiding_algorithms_frame(self):
        frame = ttk.Frame(self, padding=0, border=1)

        hiding_algorithm_label = ttk.Label(frame,text=f"used hiding algorithm: {self.master.hiding_algorithm}", justify='left').grid(column=1, row=0, sticky="we", padx=5)
        load_hiding_algorithm_from_file = ttk.Button(frame,
                                                    text="Change"). grid(column=2, row=0, sticky="n", padx=5)
        hiding_algorithm_config_button = ttk.Button(frame, 
                                                    text="Configure", 
                                                    command=partial(self.master.hiding_algorithm.display_config_window,
                                                    master=self)).grid(column=3, row=0, sticky="n", padx=5)
        return frame
    
    def get_file_parsers_frame(self):
        frame = ttk.Frame(self, padding=0, border=1)
        frame.columnconfigure(0,weight=1)
        parsers_list_label = ttk.Label(frame, text="File parsers list:").grid(column=0, row=0, sticky='we')
        parsers_list = ttk.Treeview(frame)
        for k,v in self.master.carrier_files_classes.items():
            print(k)
            parsers_list.insert('', tk.END, text=k, values=(k,))

        parsers_list.grid(column=0, row=1, sticky="wse")
        add_button = ttk.Button(frame, text="Add").grid(column=0, row=2, sticky='e')
        
        return frame
    
    def get_encryption_algorithms_frame(self):
        frame = ttk.Frame(self, padding=0, border=1)
        return frame


if __name__ == "__main__":
    app = App()
    app.mainloop()