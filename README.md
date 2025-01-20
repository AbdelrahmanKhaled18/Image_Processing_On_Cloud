# Image Processing on the Cloud Using Azure

This project demonstrates a cloud-based image processing application using Azure as the cloud service provider. The
system includes a client-server architecture with a GUI for user interaction, image processing operations on the server,
and distributed computing capabilities using MPI (Message Passing Interface).

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [System Architecture](#system-architecture)
4. [Workflow](#workflow)
5. [Technologies Used](#technologies-used)
6. [Setup Instructions](#setup-instructions)
7. [How to Use](#how-to-use)
8. [Image Processing Operations](#image-processing-operations)
9. [Contributing](#contributing)

---

## Overview

This project enables users to process images using various operations on a cloud-hosted server. Users can:

- Upload images through a GUI.
- Apply image transformations such as edge detection, color inversion, and more.
- Download the processed images.

The server processes images using distributed computation for scalability and efficiency.

---

## Features

- **User-Friendly GUI**: A desktop application built using Tkinter.
- **Distributed Computing**: Image processing tasks are distributed across multiple worker nodes using MPI.
- **Cloud-Based**: Server hosted on Azure to ensure accessibility and scalability.
- **Customizable Processing**: Users can select from a variety of image processing options.
- **File Upload/Download**: Easy transfer of images between the client and server.

---

## System Architecture

1. **Client**: A Python-based GUI for image upload, operation selection, and result download.
2. **Server**: Processes images using MPI to handle multiple tasks efficiently.
3. **Worker Nodes**: Distributed computing nodes handle image chunks for large-scale processing.

---

## Workflow

The project workflow involves three main components: **Client**, **Server**, and **Worker Nodes**. Here’s how they work
together:

1. **Client Side**:
    - Users interact with a GUI (built using Tkinter) to select images and choose processing options.
    - The client sends the selected operation and the images to the server via a socket connection.

2. **Server Side**:
    - The server receives the images and processing requests from the client.
    - It splits the images into smaller chunks for distributed processing, ensuring scalability.
    - The server uses MPI to distribute these chunks to available worker nodes.

3. **Worker Nodes**:
    - Each worker node processes its assigned image chunk using OpenCV-based transformations.
    - The processed chunks are sent back to the server.

4. **Result Compilation**:
    - The server collects all processed chunks, reassembles them into complete images, and sends the results back to the
      client.

5. **Client Output**:
    - The client displays the processed images to the user.
    - Users can choose to save the processed images locally.

---

## Technologies Used

- **Programming Languages**: Python
- **Libraries**:
    - `Tkinter`: GUI
    - `OpenCV`: Image processing
    - `mpi4py`: MPI for distributed computing
    - `Socket`: Network communication
- **Cloud Service**: Azure (Server hosted on Azure Virtual Machines)

---

## Setup Instructions

### Prerequisites

- Python 3.8 or later
- Azure account for cloud deployment
- MPI environment (e.g., OpenMPI or MPICH)
- Required Python libraries (`requirements.txt`)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/image-processing-cloud.git
   cd image-processing-cloud
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up the Server**:
    - Deploy the `server.py` script on an Azure Virtual Machine or any compatible cloud service.
    - Ensure the server has MPI installed and configured.

4. **Run the Server**:
   ```bash
   mpiexec -n <number_of_nodes> python server.py
   ```

5. **Run the Client**:
    - Execute `GUI.py` on the client machine:
      ```bash
      python GUI.py
      ```

---

## How to Use

1. Launch the client application.
2. Use the "Browse" button to select image files for processing.
3. Choose an image processing operation from the dropdown menu.
4. Click "Upload File" to send images to the server.
5. Wait for the server to process the images and display the results.
6. Use the "Download Image" button to save the processed images locally.

---

## Image Processing Operations

The following operations are supported:

1. **Edge Detection**: Detects edges using the Canny algorithm.
2. **Color Inversion**: Inverts the colors of the image.
3. **Gaussian Blur**: Applies a Gaussian filter for smoothing.
4. **Sharpening**: Enhances edges for a sharper look.
5. **Histogram Equalization**: Enhances image contrast.
6. **Adaptive Thresholding**: Applies adaptive thresholding for binarization.
7. **Dilation**: Expands bright areas in the image.
8. **Erosion**: Shrinks bright areas in the image.
9. **Enhance**: Combines contrast enhancement and sharpening.

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature name"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

