# restaurant_billing_app.py
"""
Restaurant Order & Billing System (Tkinter + pandas)
Features:
 - Predefined menu with prices
 - Enter quantities, add items to cart
 - Remove items, clear cart
 - Subtotal, Tax (GST), Discount, Grand Total
 - Save bill: append to bills_data.csv (pandas)
 - Generate HTML invoice and open in browser (invoices/ folder)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import datetime
import os
import webbrowser

# ---------- Configuration ----------
OUTDIR = "invoices"
os.makedirs(OUTDIR, exist_ok=True)
BILLS_CSV = "bills_data.csv"

GST_PERCENT = 5.0  # change if needed

# Example Menu (you can change items/prices)
MENU = {
    "Idli": 30.0,
    "Dosa": 50.0,
    "Poori": 60.0,
    "Fried Rice": 80.0,
    "Noodles": 85.0,
    "Parotta": 20.0,
    "Chicken Biryani": 120.0,
    "Meals": 90.0,
    "Paneer Butter Masala": 150.0,
    "Gulab Jamun (2pcs)": 40.0
}


# ---------- App ----------
class RestaurantBillingApp:
    def __init__(self, root):
        self.root = root
        root.title("Restaurant Order & Billing System")
        root.geometry("900x600")

        self.cart = []  # list of dicts: {'item','qty','rate','amount'}
        self.create_ui()
        self.update_totals()

    def create_ui(self):
        # Top frame - Customer details
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill='x')
        ttk.Label(top, text="Customer Name:").grid(row=0, column=0, sticky='w')
        self.cust_name = ttk.Entry(top, width=25)
        self.cust_name.grid(row=0, column=1, padx=6)
        ttk.Label(top, text="Phone:").grid(row=0, column=2, sticky='w')
        self.cust_phone = ttk.Entry(top, width=20)
        self.cust_phone.grid(row=0, column=3, padx=6)
        ttk.Label(top, text="Table / Order No:").grid(row=0, column=4, sticky='w')
        self.order_no = ttk.Entry(top, width=12)
        self.order_no.grid(row=0, column=5, padx=6)

        # Middle frame - Menu and controls
        mid = ttk.Frame(self.root, padding=8)
        mid.pack(fill='x')

        # Menu List
        menu_frame = ttk.LabelFrame(mid, text="Menu", padding=8)
        menu_frame.pack(side='left', fill='y', padx=6)

        self.qty_vars = {}  # maps item -> tk.IntVar for qty input

        for i, (name, price) in enumerate(MENU.items()):
            lbl = ttk.Label(menu_frame, text=f"{name} — ₹{price:.2f}", width=28)
            lbl.grid(row=i, column=0, sticky='w', padx=4, pady=2)
            v = tk.IntVar(value=0)
            sp = ttk.Spinbox(menu_frame, from_=0, to=100, textvariable=v, width=5)
            sp.grid(row=i, column=1, padx=4)
            self.qty_vars[name] = v

        btn_add_selected = ttk.Button(menu_frame, text="Add Selected Items", command=self.add_selected_items)
        btn_add_selected.grid(row=len(MENU), column=0, columnspan=2, pady=8)

        # Cart frame
        cart_frame = ttk.LabelFrame(mid, text="Cart", padding=8)
        cart_frame.pack(side='left', fill='both', expand=True, padx=6)

        cols = ("Item", "Qty", "Rate", "Amount")
        self.tree = ttk.Treeview(cart_frame, columns=cols, show='headings', height=15)
        for c in cols:
            self.tree.heading(c, text=c)
        self.tree.column("Item", width=300)
        self.tree.column("Qty", width=60, anchor='center')
        self.tree.column("Rate", width=80, anchor='e')
        self.tree.column("Amount", width=100, anchor='e')
        self.tree.pack(side='left', fill='both', expand=True)

        sc = ttk.Scrollbar(cart_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sc.set)
        sc.pack(side='right', fill='y')

        # Controls under cart
        ctrls = ttk.Frame(self.root, padding=8)
        ctrls.pack(fill='x')

        ttk.Button(ctrls, text="Remove Selected", command=self.remove_selected).grid(row=0, column=0, padx=6)
        ttk.Button(ctrls, text="Clear Cart", command=self.clear_cart).grid(row=0, column=1, padx=6)

        # Totals & billing options
        right = ttk.Frame(self.root, padding=8)
        right.pack(fill='x')

        self.sub_var = tk.StringVar(value="₹0.00")
        self.gst_var = tk.StringVar(value=f"₹0.00 ({GST_PERCENT}%)")
        self.disc_var = tk.DoubleVar(value=0.0)  # discount percent
        self.total_var = tk.StringVar(value="₹0.00")

        ttk.Label(right, text="Subtotal:").grid(row=0, column=0, sticky='w')
        ttk.Label(right, textvariable=self.sub_var).grid(row=0, column=1, sticky='w', padx=6)
        ttk.Label(right, text="GST (%):").grid(row=1, column=0, sticky='w')
        ttk.Label(right, textvariable=self.gst_var).grid(row=1, column=1, sticky='w', padx=6)

        ttk.Label(right, text="Discount % (optional):").grid(row=2, column=0, sticky='w')
        self.entry_disc = ttk.Entry(right, textvariable=self.disc_var, width=8)
        self.entry_disc.grid(row=2, column=1, sticky='w', padx=6)

        ttk.Label(right, text="Grand Total:", font=('TkDefaultFont', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=8)
        ttk.Label(right, textvariable=self.total_var, font=('TkDefaultFont', 10, 'bold')).grid(row=3, column=1, sticky='w', padx=6)

        # Action buttons
        actions = ttk.Frame(self.root, padding=8)
        actions.pack(fill='x')
        ttk.Button(actions, text="Save Bill (CSV + HTML)", command=self.save_bill).grid(row=0, column=0, padx=6)
        ttk.Button(actions, text="Load All Bills (Open CSV)", command=self.open_bills_csv).grid(row=0, column=1, padx=6)
        ttk.Button(actions, text="New Order (Clear Form)", command=self.new_order).grid(row=0, column=2, padx=6)

    # ---------- Cart operations ----------
    def add_selected_items(self):
        added_any = False
        for item, var in self.qty_vars.items():
            q = int(var.get())
            if q > 0:
                rate = float(MENU[item])
                amount = round(q * rate, 2)
                self.cart.append({'item': item, 'qty': q, 'rate': rate, 'amount': amount})
                added_any = True
                var.set(0)  # reset spinbox
        if not added_any:
            messagebox.showinfo("No items", "Select quantity > 0 for items you want to add.")
            return
        self.refresh_tree()
        self.update_totals()

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for it in self.cart:
            self.tree.insert('', 'end', values=(it['item'], it['qty'], f"{it['rate']:.2f}", f"{it['amount']:.2f}"))

    def remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select an item in cart to remove.")
            return
        idxs = [self.tree.index(s) for s in sel]
        for ix in sorted(idxs, reverse=True):
            try:
                del self.cart[ix]
            except IndexError:
                pass
        self.refresh_tree()
        self.update_totals()

    def clear_cart(self):
        if messagebox.askyesno("Confirm", "Clear whole cart?"):
            self.cart = []
            self.refresh_tree()
            self.update_totals()

    # ---------- Totals ----------
    def update_totals(self):
        subtotal = round(sum(item['amount'] for item in self.cart), 2)
        gst_amount = round(subtotal * (GST_PERCENT / 100.0), 2)
        disc_percent = max(0.0, float(self.disc_var.get() or 0.0))
        after_gst = subtotal + gst_amount
        discount_amount = round(after_gst * (disc_percent / 100.0), 2)
        grand_total = round(after_gst - discount_amount, 2)

        self.sub_var.set(f"₹{subtotal:.2f}")
        self.gst_var.set(f"₹{gst_amount:.2f} ({GST_PERCENT}%)")
        self.total_var.set(f"₹{grand_total:.2f}")

    # ---------- Save bill ----------
    def save_bill(self):
        if not self.cart:
            messagebox.showerror("Empty", "Cart is empty — add items before saving.")
            return

        now = datetime.datetime.now()
        invoice_no = now.strftime("%Y%m%d_%H%M%S")
        cust = self.cust_name.get().strip() or "Customer"
        phone = self.cust_phone.get().strip()
        order_label = self.order_no.get().strip() or ""

        subtotal = round(sum(it['amount'] for it in self.cart), 2)
        gst_amount = round(subtotal * (GST_PERCENT / 100.0), 2)
        disc_percent = max(0.0, float(self.disc_var.get() or 0.0))
        after_gst = subtotal + gst_amount
        discount_amount = round(after_gst * (disc_percent / 100.0), 2)
        grand_total = round(after_gst - discount_amount, 2)

        # Save master CSV row (one row per bill, with summary)
        bills_row = {
            'invoice_no': invoice_no,
            'date': now.strftime("%Y-%m-%d %H:%M:%S"),
            'customer': cust,
            'phone': phone,
            'order_label': order_label,
            'subtotal': subtotal,
            'gst': gst_amount,
            'discount_percent': disc_percent,
            'discount_amount': discount_amount,
            'grand_total': grand_total
        }
        # Append to CSV via pandas
        df_row = pd.DataFrame([bills_row])
        if os.path.exists(BILLS_CSV):
            df_row.to_csv(BILLS_CSV, mode='a', header=False, index=False)
        else:
            df_row.to_csv(BILLS_CSV, index=False)

        # Save invoice details (items) as CSV too (optional). We'll embed in HTML invoice.
        invoice_html = self.generate_invoice_html(invoice_no, now, cust, phone, order_label,
                                                  subtotal, gst_amount, disc_percent, discount_amount, grand_total, self.cart)
        invoice_path = os.path.join(OUTDIR, f"invoice_{invoice_no}.html")
        with open(invoice_path, "w", encoding="utf-8") as f:
            f.write(invoice_html)

        messagebox.showinfo("Saved", f"Bill saved.\nInvoice: {invoice_path}\nMaster record: {BILLS_CSV}")
        # Open invoice in browser
        webbrowser.open('file://' + os.path.realpath(invoice_path))

        # Reset for new order
        self.new_order(clear_customer=False)

    def generate_invoice_html(self, invoice_no, now, cust, phone, order_label,
                              subtotal, gst_amount, disc_percent, discount_amount, grand_total, items):
        css = """
            body { font-family: Arial, sans-serif; margin: 20px; }
            .box { max-width: 800px; border: 1px solid #ddd; padding: 20px; }
            h1 { margin: 0 0 10px 0; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background: #f4f4f4; }
            .right { text-align: right; }
            .total-row td { font-weight: bold; }
        """
        rows = ""
        for it in items:
            rows += f"<tr><td>{it['item']}</td><td class='right'>{it['qty']}</td><td class='right'>₹{it['rate']:.2f}</td><td class='right'>₹{it['amount']:.2f}</td></tr>\n"

        html = f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>Invoice {invoice_no}</title><style>{css}</style></head>
<body bgcolor="cyan">
<div class="box">
  <h1>Restaurant Invoice</h1>
  <div><strong>Invoice No:</strong> {invoice_no}</div>
  <div><strong>Date:</strong> {now.strftime('%Y-%m-%d %H:%M:%S')}</div>
  <div><strong>Customer:</strong> {cust} &nbsp;&nbsp; <strong>Phone:</strong> {phone} &nbsp;&nbsp; <strong>Order:</strong> {order_label}</div>

  <table>
    <thead><tr><th>Item</th><th class="right">Qty</th><th class="right">Rate</th><th class="right">Amount</th></tr></thead>
    <tbody>{rows}</tbody>
    <tfoot>
      <tr class="total-row"><td colspan="3" class="right">Subtotal</td><td class="right">₹{subtotal:.2f}</td></tr>
      <tr class="total-row"><td colspan="3" class="right">GST ({GST_PERCENT}%)</td><td class="right">₹{gst_amount:.2f}</td></tr>
      <tr class="total-row"><td colspan="3" class="right">Discount ({disc_percent}%)</td><td class="right">- ₹{discount_amount:.2f}</td></tr>
      <tr class="total-row"><td colspan="3" class="right">Grand Total</td><td class="right">₹{grand_total:.2f}</td></tr>
    </tfoot>
  </table>

  <p style="margin-top:20px;">Thank you for dining with us!</p>
</div>
</body>
</html>
"""
        return html

    def open_bills_csv(self):
        if not os.path.exists(BILLS_CSV):
            messagebox.showinfo("No data", "No bills saved yet.")
            return
        webbrowser.open('file://' + os.path.realpath(BILLS_CSV))

    def new_order(self, clear_customer=True):
        if messagebox.askyesno("New Order", "Start new order? (This will clear the cart)"):
            self.cart = []
            self.refresh_tree()
            self.disc_var.set(0.0)
            self.update_totals()
            if clear_customer:
                self.cust_name.delete(0, tk.END)
                self.cust_phone.delete(0, tk.END)
                self.order_no.delete(0, tk.END)

# ---------- Run ----------
if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#5DC5C5")  # Light blue background
    app = RestaurantBillingApp(root)

    # Periodically update totals in case discount entry changed by user
    def periodic_update():
        try:
            app.update_totals()
        except Exception:
            pass
        root.after(700, periodic_update)
    root.after(700, periodic_update)

    root.mainloop()
