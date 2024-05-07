from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showinfo
import socket

import cv2
import numpy as np

SERVER_HOST = '40.127.9.222'
SERVER_PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))


def create_form_elements(root):
    """
    Create form elements such as labels, buttons, and entry fields.
    """
    file_label = Label(root, text="File:", background="#0078D4", font="bold")
    file_entry = Entry(root, state='readonly')
    file_button = Button(root, text="Browse", command=lambda: browse_file(file_entry), background="white",
                         highlightbackground="white", highlightcolor="white")
    upload_button = Button(root, text="Upload File", command=lambda: upload_file(file_entry, selected_option),
                           background="white",
                           highlightbackground="white", highlightcolor="white")
    download_button = Button(root, text="Download Image", background="white", highlightbackground="white",
                             highlightcolor="white")

    options = ["edge_detection", "color_inversion"]
    selected_option = StringVar()
    selected_option.set(options[0])
    option_menu = OptionMenu(root, selected_option, *options)
    file_label.place(x=110, y=144)
    file_entry.place(x=160, y=150)
    file_button.place(x=287, y=147)
    upload_button.place(x=212, y=200)
    option_menu.place(x=185, y=258)
    download_button.place(x=197, y=230)


def browse_file(file_entry):
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        file_entry.config(state='normal')
        file_entry.delete(0, 'end')
        file_entry.insert(0, '\n'.join(file_paths))
        file_entry.config(state='readonly')


def upload_file(file_entry, selected_option):
    file_paths = file_entry.get()
    selected_option_value = selected_option.get()
    if file_paths:
        try:
            f = open(file_paths, 'rb')
            n = f.read(1048576)
            client_socket.sendall(selected_option_value.encode())
            while n:
                client_socket.sendall(n)
                n = f.read(1048576)

            client_socket.shutdown(socket.SHUT_WR)

            print('Sent full data')
            full_result = b''
            result = client_socket.recv(1048576)

            while result:
                full_result += result
                if not result:
                    break
                result = client_socket.recv(1048576)

            nparr = np.frombuffer(full_result, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            print(nparr)
            print(img)

            # Display the processed image
            cv2.imshow('Processed Image', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            # Process the results if needed
            showinfo("Success", "Files have been uploaded.")
        except FileNotFoundError as e:
            showinfo("Error", f"File not found: {e}")
        except OSError as e:
            if e.errno == 10058:
                showinfo("Error", "Reconnecting to the Server...\n You can upload now!")
            else:
                showinfo("Error", f"An error occurred: {e}. Please reconnect to the server.")
            reconnect_to_server()

    else:
        showinfo("Error", "Please select one or more files to upload.")


def reconnect_to_server():
    global client_socket
    try:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
    except Exception as e:
        print(f"Error closing existing connection: {e}")

    # Reconnect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print("Reconnected to the server")
