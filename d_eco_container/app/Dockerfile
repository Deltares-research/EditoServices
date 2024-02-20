FROM ghcr.io/deltares/decoimpact:latest

LABEL org.opencontainers.image.source="https://github.com/Deltares/D-EcoImpact"

ENV APP_HOME /app

WORKDIR $APP_HOME

# Copy files in local working directory to docker working directory
COPY . $APP_HOME

# Create Directories for storing files which are being created during the api calls execution
#RUN mkdir app/uploads \
#    && mkdir app/results \
#    && mkdir app/logs \
#    && mkdir app/csv-uploads \

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
