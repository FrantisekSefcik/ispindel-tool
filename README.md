# iSpindel Data Logger & Visualization System

A complete system for logging and visualizing data from iSpindel brewing devices using FastAPI and InfluxDB's built-in dashboards.

## Project Structure

```
├── app.py                 # FastAPI application
├── Dockerfile             # For building the API service
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Orchestrates all services
├── .env.template          # Example environemnt variables
```

## Features

- **Simple API**: REST endpoint for iSpindel devices to send their measurements
- **Persistent Storage**: Time-series database (InfluxDB) optimized for sensor data
- **Built-in Visualization**: Pre-configured InfluxDB dashboards showing:
  - Temperature & Gravity trends
  - Battery level monitoring
  - Angle measurements
  - Signal strength (RSSI)

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Setup

1. Clone this repository
2. Navigate to the project directory
3. Create the necessary environment variables:

```bash
cp .env.template .env
```

4. Start the services:

```bash
docker-compose up -d
```

5. Access the services:
   - API: [http://localhost:8000](http://localhost:8000)
   - InfluxDB UI: [http://localhost:8086](http://localhost:8086) (login with admin/password123)

## API Usage

To send data to the API, make a POST request to `/log` with JSON data:

```bash
curl -X POST "http://localhost:8000/log" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iSpindel001",
    "ID": 1,
    "angle": 27.5,
    "temperature": 21.4,
    "temp_units": "C",
    "battery": 3.85,
    "gravity": 1.012,
    "interval": 900,
    "RSSI": -78
  }'
```

## Configuring iSpindel

Configure your iSpindel device to send data to the API:

1. Access the iSpindel configuration page
2. Set the service type to "HTTP"
3. Enter the API endpoint URL: `http://<your-server-ip>:8000/log`
4. Set the update interval (in seconds)

## Setting Up InfluxDB Dashboards

The included initialization script will create a dashboard automatically, but you can also create dashboards manually:

1. Log into the InfluxDB interface at http://localhost:8086
2. Navigate to "Dashboards" in the left sidebar
3. Click "Create Dashboard" > "New Dashboard"
4. Add cells for the metrics you want to visualize (temperature, gravity, etc.)
5. For each cell, use Flux queries similar to:
   ```
   from(bucket: "ispindel_data")
     |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
     |> filter(fn: (r) => r["_measurement"] == "ispindel_measurement")
     |> filter(fn: (r) => r["_field"] == "temperature")
   ```

## Security Notes

- Default credentials are included for easy setup, but **should be changed** in production:
  - InfluxDB admin: admin/password123
  - InfluxDB token: "my-super-secret-token"

## Customization

- Add more metrics to the API by updating the `SpindelData` model in `app.py`
- Create additional cells or dashboards in InfluxDB's interface
- Customize data retention policies in InfluxDB's "Data" > "Buckets" section

## Troubleshooting

- Check service status: `docker-compose ps`
- View logs: `docker-compose logs -f [service_name]`
- Verify API health: `curl -X GET "http://localhost:8000/health"`