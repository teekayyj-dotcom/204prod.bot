FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables so Python output is sent straight to terminal (e.g. your container log)
ENV PYTHONUNBUFFERED=1

# Run the local testing script (Steps 2 & 3 automated)
CMD ["python", "local_test.py"]
