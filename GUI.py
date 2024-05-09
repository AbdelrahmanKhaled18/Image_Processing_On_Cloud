
import queue


import client
from client import *



task_queue = queue.Queue()

root = Tk()
root.geometry("450x400")  # starting window size
root.configure(bg="#0078D4")  # GUI background color
client.create_form_elements(root)

root.mainloop()
