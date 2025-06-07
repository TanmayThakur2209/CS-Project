import os
import csv
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry
from tkinter import ttk


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AttendanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Tracker")
        self.root.geometry("1080x720")
        self.root.iconbitmap("C:/Users/Tanmay Thakur/Desktop/CS Project/face_expression_smile_sad_emotion_emoticon_icon_262144.ico")

        self.attendance_file = "attendance.csv"
        self.attendance = self.load_attendance()
        self.Subjects = list(self.attendance.keys())

        self.create_topbar()

        self.tabview = ctk.CTkTabview(root)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        self.mark_tab = self.tabview.add("Mark Attendance")
        self.view_tab = self.tabview.add("View Records")
        self.export_tab = self.tabview.add("Export Data")
        self.visual_tab = self.tabview.add("Visualize")

        self.create_mark_tab()
        self.create_view_tab()
        self.create_export_tab()
        self.create_visual_tab()

    def create_topbar(self):
        topbar = ctk.CTkFrame(self.root)
        topbar.pack(fill=ctk.X, padx=10, pady=(10, 0))

        ctk.CTkButton(topbar, text="Add Subject", command=self.add_Subject).pack(side="left", padx=5)
        ctk.CTkButton(topbar, text="Remove Subject", command=self.remove_Subject).pack(side="left", padx=5)

    def create_mark_tab(self):
        date_frame = ctk.CTkFrame(self.mark_tab)
        date_frame.pack(pady=10)

        ctk.CTkLabel(date_frame, text="Select Date:").pack(side="left")

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TCombobox", fieldbackground="white", background="white")

        self.date_entry = DateEntry(date_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.set_date(datetime.today())
        self.date_entry.pack(side="left", padx=5)

        self.attendance_listbox = ctk.CTkScrollableFrame(self.mark_tab, height=400)
        self.attendance_listbox.pack(fill="both", expand=True, padx=10, pady=5)

        self.update_attendance_list()

        button_frame = ctk.CTkFrame(self.mark_tab)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Mark Present", command=self.mark_present).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Mark Absent", command=self.mark_absent).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Select All", command=self.select_all).pack(side="left", padx=5)

    def create_view_tab(self):
        self.view_frame = ctk.CTkScrollableFrame(self.view_tab)
        self.view_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.update_view_records()

    def create_export_tab(self):
        export_frame = ctk.CTkFrame(self.export_tab)
        export_frame.pack(pady=20)

        ctk.CTkLabel(export_frame, text="Export File Name:").pack(side="left", padx=5)
        self.export_entry = ctk.CTkEntry(export_frame, width=250)
        self.export_entry.pack(side="left", padx=5)

        default_filename = f"attendance_export_{datetime.today().strftime('%Y%m%d')}.csv"
        self.export_entry.insert(0, default_filename)

        ctk.CTkButton(export_frame, text="Export CSV", command=self.export_data).pack(side="left", padx=5)

    def create_visual_tab(self):
        frame = ctk.CTkFrame(self.visual_tab)
        frame.pack(pady=20)

        ctk.CTkLabel(frame, text="Select Subject:").pack(side="left", padx=5)
        self.selected_Subject = ctk.StringVar()
        self.Subject_menu = ctk.CTkOptionMenu(frame, variable=self.selected_Subject, command=self.update_pie_chart)
        self.Subject_menu.pack(side="left", padx=5)

        self.chart_frame = ctk.CTkFrame(self.visual_tab)
        self.chart_frame.pack(fill="both", expand=True)

        self.update_Subject_menu()

    def update_Subject_menu(self):
        sorted_names = sorted(self.Subjects)
        if sorted_names:
            self.Subject_menu.configure(values=sorted_names)
            self.selected_Subject.set(sorted_names[0])
            self.update_pie_chart()

    def update_pie_chart(self, subject=None):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        name = self.selected_Subject.get()
        if not name:
            return

        data = self.attendance.get(name, {})
        present = sum(1 for s in data.values() if s == "Present")
        absent = sum(1 for s in data.values() if s == "Absent")

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie([present, absent], labels=["Present", "Absent"], autopct='%1.1f%%',
               colors=['#4CAF50', '#F44336'], startangle=90)
        ax.set_title(f"Attendance for {name}")

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def load_attendance(self):
        attendance = {}
        if os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'r') as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    if row:
                        name = row[0]
                        present_dates = row[1].split(';') if len(row) > 1 and row[1] else []
                        absent_dates = row[2].split(';') if len(row) > 2 and row[2] else []
                        attendance[name] = {}
                        for date in present_dates:
                            attendance[name][date] = "Present"
                        for date in absent_dates:
                            attendance[name][date] = "Absent"
        return attendance

    def save_attendance(self):
        with open(self.attendance_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Dates Attended", "Dates Not Attended"])
            for name, date_status in self.attendance.items():
                present_dates = [date for date, status in date_status.items() if status == "Present"]
                absent_dates = [date for date, status in date_status.items() if status == "Absent"]
                writer.writerow([name, ';'.join(present_dates), ';'.join(absent_dates)])

    def add_Subject(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add Subject")
        dialog.geometry("400x180")
        dialog.grab_set()

        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{x}+{y}")

        ctk.CTkLabel(dialog, text="Enter Subject name:", font=ctk.CTkFont(size=16)).pack(pady=(20, 10))
        entry = ctk.CTkEntry(dialog, width=300, font=ctk.CTkFont(size=14))
        entry.pack(pady=10)
        entry.focus()

        name_var = {"value": None}

        def submit():
            name_var["value"] = entry.get()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Submit", command=submit).pack(pady=10)

        self.root.wait_window(dialog)
        name = name_var["value"]

        if name:

            if name in self.attendance:
                messagebox.showerror("Error", f"{name} already exists!")
            else:
                self.attendance[name] = {}
                self.Subjects.append(name)
                self.save_attendance()
                self.update_attendance_list()
                self.update_view_records()
                self.update_Subject_menu()
                messagebox.showinfo("Success", f"{name} added successfully!")

    def remove_Subject(self):

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add Subject")
        dialog.geometry("400x180")
        dialog.grab_set()


        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{x}+{y}")

        ctk.CTkLabel(dialog, text="Enter Subject name to remove:", font=ctk.CTkFont(size=16)).pack(pady=(20, 10))
        entry = ctk.CTkEntry(dialog, width=300, font=ctk.CTkFont(size=14))
        entry.pack(pady=10)
        entry.focus()

        name_var = {"value": None}

        def submit():
            name_var["value"] = entry.get()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Submit", command=submit).pack(pady=10)

        self.root.wait_window(dialog)
        name = name_var["value"]
        if name:
            if name in self.attendance:
                confirm = messagebox.askyesno("Confirm", f"Are you sure you want to remove {name}?")
                if confirm:
                    del self.attendance[name]
                    self.Subjects.remove(name)
                    self.save_attendance()
                    self.update_attendance_list()
                    self.update_view_records()
                    self.update_Subject_menu()
                    messagebox.showinfo("Success", f"{name} removed successfully!")
            else:
                messagebox.showerror("Error", f"{name} not found!")

    def is_valid_date(self, date_str):
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def mark_present(self):
        date = self.date_entry.get()
        if not self.is_valid_date(date):
            messagebox.showerror("Invalid Date", "Use YYYY-MM-DD format.")
            return
        for checkbox in self.attendance_listbox.winfo_children():
            if checkbox.get():
                self.attendance[checkbox.cget("text")][date] = "Present"
        self.save_attendance()
        self.update_view_records()
        self.update_pie_chart()

    def mark_absent(self):
        date = self.date_entry.get()
        if not self.is_valid_date(date):
            messagebox.showerror("Invalid Date", "Use YYYY-MM-DD format.")
            return
        for checkbox in self.attendance_listbox.winfo_children():
            if checkbox.get():
                self.attendance[checkbox.cget("text")][date] = "Absent"
        self.save_attendance()
        self.update_view_records()
        self.update_pie_chart()

    def select_all(self):
        for checkbox in self.attendance_listbox.winfo_children():
            checkbox.select()

    def update_attendance_list(self):
        for widget in self.attendance_listbox.winfo_children():
            widget.destroy()
        for name in sorted(self.attendance.keys()):
            ctk.CTkCheckBox(self.attendance_listbox, text=name).pack(anchor="w", pady=2)

    def update_view_records(self):
        for widget in self.view_frame.winfo_children():
            widget.destroy()

        headers = ["Subject", "Total Days", "Present", "Absent"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.view_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=10, pady=5)

        all_dates = set()
        for record in self.attendance.values():
            all_dates.update(record.keys())
        total_days = len(all_dates)

        for row_idx, (name, dates) in enumerate(sorted(self.attendance.items()), start=1):
            present = sum(1 for status in dates.values() if status == "Present")
            absent = sum(1 for status in dates.values() if status == "Absent")
            values = [name, total_days, present, absent]
            for col_idx, val in enumerate(values):
                ctk.CTkLabel(self.view_frame, text=str(val)).grid(row=row_idx, column=col_idx, padx=10, pady=2)

    def export_data(self):
        filename = self.export_entry.get()
        if filename:
            try:
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Name", "Dates Attended", "Dates Not Attended"])
                    for name, data in self.attendance.items():
                        present = [date for date, status in data.items() if status == "Present"]
                        absent = [date for date, status in data.items() if status == "Absent"]
                        writer.writerow([name, ';'.join(present), ';'.join(absent)])
                messagebox.showinfo("Success", f"Data exported to {filename} successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
        else:
            messagebox.showerror("Error", "Please enter a filename!")

if __name__ == "__main__":
    root = ctk.CTk()
    app = AttendanceTracker(root)
    root.mainloop()