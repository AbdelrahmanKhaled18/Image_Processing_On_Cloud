# Application Preview 
This application is used for making image processing operatiions like edge detection, color inversion or morphological operations on some some images using cloud service provider (Azure). 
we have the client file that handles the GUI and sending and recving to and from the server which is the cloud enviroment. 
in Azure, we have 3 VMs 1 MasterNode and 2 WorkerNodes
so what happens is when we run the server and the client The GUI appears , the user choose a pic to upload and an operation to be done on the image.
then the images go to the masterNode using sockets and then the masternode split the images into chunks and send them using MPI to be processed on the WorkerNodes
After the processing is done, the MasterNode recives the processed chunks from the WorkerNodes and send them back to the client be displayed and the client can download the image if he wanted 

# Installations 
## Packges installation 
* openCV: it is used for image processing 
* numpy: it is used for data manipulation and converting the images into something can be processed and sent using sockets 
* socket: used for connection between client and server 
* mpi4py: used for parallell processing 
* tkinter: used for the GUI

## Cloud enviroment setup
* you login to your azure account
* you create VMs (make sure to be the same Vnet for easier communication between the VMs )
* install the Packages mentioned above in your VMs 
* configure the hosts file in every VM to have the IP address of the others VMs in it 
* put the server file in all the VMs 


# Running The Application 
* put the GUI file and the client file into your host machine 
* in the client file, put the IP address of the master node to conect them using sockets
* in your VMs put the server file 
* run your MPI program using mpixexc 
* choose photo to upload and an operation to do 
* press the Upload button

# Youtube Video Demo
* https://youtu.be/7I3FAsmqmIs




