from hiddensnake.hiding_algorithms import LSBHider as BaseLSB
import tkinter as tk
from tkinter import Misc
from tkinter import Tk, ttk, IntVar, StringVar, messagebox
from ..utils import exit
from functools import partial

class LSBHider(BaseLSB):
    def __init__(self) -> None:
        super().__init__()

    def display_config_window(self, master):
        cw = ConfigWindow(master_window=master, parent_object=self)
        cw.geometry("300x100")
        cw.title("LSB setings")

    def __str__(self):
        return "BasicLSBHider"

class ConfigWindow(tk.Toplevel):
    def __init__(self, parent_object: LSBHider, master_window: Misc | None = None) -> None:
        super().__init__(master_window)
        self.grid()
        self.lsb_number = StringVar(self, str(parent_object.changed_bits_number))
        self.parent_object = parent_object

        self.bits_number_label = ttk.Label(self, text="Changed bits number").grid(column=0, row=0, sticky= 'nw')
        self.bits_number_input = ttk.Combobox(self, textvariable=self.lsb_number)
        self.bits_number_input['state'] = 'readonly'
        self.bits_number_input['values'] = ('1', '2', '3', '4', '5', '6', '7', '8')
        self.bits_number_input.grid(column=1, row=0, sticky = 'ne')

        self.confirm_button = ttk.Button(self, 
                                         text="Confirm", 
                                         command=self.confirm_new_configuration
                                        ).grid(column=0, row=1)
        self.exit_button = ttk.Button(self, text="Exit", command=partial(exit, top_pointer=self)).grid(column=1, row=1)

    def confirm_new_configuration(self):
        self.parent_object.set_changed_bits_number(int(self.lsb_number.get()))
        exit(self)