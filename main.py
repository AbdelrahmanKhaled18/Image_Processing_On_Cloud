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


class WorkerThread(threading.Thread):
    def __init__(self, task_queue, root):
        """
        Initialize the worker thread.

        Args:
        - task_queue: The queue for tasks.
        - root: The Tkinter root window.
        """
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.root = root
        self.root.title("File Uploader")
        self.secret_key = 'supersecretkey'
        self.upload_folder = 'static'
        self.create_form_elements()
        self.daemon = True

    def create_form_elements(self):
        """
        Create form elements such as labels, buttons, and entry fields.
        """
        self.file_label = Label(self.root, text="File:", background="#0078D4", font="bold")
        self.file_entry = Entry(self.root, state='readonly')
        self.file_button = Button(self.root, text="Browse", command=self.browse_file, background="white",
                                  highlightbackground="white", highlightcolor="white")
        self.upload_button = Button(self.root, text="Upload File", command=self.upload_file, background="white",
                                    highlightbackground="white", highlightcolor="white")
        self.download_button = Button(self.root, text="Download Image", command=self.download_image, background="white",
                                      highlightbackground="white", highlightcolor="white")
        self.options = ["edge_detection", "color_inversion"]
        self.selected_option = StringVar()
        self.selected_option.set(self.options[0])
        self.option_menu = OptionMenu(self.root, self.selected_option, *self.options)
        self.arrange_form_elements()

    def arrange_form_elements(self):
        """
        Arrange the form elements within the GUI window.
        """
        self.file_label.place(x=110, y=144)
        self.file_entry.place(x=160, y=150)
        self.file_button.place(x=287, y=147)
        self.upload_button.place(x=212, y=200)
        self.option_menu.place(x=185, y=258)
        self.download_button.place(x=197, y=230)

    def browse_file(self):
        """
        Open a file dialog to browse and select a file.
        """
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.file_entry.config(state='normal')
            self.file_entry.delete(0, 'end')
            self.file_entry.insert(0, '\n'.join(file_paths))
            self.file_entry.config(state='readonly')

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break
            image, operation = task
            result = self.process_image(image, operation)
            self.send_result(result)

    def process_image(self, image, operation):
        """
        Process the selected image based on the chosen operation.

        Args:
        - image: The path to the image file.
        - operation: The image processing operation to apply.

        Returns:
        The processed image.
        """
        img = cv2.imread(image, cv2.IMREAD_COLOR)
        operation_functions = {
            'edge_detection': lambda img: cv2.Canny(img, 100, 200),
            'color_inversion': lambda img: cv2.bitwise_not(img)
        }
        if operation in operation_functions:
            result = operation_functions[operation](img)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        return result

    """
    os.path.basename(file_path) =>
    This function returns the name of the file from the path of the file for example 
    path/example/file.txt the function returns file.txt
    
    os.path.join(os.getcwd(), self.upload_folder, secure_filename(filename)) =>
    This function joins the paths to form the current path of the image
    os.getcwd() This is for getting the current working directory
    self.upload_folder is the folder name and it is initialized in the class constructor
    secure_filename() is for security of the file
    
    shutil.copyfile(file_path, upload_path) =>
    This function copies the file from its directory to its new directory,and not moving it
     
    cv2.imshow('Image', image_processed) =>
    This function is used to show the image on the screen
    """

    def upload_file(self):
        """
        Upload the selected file to the specified upload folder.
        """
        file_paths = self.file_entry.get().split('\n')
        if file_paths:
            try:
                for file_path in file_paths:
                    filename = os.path.basename(file_path)
                    upload_path = os.path.join(os.getcwd(), self.upload_folder, secure_filename(filename))
                    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                    shutil.copyfile(file_path, upload_path)
                    image_processed = self.process_image(upload_path, self.selected_option.get())
                    # Display processed image in a new window
                    self.display_image(image_processed)

                showinfo("Success", "Files have been uploaded.")
            except Exception as e:
                showinfo("Error", f"An error occurred: {e}")
        else:
            showinfo("Error", "Please select one or more files to upload.")

    def display_image(self, image):
        """
        Display the processed image in a new window.
        """
        cv2.imshow('Processed Image', image)
        cv2.waitKey(0)  # Wait until a key is pressed
        cv2.destroyAllWindows()

    """
    _, file_extension = os.path.splitext(file_path) =>
    this line of code extract the file extension so that it can save the downloaded file with the same extension. 
    os.path.splitext(file_path) splits the file name into 2 parts and returns a tuple of the file name 
    and its extension, here the file name is ignored using _ 
    
    filedialog.asksaveasfilename(defaultextension=file_extension, filetypes=[("Image files", ".")]) => 
    this line opens the files window to choose the place to save the image, the argument defaultextension 
    sets the default extension of any saved file to the same extension as the uploaded file, and filetypes
    specifies the types of files that can be saved, in this case, it allows any type of image file. 
    then the path of the file the user choosed will be returned to save_path
    
    cv2.imwrite(save_path, image_processed) =>
    this function writes the path (save_path) to the processed image
    """

    def download_image(self):
        """
        Download the processed image.
        """
        file_path = self.file_entry.get()
        if not file_path:
            showinfo("Error", "Please select an image to download.")
            return
        image_processed = self.process_image(file_path, self.selected_option.get())
        _, file_extension = os.path.splitext(file_path)
        save_path = filedialog.asksaveasfilename(defaultextension=file_extension, filetypes=[("Image files", ".")])
        cv2.imwrite(save_path, image_processed)
        showinfo("Success", "Image has been downloaded.")

    # Example of adding tasks to the queue
    def creat_queue(self):
        file_path = self.file_entry.get()
        image_processed = self.process_image(file_path, self.selected_option.get())
        self.task_queue.put((image_processed, self.selected_option))  # ana hna 7tet self. zyada.

    def send_result(self, result):
        # Send the result to the master node
        self.comm.send(result, dest=0)


task_queue = queue.Queue()

if __name__ == "__main__":
    root = Tk()
    root.geometry("450x400")  # starting window size
    root.configure(bg="#0078D4")  # GUI background color
    num_processes = MPI.COMM_WORLD.Get_size()
    if num_processes <= 1:
        print("No MPI processes detected. Starting one WorkerThread.")
        WorkerThread(task_queue, root).start()
    else:
        print(f"{num_processes} MPI processes detected.")
        for i in range(num_processes - 1):
            WorkerThread(task_queue, root).start()  # Pass 'root' argument here

    root.mainloop()
