import tkinter as tk
from tkinter import ttk

def setup_ui(app):
    # Main frame
    main_frame = ttk.Frame(app.root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    app.root.columnconfigure(0, weight=1)
    app.root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(2, weight=1)

    # Header frame with title and language button
    header_frame = ttk.Frame(main_frame)
    header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
    header_frame.columnconfigure(0, weight=1)
    header_frame.columnconfigure(1, weight=1)
    header_frame.columnconfigure(2, weight=1)

    # Title on its own row
    app.title_label = ttk.Label(header_frame, text="MoneyRat's KeyPresser Deluxe", font=("Arial", 16, "bold"))
    app.title_label.grid(row=0, column=0, columnspan=3, sticky="we", pady=(0, 2))

    # Second row: window selector left, language button right
    app.window_combo = ttk.Combobox(header_frame, state="readonly")
    app.window_combo.grid(row=1, column=0, columnspan=2, sticky="we", padx=(0, 0))
    header_frame.columnconfigure(0, weight=1)
    header_frame.columnconfigure(1, weight=1)
    app.window_combo.bind('<<ComboboxSelected>>', app.on_window_select)
    app.update_window_list()

    app.language_button = ttk.Button(header_frame, text="Language", command=app.show_language_menu)
    app.language_button.grid(row=1, column=2, sticky="e", padx=(0, 0))

    # Add entry frame
    entry_frame = ttk.Frame(main_frame)
    entry_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
    app.key_label = ttk.Label(entry_frame, text="Key:")
    app.key_label.grid(row=0, column=0, padx=(0, 5))
    app.key_entry = ttk.Entry(entry_frame, width=10)
    app.key_entry.grid(row=0, column=1, padx=(0, 10))
    app.interval_label = ttk.Label(entry_frame, text="Interval (ms):")
    app.interval_label.grid(row=0, column=2, padx=(0, 5))
    app.interval_entry = ttk.Entry(entry_frame, width=10)
    app.interval_entry.grid(row=0, column=3, padx=(0, 10))
    app.add_button = ttk.Button(entry_frame, text="Add", command=app.add_key_config)
    app.add_button.grid(row=0, column=4, padx=(0, 5))
    app.remove_button = ttk.Button(entry_frame, text="Remove", command=app.remove_key_config)
    app.remove_button.grid(row=0, column=5)

    # Table frame
    table_frame = ttk.Frame(main_frame)
    table_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
    table_frame.columnconfigure(0, weight=1)
    table_frame.rowconfigure(0, weight=1)
    app.tree = ttk.Treeview(table_frame, columns=('key', 'interval'), show='tree headings', height=10)
    app.tree.heading('#0', text='Active')
    app.tree.heading('key', text='Key')
    app.tree.heading('interval', text='Interval (ms)')
    app.tree.column('#0', width=80, anchor='center')
    app.tree.column('key', width=150, anchor='center')
    app.tree.column('interval', width=150, anchor='center')
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=app.tree.yview)
    app.tree.configure(yscrollcommand=scrollbar.set)
    app.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    # Control buttons frame
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=3, column=0, pady=(10, 0))
    app.start_button = ttk.Button(button_frame, text="Start", command=app.start_pressing, style="Accent.TButton")
    app.start_button.grid(row=0, column=0, padx=(0, 10))
    app.stop_button = ttk.Button(button_frame, text="Stop", command=app.stop_pressing)
    app.stop_button.grid(row=0, column=1)
    app.stop_button.config(state='disabled')

    # Status label
    app.status_label = ttk.Label(main_frame, text="Status: Stopped", foreground="red")
    app.status_label.grid(row=4, column=0, pady=(10, 0))
    app.hotkey_label = ttk.Label(main_frame, text="Hotkeys: F7 = Start | F8 = Stop", font=("Arial", 9), foreground="gray")
    app.hotkey_label.grid(row=5, column=0, pady=(5, 0))
    app.edit_info_label = ttk.Label(main_frame, text="Double-click Active column to toggle, Interval column to edit", font=("Arial", 8), foreground="gray")
    app.edit_info_label.grid(row=6, column=0, pady=(2, 0))

    # PayPal Donate button at the bottom
    def open_paypal():
        import webbrowser
        webbrowser.open_new("https://www.paypal.com/donate/?business=RFHNR4TM6KPQ4&no_recurring=0&item_name=A+brazilian+software+developer+and+maker+that+enjoys+giving+back+to+the+community.+Help+me+back+if+you+can.+Much+appreciated%21&currency_code=BRL")
    try:
        app.paypal_img = tk.PhotoImage(file="paypaldonatebutton.png")
        # Resize image to about 1.5x the width of Start/Stop buttons (e.g., ~120-140px wide)
        desired_width = 140
        desired_height = int(app.paypal_img.height() * (desired_width / app.paypal_img.width()))
        app.paypal_img = app.paypal_img.subsample(max(1, app.paypal_img.width() // desired_width), max(1, app.paypal_img.height() // desired_height))
        app.paypal_button = ttk.Button(main_frame, image=app.paypal_img, command=open_paypal)
        app.paypal_button.grid(row=7, column=0, pady=(12, 0), sticky="s")
    except Exception as e:
        app.paypal_button = ttk.Button(main_frame, text="Donate with PayPal", command=open_paypal)
        app.paypal_button.grid(row=7, column=0, pady=(12, 0), sticky="s")

    # Bind events
    app.tree.bind('<Double-1>', app.on_double_click)
    app.tree.bind('<Button-1>', app.on_single_click)
    app.tree.bind('<Configure>', lambda e: app.update_tree_checkboxes())
    app.tree.bind('<Motion>', lambda e: app.update_tree_checkboxes())
    app.tree.bind('<<TreeviewSelect>>', lambda e: app.update_tree_checkboxes())
