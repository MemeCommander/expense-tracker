from flask import Flask, render_template, request, redirect, url_for, flash
from expenses import ExpenseTracker
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Initialize tracker
# We assume expenses.py is in the same directory
tracker = ExpenseTracker()

@app.route('/')
def index():
    total_all, totals = tracker.get_totals()
    
    # Sort history to show newest first
    recent_history = list(reversed(tracker.history))
    
    return render_template('index.html', 
                           total_all=total_all, 
                           totals=totals, 
                           history=recent_history,
                           last_updated=tracker.last_updated,
                           aliases=tracker.aliases)

@app.route('/add', methods=['POST'])
def add_expense():
    amount = request.form.get('amount')
    category = request.form.get('category')
    
    if amount and category:
        if tracker.add_expense(category, amount):
            flash(f"Added ${amount} to {category}", "success")
        else:
            flash("Failed to add expense. Check inputs.", "error")
    else:
        flash("Missing amount or category.", "error")
        
    return redirect(url_for('index'))

@app.route('/undo', methods=['POST'])
def undo_expense():
    tracker.undo_last()
    flash("Undid last action.", "info")
    return redirect(url_for('index'))

@app.route('/history')
def history():
    # Show full history
    full_history = list(reversed(tracker.history))
    return render_template('history.html', 
                           history=full_history,
                           aliases=tracker.aliases)

@app.route('/settings')
def settings():
    return render_template('settings.html', aliases=tracker.aliases)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
