
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

HERE = Path(__file__).resolve().parent
FEATURES = ["distance_km", "prep_time_min", "traffic_level", "rain"]

app = FastAPI(
    title="Delivery Time Predictor",
    version="1.0.0",
    description="Predict delivery time from order and traffic features."
)

model = joblib.load(HERE / "model.joblib")


class Order(BaseModel):
    distance_km: float = Field(..., gt=0, le=50)
    prep_time_min: int = Field(..., ge=0, le=120)
    traffic_level: int = Field(..., ge=1, le=3)
    rain: int = Field(..., ge=0, le=1)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Delivery Time Predictor</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          background: #f1f5f9;
          margin: 0;
          padding: 40px 16px;
          color: #0f172a;
        }
        .card {
          max-width: 520px;
          margin: auto;
          background: white;
          padding: 28px;
          border-radius: 18px;
          box-shadow: 0 8px 30px #0001;
        }
        h1 { color: #2563eb; margin-top: 0; }
        label { display: block; margin-top: 16px; font-weight: bold; }
        input, select, button {
          box-sizing: border-box;
          width: 100%;
          padding: 12px;
          margin-top: 7px;
          border: 1px solid #cbd5e1;
          border-radius: 8px;
          font-size: 16px;
        }
        button {
          background: #2563eb;
          color: white;
          border: 0;
          cursor: pointer;
          margin-top: 24px;
        }
        button:disabled { opacity: .6; }
        #result {
          margin-top: 20px;
          padding: 14px;
          background: #eff6ff;
          border-radius: 8px;
          white-space: pre-wrap;
        }
        .links { margin-top: 20px; }
      </style>
    </head>
    <body>
      <main class="card">
        <h1>Delivery Time Predictor</h1>
        <p>Enter order details to estimate delivery time.</p>

        <form id="predictionForm">
          <label for="distance">Distance (km)</label>
          <input id="distance" type="number" min="0.1" max="50"
                 step="0.1" value="5" required>

          <label for="prep">Preparation time (minutes)</label>
          <input id="prep" type="number" min="0" max="120"
                 step="1" value="20" required>

          <label for="traffic">Traffic level</label>
          <select id="traffic">
            <option value="1">Low</option>
            <option value="2" selected>Medium</option>
            <option value="3">High</option>
          </select>

          <label for="rain">Is it raining?</label>
          <select id="rain">
            <option value="0" selected>No</option>
            <option value="1">Yes</option>
          </select>

          <button id="submitButton" type="submit">
            Predict Delivery Time
          </button>
        </form>

        <div id="result" role="status" aria-live="polite">
          Your prediction will appear here.
        </div>

        <div class="links">
          <a href="/docs">API Documentation</a>
        </div>
      </main>

      <script>
        const form = document.getElementById("predictionForm");
        const result = document.getElementById("result");
        const button = document.getElementById("submitButton");

        form.addEventListener("submit", async (event) => {
          event.preventDefault();
          button.disabled = true;
          result.textContent = "Calculating prediction...";

          const payload = {
            distance_km: Number(document.getElementById("distance").value),
            prep_time_min: Number(document.getElementById("prep").value),
            traffic_level: Number(document.getElementById("traffic").value),
            rain: Number(document.getElementById("rain").value)
          };

          try {
            const response = await fetch("/predict", {
              method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify(payload)
            });
            const data = await response.json();

            if (!response.ok) {
              result.textContent = "Request failed (" + response.status +
                "): " + JSON.stringify(data, null, 2);
            } else {
              result.textContent =
                "Estimated delivery time: " + data.delivery_min +
                " minutes\\nModel version: " + data.model_version;
            }
          } catch (error) {
            result.textContent = "Could not contact the API. Please try again.";
          } finally {
            button.disabled = false;
          }
        });
      </script>
    </body>
    </html>
    """


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
def predict(order: Order):
    row = pd.DataFrame([order.model_dump()])[FEATURES]
    return {
        "delivery_min": round(float(model.predict(row)[0]), 1),
        "model_version": app.version,
    }
