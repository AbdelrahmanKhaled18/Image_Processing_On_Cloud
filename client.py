from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showinfo
import socket

import cv2
import numpy as np

SERVER_HOST = '40.127.9.222'
SERVER_PORT = 12345

img = None
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
    upload_button = Button(root, text="Upload File", command=lambda: upload_file(file_entry,selected_option),
                           background="white",
                           highlightbackground="white", highlightcolor="white")
    download_button = Button(root, text="Download Image", command=lambda: download_image(img), background="white",
                             highlightbackground="white",
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
    global img
    file_paths = file_entry.get().split('\n')
    selected_option_value = selected_option.get()

    if file_paths:

        try:
            client_socket.sendall(selected_option_value.encode())
            for file_path in file_paths:
                with open(file_path, 'rb') as f:
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        client_socket.sendall(data)
                    client_socket.sendall(b'SPLITER')

            client_socket.shutdown(socket.SHUT_WR)
            print('Sent full data')
            full_result = b''
            while True:
                result = client_socket.recv(1024)
                if not result:
                    break
                full_result += result

            images_split = full_result.split(b"END_OF_IMAGE")
            for img_data in images_split:
                if img_data:
                    nparr = np.frombuffer(img_data, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if img is not None:
                        cv2.imshow('Processed Image', img)
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()
                        showinfo("Success", "Files have been uploaded and displayed.")
                    else:
                        showinfo("Error", "Failed to decode image.")

        except FileNotFoundError as e:
            showinfo("Error", f"File not found: {e}")
        except OSError as e:
            if e.errno == 10058 or e.errno == 10057 or e.errno == 10053:
                showinfo("Error", "Reconnecting to the Server...\n You can upload now!")
                reconnect_to_server()
            else:
                showinfo("Error", f"An error occurred: {e}. Please reconnect to the server.")
                reconnect_to_server()
        except BrokenPipeError as e:
            reconnect_to_server()
    else:
        showinfo("Error", "Please select one or more files to upload.")


def download_image(img):
    """
    Download the processed image.
    """
    file_extension = ".jpg"
    if img is None:
        showinfo("Error", "Please select an image to download.")
        return
    elif img.size == 0:  # Check if the image array is empty
        showinfo("Error", "The image array is empty.")
        return
    else:
        save_path = filedialog.asksaveasfilename(defaultextension=file_extension, filetypes=[("Image files", ".")])
        if save_path:
            cv2.imwrite(save_path, img)
            showinfo("Success", "Image has been downloaded.")
        else:
            showinfo("Error", "No save path selected.")




def reconnect_to_server():
    print("Trying to reconnect...")
    global client_socket

    try:
        # Close the socket if it's still open
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        print("Closed existing connection")
    except Exception as e:
        print(f"Error closing existing connection: {e}")

    try:
        # Reconnect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print("Reconnected to the server")
    except Exception as e:
        print(f"Error reconnecting to server: {e}")