# The Dockerfile defines the image's environment
# Import Python runtime and set up working directory
FROM gcr.io/google-appengine/python

RUN virtualenv -p python3.7 /env
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

WORKDIR /app
ADD . /app

# Install any necessary dependencies
RUN pip install -r requirements.txt

# Open port 8080 for serving the webpage
EXPOSE 8080

# Run app.py when the container launches
CMD ["python", "app.py"]
