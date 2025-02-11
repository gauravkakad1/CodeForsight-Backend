# Use an official Python runtime as base
FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y graphviz

# Verify Graphviz installation
RUN dot -V

# Set the working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 10000

# Run FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
