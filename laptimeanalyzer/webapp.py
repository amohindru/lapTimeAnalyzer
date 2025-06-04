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

    driver1 = request.args.get('driver1') or (drivers[0] if drivers else None)
    driver2 = request.args.get('driver2') or (drivers[1] if len(drivers) > 1 else driver1)

    if driver1 and driver2:
        df1 = df[df['driver'] == driver1]
        df2 = df[df['driver'] == driver2]
        merged = df1[['lap', 'lap_time']].merge(
            df2[['lap', 'lap_time']], on='lap', suffixes=(f'_{driver1}', f'_{driver2}')
        )
        merged['diff'] = merged[f'lap_time_{driver1}'] - merged[f'lap_time_{driver2}']
        title = f"{driver1} vs {driver2} (positive means {driver1} slower)"
        fig = px.bar(merged, x='lap', y='diff', title=title)
        compare_graph = fig.to_html(full_html=False)
    else:
        compare_graph = ''

    return render_template(
        'dashboard.html',
        drivers=drivers,
        selected_driver1=driver1,
        selected_driver2=driver2,
        compare_graph=compare_graph,
        year=lap_year,
        circuit_name=df['track'].iloc[0] if not df.empty else '',
    )


if __name__ == '__main__':
    app.run(debug=True)
