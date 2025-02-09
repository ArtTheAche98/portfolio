# Personal Scraper and Content Optimizer

This repository contains a Django-based web application that scrapes content from target URLs, optimizes posts using DeepSeek AI, and automatically posts them to LinkedIn. The project is containerized with Docker and uses Celery for asynchronous tasks along with Redis as the message broker.

## Features

- **Scraping:** Extracts content from pages using requests, BeautifulSoup, and Scrapy.
- **Content Optimization:** Uses DeepSeek (compatible with OpenAI's API) to transform raw content into elegant LinkedIn posts.
- **Asynchronous Processing:** Celery workers and Celery Beat run scraping and posting tasks on schedules.
- **Containerization:** Docker Compose orchestrates the web server, Celery workers, Celery Beat, and Redis.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A DeepSeek API key and LinkedIn API credentials (set in the `.env` file)

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/ArtTheAche/portfolio/personal.git
   cd personal
   ```

2. **Create and Configure the .env File**

   A sample .env file is provided in the repository. Update it with your credentials and configurations:

3. **Docker Compose Services**

   The docker-compose.yml sets up the following services:

   - **web:** Runs the Django application using Gunicorn.
   - **celery:** Runs the Celery worker.
   - **celery-beat:** Runs the Celery Beat scheduler.
   - **redis:** Provides the Redis service (mapped to host port 6380 in this configuration).

   If you are using local Redis services or have port conflicts, you may need to adjust the ports in the docker-compose file.

4. **Install Requirements**

   All Python dependencies are listed in requirements.txt. This file is used by the Dockerfile to install dependencies in the container.

5. **Running the Application**

   ### Build and Start Containers

   From the project root, run:

   ```bash
   docker-compose up --build
   ```

   This command builds the containers and starts all services. The web server will be available at http://localhost:8000.

   ### Manage Containers

   - **Stop Containers:** Press Ctrl+C in the terminal where docker-compose is running or run:

     ```bash
     docker-compose down
     ```

   - **View Logs:** To inspect logs from a given service, use:

     ```bash
     docker-compose logs <service_name>
     ```

6. **Celery and Scheduling**

   The Celery worker and beat are configured to automatically pick up tasks (like scraping and posting) from within the Django application. Make sure the tasks are working by checking logs in the docker containers.

## Deployment

You can deploy this containerized application to any virtual machine or cloud provider that supports Docker. Simply push your code to your repository and run docker-compose up --build on the host machine.

## Troubleshooting

- **Port Conflicts:**
  If you see errors like "Ports are not available," check whether the host ports (e.g., 6379 for Redis or 8000 for Django) are already in use. Adjust the port mapping in docker-compose.yml if necessary.

- **Celery Connection Issues:**
  Ensure your CELERY_BROKER_URL in the .env is set to use redis://redis:6379/0 (i.e., the Redis service name in Docker). If using a changed port mapping, update the URL accordingly.

- **Dependency Errors:**
  If the Docker build fails due to dependency errors (especially with libraries like lxml), ensure the necessary system libraries (e.g., libxml2-dev, libxslt1-dev) are installed by referring to the Dockerfile.

## Contributing

Feel free to fork the repository, submit issues, or make pull requests if you have enhancements or bug fixes to contribute.

## License

This project is open-source.
