# lapTimeAnalyzer

F1 Laptime Analyzer - Visualize laptime deltas and analyze differences between drivers, teams, and tracks.

## Running the Web Application

To launch the Flask webapp locally:

```bash
python -m laptimeanalyzer.webapp
```

This will start a development server on <http://localhost:5000> where you can select a season and circuit to fetch lap times from the Ergast API. The dashboard lets you compare two drivers lap by lap to see who was quicker on each lap.

## Deployment Notes

The Flask app can be hosted on platforms such as Heroku or Render. Configure the environment to install the requirements and run `python -m laptimeanalyzer.webapp` as the web command.
