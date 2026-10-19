# Delivery Time Predictor API

FastAPI service for the SCSE3040 delivery-time prediction practical.

## Endpoints
- `GET /health` — health check
- `GET /docs` — interactive API documentation
- `POST /predict` — validated delivery-time prediction

## Deploy on Render using Docker
1. Create a GitHub repository and upload the contents of this folder to its root.
2. In Render, create a new **Web Service** and connect that GitHub repository.
3. Choose the Docker runtime if asked. Keep the default Dockerfile path `./Dockerfile`.
4. Deploy and wait until the service reports Live.
5. Open `https://YOUR-SERVICE.onrender.com/docs`.
6. Test the successful and invalid request examples below. Use your actual assigned Render URL in the submission PDF.

## Successful request example
```json
{
  "distance_km": 5,
  "prep_time_min": 20,
  "traffic_level": 2,
  "rain": 1
}
```

## Invalid request example (should return HTTP 422)
```json
{
  "distance_km": -1,
  "prep_time_min": 20,
  "traffic_level": 2,
  "rain": 1
}
```

## Local run (optional)
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```
Then visit `http://127.0.0.1:8000/docs`.

AI-use disclosure: AI assisted with writing/debugging deployment code. Update the wording if your actual use differs and follow the course policy.
