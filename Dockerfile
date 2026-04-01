FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure the database file exists so it can be mounted via volume without issue
RUN touch Expenses.json

# Expose port (Gunicorn default is 8000)
EXPOSE 8000

# Run gunicorn serving the Flask app ('app' module, 'app' variable)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
