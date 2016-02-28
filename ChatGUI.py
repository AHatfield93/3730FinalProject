#
# EC3730 Group Project -  Sean Hacker, Amber Hatfield, and Austin Norby 
# CHAT GUI using Tkinter
#

import sys
from Tkinter import *
from tkFileDialog import asksaveasfilename
import threading
import socket
import random
import math

# GLOBALS
conn_array = []  # stores open sockets
ipAddress_array = dict()  # key: the open sockets in conn_array,
                        # value: ipAdresses for the connection
ipAddress = "Self"

location = 0
port = 0
top = ""
isCLI=False
main_body_text = 0

def connects(clientType):
    global conn_array
    connecter.config(state=DISABLED)
    if len(conn_array) == 0:
        if clientType == 0:
            client_options_window(root)
        if clientType == 1:
            options_window(root)
    else:
        # connecter.config(state=NORMAL)
        for connection in conn_array:
            connection.send("-001".encode())
        processFlag("-001")
def options_window(master):
    """Launches server options window for getting port."""
    top = Toplevel(master)
    top.title("Connection options")
    top.grab_set()
    top.protocol("WM_DELETE_WINDOW", lambda: optionDelete(top))
    Label(top, text="Reciever IP:").grid(row=0)
    recieverIP = Entry(top)
    recieverIP.grid(row=0, column=1)
    recieverIP.focus_set()
    Label(top, text="Reciever MAC:").grid(row=1)
    recieverMac = Entry(top)
    recieverMac.grid(row=1, column=1)
    recieverMac.focus_set()
    Label(top, text="Listening Port:").grid(row=2)
    port = Entry(top)
    port.grid(row=2, column=1)
    port.focus_set()
    Label(top, text="Sending Port:").grid(row=3)
    port = Entry(top)
    port.grid(row=3, column=1)
    port.focus_set()
    go = Button(top, text="Launch", command=lambda:
            options_go(port.get(), top))
    go.grid(row=4, column=1)

def options_go(port, window):
    """Processes the options entered by the user in the
    server options window.
    """
    if options_sanitation(port):
        if not isCLI:
            window.destroy()
        Server(int(port)).start()
    elif isCLI:
        sys.exit(1)

def optionDelete(window):
    connecter.config(state=NORMAL)
    window.destroy()

#GUI
    
root = Tk()
root.title("EC3730 Project - P2P Chat")

menubar = Menu(root)

file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label="Options",
                            command=lambda: options_window(root))
file_menu.add_command(label="Exit", command=lambda: root.destroy())
menubar.add_cascade(label="File", menu=file_menu)

root.config(menu=menubar)

main_body = Frame(root, height=20, width=50)
main_body_text = Text(main_body)
body_text_scroll = Scrollbar(main_body)
main_body_text.focus_set()
body_text_scroll.pack(side=RIGHT, fill=Y)
main_body_text.pack(side=LEFT, fill=Y)
body_text_scroll.config(command=main_body_text.yview)
main_body_text.config(yscrollcommand=body_text_scroll.set)
main_body.pack()

main_body_text.insert(END, "Welcome to Amber, Austin, and Sean's Group Project!")
main_body_text.config(state=DISABLED)

text_input = Entry(root, width=60)

text_input.pack()

statusConnect = StringVar(root)
statusConnect.set("Connect")
clientType = 1
var = StringVar(root)
var.set("TCP") # initial value
option = OptionMenu(root, var, "TCP", "UDP", "ICP", "HTTP")
option.pack(anchor=E)
connecter = Button(root, textvariable=statusConnect, command=lambda: connects(clientType))
connecter.pack()

root.mainloop()
