import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import random
import os

def assign_seats(df, num_halls, seats_per_hall):
    total_seats = num_halls * seats_per_hall
    if len(df) > total_seats:
        raise ValueError("Not enough seats for all students!")

    
    dept_groups = {dept: list(rows.itertuples(index=False, name=None)) for dept, rows in df.groupby("Department")}

   
    interleaved = []
    while any(dept_groups.values()):
        for dept in list(dept_groups.keys()):
            if dept_groups[dept]:
                interleaved.append(dept_groups[dept].pop(0))

   
    random.shuffle(interleaved)

    
    for i in range(1, len(interleaved)):
        if interleaved[i][2] == interleaved[i - 1][2]:
            for j in range(i + 1, len(interleaved)):
                if interleaved[j][2] != interleaved[i][2]:
                    interleaved[i], interleaved[j] = interleaved[j], interleaved[i]
                    break

    # Create final seating plan
    seating_plan = {}
    student_index = 0
    for hall in range(1, num_halls + 1):
        hall_students = []
        for seat in range(1, seats_per_hall + 1):
            if student_index < len(interleaved):
                row = interleaved[student_index]
                hall_students.append({
                    "Name": row[0],
                    "Register No": row[1],
                    "Department": row[2],
                })
                student_index += 1
        seating_plan[f"Hall {hall}"] = hall_students

    return seating_plan


def browse_file():
    file_path = filedialog.askopenfilename(
        title="Select Student CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )
    if file_path:
        file_label.config(text=os.path.basename(file_path))
        global csv_path
        csv_path = file_path


def generate_plan():
    try:
        if not csv_path:
            messagebox.showerror("Error", "Please load a student CSV file first!")
            return

        num_halls = int(halls_entry.get())
        seats_per_hall = int(seats_entry.get())

        df = pd.read_csv(csv_path)
        required_cols = {"Name", "Register No", "Department"}
        if not required_cols.issubset(df.columns):
            messagebox.showerror("Error", "CSV must contain Name, Register No, and Department columns.")
            return

        seating_plan = assign_seats(df, num_halls, seats_per_hall)
        display_plan(seating_plan)

    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for halls and seats!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")


def display_plan(seating_plan):
    for widget in result_frame.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(result_frame, bg="#0a192f", highlightthickness=0)
    scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    for hall, students in seating_plan.items():
        hall_label = tk.Label(scrollable_frame, text=hall, font=("Segoe UI", 14, "bold"), bg="#112240", fg="#64ffda", pady=5)
        hall_label.pack(fill="x", pady=5)

        columns = ("Name", "Register No", "Department")
        tree = ttk.Treeview(scrollable_frame, columns=columns, show="headings", height=8)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200, anchor="center")

        for s in students:
            tree.insert("", "end", values=(s["Name"], s["Register No"], s["Department"]))

        tree.pack(fill="x", pady=5)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


# GUI Setup
root = tk.Tk()
root.title("AI-Based Exam Hall Seating Planner v4.0")
root.geometry("900x600")
root.configure(bg="#0a192f")

title_label = tk.Label(root, text="🎓 AI-Based Exam Hall Seating Planner", font=("Segoe UI", 18, "bold"), bg="#0a192f", fg="#64ffda")
title_label.pack(pady=15)

main_frame = tk.Frame(root, bg="#112240", bd=2, relief="groove")
main_frame.pack(pady=10, padx=20, fill="x")

load_btn = tk.Button(main_frame, text="📂 Load Student CSV", command=browse_file, bg="#1f4068", fg="white", font=("Segoe UI", 11, "bold"), padx=10, pady=5)
load_btn.grid(row=0, column=0, padx=10, pady=10)

file_label = tk.Label(main_frame, text="No file selected", bg="#112240", fg="lightgray", font=("Segoe UI", 10))
file_label.grid(row=0, column=1, padx=10, pady=10)

tk.Label(main_frame, text="No. of Halls:", bg="#112240", fg="white", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="e", padx=10)
halls_entry = tk.Entry(main_frame, width=10)
halls_entry.grid(row=1, column=1, sticky="w", padx=10)

tk.Label(main_frame, text="Seats per Hall:", bg="#112240", fg="white", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="e", padx=10)
seats_entry = tk.Entry(main_frame, width=10)
seats_entry.grid(row=2, column=1, sticky="w", padx=10)

generate_btn = tk.Button(main_frame, text="💡 Generate Seating Plan", command=generate_plan, bg="#00b894", fg="white", font=("Segoe UI", 11, "bold"), padx=10, pady=5)
generate_btn.grid(row=3, column=0, columnspan=2, pady=15)

result_frame = tk.Frame(root, bg="#0a192f")
result_frame.pack(fill="both", expand=True, padx=20, pady=10)

csv_path = None
root.mainloop()
