import os
import queue
import shutil
import threading
from mpi4py import MPI
import cv2
from tkinter import Tk, Label, Button, filedialog, StringVar, OptionMenu
from tkinter.ttk import Entry
from tkinter.messagebox import showinfo
from werkzeug.utils import secure_filename

import client
from client import *

""""
def download_image():
   
    file_path = self.file_entry.get()
    if not file_path:
        showinfo("Error", "Please select an image to download.")
        return
    image_processed = self.process_image(file_path, self.selected_option.get())
    _, file_extension = os.path.splitext(file_path)
    save_path = filedialog.asksaveasfilename(defaultextension=file_extension, filetypes=[("Image files", ".")])
    cv2.imwrite(save_path, image_processed)
    showinfo("Success", "Image has been downloaded.")
    """

task_queue = queue.Queue()

root = Tk()
root.geometry("450x400")  # starting window size
root.configure(bg="#0078D4")  # GUI background color
client.create_form_elements(root)

root.mainloop()
