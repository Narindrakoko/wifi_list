#!/usr/bin/env python3

import subprocess
import re
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

def get_wifi_list():
    try:
        # Execute the nmcli command to list Wi-Fi networks
        result = subprocess.run(['nmcli', '-f', 'BSSID,SSID,MODE,CHAN,RATE,SIGNAL,BARS', 'device', 'wifi', 'list'], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to fetch Wi-Fi list\n{e}")
        return ""

def parse_wifi_list(output):
    # Split the output into lines and process each line
    lines = output.strip().split('\n')[1:]  # Skip the header line
    wifi_list = []
    for line in lines:
        # Use regular expression to split the line based on spaces but preserve spaces within quoted strings
        match = re.match(r'(\S+)\s+(.+?)\s{2,}(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
        if match:
            bssid, ssid, mode, chan, rate, signal, bar = match.groups()
            wifi_list.append((bssid, ssid, mode, chan, rate, signal, bar))
    return wifi_list

def populate_table():
    for row in wifi_list:
        tree.insert("", "end", values=row)

def connect_to_wifi():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a network to connect to.")
        return

    ssid = tree.item(selected_item[0], "values")[1]
    password = simpledialog.askstring("Wi-Fi Password", f"Enter password for {ssid}:", show='*')

    if password:
        result = subprocess.run(['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password], capture_output=True, text=True)
        if result.returncode == 0:
            messagebox.showinfo("Success", f"Connected to {ssid}")
        else:
            messagebox.showerror("Error", f"Failed to connect to {ssid}\n{result.stderr}")

def refresh_wifi_list():
    global wifi_list
    wifi_output = get_wifi_list()
    wifi_list = parse_wifi_list(wifi_output)
    for row in tree.get_children():
        tree.delete(row)
    populate_table()

def filter_wifi_list(event):
    query = search_var.get().lower()
    for row in tree.get_children():
        tree.delete(row)
    for wifi in wifi_list:
        if query in wifi[1].lower():
            tree.insert("", "end", values=wifi)

# Get and parse the Wi-Fi list
wifi_output = get_wifi_list()
wifi_list = parse_wifi_list(wifi_output)

# Create the main window
root = tk.Tk()
root.title("Wi-Fi Networks")

# Create the treeview with columns
columns = ("BSSID", "SSID", "Mode", "Chan", "Rate", "Signal", "Bar")
tree = ttk.Treeview(root, columns=columns, show="headings")

# Define headings and enable sorting
for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: sort_by(_col, False))

def sort_by(col, descending):
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    tree.heading(col, command=lambda: sort_by(col, not descending))

# Populate the treeview
populate_table()

# Add the treeview to the window and pack it
tree.pack(fill=tk.BOTH, expand=True)

# Add search bar
search_var = tk.StringVar()
search_var.trace("w", filter_wifi_list)
search_entry = tk.Entry(root, textvariable=search_var)
search_entry.pack(pady=5)

# Create and add buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

refresh_button = tk.Button(button_frame, text="Refresh", command=refresh_wifi_list)
refresh_button.pack(side=tk.LEFT, padx=5)

connect_button = tk.Button(button_frame, text="Connect", command=connect_to_wifi)
connect_button.pack(side=tk.LEFT, padx=5)

# Start the GUI event loop
root.mainloop()
