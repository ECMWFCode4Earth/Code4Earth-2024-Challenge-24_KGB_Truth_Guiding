# Use the official Python image as the base
FROM python:3.9

# Set the working directory in the container
WORKDIR /app/upload_db

# Copy the current directory contents (the context set in docker-compose) into the container at /app/upload_db
COPY . /app/upload_db

# Install any dependencies specified in a requirements.txt file (if needed)
COPY requirements.txt /app/upload_db/
RUN pip install --no-cache-dir -r requirements.txt

# Install Neo4j driver for Python to interact with the Neo4j database
RUN pip install neo4j==5.24.0

# Ensure the assets folder is accessible (if needed for this service)
# WORKDIR /app
# COPY ./assets /app/assets

# Set the default command to execute when the container starts
# CMD ["python", "upload_neo4j_from_json.py"]
RUN chmod +x /app/upload_db/wait-for-it.sh