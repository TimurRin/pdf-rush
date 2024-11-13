import tkinter as tk
from tkinter import messagebox, PhotoImage
import webbrowser


def open_file():
    # Add your code to open a file here
    pass


def save_file():
    # Add your code to save a file here
    pass


def exit_app():
    # Add your code to exit the application here
    pass


def show_about_popup():
    messagebox.showinfo("About", "PDF Rush - Version 1.0")


def open_github_url():
    webbrowser.open("https://github.com/TimurRin/pdf-rush")


def open_moziev_url():
    webbrowser.open("https://timurrin.github.io/")


def jump_to_page():
    # Add your code to jump to a specific page here
    pass


def previous_page():
    # Add your code to go to the previous page here
    pass


def next_page():
    # Add your code to go to the next page here
    pass


def rotate_page():
    # Add your code to rotate the current page here
    pass


def delete_page():
    # Add your code to delete the current page here
    pass


def main():
    # Create the main window
    window = tk.Tk()
    window.title("PDF Rush")

    logo = PhotoImage(file="img/logo.png")
    window.iconphoto(False, logo)

    # Create the status bar
    status_bar = tk.Label(window, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Create the top menu
    menu_bar = tk.Menu(window)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Open", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=exit_app)
    menu_bar.add_cascade(label="File", menu=file_menu)

    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="About", command=show_about_popup)
    help_menu.add_separator()
    help_menu.add_command(label="PDF Rush's GitHub", command=open_github_url)
    help_menu.add_command(label="Timur Moziev's website", command=open_moziev_url)
    menu_bar.add_cascade(label="Help", menu=help_menu)

    window.config(menu=menu_bar)

    # Create the image pane
    image_pane = tk.Label(window, text="Image Pane")
    image_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create the right control buttons
    control_frame = tk.Frame(window)
    control_frame.pack(side=tk.RIGHT, padx=10)

    jump_button = tk.Button(control_frame, text="Jump to Page", command=jump_to_page)
    jump_button.pack(pady=10)

    prev_button = tk.Button(control_frame, text="Previous Page", command=previous_page)
    prev_button.pack(pady=10)

    next_button = tk.Button(control_frame, text="Next Page", command=next_page)
    next_button.pack(pady=10)

    rotate_button = tk.Button(control_frame, text="Rotate Page", command=rotate_page)
    rotate_button.pack(pady=10)

    delete_button = tk.Button(control_frame, text="Delete Page", command=delete_page)
    delete_button.pack(pady=10)

    # Start the main loop
    window.mainloop()


if __name__ == "__main__":
    main()
