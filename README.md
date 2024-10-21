# xml_file_processing_task-

# Flask Application

This is a simple Flask-based application. This guide will explain how to run the application using `curl`, `Docker`, or by directly installing dependencies with `pip`.

## Requirements

- Python 3.10+
- Flask
- Docker (optional, for Docker method)
- `pip` (for local installation)

---

## Running the Application

### 1. Run via `curl` (REST API call)

Once the Flask application is running (via Docker or locally), you can interact with it using `curl`.

Here is an example `curl` command to send a request to the Flask application:

```bash
curl http://localhost:5000/your-endpoint -X POST -d '{"key":"value"}' -H "Content-Type: application/json"
```

- Replace `/your-endpoint` with your specific route, and the `-d` option with your payload if required.
- Make sure the application is running on port `5000`.

---

### 2. Run via Docker

You can run the Flask application inside a Docker container using the `Dockerfile` and `docker-compose.yml`.

#### Steps:

1. **Build the Docker image:**

   Run the following command to build the image using your `Dockerfile`:

   ```bash
   docker build -t flask_app .
   ```

2. **Run the Docker container:**

   Use `docker-compose` to run the container:

   ```bash
   docker-compose up
   ```

   This will start the container, map port `5000` on your local machine to port `5000` in the container, and run the Flask application.

#### Test the Application:

Once the application is running in Docker, you can access it by navigating to:

```
http://localhost:5000
```

You can also use `curl` to send requests to the application:

```bash
curl http://localhost:5000/your-endpoint -X GET
```

---

### 3. Run via Pip Installation (Locally)

To run the application locally, you can install the dependencies using `pip`.

#### Steps:

1. **Clone the repository:**

   Clone the code to your local machine:

   ```bash
   git clone https://github.com/your-repo-url/flask-app.git
   cd flask-app
   ```

2. **Create a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**

   Install the dependencies listed in the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask application:**

   You can now start the Flask application using:

   ```bash
   python solution.py
   ```

#### Access the Application:

Once the Flask application is running, you can access it via your browser or `curl`:

```
http://localhost:5000
```

Test using `curl`:

```bash
curl http://localhost:5000/your-endpoint -X GET
```

---

## Summary

- **Docker**: Use `docker-compose up` to run the app in a Docker container.
- **Pip Installation**: Install dependencies with `pip install -r requirements.txt` and run `python solution.py`.
- **curl**: Use `curl` to send HTTP requests to the running application.

If you have any issues or need further assistance, feel free to open an issue in the repository!
