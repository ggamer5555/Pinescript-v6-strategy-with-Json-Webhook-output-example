
from termcolor import colored
import numpy as np
import sqlite3
import threading
from tabulate import tabulate


from logging.handlers import TimedRotatingFileHandler
from logging import Formatter

from datetime import datetime, timedelta

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from datetime import datetime, timedelta
from matplotlib.animation import FuncAnimation
import matplotlib
matplotlib.use('agg')



# Function
#  to fetch equity data for the last 3 days
def load_equity_data():
        # Connect to SQLite database for equity data
    conn = sqlite3.connect('equity_data.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    # Calculate the datetime for 3 days ago
    three_days_ago = datetime.now() - timedelta(days=3)

    # Fetch equity data for the last 3 days
    cursor.execute("SELECT timestamp, equity FROM equity WHERE timestamp >= ?", (three_days_ago,))
    rows = cursor.fetchall()
    conn.close()
    return rows



def start_chart_2():
    root_2 = tk.Tk()
    root_2.title("Equity Chart")

    frame = ttk.Frame(root_2)
    frame.grid(row=0,column=0)

    def on_closing():
        root_2.destroy()

    root_2.protocol("WM_DELETE_WINDOW", on_closing)


        # Create Matplotlib Figure and Axis
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().grid(row=0,column=0)


    def update_plot(i):
        # Fetch equity data for the last 3 days
        equity_data = load_equity_data()
        timestamps = [row[0] for row in equity_data]
        equity_values = [row[1] for row in equity_data]

        # Clear previous plot
        ax.clear()

        # Plot equity data
        ax.plot(timestamps, equity_values, marker='o', linestyle='-')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_title('Real-time Equity Chart (Last 3 Days)')
        ax.tick_params(axis='x', rotation=90)  # Rotate x-axis labels for better visibility
        canvas.draw()

    # Update the plot every 30 seconds
    ani = FuncAnimation(fig, update_plot, interval=120000, cache_frame_data=False)

    root_2.mainloop()





if __name__ == '__main__':
    thread0_1 = threading.Thread(target=start_chart_2)
    thread5 = threading.Thread(target=load_equity_data)


    thread0_1.start()
    thread5.start()


    thread0_1.join()
    thread5.join()







