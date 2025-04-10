import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class FinanceTracker:
    def __init__(self, filename: str = "transactions.json"):
        self.filename = filename
        self.transactions = []
        self.budgets = {}
        self.recurring = []
        self.notifications = []
        self._load_data()
        self._process_recurring()

    def _load_data(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                
                # Handle both old (list) and new (dict) formats
                if isinstance(data, list):
                    self.transactions = data
                else:
                    self.transactions = data.get('transactions', [])
                    self.budgets = data.get('budgets', {})
                    self.recurring = data.get('recurring', [])
                    self.notifications = data.get('notifications', [])
                    
        except (FileNotFoundError, json.JSONDecodeError):
            self.transactions = []
            self.budgets = {}
            self.recurring = []
            self.notifications = []

    def _save_data(self):
        with open(self.filename, 'w') as f:
            json.dump({
                'transactions': self.transactions,
                'budgets': self.budgets,
                'recurring': self.recurring,
                'notifications': self.notifications
            }, f, indent=4)

    def add_transaction(self, amount: float, category: str, 
                       trans_type: str, date: str = None) -> Optional[Dict]:
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            transaction = {
                'amount': float(amount),
                'category': category.lower(),
                'type': trans_type.lower(),
                'date': date
            }
            
            self.transactions.append(transaction)
            self._check_budgets(transaction)
            self._save_data()
            return transaction
            
        except ValueError:
            return None

    def _process_recurring(self):
        today = datetime.now().date()
        processed = []
        
        for rt in self.recurring:
            last_date = datetime.strptime(rt['last_applied'], "%Y-%m-%d").date() if rt['last_applied'] else None
            interval = timedelta(days=rt['interval'])
            next_date = last_date + interval if last_date else today
            
            if not last_date or today >= next_date:
                self.add_transaction(
                    rt['amount'],
                    rt['category'],
                    rt['type'],
                    today.strftime("%Y-%m-%d")
                )
                rt['last_applied'] = today.strftime("%Y-%m-%d")
                processed.append(rt)
        
        if processed:
            self._save_data()
        return processed

    def _check_budgets(self, transaction):
        if transaction['type'] != 'expense':
            return
        
        category = transaction['category']
        if category not in self.budgets:
            return
        
        current_month = datetime.now().strftime("%Y-%m")
        monthly_spent = sum(
            t['amount'] for t in self.transactions
            if t['type'] == 'expense'
            and t['category'] == category
            and t['date'].startswith(current_month)
        )
        
        budget_limit = self.budgets[category]
        if monthly_spent > budget_limit:
            self.notifications.append({
                'type': 'budget_alert',
                'category': category,
                'amount': transaction['amount'],
                'limit': budget_limit,
                'spent': monthly_spent,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'message': f"Budget exceeded for {category.title()}! (${monthly_spent:.2f} of ${budget_limit:.2f})"
            })
            self._save_data()

    def get_available_funds(self) -> float:
        total_income = sum(t['amount'] for t in self.transactions if t['type'] == 'income')
        total_expenses = sum(t['amount'] for t in self.transactions if t['type'] == 'expense')
        
        upcoming_recurring = sum(
            rt['amount'] for rt in self.recurring
            if rt['type'] == 'expense'
            and (not rt['last_applied'] or 
                datetime.now().date() >= (
                    datetime.strptime(rt['last_applied'], "%Y-%m-%d").date() + 
                    timedelta(days=rt['interval'])
                )
            )
        )
        
        return total_income - (total_expenses + upcoming_recurring)

    def get_budget_status(self) -> Dict:
        current_month = datetime.now().strftime("%Y-%m")
        expenses = [t for t in self.transactions 
                   if t['type'] == 'expense'
                   and t['date'].startswith(current_month)]
        
        category_spending = defaultdict(float)
        for t in expenses:
            category_spending[t['category']] += t['amount']
        
        return {
            category: {
                'limit': limit,
                'spent': category_spending.get(category, 0),
                'remaining': max(0, limit - category_spending.get(category, 0))
            }
            for category, limit in self.budgets.items()
        }