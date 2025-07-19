import tkinter as tk
from tkinter import messagebox
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

os.makedirs("screenshots", exist_ok=True)

# --- Step 0: Globals & Setup ---
dark_mode = False

# Main window
root = tk.Tk()
save_screenshot_var = tk.BooleanVar(value=True)

root.title("Personal Finance Tracker")
root.geometry("500x700")
root.configure(bg="#1ba89f")  # Light mode default

# --- Step 1: Welcome Label ---
label = tk.Label(
    root,
    text="Welcome to Finance Tracker!",
    font=("Helvetica", 16, "italic bold"),
    fg="#ffffff",
    bg="#1ba84a",
    pady=10
)
label.pack(pady=20)

# --- Step 2: Monthly Budget ---
budget_label = tk.Label(root, text="Monthly Budget (₹):", bg="#1ba84a", font=("Arial", 12), fg="white")
budget_label.pack()
budget_entry = tk.Entry(root)
budget_entry.pack(pady=5)


# --- Step 3: Horizontal Frame for Amount & Note ---
input_frame = tk.Frame(root, bg="#1ba84a")
input_frame.pack(pady=5)

# Amount inside input_frame
amount_label = tk.Label(input_frame, text="Amount (₹):", bg="#1ba84a", font=("Arial", 12), fg="white")
amount_label.pack(side="left", padx=5)
amount_entry = tk.Entry(input_frame, width=10)
amount_entry.pack(side="left", padx=5)

# Note inside input_frame
note_label = tk.Label(input_frame, text="Activity / Note:", bg="#1ba84a", font=("Arial", 12), fg="white")
note_label.pack(side="left", padx=5)
note_entry = tk.Entry(input_frame, width=15)
note_entry.pack(side="left", padx=5)


# Category
category_label = tk.Label(root, text="Category:", bg="#1ba84a", font=("Arial", 12), fg="white")
category_label.pack()
category_var = tk.StringVar()
category_var.set("Select Category")
categories = ["Food", "Transport", "Bills", "Entertainment", "Others"]
category_menu = tk.OptionMenu(root, category_var, *categories)
category_menu.pack(pady=5)

screenshot_checkbox = tk.Checkbutton(
    root,
    text="💾 Save Summary Chart as Screenshot",
    variable=save_screenshot_var,
    onvalue=True,
    offvalue=False,
    bg="#1ba84a",
    fg="white",
    font=("Arial", 10)
)
screenshot_checkbox.pack(pady=5)

# --- Step 4: Add Transaction ---
def add_transaction():
    amt = amount_entry.get()
    note = note_entry.get()
    category = category_var.get()
    date = datetime.now().strftime("%d-%m-%Y")

    if not amt or not note or category == "Select Category":
        messagebox.showwarning("⚠ Warning", "Please fill all fields.")
        return

    # Save budget
    budget_file = os.path.join("data", "budget.txt")
    budget_value = budget_entry.get()
    if budget_value:
        with open(budget_file, "w") as bf:
            bf.write(budget_value)
    elif os.path.exists(budget_file):
        with open(budget_file, "r") as bf:
            budget_value = bf.read()
    else:
        budget_value = "0"

    # Save transaction
    file_path = os.path.join("data", "transactions.csv")
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Amount", "Activity", "Category", "Date"])
        writer.writerow([amt, note, category, date])

    # Check budget limit
    total_spending = 0.0
    with open(file_path, mode='r') as file:
        next(file)
        for row in csv.reader(file):
            try:
                total_spending += float(row[0])
            except:
                pass

    try:
        if total_spending > float(budget_value):
            messagebox.showwarning("Budget Alert", f"Budget Exceeded!\nTotal Spent: ₹{total_spending}")
    except:
        pass

    # Clear fields
    amount_entry.delete(0, tk.END)
    note_entry.delete(0, tk.END)
    category_var.set("Select Category")

    print(f"Saved: ₹{amt}, {note}, {category}, {date}")

# --- Step 5: View History ---
def view_history():
    history_window = tk.Toplevel(root)
    history_window.title("Transaction History")
    history_window.geometry("400x400")
    history_window.configure(bg="#f5f5f5")

    heading = tk.Label(history_window, text="Transaction History", font=("Arial", 14, "bold"), bg="#f5f5f5")
    heading.pack(pady=10)

    file_path = os.path.join("data", "transactions.csv")
    if not os.path.exists(file_path):
        msg = tk.Label(history_window, text="No transactions found!", bg="#f5f5f5", fg="red")
        msg.pack()
        return

    with open(file_path, mode='r') as file:
        for line in file.readlines()[1:]:
            line = line.strip().split(",")
            if len(line) == 4:
                amt, activity, category, date = line
                label = tk.Label(history_window, text=f"₹{amt} | {activity} | {category} | {date}", bg="#f5f5f5", anchor="w", font=("Arial", 10))
                label.pack(padx=10, anchor="w")

# --- Step 7C: Clear All Transaction History ---
def clear_history():
    file_path = os.path.join("data", "transactions.csv")
    
    if not os.path.exists(file_path):
        messagebox.showinfo("No Data", "No transactions to clear.")
        return

    confirm = messagebox.askyesno("Confirm", "Are you sure you want to clear all history?")
    if confirm:
        try:
            with open(file_path, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Amount", "Activity", "Category", "Date"])  # Write header again
            messagebox.showinfo("Cleared", "All transaction history cleared.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear data.\n{str(e)}")

# --- Step 6: View Summary Pie Chart ---
def view_summary():
    file_path = os.path.join("data", "transactions.csv")
    if not os.path.exists(file_path):
        messagebox.showinfo("No Data", "No transactions found.")
        return

    transactions = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            transactions.append(row)

    if not transactions:
        messagebox.showinfo("No Data", "No transactions to summarize.")
        return

    expense_data = {}
    for t in transactions:
        if t["Category"] != "Income":
            cat = t["Category"]
            amt = float(t["Amount"])
            expense_data[cat] = expense_data.get(cat, 0) + amt

    if not expense_data:
        messagebox.showinfo("No Expenses", "No expense data to show.")
        return

    # Create Pie Chart
    plt.figure(figsize=(6, 6))
    plt.pie(expense_data.values(), labels=expense_data.keys(), autopct='%1.1f%%', startangle=140)
    plt.title("Expense Summary by Category")
    plt.tight_layout()

    if save_screenshot_var.get():
        filename = f"screenshots/pie_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename)
        print(f"Screenshot saved: {filename}")

    plt.show()

# --- Step 6B: View Budget vs Spending Chart ---
def view_budget_vs_spending():
    # Read budget
    budget_file = os.path.join("data", "budget.txt")
    if not os.path.exists(budget_file):
        messagebox.showinfo("No Budget", "No budget set.")
        return

    with open(budget_file, "r") as bf:
        try:
            budget = float(bf.read())
        except:
            messagebox.showerror("Error", "Invalid budget value.")
            return

    # Read total spending
    transactions_file = os.path.join("data", "transactions.csv")
    if not os.path.exists(transactions_file):
        messagebox.showinfo("No Data", "No transactions found.")
        return

    total_spent = 0.0
    with open(transactions_file, mode='r') as file:
        next(file)  # Skip header
        for row in csv.reader(file):
            try:
                amount = float(row[0])
                total_spent += amount
            except:
                continue

    # Show bar chart
    labels = ['Budget', 'Spent']
    values = [budget, total_spent]
    colors = ['green', 'red']

    plt.figure(figsize=(5, 5))
    plt.bar(labels, values, color=colors)
    plt.title("Budget vs Actual Spending")
    plt.ylabel("Amount (₹)")
    plt.tight_layout()

    if save_screenshot_var.get():
        filename = f"screenshots/budget_vs_spent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename)
        print(f"Screenshot saved: {filename}")

    plt.show()

# --- Step 7A: Export CSV Backup ---
def export_csv():
    source = os.path.join("data", "transactions.csv")
    dest = os.path.join("data", "backup.csv")

    if os.path.exists(source):
        with open(source, 'r') as src_file, open(dest, 'w', newline='') as dst_file:
            dst_file.write(src_file.read())
        messagebox.showinfo("Exported", "Data exported to backup.csv")
    else:
        messagebox.showwarning("No Data", "No transactions to export.")

# --- Step 7B: Dark Mode Toggle ---
def toggle_mode():
    global dark_mode
    dark_mode = not dark_mode

    bg_color = "#222222" if dark_mode else "#1ba84a"
    fg_color = "white" if dark_mode else "black"
    title_color = "#333333" if dark_mode else "#33a3cc"
    title_fg = "white" if dark_mode else "#6e0c0c"

    root.configure(bg=bg_color)
    widgets = root.winfo_children()
    for widget in widgets:
        try:
            widget.configure(bg=bg_color, fg=fg_color)
        except:
            pass
    label.configure(bg=title_color, fg=title_fg)

# --- Step 8: Buttons ---
add_btn = tk.Button(root, text="Add Transaction", command=add_transaction, bg="#4CAF50", fg="white", padx=10, pady=5)
add_btn.pack(pady=10)

history_btn = tk.Button(root, text="View History", command=view_history, bg="#2196F3", fg="white", padx=10, pady=5)
history_btn.pack(pady=10)

summary_btn = tk.Button(root, text="View Summary", command=view_summary, bg="#FF9800", fg="white", padx=10, pady=5)
summary_btn.pack(pady=10)

export_btn = tk.Button(root, text="Export as CSV", command=export_csv, bg="#9C27B0", fg="white", padx=10, pady=5)
export_btn.pack(pady=10)

budget_vs_btn = tk.Button(
    root,
    text="Budget vs Spending",
    command=view_budget_vs_spending,
    bg="#FFC107",
    fg="black",
    padx=10,
    pady=5
)
budget_vs_btn.pack(pady=10)

mode_btn = tk.Button(root, text="Toggle Dark Mode", command=toggle_mode, bg="#607D8B", fg="white", padx=10, pady=5)
mode_btn.pack(pady=10)

clear_btn = tk.Button(
    root,
    text="Clear History",
    command=clear_history,
    bg="#f44336",
    fg="white",
    padx=10,
    pady=5
)
clear_btn.pack(pady=10)

# Run App
root.mainloop()
