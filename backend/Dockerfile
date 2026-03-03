FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Make start script executable
RUN chmod +x start.sh

CMD ["./start.sh"]
