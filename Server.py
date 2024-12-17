import socket
import sys
import threading
import numpy as np
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import paramiko
import time

from datetime import datetime
current_date_and_time = datetime.now()

print("The current date and time is", current_date_and_time)
LARGEFONT = ("Verdana",35)

# IP address and port to listen on
server_ip = "192.168.43.115"
server_port = 1234

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the IP address and port
server_socket.bind((server_ip, server_port))

# Listen for incoming connections
server_socket.listen(2)  # Allowing up to 2 clients

print("Door monitoring server is observing at {}:{}".format(server_ip, server_port))
print()

# Empty dictionary to store water level values for each client
door_sense_values = {}


def send_message(client_socket, message):
    client_socket.send(message.encode())


def button1_clicked(client_socket):
    message = 1
    send_message(client_socket, str(message))


def button2_clicked(client_socket):
    message = 0
    send_message(client_socket, str(message))

last_line = ""

def handle_client(client_socket, client_address):
    # Create an empty list to store values for this client
    global last_line
    door_sense_values[client_address] = []

    try:
        while True:
            # Receive data from the client
            data = client_socket.recv(1024).decode()

            with open("connection1.txt", "a") as f:
                f.write(str(current_date_and_time)+"\n")
                f.write(str(client_address) + "\n")
                f.write(data + "\n")  
            last_line  = data    
            print("****",last_line)
            # Define the remote and local file paths
            if client_address[0] == "192.168.43.152":
                username = 'sharath'  # Raspberry Pi username
                remote_file_path = '/home/sharath/Desktop/client1.jpg'
        # Destination file path on the local machine
                local_file_path = './client1_{}.jpg'.format(int(time.time()))  # Add unique identifier
       

            if client_address[0] == "192.168.43.44":
                username = 'pi'  # Raspberry Pi username
                remote_file_path = '/home/pi/Desktop/client2.jpg'
                local_file_path = './client_2_{}.jpeg'.format(int(time.time()))  # Add unique identifier
       
            # Create an SSH client
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the Raspberry Pi
            client.connect(hostname, username=username, password=password)

        # Download the file from the Raspberry Pi
            sftp_client = client.open_sftp()
            sftp_client.get(remote_file_path, local_file_path)
            sftp_client.close()

        # Close the SSH connection
            client.close()
           
            # Create the main window
            window = tk.Tk()
       
            # Set the window title
            window.title("Image Viewer")
            # Add heading label
            heading_label = tk.Label(window, text="You have someone at your door!", font=("Arial", 16, "bold"))
            heading_label.pack(pady=10)

            # Load the received image
            try:
                # Open the image and calculate the new dimensions while maintaining the aspect ratio
                image = Image.open(local_file_path)
                original_width, original_height = image.size
                aspect_ratio = original_width / original_height

                # Increase the size proportionally based on the new width of 600 pixels
                new_width = 600
                new_height = int(new_width / aspect_ratio)

                # Resize the image
                image = image.resize((new_width, new_height))

                # Create the PhotoImage and display the image label
                photo = ImageTk.PhotoImage(image)
                image_label = tk.Label(window, image=photo)
                image_label.pack(pady=10)
            except (FileNotFoundError, PIL.UnidentifiedImageError) as e:
                print("Error loading image:", e)
                   
            print("**",last_line)
            message_label = ttk.Label(window, text= last_line, font=LARGEFONT)
            message_label.pack(pady=10)

            # Create Button 1
            button1 = tk.Button(window, text="open ", command=lambda: button1_clicked(client_socket))
            button1.pack(pady=10)

            # Create Button 2
            button2 = tk.Button(window, text="dont open", command=lambda: button2_clicked(client_socket))
            button2.pack(pady=10)

            # Start the Tkinter event loop
            window.mainloop()  
             
            if not data:
                break  # Break the loop if no data is received

            # Print the received data
            print("Received data from client {}: {}".format(client_address, data))

            # Append the received data to the water level values list for this client
            door_sense_values[client_address].append(data)

    except Exception as e:
        print("Error handling client {}: {}".format(client_address, str(e)))

    finally:
        # Close the client socket
        client_socket.close()
        print("Client disconnected:", client_address)




try:
    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print("Client connected:", client_address)

        hostname = client_address[0]  # Raspberry Pi IP address
        password = 'raspberry'  # Raspberry Pi password

     

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

       

except KeyboardInterrupt:
    # Close the server socket on keyboard interrupt
    server_socket.close()

    # Create the Excel database file
    df = pd.DataFrame(columns=["Time", "Person no"])

    # Store Person data in the Excel database
    for client_address, values in door_sense_values.items():
        # Create the x-axis values (time steps)
        time_steps = np.arange(len(values))

        # Add the time and Person data to the DataFrame
        data = {
            "Time": [datetime.now() + pd.DateOffset(seconds=t) for t in time_steps],
            "Person": values
        }
        df_client = pd.DataFrame(data)
        df = pd.concat([df, df_client], ignore_index=True)

    # Save the DataFrame to an Excel file
    file_path = "Door_monitor_data.xlsx"
    df.to_excel(file_path, index=False)
    print("Foor Monitoring system data saved in the Excel database: {}".format(file_path))
