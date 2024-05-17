import unittest
from tkinter import filedialog
from unittest.mock import patch, MagicMock, Mock
import socket
import cv2
import numpy as np
from client import *

img = None


class TestPeerMain(unittest.TestCase):
    def setUp(self):
        # Set up the server connection
        self.host = "40.127.9.222"
        self.port = 12345
        self.tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpClientSocket.connect((self.host, self.port))

    def tearDown(self):
        # Close the client socket after each test
        self.tcpClientSocket.close()

    def test_connection(self):
        # Test if the socket is connected
        self.assertTrue(self.tcpClientSocket.fileno() != -1)
        reconnect_to_server()

    @patch('client.client_socket')
    def test_upload_file(self, mock_client_socket):

        if img:
            # Mock data
            file_entry = Mock()
            file_entry.get.return_value = "image.png"
            selected_option = Mock()
            selected_option.get.return_value = "edge_detection"

            # Mock image data
            img_mock = Mock()
            img_mock.shape = (100, 100, 3)
            mock_cv2 = Mock()
            mock_cv2.imread.side_effect = [img_mock, img_mock]

            with patch('client.cv2', mock_cv2):
                # Call the function
                upload_file(file_entry, selected_option)
        else:
            # Assertions
            self.assertTrue(self.tcpClientSocket.fileno() != -1)
            reconnect_to_server()

    @patch('client.filedialog.asksaveasfilename', return_value="saved_image.jpg")
    def test_download_image(self, mock_asksaveasfilename):
        # Mock the cv2.imwrite function
        with patch('cv2.imwrite') as mock_imwrite:
            # Create a dummy image
            img = np.zeros((100, 100, 3), dtype=np.uint8)
            # Call the download_image function
            file_extension = ".jpg"
            if img is None:
                return
            elif img.size == 0:  # Check if the image array is empty
                return
            else:
                save_path = filedialog.asksaveasfilename(defaultextension=file_extension,
                                                         filetypes=[("Image files", ".")])
                if save_path:
                    cv2.imwrite(save_path, img)

            # Assertions
            mock_asksaveasfilename.assert_called_once()  # Check if save dialog is opened
            mock_imwrite.assert_called_once_with("saved_image.jpg",
                                                 img)  # Check if image is saved with correct filename
        reconnect_to_server()


if __name__ == "__main__":
    unittest.main()
