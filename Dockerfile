# Define the base image with Python
FROM python:3.9-alpine

# Copy all contents from the current 
# directory to the working directory
COPY . .

RUN apk add --no-cache gcc musl-dev

# Install Python dependencies
RUN pip install --no-cache-dir poetry
RUN poetry export --without-hashes --without dev -f requirements.txt -o requirements.txt
RUN pip install -r requirements.txt

# Define the default command to 
# execute the application
CMD ["python", "-m", "src"]