FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (7860 is the default port for Hugging Face Spaces)
EXPOSE 7860

# Run using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "backend.app:app"]
