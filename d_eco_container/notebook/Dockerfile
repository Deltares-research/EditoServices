FROM ghcr.io/deltares/decoimpact:latest

LABEL org.opencontainers.image.source="https://github.com/Deltares/D-EcoImpact"

ENV APP_HOME /app

WORKDIR $APP_HOME

# Copy files in local working directory to docker working directory
COPY . $APP_HOME

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Install Jupyter
RUN pip install --no-cache-dir notebook

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Run jupyter notebook when the container launches
CMD ["jupyter", "notebook", "run-decoimpact.ipynb", "--ip='*'", "--port=5001", "--no-browser", "--allow-root"]
