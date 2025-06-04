import pandas as pd
import requests


def _time_to_seconds(t):
    """Convert a lap time string like '1:39.019' to seconds."""
    if not isinstance(t, str):
        return float('nan')
    parts = t.split(":")
    if len(parts) == 2:
        minutes, sec = parts
    else:
        minutes, sec = 0, parts[0]
    return int(minutes) * 60 + float(sec)


def load_lap_times(file_obj):
    """Load lap times from a CSV file into a DataFrame."""
    return pd.read_csv(file_obj)


def compute_deltas(df, time_col="lap_time"):
    """Compute lap time deltas relative to the fastest lap."""
    fastest = df[time_col].min()
    df = df.copy()
    df["delta"] = df[time_col] - fastest
    return df


def fetch_circuits(year):
    """Return a list of (round, circuit name) tuples for a given year."""
    url = f"https://ergast.com/api/f1/{year}.json"
    res = requests.get(url, timeout=10)
    races = res.json().get("MRData", {}).get("RaceTable", {}).get("Races", [])
    return [(r["round"], r["Circuit"]["circuitName"]) for r in races]


def fetch_lap_times(year, round_num):
    """Fetch lap times for a given year and race round from the Ergast API."""
    base = "https://ergast.com/api/f1"
    lap_url = f"{base}/{year}/{round_num}/laps.json?limit=2000"
    lap_res = requests.get(lap_url, timeout=10)
    races = lap_res.json().get("MRData", {}).get("RaceTable", {}).get("Races", [])
    if not races:
        return pd.DataFrame()
    laps = races[0].get("Laps", [])

    rows = []
    for lap in laps:
        num = int(lap["number"])
        for t in lap.get("Timings", []):
            rows.append(
                {
                    "lap": num,
                    "driverId": t["driverId"],
                    "lap_time": _time_to_seconds(t["time"]),
                }
            )

    res_url = f"{base}/{year}/{round_num}/results.json"
    results_json = requests.get(res_url, timeout=10).json()
    race = results_json.get("MRData", {}).get("RaceTable", {}).get("Races", [])[0]
    results = race.get("Results", [])
    circuit_name = race.get("Circuit", {}).get("circuitName")

    driver_map = {
        r["Driver"]["driverId"]: {
            "driver": f"{r['Driver']['givenName']} {r['Driver']['familyName']}",
            "team": r["Constructor"]["name"],
        }
        for r in results
    }

    df = pd.DataFrame(rows)
    df["driver"] = df["driverId"].map(lambda d: driver_map.get(d, {}).get("driver"))
    df["team"] = df["driverId"].map(lambda d: driver_map.get(d, {}).get("team"))
    df["track"] = circuit_name
    df.drop(columns=["driverId"], inplace=True)
    return df
