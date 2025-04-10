import tkinter as tk
from tkinter import ttk, messagebox, font, simpledialog
from tracker import FinanceTracker
from visualization import create_spending_heatmap, create_spending_sparkline
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# Set matplotlib backend
matplotlib.use('TkAgg')

class FinanceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.tracker = FinanceTracker()
        self.dark_mode = False
        self.setup_ui()
        self.update_ui(full_refresh=True)
        
    def setup_ui(self):
        self.root.title("Finance Tracker Pro")
        self.root.geometry("1100x800")
        self.root.minsize(900, 700)
        
        # Font setup
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(size=9)
        self.bold_font = font.Font(weight="bold")
        self.title_font = font.Font(size=11, weight="bold")
        
        # Color schemes
        self.light_colors = {
            "primary": "#3498db", "secondary": "#7f8c8d", "success": "#2ecc71",
            "danger": "#e74c3c", "warning": "#f39c12", "dark": "#2c3e50",
            "light": "#ecf0f1", "white": "#ffffff", "text": "#333333"
        }
        self.dark_colors = {
            "primary": "#2980b9", "secondary": "#95a5a6", "success": "#27ae60",
            "danger": "#c0392b", "warning": "#d35400", "dark": "#34495e",
            "light": "#2d2d2d", "white": "#3d3d3d", "text": "#ffffff"
        }
        self.colors = self.light_colors
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.update_styles()
        
        # Setup tabs
        self.notebook = ttk.Notebook(self.root)
        self.setup_dashboard_tab()
        self.setup_transactions_tab()
        self.setup_budgets_tab()
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Dark mode toggle
        ttk.Button(self.root, 
                 text="🌓 Toggle Dark Mode", 
                 command=self.toggle_dark_mode
                 ).pack(anchor='ne', padx=10, pady=5)
    
    def update_styles(self):
        """Update all widget styles based on current color scheme"""
        self.style.configure(".", 
                           background=self.colors["light"], 
                           foreground=self.colors["text"])
        self.style.configure("TFrame", background=self.colors["light"])
        self.style.configure("TLabel", 
                           background=self.colors["light"], 
                           foreground=self.colors["text"])
        self.style.configure("TNotebook", background=self.colors["light"])
        self.style.configure("TNotebook.Tab", 
                           padding=[15, 5],
                           background=self.colors["light"],
                           foreground=self.colors["text"],
                           font=self.title_font)
        self.style.map("TNotebook.Tab", 
                      background=[("selected", self.colors["white"])])
        
        self.style.configure("TButton", 
                           padding=6,
                           font=self.default_font,
                           background=self.colors["primary"],
                           foreground="white")
        self.style.map("TButton",
                      background=[("active", self.colors["secondary"])])
        
        self.style.configure("Treeview", 
                           fieldbackground=self.colors["white"],
                           background=self.colors["white"],
                           foreground=self.colors["dark"],
                           rowheight=25)
        self.style.configure("Treeview.Heading", 
                           font=self.bold_font,
                           background=self.colors["primary"],
                           foreground="white")
        self.style.map("Treeview", 
                      background=[("selected", self.colors["primary"])],
                      foreground=[("selected", "white")])
        
        self.style.configure("Horizontal.TProgressbar",
                           troughcolor=self.colors["light"],
                           background=self.colors["success"],
                           lightcolor=self.colors["success"],
                           darkcolor=self.colors["success"])
    
    def toggle_dark_mode(self):
        """Switch between light and dark themes"""
        self.dark_mode = not self.dark_mode
        self.colors = self.dark_colors if self.dark_mode else self.light_colors
        self.update_styles()
        self.update_ui(full_refresh=True)
    
    def setup_dashboard_tab(self):
        """Setup the dashboard tab with summary cards and visualizations"""
        self.dashboard_tab = ttk.Frame(self.notebook)
        container = ttk.Frame(self.dashboard_tab)
        container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Summary cards
        cards_frame = ttk.Frame(container)
        cards_frame.pack(fill='x', pady=(0, 15))
        
        cards = [
            {"title": "Available Funds", "icon": "💰", "color": self.colors["success"], "var": "available_var"},
            {"title": "Monthly Spending", "icon": "💸", "color": self.colors["danger"], "var": "monthly_spend_var"},
            {"title": "Budget Status", "icon": "📊", "color": self.colors["primary"], "var": "budget_status_var"}
        ]
        
        for card in cards:
            frame = ttk.Frame(cards_frame)
            frame.pack(side='left', expand=True, fill='both', padx=5)
            
            header = ttk.Frame(frame)
            header.pack(fill='x', padx=10, pady=(10, 5))
            
            ttk.Label(header, 
                     text=f"{card['icon']} {card['title']}", 
                     font=self.title_font,
                     foreground=card["color"]).pack(side='left')
            
            value_frame = ttk.Frame(frame)
            value_frame.pack(fill='both', expand=True, pady=(0, 10))
            
            setattr(self, card["var"], tk.StringVar(value="$0.00"))
            ttk.Label(value_frame, 
                     textvariable=getattr(self, card["var"]), 
                     font=('Helvetica', 18, 'bold'),
                     foreground=card["color"]).pack()
        
        # Budget progress bar
        self.budget_progress = ttk.Progressbar(container, 
                                             orient='horizontal',
                                             length=200,
                                             mode='determinate',
                                             style="Horizontal.TProgressbar")
        self.budget_progress.pack(pady=10)
        
        # Sparkline container
        self.spark_frame = ttk.Frame(container)
        self.spark_frame.pack()
        self.spark_canvas = None
        
        # Heatmap container
        self.heat_frame = ttk.LabelFrame(container, 
                                       text="🔥 Spending Heatmap",
                                       padding=10)
        self.heat_frame.pack(fill='x', pady=(10, 5))
        self.heatmap_canvas = None
        
        # Recent transactions
        self.recent_frame = ttk.LabelFrame(container, 
                                         text="🕒 Recent Transactions",
                                         padding=10)
        self.recent_frame.pack(fill='both', expand=True)
        
        self.recent_tree = ttk.Treeview(self.recent_frame, 
                                      columns=("Date", "Amount", "Category"), 
                                      show="headings")
        for col in ["Date", "Amount", "Category"]:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=100, anchor='center')
        
        self.recent_tree.column("Date", width=150)
        self.recent_tree.column("Amount", width=120)
        
        scrollbar = ttk.Scrollbar(self.recent_frame, 
                                orient="vertical", 
                                command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scrollbar.set)
        
        self.recent_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.notebook.add(self.dashboard_tab, text="Dashboard")
    
    def setup_heatmap(self, parent_frame):
        """Initialize or update heatmap visualization"""
        if hasattr(self, 'heatmap_canvas') and self.heatmap_canvas:
            self.heatmap_canvas.get_tk_widget().destroy()
            
        fig = create_spending_heatmap(self.tracker.transactions)
        if fig:
            self.heatmap_canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            self.heatmap_canvas.draw()
            self.heatmap_canvas.get_tk_widget().pack(fill='x', padx=10, pady=5)
        else:
            ttk.Label(parent_frame, text="No spending data available").pack()
    
    def setup_sparkline(self, parent_frame):
        """Initialize or update sparkline visualization"""
        if hasattr(self, 'spark_canvas') and self.spark_canvas:
            self.spark_canvas.get_tk_widget().destroy()
            
        fig = create_spending_sparkline(self.tracker.transactions)
        if fig:
            self.spark_canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            self.spark_canvas.draw()
            self.spark_canvas.get_tk_widget().pack()
    
    def setup_transactions_tab(self):
        """Setup the transactions tab with entry form and list"""
        self.transactions_tab = ttk.Frame(self.notebook)
        container = ttk.Frame(self.transactions_tab)
        container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Add Transaction Frame
        add_frame = ttk.LabelFrame(container, 
                                 text="➕ Add Transaction", 
                                 padding=15)
        add_frame.pack(fill='x', pady=(0, 15))
        
        # Form fields
        ttk.Label(add_frame, text="Amount:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.amount_entry = ttk.Entry(add_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(add_frame, text="Category:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.category_entry = ttk.Entry(add_frame)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Quick category buttons
        quick_categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment"]
        cat_frame = ttk.Frame(add_frame)
        cat_frame.grid(row=2, column=1, sticky='ew', padx=5)
        for cat in quick_categories:
            ttk.Button(cat_frame, 
                     text=cat, 
                     width=8,
                     command=lambda c=cat: self.category_entry.insert(0, c)
                     ).pack(side='left', padx=2)
        
        ttk.Label(add_frame, text="Type:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.type_var = tk.StringVar(value="Expense")
        type_combo = ttk.Combobox(add_frame, 
                                textvariable=self.type_var, 
                                values=["Expense", "Income"], 
                                state="readonly")
        type_combo.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        # Action buttons
        button_frame = ttk.Frame(add_frame)
        button_frame.grid(row=4, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, 
                  text="Add Transaction", 
                  command=self.add_transaction).pack(side='left', padx=5)
        ttk.Button(button_frame,
                  text="Add via AI",
                  command=self.open_ai_window).pack(side='left', padx=5)
        ttk.Button(button_frame,
                  text="Add Recurring",
                  command=self.add_recurring_bill).pack(side='left', padx=5)
        
        # Transaction List
        list_frame = ttk.LabelFrame(container, 
                                  text="All Transactions", 
                                  padding=10)
        list_frame.pack(fill='both', expand=True)
        
        self.transaction_tree = ttk.Treeview(list_frame, 
                                           columns=("Date", "Amount", "Category", "Type"), 
                                           show="headings")
        for col in ["Date", "Amount", "Category", "Type"]:
            self.transaction_tree.heading(col, text=col)
            self.transaction_tree.column(col, width=100, anchor='center')
        
        self.transaction_tree.column("Date", width=150)
        self.transaction_tree.column("Amount", width=120)
        self.transaction_tree.column("Category", width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, 
                                orient="vertical", 
                                command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscrollcommand=scrollbar.set)
        
        self.transaction_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # List action buttons
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(side='bottom', fill='x', pady=(5, 0))
        
        ttk.Button(action_frame, 
                  text="Delete Selected", 
                  command=self.delete_transaction).pack(side='left', padx=5)
        ttk.Button(action_frame, 
                  text="Refresh", 
                  command=lambda: self.update_ui(full_refresh=True)).pack(side='left', padx=5)
        
        self.notebook.add(self.transactions_tab, text="Transactions")
    
    def setup_budgets_tab(self):
        """Setup the budgets tab with summary and management"""
        self.budgets_tab = ttk.Frame(self.notebook)
        container = ttk.Frame(self.budgets_tab)
        container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Budget Summary
        summary_frame = ttk.LabelFrame(container, 
                                     text="Budget Summary", 
                                     padding=15)
        summary_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(summary_frame, 
                 text="Available Funds:", 
                 font=self.bold_font).pack(side='left')
        
        self.available_funds_var = tk.StringVar(value="$0.00")
        ttk.Label(summary_frame, 
                 textvariable=self.available_funds_var,
                 font=self.bold_font,
                 foreground=self.colors["success"]).pack(side='left', padx=10)
        
        ttk.Button(summary_frame, 
                  text="Set New Budget", 
                  command=self.show_budget_window).pack(side='right')
        
        # Budget Status
        status_frame = ttk.LabelFrame(container, 
                                    text="Current Budgets", 
                                    padding=10)
        status_frame.pack(fill='both', expand=True)
        
        self.budget_tree = ttk.Treeview(status_frame, 
                                      columns=("Category", "Limit", "Spent", "Remaining"), 
                                      show="headings")
        for col in ["Category", "Limit", "Spent", "Remaining"]:
            self.budget_tree.heading(col, text=col)
            self.budget_tree.column(col, width=100, anchor='center')
        
        self.budget_tree.column("Category", width=150)
        
        scrollbar = ttk.Scrollbar(status_frame, 
                                orient="vertical", 
                                command=self.budget_tree.yview)
        self.budget_tree.configure(yscrollcommand=scrollbar.set)
        
        self.budget_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.notebook.add(self.budgets_tab, text="Budgets")
    
    def show_budget_window(self):
        """Show budget management popup window"""
        budget_win = tk.Toplevel(self.root)
        budget_win.title("Budget Management")
        
        ttk.Label(budget_win, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        category_entry = ttk.Entry(budget_win)
        category_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(budget_win, text="Monthly Limit:").grid(row=1, column=0, padx=5, pady=5)
        limit_entry = ttk.Entry(budget_win)
        limit_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(budget_win, 
                  text="Set Budget", 
                  command=lambda: self.set_budget(
                      category_entry.get(),
                      limit_entry.get()
                  )).grid(row=2, columnspan=2, pady=10)
    
    def set_budget(self, category, amount):
        """Set budget for a category"""
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                messagebox.showerror("Error", "Budget must be positive")
                return
                
            self.tracker.budgets[category.lower()] = amount_float
            self.tracker._save_data()
            messagebox.showinfo("Success", f"Budget set for {category}")
            self.update_ui()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount. Enter a number.")
    
    def add_recurring_bill(self):
        """Add a new recurring bill"""
        amount = simpledialog.askfloat("Recurring Bill", "Monthly amount:")
        if amount:
            category = simpledialog.askstring("Recurring Bill", "Category:")
            if category:
                self.tracker.recurring.append({
                    'amount': amount,
                    'category': category,
                    'type': 'expense',
                    'interval': 30,
                    'last_applied': None
                })
                self.tracker._save_data()
                messagebox.showinfo("Success", "Recurring bill added!")
                self.update_ui()
    
    def open_ai_window(self):
        """Open window for AI transaction parsing"""
        ai_win = tk.Toplevel(self.root)
        ai_win.title("Add Transaction via AI")
        
        ttk.Label(ai_win, text="Describe your transaction:").pack(pady=10)
        self.ai_entry = ttk.Entry(ai_win, width=50)
        self.ai_entry.pack(pady=5)
        
        ttk.Button(ai_win, text="Parse", command=self.parse_ai_input).pack(pady=10)
    
    def parse_ai_input(self):
        """Parse natural language transaction description"""
        try:
            from nlp_queries import extract_transaction_details
        except ImportError:
            messagebox.showerror("Error", "NLP module not found")
            return
            
        text = self.ai_entry.get()
        if not text:
            messagebox.showwarning("Warning", "Enter a description")
            return
        
        result = extract_transaction_details(text)
        if not result:
            messagebox.showerror("Error", "Couldn't parse. Try: 'Spent $20 on food yesterday'")
            return
        
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, str(result['amount']))
        self.category_entry.delete(0, tk.END)
        self.category_entry.insert(0, result['category'])
        self.type_var.set(result['type'].title())
        
        messagebox.showinfo("Success", f"Detected: {result}")
        self.ai_entry.master.destroy()
    
    def add_transaction(self):
        """Add a new transaction"""
        try:
            amount = float(self.amount_entry.get())
            category = self.category_entry.get().strip()
            trans_type = self.type_var.get().lower()
            
            if amount <= 0 or not category:
                raise ValueError("Invalid values")
            
            if trans_type == "expense":
                available = self.tracker.get_available_funds()
                if amount > available:
                    if not messagebox.askyesno(
                        "Low Funds",
                        f"Only ${available:.2f} available. Add this expense anyway?"
                    ):
                        return
            
            if self.tracker.add_transaction(amount, category, trans_type):
                messagebox.showinfo("Success", "Transaction added")
                self.update_ui()
                self.amount_entry.delete(0, tk.END)
                self.category_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Failed to add transaction")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def delete_transaction(self):
        """Delete selected transaction"""
        selected = self.transaction_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a transaction first")
            return

        item = self.transaction_tree.item(selected[0])
        values = item['values']
        
        try:
            date = values[0]
            amount = float(values[1].replace("$", ""))
            category = values[2].lower()
            trans_type = values[3].lower()
            
            for t in self.tracker.transactions:
                if (t['date'] == date and 
                    t['amount'] == amount and 
                    t['category'].lower() == category and 
                    t['type'].lower() == trans_type):
                    
                    self.tracker.transactions.remove(t)
                    self.tracker._save_data()
                    messagebox.showinfo("Success", "Transaction deleted")
                    self.update_ui()
                    return
                    
            messagebox.showerror("Error", "Transaction not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {str(e)}")
    
    def update_ui(self, full_refresh=False):
        """Refresh all UI elements with smart updates"""
        # Update financial summaries
        available = self.tracker.get_available_funds()
        self.available_var.set(f"${available:.2f}")
        self.available_funds_var.set(f"${available:.2f}")

        current_month = datetime.now().strftime("%Y-%m")
        monthly_spent = sum(
            t['amount'] for t in self.tracker.transactions
            if t['type'] == 'expense' and t['date'].startswith(current_month)
        )
        self.monthly_spend_var.set(f"${monthly_spent:.2f}")

        # Update budget progress
        if self.tracker.budgets:
            budget = next(iter(self.tracker.budgets.values()))
            self.budget_progress['maximum'] = budget
            self.budget_progress['value'] = min(monthly_spent, budget)
            if monthly_spent > budget * 0.8:  # Change color if approaching limit
                self.style.configure("Horizontal.TProgressbar",
                                   background=self.colors["danger"])
            else:
                self.style.configure("Horizontal.TProgressbar",
                                   background=self.colors["success"])

        # Update transactions list
        if full_refresh or not hasattr(self, 'last_transaction_count') or \
           self.last_transaction_count != len(self.tracker.transactions):
            
            self.transaction_tree.delete(*self.transaction_tree.get_children())
            for t in sorted(self.tracker.transactions, 
                          key=lambda x: x['date'], reverse=True):
                self.transaction_tree.insert("", "end", values=(
                    t['date'],
                    f"${t['amount']:.2f}",
                    t['category'].title(),
                    t['type'].title()
                ))
            self.last_transaction_count = len(self.tracker.transactions)

        # Update recent transactions
        self.recent_tree.delete(*self.recent_tree.get_children())
        for t in sorted(self.tracker.transactions, 
                       key=lambda x: x['date'], reverse=True)[:5]:
            self.recent_tree.insert("", "end", values=(
                t['date'],
                f"${t['amount']:.2f}",
                t['category'].title()
            ))

        # Update budgets
        current_budgets = set(self.tracker.budgets.items())
        if full_refresh or not hasattr(self, 'last_budgets') or \
           current_budgets != self.last_budgets:
            
            self.budget_tree.delete(*self.budget_tree.get_children())
            for category, data in self.tracker.get_budget_status().items():
                self.budget_tree.insert("", "end", values=(
                    category.title(),
                    f"${data['limit']:.2f}",
                    f"${data['spent']:.2f}",
                    f"${data['remaining']:.2f}"
                ))
            self.last_budgets = current_budgets

        # Update visualizations
        self.setup_heatmap(self.heat_frame)
        self.setup_sparkline(self.spark_frame)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.mainloop()