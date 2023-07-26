# Copyright (c) 2023, Timur Moziev
# All rights reserved.

# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import sys, os
import PyPDF2
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import fitz
from PIL import Image, ImageTk
import json
import webbrowser

if getattr(sys, "frozen", False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))


class PDFEditorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.app_name = f"PDF Rush {self.get_version_info()}"
        self.root.title(self.app_name)
        self.current_page = 0
        self.total_files = 0
        self.file_number = {}
        self.all_pages = []
        self.pdf_files = []
        self.num_pages = 0
        self.canvas_width = 1024
        self.canvas_height = 700
        self.page_rotations = {}
        self.page_rotations_init = {}
        self.deleted_pages = {}
        self.unsaved_changes = {}
        self.current_folder = application_path
        self.output_folder = os.path.join(self.current_folder, "_pdf_rush")
        self.replace_existing = tk.BooleanVar()
        self.img_tk = None
        self.create_ui()

    def get_version_info(self):
        version_file = os.path.join(os.path.dirname(__file__), "version.json")
        with open(version_file, "r") as f:
            version_data = json.load(f)

        major = version_data.get("major", 0)
        minor = version_data.get("minor", 0)
        patch = version_data.get("patch", 0)

        return f"v{major}.{minor}.{patch}"

    def create_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame, width=self.canvas_width, height=self.canvas_height
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.file_info_frame = tk.Frame(self.main_frame, padx=10, pady=5)
        self.file_info_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=True)

        tk.Label(
            self.file_info_frame, text=self.app_name, font=("Helvetica", 16, "bold")
        ).pack(pady=10)

        load_button = tk.Button(
            self.file_info_frame, text="Load file", command=self.ask_file
        )
        load_button.pack(side=tk.TOP, pady=5)

        load_button = tk.Button(
            self.file_info_frame, text="Load folder", command=self.ask_folder
        )
        load_button.pack(side=tk.TOP, pady=5)

        self.folder_info_label = tk.Label(self.file_info_frame, text="", anchor=tk.W)
        self.folder_info_label.pack(anchor=tk.W)

        self.file_name_label = tk.Label(self.file_info_frame, text="", anchor=tk.W)
        self.file_name_label.pack(anchor=tk.W)

        self.page_number_label = tk.Label(self.file_info_frame, text="", anchor=tk.W)
        self.page_number_label.pack(anchor=tk.W)

        self.page_info_label = tk.Label(self.file_info_frame, text="", anchor=tk.W)
        self.page_info_label.pack(anchor=tk.W)

        self.unsaved_changes_label = tk.Label(
            self.file_info_frame,
            text="Unsaved changes:",
            anchor=tk.W,
            font=("Helvetica", 12, "bold"),
        )
        self.unsaved_changes_label.pack(anchor=tk.W, pady=5)

        self.unsaved_changes_listbox = tk.Listbox(
            self.file_info_frame, height=15, width=50
        )
        self.unsaved_changes_listbox.pack(anchor=tk.W)

        self.save_button = tk.Button(
            self.file_info_frame, text="Save Changes", command=self.save_changes
        )
        self.save_button.pack(anchor=tk.W, pady=10)

        self.replace_checkbox = tk.Checkbutton(
            self.file_info_frame,
            text="Replace existing",
            variable=self.replace_existing,
        )
        self.replace_checkbox.pack(anchor=tk.W)

        self.about_button = tk.Button(
            self.file_info_frame, text="About", command=self.show_about_info
        )
        self.about_button.pack(side=tk.BOTTOM, pady=2)

        self.help_button = tk.Button(
            self.file_info_frame, text="Help", command=self.show_help
        )
        self.help_button.pack(side=tk.BOTTOM, pady=2)

        self.jump_button = tk.Button(
            self.canvas_frame, text="Jump to Page", command=self.jump_to_page
        )
        self.jump_button.pack(side=tk.LEFT, padx=10)

        self.prev_button = tk.Button(
            self.canvas_frame, text="Previous Page", command=self.previous_page
        )
        self.prev_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(
            self.canvas_frame, text="Next Page", command=self.next_page
        )
        self.next_button.pack(side=tk.LEFT, padx=10)

        self.rotate_button = tk.Button(
            self.canvas_frame, text="Rotate Page", command=self.rotate_page
        )
        self.rotate_button.pack(side=tk.LEFT, padx=10)

        self.delete_button = tk.Button(
            self.canvas_frame, text="Delete Page", command=self.delete_page
        )
        self.delete_button.pack(side=tk.LEFT, padx=10)

        self.disable_control_buttons()

        self.root.bind("<Left>", lambda event: self.previous_page())
        self.root.bind("<Right>", lambda event: self.next_page())
        self.root.bind("<Up>", lambda event: self.rotate_page(90))
        self.root.bind("<Down>", lambda event: self.rotate_page(-90))
        self.root.bind("<space>", lambda event: self.jump_to_page())
        self.root.bind("<Delete>", lambda event: self.delete_page())
        self.root.bind("<Return>", lambda event: self.save_changes())
        

        self.root.mainloop()

    def show_help(self):
        message = f"Keyboard bindings:\nLeft Arrow: go to the previous page\nRight Arrow: go to the next page\nSpace: go to any page (from total)\nUp Arrow: rotate the current page clockwise\nDown Arrow: rotate the current page counter-clockwise\nDelete: mark page as deleted\nEnter: Save changes"
        show_custom_message_box(f"{self.app_name} help", message)

    def show_about_info(self):
        message = f"{self.app_name} is a simple PDF editor application.\nThe name PDF Rush reflects the very essence of the app: perform basic PDFs manipulation at high speed.\n\nKey features:\n- View and edit multiple PDF files in a single interface\n- Rotate pages to adjust the orientation\n- Delete specific pages from PDF files\nUse key bindings (see Help) to do editing even faster\n- Save edited files with the option to replace the original or create a new output folder\n\nGitHub repo: https://github.com/TimurRin/pdf-rush\n\nAuthors:\nTimur Moziev @TimurRin (idea, development)\nMaria Zhizhina (testing)"
        hyperlinks = {
            "https://github.com/TimurRin/pdf-rush": "https://github.com/TimurRin/pdf-rush",
            "@TimurRin": "https://github.com/TimurRin",
        }
        show_custom_message_box(f"About {self.app_name}", message, hyperlinks)

    def ask_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Portable Document Format", ".pdf")])
        if file_path:
            self.current_folder = os.path.dirname(file_path)
            self.output_folder = os.path.join(self.current_folder, "_pdf_rush")
            self.pdf_files = [os.path.basename(file_path)]
            self.load_files()

    def ask_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.load_folder(folder_path)

    def load_folder(self, folder_path):
        self.reset_session()
        self.current_folder = folder_path
        self.output_folder = os.path.join(self.current_folder, "_pdf_rush")
        self.pdf_files = [
            file
            for file in os.listdir(self.current_folder)
            if file.lower().endswith(".pdf")
        ]
        self.load_files()
        pass

    def load_files(self):
        if self.pdf_files:
            self.all_pages = []
            self.page_rotations = {}
            self.page_rotations_init = {}
            self.deleted_pages = {}
            self.unsaved_changes = {}
            self.total_files = len(self.pdf_files)
            self.file_number = {}
            file_count = 0
            for pdf_file in self.pdf_files:
                file_path = os.path.join(self.current_folder, pdf_file)
                try:
                    pdf_reader = PyPDF2.PdfReader(file_path)
                    for i, page in enumerate(pdf_reader.pages):
                        self.all_pages.append((file_path, i))
                        self.page_rotations[(file_path, i)] = page.rotation
                        self.page_rotations_init[(file_path, i)] = page.rotation
                    self.unsaved_changes[file_path] = {"rot": 0, "del": 0}
                    file_count += 1
                    self.file_number[file_path] = file_count
                except:
                    messagebox.showinfo("Oops...", f"Failed to open {file_path}")
                    continue
            self.num_pages = len(self.all_pages)
            self.current_page = min(self.num_pages - 1, self.current_page)

            self.folder_info_label.config(
                text=f"Folder: {os.path.basename(self.current_folder)}"
            )

            self.show_current_page()
            self.update_unsaved_changes_listbox()

            self.enable_control_buttons()
        else:
            messagebox.showinfo("No Files Found", "No PDF files found in the folder.")

    def disable_control_buttons(self):
        for widget in (
            self.save_button,
            self.replace_checkbox,
            self.canvas,
            self.unsaved_changes_listbox,
            self.prev_button,
            self.next_button,
            self.jump_button,
            self.rotate_button,
            self.delete_button,
        ):
            widget.configure(state="disabled")

    def enable_control_buttons(self):
        for widget in (
            self.save_button,
            self.replace_checkbox,
            self.canvas,
            self.unsaved_changes_listbox,
            self.prev_button,
            self.next_button,
            self.jump_button,
            self.rotate_button,
            self.delete_button,
        ):
            widget.configure(state="normal")

    def reset_session(self):
        self.pdf_files = []
        self.all_pages = []
        self.file_number = {}
        self.page_rotations = {}
        self.page_rotations_init = {}
        self.deleted_pages = {}
        self.unsaved_changes = {}
        self.total_files = 0
        self.num_pages = 0
        self.canvas.delete("all")
        self.file_name_label.config(text="")
        self.page_number_label.config(text="")
        self.page_info_label.config(text="")
        self.unsaved_changes_listbox.delete(0, tk.END)

        self.disable_control_buttons()

    def show_current_page(self):
        self.canvas.delete("all")
        file_path, page_index = self.all_pages[self.current_page]
        page_rotation = self.page_rotations[(file_path, page_index)]
        page_rotation_init = self.page_rotations_init[(file_path, page_index)]
        page_deleted = page_index in self.deleted_pages.get(file_path, set())

        doc = fitz.open(file_path)
        rotated_page = doc.load_page(page_index)
        rotated_page.set_rotation(page_rotation)

        if page_index in self.deleted_pages.get(file_path, set()):
            watermark_text = "EXTERMINATE"
            watermark_color = (
                0.9,
                0.2,
                0.2,
            )
            watermark_font_size = rotated_page.rect.width / 12

            watermark_width = fitz.get_text_length(
                watermark_text, "helvetica-bold", fontsize=watermark_font_size
            )
            watermark_x = (rotated_page.rect.width - watermark_width) / 2
            watermark_y = rotated_page.rect.height / 2

            rotated_page.insert_text(
                (watermark_x, watermark_y),
                watermark_text,
                fontsize=watermark_font_size,
                color=watermark_color,
                rotate=page_rotation,
                fontname="helvetica-bold",
            )

        pix = rotated_page.get_pixmap()
        doc.close()

        img_width, img_height = pix.width, pix.height
        scale_factor = min(self.canvas_width / img_width, self.canvas_height / img_height)
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)

        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img = img.resize((new_width, new_height), Image.ANTIALIAS)

        self.img_tk = ImageTk.PhotoImage(img)

        x_position = (self.canvas_width - new_width) / 2
        y_position = (self.canvas_height - new_height) / 2

        self.canvas.create_image(x_position, y_position, anchor=tk.NW, image=self.img_tk)

        self.file_name_label.config(
            text=f"File {self.file_number[file_path]}/{self.total_files}: {os.path.basename(file_path)}"
        )
        self.page_number_label.config(
            text=f"Page in file: {page_index + 1}/{len(PyPDF2.PdfReader(file_path).pages)}. Page in folder: {self.current_page + 1}/{self.num_pages}"
        )
        self.page_info_label.config(
            text=f"Rotation: {page_rotation}° (initial: {page_rotation_init}°), to delete: {'YES' if page_deleted else 'no'}"
        )

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_current_page()

    def next_page(self):
        if self.current_page < self.num_pages - 1:
            self.current_page += 1
            self.show_current_page()

    def jump_to_page(self):
        page_num = simpledialog.askinteger(
            "Jump to Page",
            "Enter the page number to jump to:",
            parent=self.root,
            minvalue=1,
            maxvalue=self.num_pages,
        )

        if page_num:
            page_index = page_num - 1
            self.current_page = page_index
            self.show_current_page()

    def rotate_page(self, degree=90):
        file_path, page_index = self.all_pages[self.current_page]
        self.page_rotations[(file_path, page_index)] = (
            self.page_rotations[(file_path, page_index)] + degree
        ) % 360
        self.show_current_page()
        self.update_unsaved_changes_listbox()

    def delete_page(self):
        file_path, page_index = self.all_pages[self.current_page]
        deleted_pages_set = self.deleted_pages.setdefault(file_path, set())

        if page_index in deleted_pages_set:
            deleted_pages_set.remove(page_index)
            self.unsaved_changes[file_path]["del"] -= 1
        else:
            deleted_pages_set.add(page_index)
            self.unsaved_changes[file_path]["del"] += 1

        self.show_current_page()
        self.update_unsaved_changes_listbox()

    def update_unsaved_changes_listbox(self):
        self.unsaved_changes_listbox.delete(0, tk.END)
        for file_path, changes in self.unsaved_changes.items():
            pages = len(PyPDF2.PdfReader(file_path).pages)
            changes["rot"] = 0
            for page in range(pages):
                if ((file_path, page) in self.page_rotations) and self.page_rotations[
                    (file_path, page)
                ] != self.page_rotations_init[(file_path, page)]:
                    changes["rot"] += 1
            num_rotations = changes["rot"]
            num_deletions = changes["del"]
            if num_rotations > 0 or num_deletions > 0:
                file_name = os.path.basename(file_path)
                self.unsaved_changes_listbox.insert(
                    tk.END, f"{file_name} (rot {num_rotations}, del {num_deletions})"
                )

    def save_changes(self):
        save_folder = self.output_folder
        replace_existing = self.replace_existing.get()

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        saved_files = []

        for file_path in self.unsaved_changes:
            changes = self.unsaved_changes[file_path]
            num_rotations = changes["rot"]
            num_deletions = changes["del"]
            if num_rotations > 0 or num_deletions > 0:
                pdf_reader = PyPDF2.PdfReader(file_path)
                pdf_writer = PyPDF2.PdfWriter()
                for i, page in enumerate(pdf_reader.pages):
                    if i not in self.deleted_pages.get(file_path, set()):
                        page.rotation = self.page_rotations[(file_path, i)]
                        pdf_writer.add_page(page)

                if replace_existing and os.path.exists(file_path):
                    with open(file_path, "wb") as f:
                        pdf_writer.write(f)
                else:
                    with open(
                        os.path.join(save_folder, os.path.basename(file_path)), "wb"
                    ) as f:
                        pdf_writer.write(f)

                saved_files.append(os.path.basename(file_path))

        self.deleted_pages.clear()
        self.unsaved_changes.clear()

        if saved_files:
            num_saved_files = len(saved_files)
            summary_message = (
                f"{num_saved_files} file(s) saved to {save_folder}:\n"
                + "\n".join(saved_files)
            )
            messagebox.showinfo("Saved", summary_message)
            self.load_files()
        else:
            messagebox.showinfo("No Changes", "No files were edited or saved.")


class CustomMessageBox(tk.Toplevel):
    def __init__(self, title, message, hyperlinks=None):
        super().__init__()
        self.title(title)
        self.message = message

        self.text = tk.Text(self, wrap="word", padx=7, pady=5)
        self.text.pack(fill=tk.BOTH, expand=True)

        self.text.insert(tk.END, self.message)

        self.hyperlinks = hyperlinks
        if self.hyperlinks:
            self.add_hyperlinks()

        self.ok_button = tk.Button(self, text="OK", command=self.destroy)
        self.ok_button.pack(pady=5)

    def add_hyperlinks(self):
        for hyperlink, url in self.hyperlinks.items():
            start_index = self.text.search(hyperlink, "1.0", tk.END)
            if start_index:
                end_index = f"{start_index}+{len(hyperlink)}c"
                self.text.tag_add(hyperlink, start_index, end_index)
                self.text.tag_configure(hyperlink, foreground="blue", underline=True)
                self.text.tag_bind(
                    hyperlink, "<Button-1>", lambda e, u=url: self.open_url(u)
                )

    def open_url(self, url):
        webbrowser.open(url)


def show_custom_message_box(title, message, hyperlinks=None):
    CustomMessageBox(title, message, hyperlinks).wait_window()


if __name__ == "__main__":
    app = PDFEditorApp()
