# Use the official Miniconda3 image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Copy the environment.yml to the working directory
COPY environment.yml .

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    libegl1 \
    libglvnd0 \
    libglib2.0-0 \
    libgl1-mesa-glx \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Verify installation of system-level dependencies
RUN ldconfig -p | grep libEGL
RUN cmake --version

# Update conda and ensure the classic solver is set
RUN conda update conda -n base -c defaults && \
    conda config --set solver classic

# Install the conda environment
RUN conda env create -f environment.yml

# Activate the environment and install additional packages
SHELL ["conda", "run", "-n", "face-recognition-app", "/bin/bash", "-c"]

# Copy the rest of the application code to the working directory
COPY . .

# Change the working directory to FaceRecogAtt
WORKDIR /app/FaceRecogAtt

# Print the directory structure to verify files
RUN ls -R /app/FaceRecogAtt

# Print the Conda environment structure to verify creation
RUN conda env list
RUN conda list -n face-recognition-app

# Set the entry point to Streamlit
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "face-recognition-app", "streamlit", "run"]

# Command to run the Streamlit app
CMD ["with_interface.py"]

