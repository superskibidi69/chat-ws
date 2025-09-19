# Use Python 3.13 slim
FROM python:3.13-slim

# Set workdir
WORKDIR /

# Copy requirements if you have one (or install manually)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Expose port from environment
ENV PORT 8765
EXPOSE $PORT

# Run server
CMD ["python", "main.py"]
