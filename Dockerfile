# Use the official Python image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Install system-level dependencies for dlib and others
RUN apt-get update && apt-get install -y \
    libegl1 \
    libglvnd0 \
    libglib2.0-0 \
    libgl1-mesa-glx \
    cmake \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Create a virtual environment
RUN python -m venv venv

# Activate the virtual environment and install the dependencies
RUN ./venv/bin/pip install --upgrade pip \
    && ./venv/bin/pip install -r requirements.txt

# Copy the known_faces directory
COPY FaceRecogAtt/known_faces /app/FaceRecogAtt/known_faces

# Debugging step: List the contents of the known_faces directory
RUN ls -R /app/FaceRecogAtt/known_faces

# Copy the rest of the application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Set the entry point to Streamlit
ENTRYPOINT ["./venv/bin/streamlit", "run"]

# Command to run the Streamlit app
CMD ["FaceRecogAtt/with_interface.py"]
