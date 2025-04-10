import re
import dateparser
from typing import Dict, Optional

def extract_transaction_details(sentence: str) -> Optional[Dict]:
    """Enhanced NLP parser for financial transactions"""
    sentence = sentence.lower().strip()
    
    # Improved amount extraction (handles decimals and currency symbols)
    amount_match = re.search(r"(\d+\.?\d*)", sentence.replace(",", ""))
    amount = float(amount_match.group(1)) if amount_match else None
    
    # Better category extraction
    category = "Uncategorized"
    for prep in ["on", "for", "at"]:
        if prep in sentence:
            parts = sentence.split(prep)
            if len(parts) > 1:
                category = re.sub(r"\d+|\W+", " ", parts[1]).strip().title()
                break
    
    # More robust type detection
    expense_keywords = ["spent", "paid", "bought", "purchase", "cost"]
    income_keywords = ["got", "earned", "received", "salary", "income"]
    
    transaction_type = None
    if any(word in sentence for word in expense_keywords):
        transaction_type = "expense"
    elif any(word in sentence for word in income_keywords):
        transaction_type = "income"
    
    # Better date parsing
    parsed_date = dateparser.parse(sentence, settings={'PREFER_DATES_FROM': 'past'})
    date = parsed_date.strftime("%Y-%m-%d") if parsed_date else None
    
    if not all([amount, transaction_type, date]):
        return None
        
    return {
        "amount": round(float(amount), 2),
        "category": category,
        "type": transaction_type,
        "date": date
    }