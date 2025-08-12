# Start from the official Python base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy dependencies specification file
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of your application files into the container
COPY . /app

# Expose the default Streamlit port
EXPOSE 8501

# Set the command to run your Streamlit app
CMD ["streamlit", "run", "Leaderboard.py"]
