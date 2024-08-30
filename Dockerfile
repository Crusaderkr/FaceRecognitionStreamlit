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

# Copy the environment file
COPY environment.yml .

# Create the Conda environment and activate it
RUN apt-get install -y --no-install-recommends wget bzip2 ca-certificates \
    && wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && /bin/bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda \
    && rm Miniconda3-latest-Linux-x86_64.sh \
    && /opt/conda/bin/conda env create -f environment.yml

# Activate the environment and ensure Streamlit and other packages are available
ENV PATH /opt/conda/envs/face-recognition-app/bin:$PATH

# Copy the application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Set the entry point to Streamlit
ENTRYPOINT ["streamlit", "run"]

# Command to run the Streamlit app
CMD ["FaceRecogAtt/with_interface.py"]
