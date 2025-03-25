#!/usr/bin/env python3

import os
import json
import pandas as pd
import numpy as np
import pdfkit
import jinja2

# Example: Your custom result class
from folderresults import AggregatedResults
import plot_gen  # Our new separate plotting module

def main():
    # Directory to load data from
    load_dir = './test/'

    # Load form.json
    with open(os.path.join(load_dir, 'form.json')) as f:
        form = json.load(f)

    # Load cohorts.json (peer data)
    with open('cohorts.json') as f:
        cohort_map = json.load(f)

    # Identify the participant's cohort
    with open(os.path.join(load_dir, 'cohort.json')) as f:
        cohort_json = json.load(f)
        cohort = cohort_json['cohort']

    # This is the peer data for that cohort
    participant_peer_data = cohort_map[cohort]
    print(participant_peer_data)

    # Load DMO history
    with open(os.path.join(load_dir, 'dmo_history.json')) as f:
        dmo_history = json.load(f)

    # Example: build your typical arrays (just a demonstration)
    # The real code depends on your actual data structure
    dmo_index = [entry['StartDay'] for entry in dmo_history]
    dmo_walking_speed = [entry['MeanWalkingSpeed'] for entry in dmo_history]

    # Convert into a DataFrame
    # Suppose you want to plot 'Walking Speed' vs 'Capture Day'
    # We'll just override with example data for demonstration:
    dmo_speed_df = pd.DataFrame({
        "Capture Day": [1, 2, 3, 4, 5],
        "Walking Speed (m/sec)": [0.52, 0.50, 0.47, 0.49, 0.48]
    }).set_index("Capture Day")

    # Generate a line plot for DMO speed
    plot_gen.save_plot(
        data=dmo_speed_df,
        plot_type='line',
        xlabel='Assessment Number',
        ylabel='Walking Speed (m/sec)',
        title='Change in Walking Speed',
        filename='assets/img/dmo.svg'
    )

    # Another sample for your 'Longest Walking Bout' data
    # (Overriding with example numbers)
    dmo_max_bout_df = pd.DataFrame({
        "Capture Day": [1, 2, 3, 4, 5],
        "Longest Walk Bout (s)": [38.2, 40.51, 39.8, 37.6, 33.2]
    }).set_index("Capture Day")
    plot_gen.save_plot(
        data=dmo_max_bout_df.rename(columns={"Longest Walk Bout (s)":"Longest Bout (s)"}),
        plot_type='line',
        xlabel='Assessment Number',
        ylabel='Longest Bout (s)',
        title='Change in Longest Walking Bouts',
        filename='assets/img/wbd.svg'
    )

    # Now load or compute the participant's results
    result = AggregatedResults()
    result.read_data(load_dir)

    # Peer comparison data frames
    peer_mws_df = pd.DataFrame(
        [result.mean_walking_speed, participant_peer_data['mws']],
        columns=['Walking Speed'],
        index=[form['participantId'], cohort]
    )
    peer_msl_df = pd.DataFrame(
        [result.mean_stride_length, participant_peer_data['msl']],
        columns=['Stride Length'],
        index=[form['participantId'], cohort]
    )
    peer_cad_df = pd.DataFrame(
        [result.mean_cadence, participant_peer_data['mc']],
        columns=['Cadence'],
        index=[form['participantId'], cohort]
    )

    # Create bar charts for peer comparison
    plot_gen.save_plot(
        peer_mws_df,
        'bar',
        '',
        'Mean Walking Speed (m/s)',
        'Peer Comparison - Walking Speed',
        'assets/img/peer_ws.svg'
    )
    plot_gen.save_plot(
        peer_msl_df,
        'bar',
        '',
        'Mean Stride Length (m)',
        'Peer Comparison - Stride Length',
        'assets/img/peer_msl.svg'
    )
    plot_gen.save_plot(
        peer_cad_df,
        'bar',
        '',
        'Mean Cadence (/s)',
        'Peer Comparison - Cadence',
        'assets/img/peer_mcad.svg'
    )

    # Example: multi-subplot bar chart for daily stride charts (hourly data)
    steps_index = list(range(24))  # Hours
    all_step_data = []
    all_step_labels = []

    # for i in range(result.number_sessions):
    #     session = result.results[i]
    #     steps = []
    #     for j in range(len(session.hourly_speed)):
    #         # Directly append the integer if session.hourly_speed[j] is just an int
    #         steps.append(session.hourly_speed[j])
    #     all_step_data.append(steps)
    #     all_step_labels.append(session.day)


    # plot_gen.plot_bar_multiple(
    #     data_list=all_step_data,
    #     labels=all_step_labels,
    #     ylabel='Minutes of activity',
    #     title='Activity levels',
    #     filename='assets/img/hourly_steps.svg'
    # )

    # Now, optionally build a summary dictionary for a Jinja2 template
    sd = {
        'title': 'Mobility Report',
        'ns': f"{result.number_sessions}",
        'nbs': f"{result.number_of_bouts}",
        'cad': f"{result.mean_cadence:10.2f}",
        'mws': f"{result.mean_walking_speed:10.2f}",
        'sl': f"{result.mean_stride_length:10.2f}",
        'avg_steps': f"{15000:10.0f}",
        'ads': result.earliest_day().day + ' - ' + result.last_day().day,
        'stdt': result.earliest_day().day,
        'eddt': result.last_day().day,
        'mdwts': f"{result.mean_daily_walking_time:10.2f}",
        'mdwth': f"{(result.mean_daily_walking_time / 3600):2.2f}",
        'pid': form['participantId']
    }

    # Add some logic to compare participant vs peer
    if result.mean_walking_speed > participant_peer_data['mws']:
        sd['pmws_comments'] = 'Your walking speed is faster than the average for your condition'
    else:
        sd['pmws_comments'] = 'Your walking speed is slower than the average for your condition'

    # etc. for stride length, cadence, etc.
    # ... fill out sd dict as needed ...

    # Render a Jinja2 template (index.html) into an HTML report
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=''))
    template = env.get_template('index.html')
    html = template.render(results=result, pid='100', sd=sd)

    with open('report.html', 'w') as f:
        f.write(html)

    # Optionally convert HTML to PDF:
    # pdfkit.from_file('report.html', 'report.pdf')


if __name__ == '__main__':
    main()
