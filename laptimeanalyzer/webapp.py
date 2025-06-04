from flask import Flask, request, render_template, redirect, url_for
import plotly.express as px

from .data import load_lap_times, compute_deltas

app = Flask(__name__)

# In-memory storage of uploaded data
lap_data = None


@app.route('/', methods=['GET', 'POST'])
def index():
    global lap_data
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            lap_data = compute_deltas(load_lap_times(file))
            return redirect(url_for('dashboard'))
    return render_template('index.html')


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
    )


if __name__ == '__main__':
    app.run(debug=True)
