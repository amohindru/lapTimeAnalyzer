from flask import Flask, request, render_template, redirect, url_for
import plotly.express as px

from .data import compute_deltas, fetch_lap_times, fetch_circuits

app = Flask(__name__)

# In-memory storage of fetched data
lap_data = None
lap_year = None
lap_circuit = None


@app.route('/', methods=['GET', 'POST'])
def index():
    global lap_data, lap_year, lap_circuit

    years = list(range(2018, 2024))
    year = request.form.get('year') or request.args.get('year') or str(years[-1])
    circuits = fetch_circuits(year)

    if request.method == 'POST' and request.form.get('circuit'):
        lap_year = year
        lap_circuit = request.form['circuit']
        lap_data = compute_deltas(fetch_lap_times(year, lap_circuit))
        return redirect(url_for('dashboard'))

    return render_template(
        'index.html',
        years=years,
        circuits=circuits,
        selected_year=year,
        selected_circuit=request.form.get('circuit'),
    )


@app.route('/dashboard')
def dashboard():
    global lap_data
    if lap_data is None:
        return redirect(url_for('index'))

    df = lap_data.copy()
    drivers = sorted(df['driver'].dropna().unique()) if 'driver' in df.columns else []
    teams = sorted(df['team'].dropna().unique()) if 'team' in df.columns else []
    tracks = sorted(df['track'].dropna().unique()) if 'track' in df.columns else []

    driver = request.args.get('driver')
    team = request.args.get('team')
    track = request.args.get('track')

    if driver:
        df = df[df.get('driver') == driver]
    if team:
        df = df[df.get('team') == team]
    if track:
        df = df[df.get('track') == track]

    if 'lap' in df.columns and 'lap_time' in df.columns:
        fig_time = px.line(df, x='lap', y='lap_time', color='driver', title='Lap Times')
        fig_delta = px.line(df, x='lap', y='delta', color='driver', title='Lap Time Deltas')
        time_graph = fig_time.to_html(full_html=False)
        delta_graph = fig_delta.to_html(full_html=False)
    else:
        time_graph = delta_graph = ''

    return render_template(
        'dashboard.html',
        drivers=drivers,
        teams=teams,
        tracks=tracks,
        selected_driver=driver,
        selected_team=team,
        selected_track=track,
        time_graph=time_graph,
        delta_graph=delta_graph,
        year=lap_year,
        circuit_name=df['track'].iloc[0] if not df.empty else '',
    )


if __name__ == '__main__':
    app.run(debug=True)
