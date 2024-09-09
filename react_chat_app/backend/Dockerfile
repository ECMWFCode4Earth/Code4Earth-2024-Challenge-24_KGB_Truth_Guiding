# Use the official Python image from the Docker Hub
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt to the container
COPY requirements.txt /app/

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code to the working directory in the container
COPY . /app

# Expose the port the app runs on
EXPOSE 5001

# Set environment variables
ENV FLASK_APP=app.py

# Run the Flask application
CMD ["flask", "run", "--port=5001"]
