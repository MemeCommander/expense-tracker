import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, List, Tuple, Optional

FILENAME = "Expenses.json"
EST = ZoneInfo("America/Toronto")  # Eastern Time

# Default Aliases
DEFAULT_ALIASES = {
    "gcg": ("Great Canadian Games", "Frivolous"),
    "mfd": ("Misc Food", "Wasteful"),
    "dia": ("Diadem", "Frivolous"),
    "cbr": ("College Boreal", "Frivolous"),
    "shp": ("Shopping", "Neutral"),
    "grc": ("Groceries", "Good"),
    "stm": ("Steam", "Frivolous")
}

class ExpenseTracker:
    def __init__(self, filename: str = FILENAME):
        self.filename = filename
        self.expenses: Dict[str, Dict] = {}
        self.history: List[Dict] = []
        self.last_updated: str = "Never"
        self.aliases = DEFAULT_ALIASES.copy()
        self.load_data()

    def load_data(self):
        """Loads data from JSON file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                print("Error decoding JSON. Starting with empty data.")
                data = {}
        else:
            data = {}

        # Pull categories (dicts with "amount")
        self.expenses = {k: v for k, v in data.items() if isinstance(v, dict) and "amount" in v}
        self.last_updated = data.get("last_updated", "Never")
        self.history = data.get("history", [])
        # Load aliases if present, otherwise keep defaults (already set in __init__)
        if "aliases" in data:
            self.aliases = {k: tuple(v) for k, v in data.get("aliases", {}).items()}

    def save_data(self):
        """Saves current state to JSON file."""
        save_data = {
            **self.expenses,
            "last_updated": self.last_updated,
            "history": self.history,
            "aliases": self.aliases
        }
        try:
            with open(self.filename, "w") as f:
                json.dump(save_data, f, indent=4)
        except IOError as e:
            print(f"Error saving data: {e}")

    def get_totals(self) -> Tuple[float, Dict[str, float]]:
        """Calculates totals."""
        total_all = 0.0
        totals = {"Good": 0.0, "Neutral": 0.0, "Frivolous": 0.0, "Wasteful": 0.0}

        for info in self.expenses.values():
            amt = info["amount"]
            ctype = info["type"]
            if ctype in totals:
                totals[ctype] += amt
            total_all += amt
        
        return total_all, totals

    def show_summary(self):
        """Prints the summary of expenses."""
        print(f"\nLast Updated: {self.last_updated}\n")
        
        total_all, totals = self.get_totals()

        print("Category Breakdown:")
        # Sort by amount desc for better visibility
        sorted_cats = sorted(self.expenses.items(), key=lambda x: x[1]['amount'], reverse=True)
        
        for cat, info in sorted_cats:
            print(f"  {cat}: ${info['amount']:.2f}")

        print(f"\nTotal Spent Overall: ${total_all:.2f}")
        print(f"Total Good: ${totals['Good']:.2f}")
        print(f"Total Neutral: ${totals['Neutral']:.2f}")
        print(f"Total Bad (Frivolous + Wasteful): ${totals['Frivolous'] + totals['Wasteful']:.2f}\n")

    def add_expense(self, category_input: str, amount_str: str) -> bool:
        """Adds an expense. Returns True if successful."""
        try:
            amount_total = sum(float(x) for x in amount_str.split(","))
        except ValueError:
            print("Invalid number(s).\n")
            return False

        category_input = category_input.strip().lower()
        if not category_input:
            print("Category cannot be empty.\n")
            return False

        # Alias handler
        if category_input in self.aliases:
            category, cat_type = self.aliases[category_input]
        else:
            # Capitalize first letter of each word for new categories
            category = category_input.title() 
            
            if category not in self.expenses:
                try:
                    type_input = input(f"New Category '{category}'. Type [G/N/F/W] (default Neutral): ").strip().upper()
                except (EOFError, RuntimeError):
                    type_input = "N"
                
                cat_type = (
                    "Good" if type_input == "G" else
                    "Neutral" if type_input in ("N", "") else
                    "Frivolous" if type_input == "F" else
                    "Wasteful"
                )
            else:
                cat_type = self.expenses[category]["type"]

        # Update amount
        if category not in self.expenses:
            self.expenses[category] = {"amount": amount_total, "type": cat_type}
        else:
            self.expenses[category]["amount"] += amount_total

        # Timestamp
        self.last_updated = datetime.now(EST).strftime("%Y-%m-%d %H:%M %Z")

        # Log history
        self.history.append({
            "timestamp": self.last_updated,
            "category": category,
            "amount_added": amount_total,
            "new_total": self.expenses[category]["amount"],
            "type": cat_type # Store type in history too for context
        })

        self.save_data()
        print(f"Added ${amount_total:.2f} to {category} ({cat_type}).\n")
        return True

    def undo_last(self):
        """Undoes the last action."""
        if not self.history:
            print("Nothing to undo.")
            return

        last_action = self.history.pop()
        category = last_action["category"]
        amount_added = last_action["amount_added"]

        if category in self.expenses:
            self.expenses[category]["amount"] -= amount_added
            
            # If amount drops to 0 or less, maybe remove category? 
            # For now, let's keep it but warn if negative (shouldn't happen with normal use)
            if self.expenses[category]["amount"] <= 0.001: # Float epsilon
                 # Optional: del self.expenses[category]
                 self.expenses[category]["amount"] = 0.0

        # Update timestamp to now (or revert? usually now is better to show when edit happened)
        self.last_updated = datetime.now(EST).strftime("%Y-%m-%d %H:%M %Z")
        
        self.save_data()
        print(f"Undid addition of ${amount_added:.2f} to {category}.\n")

    def show_history_log(self, limit=5):
        """Shows recent history."""
        print(f"\n--- Recent History (Last {limit}) ---")
        for entry in reversed(self.history[-limit:]):
            print(f"{entry['timestamp']}: {entry['category']} +${entry['amount_added']:.2f}")
        print("-------------------------------------\n")

def main():
    tracker = ExpenseTracker()

    while True:
        tracker.show_summary()

        print("Commands: [Amount] to add, 'u' to undo, 'h' to history, 'x' to exit")
        user_input = input("Enter command: ").strip()

        if user_input.lower() == "x":
            break
        elif user_input.lower() in ("u", "undo"):
            tracker.undo_last()
            continue
        elif user_input.lower() in ("h", "history"):
            tracker.show_history_log()
            input("Press Enter to continue...")
            continue
        
        # Assume it's an amount if not a command
        amount_input = user_input
        
        # Check if it looks like a number (simple check)
        try:
            # Just to check if it's a valid number start
            float(amount_input.split(",")[0])
        except ValueError:
            print("Invalid command or number.")
            continue

        category_input = input("Enter category (or alias): ").strip()
        tracker.add_expense(category_input, amount_input)

if __name__ == "__main__":
    main()
