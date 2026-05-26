
# from datetime import datetime, timezone

# def aware_utcnow():
#     return datetime.now(timezone.utc)

# def aware_utcfromtimestamp(timestamp):
#     return datetime.fromtimestamp(timestamp, timezone.utc)

# def naive_utcnow():
#     return aware_utcnow().replace(tzinfo=None)

# def naive_utcfromtimestamp(timestamp):
#     return aware_utcfromtimestamp(timestamp).replace(tzinfo=None)

# print(aware_utcnow())
# print(aware_utcfromtimestamp(0))
# print(naive_utcnow())
# print(naive_utcfromtimestamp(0))


# import MetaTrader5 as mt5
# import pandas as pd



    font_size = 15
    padding_size = 3

        # Tkinter Application
    root = tk.Tk()
    root.title("Equity Chart")

    style = ttk.Style(root)
    root.tk.call("source", "forest-dark.tcl")
    style.theme_use("forest-dark")

    frame = ttk.Frame(root)
    frame.grid(row=0,column=0)

    frame_2 = ttk.Frame(root)
    frame_2.grid(row=0,column=1)




    # # Create Toolbar
    # toolbar = NavigationToolbar2Tk(canvas, root)
    # toolbar.update()
    # toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    # Close database connection when the GUI window is closed
    def on_closing():
        conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)


    norm_orders_frame = ttk.Labelframe(frame, text="normal order details")
    norm_orders_frame.grid(row=0,column=0)

    bbw_orders_frame = ttk.Labelframe(frame, text="BBW order details")
    bbw_orders_frame.grid(row=1,column=0)

    oi_orders_frame = ttk.Labelframe(frame, text="OI order details")
    oi_orders_frame.grid(row=2,column=0)

    details_frame = ttk.Labelframe(frame, text="details")
    details_frame.grid(row=3,column=0)

    spread_frame = ttk.Labelframe(frame, text="spread live")
    spread_frame.grid(row=4,column=0)

    euity_frame = ttk.Frame(frame_2)
    euity_frame.grid(row=0,column=0)

        # Create Matplotlib Figure and Axis
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=euity_frame)
    canvas.get_tk_widget().grid(row=0,column=0)



    text_label_TP = ttk.Label(norm_orders_frame, text="TP")
    text_label_TP.grid(row=0,column=0)
    text_label_SL = ttk.Label(norm_orders_frame, text="SL")
    text_label_SL.grid(row=1,column=0)
    text_label_side = ttk.Label(norm_orders_frame, text="side")
    text_label_side.grid(row=2,column=0)
    text_label_active = ttk.Label(norm_orders_frame, text="Norm active")
    text_label_active.grid(row=3,column=0)

    text_label_TP_bbw = ttk.Label(bbw_orders_frame, text="TP")
    text_label_TP_bbw.grid(row=0,column=0)
    text_label_SL_bbw = ttk.Label(bbw_orders_frame, text="SL")
    text_label_SL_bbw.grid(row=1,column=0)
    text_label_side_bbw = ttk.Label(bbw_orders_frame, text="side")
    text_label_side_bbw.grid(row=2,column=0)
    text_label_active_bbw = ttk.Label(bbw_orders_frame, text="BBW active")
    text_label_active_bbw.grid(row=3,column=0)

    text_label_TP_oi = ttk.Label(oi_orders_frame, text="TP")
    text_label_TP_oi.grid(row=0,column=0)
    text_label_SL_oi = ttk.Label(oi_orders_frame, text="SL")
    text_label_SL_oi.grid(row=1,column=0)
    text_label_side_oi = ttk.Label(oi_orders_frame, text="side")
    text_label_side_oi.grid(row=2,column=0)
    text_label_active_oi = ttk.Label(oi_orders_frame, text="OI active")
    text_label_active_oi.grid(row=3,column=0)
    text_dca_orders_short_oi = ttk.Label(oi_orders_frame, text="OI position amount")
    text_dca_orders_short_oi.grid(row=4,column=0)

    text_ema_status = ttk.Label(details_frame, text="EMA status")
    text_ema_status.grid(row=0,column=0)
    text_time_active = ttk.Label(details_frame, text="time active")
    text_time_active.grid(row=1,column=0)
    text_orders_can_be_placed = ttk.Label(details_frame, text="can orders be placed")
    text_orders_can_be_placed.grid(row=2,column=0)
    text_dd_daily_active = ttk.Label(details_frame, text="Daily Drawdown active")
    text_dd_daily_active.grid(row=3,column=0)
    text_dd_percentage = ttk.Label(details_frame, text="Daily Drawdown %")
    text_dd_percentage.grid(row=4,column=0)
    text_total_risk_active = ttk.Label(details_frame, text="total risk")
    text_total_risk_active.grid(row=5,column=0)
    text_deals_in_history = ttk.Label(details_frame, text="deals in history")
    text_deals_in_history.grid(row=6,column=0)

    text_spread = ttk.Label(spread_frame, text="%")
    text_spread.grid(row=0,column=0)


    # live_label_ema_status = ttk.Label(root, textvariable=label_ema_status)
    # live_label_time_active = ttk.Label(root, textvariable=label_time_active)
    # live_label_orders_can_be_placed = ttk.Label(root, textvariable=label_orders_can_be_placed)
    # live_label_dd_daily_active = ttk.Label(root, textvariable=label_dd_daily_active)
    # live_label_dd_percentage = ttk.Label(root, textvariable=label_dd_percentage)

    # live_label_total_risk_active = ttk.Label(root, textvariable=label_total_risk_active)
    # live_label_deals_in_history = ttk.Label(root, textvariable=label_deals_in_history)
    # live_label_dca_orders_short_oi = ttk.Label(root, textvariable=label_dca_orders_short_oi)





    # Function to update label_text whenever dbTP1 changes
    def update_label_text():
        label_dbTP1.set(dbTP1)
        label_dbTP2.set(dbTP2)
        label_dbTP3.set(dbTP3)
        label_dbSL1.set(dbSL1)
        label_dbSL2.set(dbSL2)
        label_dbSL3.set(dbSL3)
        label_side1.set(side1)
        label_side2.set(side2)
        label_side3.set(side3)
        label_norm_active.set(norm_active)
        label_bbw_active.set(bbw_active)
        label_oi_active.set(oi_active)
        label_ema_status.set(ema_status)
        label_time_active.set(time_active)
        label_orders_can_be_placed.set(orders_can_be_placed)
        label_dd_daily_active.set(dd_daily_active)
        label_dd_percentage.set(dd_percentage)
        label_total_risk_active.set(total_risk_active)
        label_deals_in_history.set(deals_in_history)
        label_dca_orders_short_oi.set(dca_orders_short_oi)
        label_spread_now.set(spread_now)



    label_dbTP1 = tk.StringVar(value=dbTP1)
    label_dbTP2 = tk.StringVar(value=dbTP2)
    label_dbTP3 = tk.StringVar(value=dbTP3)

    label_dbSL1 = tk.StringVar(value=dbSL1)
    label_dbSL2 = tk.StringVar(value=dbSL2)
    label_dbSL3 = tk.StringVar(value=dbSL3)

    label_side1 = tk.StringVar(value=side1)
    label_side2 = tk.StringVar(value=side2)
    label_side3 = tk.StringVar(value=side3)

    label_norm_active = tk.StringVar(value=norm_active)
    label_bbw_active = tk.StringVar(value=bbw_active)
    label_oi_active = tk.StringVar(value=oi_active)

    label_ema_status = tk.StringVar(value=ema_status)
    label_time_active = tk.StringVar(value=time_active)
    label_orders_can_be_placed = tk.StringVar(value=orders_can_be_placed)
    label_dd_daily_active = tk.StringVar(value=dd_daily_active)
    label_dd_percentage = tk.StringVar(value=dd_percentage)

    label_total_risk_active = tk.StringVar(value=total_risk_active)
    label_deals_in_history = tk.StringVar(value=deals_in_history)
    label_dca_orders_short_oi = tk.StringVar(value=dca_orders_short_oi)
    label_spread_now = tk.StringVar(value=spread_now)  # Initialize label_spread_now

    # Create labels using the StringVar variables
    live_label_dbTP1 = ttk.Label(norm_orders_frame, textvariable=label_dbTP1, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_dbTP2 = ttk.Label(bbw_orders_frame, textvariable=label_dbTP2, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_dbTP3 = ttk.Label(oi_orders_frame, textvariable=label_dbTP3, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_label_dbSL1 = ttk.Label(norm_orders_frame, textvariable=label_dbSL1, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_dbSL2 = ttk.Label(bbw_orders_frame, textvariable=label_dbSL2, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_dbSL3 = ttk.Label(oi_orders_frame, textvariable=label_dbSL3, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_label_side1 = ttk.Label(norm_orders_frame, textvariable=label_side1, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_side2 = ttk.Label(bbw_orders_frame, textvariable=label_side2, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_side3 = ttk.Label(oi_orders_frame, textvariable=label_side3, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_label_norm_active = ttk.Label(norm_orders_frame, textvariable=label_norm_active, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_bbw_active = ttk.Label(bbw_orders_frame, textvariable=label_bbw_active, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_oi_active = ttk.Label(oi_orders_frame, textvariable=label_oi_active, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_label_dca_orders_short_oi = ttk.Label(oi_orders_frame, textvariable=label_dca_orders_short_oi, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_label_ema_status = ttk.Label(details_frame, textvariable=label_ema_status, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_time_active = ttk.Label(details_frame, textvariable=label_time_active, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_orders_can_be_placed = ttk.Label(details_frame, textvariable=label_orders_can_be_placed, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_dd_daily_active = ttk.Label(details_frame, textvariable=label_dd_daily_active, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_dd_percentage = ttk.Label(details_frame, textvariable=label_dd_percentage, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_label_total_risk_active = ttk.Label(details_frame, textvariable=label_total_risk_active, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_deals_in_history = ttk.Label(details_frame, textvariable=label_deals_in_history, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_spread_now = ttk.Label(spread_frame, textvariable=label_spread_now, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size)) 

    # Pack the labels using the pack() method
    live_label_dbTP1.grid(row=0,column=1)
    live_label_dbTP2.grid(row=0,column=1)
    live_label_dbTP3.grid(row=0,column=1)

    live_label_dbSL1.grid(row=1,column=1)
    live_label_dbSL2.grid(row=1,column=1)
    live_label_dbSL3.grid(row=1,column=1)

    live_label_side1.grid(row=2,column=1)
    live_label_side2.grid(row=2,column=1)
    live_label_side3.grid(row=2,column=1)

    live_label_norm_active.grid(row=3,column=1)
    live_label_bbw_active.grid(row=3,column=1)
    live_label_oi_active.grid(row=3,column=1)

    live_label_dca_orders_short_oi.grid(row=4,column=1)

    live_label_ema_status.grid(row=0,column=1)
    live_label_time_active.grid(row=1,column=1)
    live_label_orders_can_be_placed.grid(row=2,column=1)
    live_label_dd_daily_active.grid(row=3,column=1)
    live_label_dd_percentage.grid(row=4,column=1)

    live_label_total_risk_active.grid(row=5,column=1)
    live_label_deals_in_history.grid(row=6,column=1)
    live_spread_now.grid(row=0,column=1)






def start_chart():



    # Simulate change in dbTP1 (You can change dbTP1 value dynamically in your application)
    def simulate_db_change():
        update_label_text()
        root.after(200, simulate_db_change)  # Update every 1 second

    simulate_db_change()



    # Function to update the plot with equity data
    def update_plot(i):
        # Fetch equity data for the last 3 days
        equity_data = rows
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
    ani = FuncAnimation(fig, update_plot, interval=5000)

    root.mainloop()



# order
#(TradeOrder(ticket=142202536, time_setup=1708653320, time_setup_msc=1708653320527, time_done=0, time_done_msc=0, time_expiration=0, type=2, type_time=0, type_filling=2, state=1, magic=0, position_id=0, position_by_id=0, reason=0, volume_initial=0.01, volume_current=0.01, price_open=51072.52, sl=0.0, tp=0.0, price_current=51306.0, price_stoplimit=0.0, symbol='BTCUSD', comment='', external_id=''),)

# position
#(TradePosition(ticket=142202428, time=1708653216, time_msc=1708653216626, time_update=1708653216, time_update_msc=1708653216626, type=0, magic=0, identifier=142202428, reason=0, volume=0.01, price_open=51330.0, sl=0.0, tp=0.0, price_current=51385.3, swap=0.0, profit=0.55, symbol='BTCUSD', comment='', external_id=''),)
                
