import socket
import cv2
import numpy as np
from mpi4py import MPI
import logging
import time
import threading

initTime = time.time()
logging.basicConfig(filename="log.txt", filemode="w", datefmt="%H:%M:%S", level=logging.INFO)


def log(step: str):
    logging.info(f"{step}: {time.time() - initTime}")


# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def process_image_chunk(decoded_chunk, selected_option):
    if selected_option == "edge_detection":
        edges = cv2.Canny(decoded_chunk, 100, 200)
        processed_chunk = edges
    elif selected_option == "color_inversion":
        processed_chunk = cv2.bitwise_not(decoded_chunk)
    elif selected_option == "gaussian_blur":
        processed_chunk = cv2.GaussianBlur(decoded_chunk, (5, 5), 0)
    elif selected_option == "sharpen":
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        processed_chunk = cv2.filter2D(decoded_chunk, -1, kernel)
    elif selected_option == "histogram_equalization":
        if len(decoded_chunk.shape) == 2:
            processed_chunk = cv2.equalizeHist(decoded_chunk)
        else:
            img_yuv = cv2.cvtColor(decoded_chunk, cv2.COLOR_BGR2YUV)
            img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
            processed_chunk = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    elif selected_option == "adaptive_threshold":
        gray = cv2.cvtColor(decoded_chunk, cv2.COLOR_BGR2GRAY)
        processed_chunk = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    elif selected_option == "dilation":
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
        processed_chunk = cv2.dilate(decoded_chunk, kernel)
    elif selected_option == "erosion":
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
        processed_chunk = cv2.erode(decoded_chunk, kernel)
    elif selected_option == "enhance":
        lab = cv2.cvtColor(decoded_chunk, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced_image = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        kernel = np.array([[0, -0.5, 0], [-0.5, 3, -0.5], [0, -0.5, 0]])
        processed_chunk = cv2.filter2D(enhanced_image, -1, kernel)
    else:
        processed_chunk = decoded_chunk

    return processed_chunk


def handle_client(client_socket, client_address):
    print(f"Connection from {client_address} has been established.")
    log(f"Connection made")

    try:
        selected_option = client_socket.recv(1024).decode()
        log("Selected option received")
        images_no = int.from_bytes(client_socket.recv(8), byteorder="big")
        log("Number of images received")

        images = []
        for _ in range(images_no):
            rows = int.from_bytes(client_socket.recv(8), byteorder="big")
            cols = int.from_bytes(client_socket.recv(8), byteorder="big")
            bytes_no = rows * cols * 3

            raw_image = b""
            while len(raw_image) < bytes_no:
                bytes_remaining = bytes_no - len(raw_image)
                bytes_to_recv = 4096 if bytes_remaining > 4096 else bytes_remaining
                raw_image += client_socket.recv(bytes_to_recv)
            log(f"Image received")
            images.append(np.frombuffer(raw_image, dtype=np.ubyte).reshape(rows, cols, 3).astype(np.uint8))
            log(f"Image formatted")
        log(f"All images received and formatted")

        if len(images) == 1:
            img = images[0]
            chunk_size = int(np.ceil(img.shape[0] / (size - 1)))
            num_chunks = size - 1
            for i in range(1, size):
                start_idx = (i - 1) * chunk_size
                end_idx = start_idx + chunk_size if i < size - 1 else len(img)
                chunk = img[start_idx:end_idx, :]

                encoded_chunk = cv2.imencode(".jpg", chunk)[1].tobytes()
                data_to_send = [encoded_chunk, selected_option]
                comm.send(data_to_send, dest=i)
            log("Images sent to workers")

            processed_chunks = []
            for i in range(1, num_chunks + 1):
                log("Received chunk")
                processed_chunk = comm.recv(source=i)
                nparr = np.frombuffer(processed_chunk, np.uint8)
                processed_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                processed_chunks.append(processed_img)

            log("Received all chunks")

            processed_img = np.concatenate(processed_chunks)
            log("Results formatted")
            ready_img = processed_img.astype(np.ubyte).tobytes()
            log("Result Byte-d")
            client_socket.sendall(ready_img)
            log("Results sent")
        elif len(images) > 1:
            num_workers = min(len(images), size - 1)
            for i, img in enumerate(images):
                worker_rank = 1 + (i % num_workers)
                encoded_image = cv2.imencode(".jpg", img)[1].tobytes()
                data_to_send = [encoded_image, selected_option]
                log(f"sending image {i} to Node {worker_rank}")
                comm.send(data_to_send, dest=worker_rank)
            for i in range(len(images)):
                processed_chunk = comm.recv()
                log(f"Received chunk number {i}")
                nparr = np.frombuffer(processed_chunk, np.uint8)
                processed_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                ready_img = processed_img.astype(np.ubyte).tobytes()
                client_socket.sendall(ready_img)

    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
        log(f"Error handling client {client_address}: {e}")
    finally:
        client_socket.close()
        log("Connection closed")


def master_node(server_socket):
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


def worker_node():
    while True:
        chunk = comm.recv(source=0)
        chunk_data, selected_option = chunk
        nparr = np.frombuffer(chunk_data, np.uint8)
        img_ready = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        processed_chunk = process_image_chunk(img_ready, selected_option)

        encoded_processed_chunk = cv2.imencode(".jpg", processed_chunk)[1].tobytes()
        comm.send(encoded_processed_chunk, dest=0)


if __name__ == "__main__":
    print("Entered")
    if rank == 0:  # Master node
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", 12345))
        server_socket.listen(5)
        print("Server is listening...")
        master_node(server_socket)
    else:  # Worker nodes
        worker_node()
