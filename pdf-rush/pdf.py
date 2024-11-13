import sys, os
import PyPDF2

def load_files(self):
    if not self.pdf_files:
        messagebox.showinfo("No Files Found", "No PDF files found in the folder.")
        return

    self.reset_file_data()
    self.load_pdf_files()
    self.update_ui_after_loading_files()

def reset_file_data(self):
    self.all_pages = []
    self.page_rotations = {}
    self.page_rotations_init = {}
    self.deleted_pages = {}
    self.unsaved_changes = {}
    self.total_files = len(self.pdf_files)
    self.file_number = {}
    self.file_pages = {}

def load_pdf_files(self):
    file_count = 0
    for pdf_file in self.pdf_files:
        file_path = os.path.join(self.current_folder, pdf_file)
        try:
            self.load_pdf_file(file_path, file_count)
            file_count += 1
        except:
            messagebox.showinfo("Oops...", f"Failed to open {file_path}")
            continue

def load_pdf_file(self, file_path, file_count):
    pdf_reader = PyPDF2.PdfReader(file_path)
    for i, page in enumerate(pdf_reader.pages):
        self.all_pages.append((file_path, i))
        self.page_rotations[(file_path, i)] = page.rotation
        self.page_rotations_init[(file_path, i)] = page.rotation
    self.unsaved_changes[file_path] = {"rot": 0, "del": 0}
    self.file_number[file_path] = file_count
    self.file_pages[file_path] = len(pdf_reader.pages)

def update_ui_after_loading_files(self):
    self.num_pages = len(self.all_pages)
    self.current_page = min(self.num_pages - 1, self.current_page)

    self.folder_info_label.config(
        text=f"Folder: {os.path.basename(self.current_folder)}"
    )

    self.show_current_page()
    self.update_unsaved_changes_listbox()

    self.enable_control_buttons()
