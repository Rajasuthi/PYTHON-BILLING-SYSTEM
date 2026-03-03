import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

items = []

def add_item():
    name = item_entry.get()
    qty = qty_entry.get()
    price = price_entry.get()

    if name == "" or qty == "" or price == "":
        messagebox.showwarning("Alert", "All fields are required!")
        return

    qty = int(qty)
    price = float(price)
    total = qty * price

    items.append({"Item": name, "Qty": qty, "Rate": price, "Total": total})

    table.insert("", tk.END, values=(name, qty, price, total))
    update_total()

    item_entry.delete(0, tk.END)
    qty_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

def update_total():
    total = sum(i["Total"] for i in items)
    total_label.config(text=f"Total: ₹{total}")

def save_csv():
    if not items:
        messagebox.showerror("Error", "Add items first!")
        return
    
    df = pd.DataFrame(items)
    df.to_csv("grocery_bill.csv", index=False)
    messagebox.showinfo("Saved", "Bill saved as grocery_bill.csv")

root = tk.Tk()
root.title("Grocery Billing Backend - Tkinter + Pandas")
root.geometry("500x500")

tk.Label(root, text="🛒 Grocery Billing (Backend)", font=("Arial",18,"bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack()

tk.Label(frame, text="Item:").grid(row=0, column=0)
item_entry = tk.Entry(frame)
item_entry.grid(row=0, column=1)

tk.Label(frame, text="Qty:").grid(row=1, column=0)
qty_entry = tk.Entry(frame)
qty_entry.grid(row=1, column=1)

tk.Label(frame, text="Rate:").grid(row=2, column=0)
price_entry = tk.Entry(frame)
price_entry.grid(row=2, column=1)

tk.Button(root, text="Add Item", command=add_item).pack(pady=5)

columns = ("Item", "Qty", "Rate", "Total")
table = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    table.heading(col, text=col)
table.pack()

total_label = tk.Label(root, text="Total: ₹0", font=("Arial",14,"bold"), fg="green")
total_label.pack(pady=10)

tk.Button(root, text="Save Bill (CSV)", command=save_csv).pack()

root.mainloop()
