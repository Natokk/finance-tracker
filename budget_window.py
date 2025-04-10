import tkinter as tk
from tkinter import ttk, messagebox

class BudgetWindow(tk.Toplevel):
    def __init__(self, parent, tracker):
        super().__init__(parent)
        self.tracker = tracker
        self.title("Budget Management")
        self.geometry("400x300")
        
        self.setup_ui()
        self.load_budgets()
        
    def setup_ui(self):
        # Budget entry frame
        entry_frame = ttk.Frame(self)
        entry_frame.pack(pady=10)
        
        ttk.Label(entry_frame, text="Category:").grid(row=0, column=0, padx=5)
        self.category_entry = ttk.Entry(entry_frame)
        self.category_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(entry_frame, text="Amount:").grid(row=1, column=0, padx=5)
        self.amount_entry = ttk.Entry(entry_frame)
        self.amount_entry.grid(row=1, column=1, padx=5)
        
        ttk.Button(entry_frame, text="Set Budget", 
                  command=self.set_budget).grid(row=2, columnspan=2, pady=10)
        
        # Budget list
        self.tree = ttk.Treeview(self, columns=("Category", "Budget", "Spent"), show="headings")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Budget", text="Budget")
        self.tree.heading("Spent", text="Spent")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
    def load_budgets(self):
        self.tree.delete(*self.tree.get_children())
        status = self.tracker.get_budget_status()
        for category, data in status.items():
            self.tree.insert("", "end", values=(
                category, 
                f"${data['budget']:.2f}", 
                f"${data['spent']:.2f}"
            ))
    
    def set_budget(self):
        category = self.category_entry.get().strip()
        amount = self.amount_entry.get().strip()
        
        if not category or not amount:
            messagebox.showwarning("Warning", "Please enter both category and amount")
            return
            
        if self.tracker.set_budget(category, amount):
            messagebox.showinfo("Success", "Budget set successfully!")
            self.load_budgets()
        else:
            messagebox.showerror("Error", "Invalid budget amount")