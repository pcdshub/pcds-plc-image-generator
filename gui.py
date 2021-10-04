import ipaddress
import logging
import os
import pathlib
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

from console import MODEL_TO_URL, generate_image

logger = logging.getLogger(__name__)


def open_directory(path):
    """Open 'path' in explorer/finder/etc."""
    if sys.platform == "win32":
        return os.startfile(path)
    if sys.platform == "darwin":
        return subprocess.Popen(["open", path])
    return subprocess.Popen(["xdg-open", path])


def create_window():
    """Create and return a Tkinter GUI window."""
    window = tk.Tk()
    window.title("PCDS PLC Image Generator")

    row = -1

    def to_row(*widgets):
        nonlocal row
        row += 1
        for idx, widget in enumerate(widgets):
            widget.grid(row=row, column=idx)

    plc_model_combo = tk.ttk.Combobox(
        master=window, values=tuple(MODEL_TO_URL), state="readonly"
    )
    plc_name_entry = tk.Entry(master=window)
    plc_desc_entry = tk.Entry(master=window)
    plc_ip_entry = tk.Entry(master=window)
    create_button = tk.Button(master=window, text="Create")
    status_label = tk.Label(master=window)

    to_row(tk.Label(master=window, text="PLC Model"), plc_model_combo)
    to_row(tk.Label(master=window, text="PLC Name"), plc_name_entry)
    to_row(tk.Label(master=window, text="PLC Description"), plc_desc_entry)
    to_row(tk.Label(master=window, text="PLC IP Address"), plc_ip_entry)
    to_row(create_button)
    to_row(status_label)

    def create_image(event):
        model = plc_model_combo.get()
        name = plc_name_entry.get().strip()
        description = plc_desc_entry.get().strip()
        addr = plc_ip_entry.get().strip()
        if not name:
            status_label.config(text="Please enter a PLC name")
            return

        if not model:
            status_label.config(text="Please select a PLC model")
            return

        try:
            ipaddress.IPv4Address(addr)
        except Exception:
            status_label.config(text="Please enter a valid IP address")
            return

        generation_desc = f"{model} {name!r} ({addr})"
        status_label.config(text=f"Generating image for {generation_desc}...")
        generate_image(
            plc_model=model,
            plc_name=name,
            ip_address=addr,
            plc_description=description,
            auto_delete=True,
        )
        status_label.config(text=f"Generated image for {generation_desc}.")

        image_path = pathlib.Path("images").resolve() / name
        if image_path.exists():
            try:
                open_directory(image_path)
            except Exception:
                logger.exception("Failed to open the directory %s", image_path)

    create_button.bind("<Button-1>", create_image)
    return window


def main():
    """Create the main tk window and run the main loop."""
    window = create_window()
    window.mainloop()


if __name__ == "__main__":
    main()
