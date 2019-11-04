############################################################
# Dockerfile to run a Django-based web application
# Based on an AMI
############################################################

# Set the base image to use to Ubuntu
FROM python:3.7

# Set the file maintainer (your name - the file's author)
MAINTAINER Michael Corey

# Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
# Local directory with project source
ENV DOCKYARD_SRC=.

# Directory in container for all project files
ENV DOCKYARD_SRVHOME=/srv

# Directory in container for project source files
ENV DOCKYARD_SRVPROJ=$DOCKYARD_SRVHOME/$DOCKYARD_SRC

# Update the default application repository sources list
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y nginx
RUN apt-get install -y cron

##############
# CRON STUFF #
##############

# Copy hello-cron file to the cron.d directory
COPY scrape_cron /etc/cron.d/scrape_cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/scrape_cron

# Apply cron job
RUN crontab /etc/cron.d/scrape_cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
#CMD cron && tail -f /var/log/cron.log
#CMD ["cron", "-f"]

# Create application subdirectories
WORKDIR $DOCKYARD_SRVHOME
RUN mkdir media static logs

#read
VOLUME ["$DOCKYARD_SRVHOME/media/", "$DOCKYARD_SRVHOME/logs/"]

# Copy application source code to SRCDIR
COPY $DOCKYARD_SRC $DOCKYARD_SRVPROJ

# Install Python dependencies
RUN pip install -r $DOCKYARD_SRVPROJ/requirements.txt

# Port to expose
EXPOSE 8000
EXPOSE 80

# Copy entrypoint script into the image
WORKDIR $DOCKYARD_SRVPROJ
COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
COPY ./django_nginx.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/django_nginx.conf /etc/nginx/sites-enabled
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
ENTRYPOINT ["/docker-entrypoint.sh"]
