import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import seaborn as sns

root = tk.Tk()
root.title("Restaurant Sales Analytics Dashboard by kalavathi")
root.geometry("1270x690+0+0")
root.configure(bg="firebrick4")

topframe = tk.Frame(root, bd=10, relief=tk.RIDGE,bg="firebrick4")
topframe.pack(side=tk.TOP)

labeltitle=tk.Label(topframe,text="RESTAURANT MANAGEMENT SYSTEM",font=("arial",30,"bold"),fg="yellow",bg="red4",width=51,bd=9)
labeltitle.grid(row=0,column=0)


df = None
canvas = None  # Global canvas


def load_data():
    global df
    file_path = filedialog.askopenfilename(filetypes=[("Excel files","*.xlsx")])
    if file_path:
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()  # Remove spaces
            df['Date'] = pd.to_datetime(df['Date'])
            messagebox.showinfo("Success", "Excel Data Loaded Successfully!")
            display_summary()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel file:\n{e}")

summary_label = tk.Label(root, text="", font=("Arial", 12,"bold"), bg="#f2f2f2")
summary_label.pack(side=tk.BOTTOM,pady=10)

def display_summary():
    if df is not None:
        total_revenue = np.sum(df['Price'] * df['Quantity'])
        total_orders = np.sum(df['Quantity'])
        avg_order_value = total_revenue / total_orders
        summary_text = f"Total Revenue: Rs {total_revenue}\nTotal Orders: {total_orders}\nAverage Order Value: Rs {avg_order_value:.2f}"
        summary_label.config(text=summary_text)

def plot_revenue_trend():
    global canvas
    if df is not None:
        revenue_trend = df.groupby('Date').apply(lambda x: np.sum(x['Price']*x['Quantity']))
        fig, ax = plt.subplots(figsize=(7,7))
        sns.lineplot(x=revenue_trend.index, y=revenue_trend.values, marker='o', ax=ax)
        ax.set_title("Daily Revenue Trend")
        ax.set_xlabel("Date")
        ax.set_ylabel("Revenue")
        plt.xticks(rotation=45)

        if canvas:
            canvas.get_tk_widget().destroy()
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

def plot_popular_items():
    global canvas
    if df is not None:
        item_sales = df.groupby('Item')['Quantity'].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(7,7))
        sns.barplot(x=item_sales.index, y=item_sales.values, palette='viridis', ax=ax)
        ax.set_title("Most Popular Items")
        ax.set_xlabel("Item")
        ax.set_ylabel("Quantity Sold")
        plt.xticks(rotation=45)

        if canvas:
            canvas.get_tk_widget().destroy()
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)


# ================= MENU FRAME =================
menuframe = tk.Frame(root, bg="lightgray", bd=5, relief=tk.RIDGE)
menuframe.pack(side=tk.TOP, fill=tk.X)

# =============== BUTTONS INSIDE FRAME ===============
btn_read = tk.Button(menuframe, text="Read Excel File", width=20,
                     command=lambda: upload_file(), font=("arial",19,"bold"),
                     bg="yellow", bd=3, fg="black")
btn_read.pack(side=tk.LEFT, padx=5, pady=5)

btn_load = tk.Button(menuframe, text="Load Sales Excel", width=20,
                    command=load_data, font=("arial",19,"bold"),
                     bg="#4CAF50", bd=3, fg="black")
btn_load.pack(side=tk.LEFT, padx=5, pady=5)

btn_trend = tk.Button(menuframe, text="Show Revenue Trend", width=20,
                      command=plot_revenue_trend, font=("arial",19,"bold"),
                      bg="#2196F3", bd=3, fg="black")
btn_trend.pack(side=tk.LEFT, padx=5, pady=5)

btn_popular = tk.Button(menuframe, text="Show Popular Items", width=20,
                        command=plot_popular_items, font=("arial",19,"bold"),
                        bg="#FF5722", bd=3, fg="black")
btn_popular.pack(side=tk.LEFT, padx=5, pady=5)

# =============== TEXT BOX ========================
t1 = tk.Text(root, height=30, width=60, bg="white")
t1.pack(side=tk.LEFT,pady=10)

# Example function
def upload_file():
    file = filedialog.askopenfilename(filetypes=[("Excel file",".xlsx")])
    if file:
        df = pd.read_excel(file)
        t1.insert(tk.END, df.head())

root.mainloop()
 





