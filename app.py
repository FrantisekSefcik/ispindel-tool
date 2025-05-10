from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os

# InfluxDB connection settings from environment variables
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://0.0.0.0:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "my-super-secret-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "brewery")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "ispindel_data")


# Data model based on the provided iSpindel data format
class SpindelData(BaseModel):
    name: str
    ID: int
    angle: float
    temperature: float
    temp_units: str
    battery: float
    gravity: float
    interval: int
    RSSI: int


# Initialize FastAPI app
app = FastAPI(title="iSpindel Data Logger")

# Create InfluxDB client
influx_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)


@app.get("/")
def read_root():
    return {"status": "online", "message": "iSpindel Data Logger API"}


@app.post("/log")
def log_data(data: SpindelData):
    try:
        # Create a measurement point for InfluxDB
        point = Point("ispindel_measurement") \
            .tag("device_name", data.name) \
            .tag("device_id", str(data.ID)) \
            .tag("temp_units", data.temp_units) \
            .field("angle", data.angle) \
            .field("temperature", data.temperature) \
            .field("battery", data.battery) \
            .field("gravity", data.gravity) \
            .field("interval", data.interval) \
            .field("rssi", data.RSSI)

        # Write to InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)

        return {"status": "success", "message": f"Data logged for {data.name}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log data: {str(e)}")


@app.get("/health")
def health_check():
    try:
        # Simple health check to verify the API can connect to InfluxDB
        health = influx_client.health()
        if health.status == "pass":
            return {"status": "healthy", "influxdb_connection": "ok"}
        else:
            return {"status": "degraded", "influxdb_connection": "failing"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)