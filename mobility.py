import pandas as pd
import numpy as np
import jinja2
import os
import json
from folderresults import *
import plot_gen  # Import the new plotting module
import pdfkit
# Directory to load data from
load_dir = './test/'

# Load the form.json data
with open(load_dir + 'form.json') as f:
    form = json.load(f)

# Load the cohort typical DMOs
with open('cohorts.json') as f:
    cohort_map = json.load(f)

# Identify the cohort from cohort.json
with open(load_dir + 'cohort.json') as f:
    cohort_json = json.load(f)
    cohort = cohort_json['cohort']

# Keep the peer data
participant_peer_data = cohort_map[cohort]
print(participant_peer_data)


# Load the DMO history 
with open(load_dir + 'dmo_history.json') as f:
    dmo_history = json.load(f)

dmo_index = [entry['StartDay'] for entry in dmo_history]
dmo_walking_speed = [entry['MeanWalkingSpeed'] for entry in dmo_history]
dmo_walking_bout_maximum_duration = [entry['MaximumWalkingBoutDuration'] for entry in dmo_history]

dmo_speed_df = pd.DataFrame(dmo_walking_speed, columns=['Walking Speed'], index=dmo_index)
dmo_maximum_bout_duration_df = pd.DataFrame(dmo_walking_bout_maximum_duration, columns=['Maximum Walking Bout Duration'], index=dmo_index)

# Generate and save line plots
plot_gen.save_plot(dmo_speed_df, 'line', 'Capture Day', 'Walking Speed (m/sec)', 'Change in Walking Speed', 'assets/img/dmo.svg')
plot_gen.save_plot(dmo_maximum_bout_duration_df, 'line', 'Capture Day', 'Longest Walking Bout(s)', 'Change in Longest Walking Bouts', 'assets/img/wbd.svg')

# Load the data from this collection
result = AggregatedResults()
result.read_data(load_dir)

# Peer comparison dataframes
peer_mws_df = pd.DataFrame([result.mean_walking_speed, participant_peer_data['mws']], columns=['Walking Speed'], index=[form['participantId'], cohort])
peer_msl_df = pd.DataFrame([result.mean_stride_length, participant_peer_data['msl']], columns=['Stride Length'], index=[form['participantId'], cohort])
peer_cad_df = pd.DataFrame([result.mean_cadence, participant_peer_data['mc']], columns=['Cadence'], index=[form['participantId'], cohort])

# Generate and save bar plots
plot_gen.save_plot(peer_mws_df, 'bar', '', 'Mean Walking Speed \n (m/s)', 'Peer Comparison - Walking Speed', 'assets/img/peer_ws.svg')
plot_gen.save_plot(peer_msl_df, 'bar', '', 'Mean Stride Length (m)', 'Peer Comparison - Stride Length', 'assets/img/peer_msl.svg')
plot_gen.save_plot(peer_cad_df, 'bar', '', 'Mean Cadence (/s)', 'Peer Comparison - Cadence', 'assets/img/peer_mcad.svg')

# Load the template
env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=''))
template = env.get_template('index.html')

# daily stride chart 
steps_index = list(range(24))  # Hourly index
all_step_data = []
all_step_labels = []

for i in range(result.number_sessions):
    session = result.results[i]
    steps = []
    for j in range(0, len(session.hourly_speed)):
        steps.append(session.hourly_speed[j]['strides'])
    all_step_data.append(steps)
    all_step_labels.append(session.day)

plot_gen.plot_bar_multiple(all_step_data,all_step_labels,'Minutes of activity','Activity levels','assets/img/hourly_steps.svg')



# Build the summary data
sd = {
    # Title
    'title': 'Mobility Report',
    
    # Number of sessions
    'ns':f"{result.number_sessions}",

    # Number of bouts
    'nbs': f"{result.number_of_bouts}",

    # Mean Cadence
    'cad': f"{result.mean_cadence:10.2f}",

    # Mean walking speed
    'mws': f"{result.mean_walking_speed:10.2f}",

    # Mean Stride Length
    'sl': f"{result.mean_stride_length:10.2f}",

    # Mean Daily Steps 
    # 'avg_steps' : f"{result.mean_daily_steps:10.2f}",
    'avg_steps' : f"{15000:10.0f}",
    # Data collection range
    'ads': result.earliest_day().day + ' - ' + result.last_day().day,

    # Start date
    'stdt': result.earliest_day().day,

    # End date
    'eddt': result.last_day().day,

    # Averate daily walking time in seconds
    'mdwts': f"{result.mean_daily_walking_time:10.2f}",

    # Average daily walking time in hours,
    'mdwth': f"{(result.mean_daily_walking_time / 3600):2.2f}",

    # Participant Code
    'pid': form['participantId']
}


# Some comments for the comparison plots
if result.mean_walking_speed>participant_peer_data['mws']:
    sd['pmws_comments'] = 'Your walking speed is faster than the average for your condition'
elif result.mean_walking_speed<participant_peer_data['mws']:
    sd['pmws_comments'] = 'Your walking speed is slower than the average for your condition'
else:
    sd['pwms_comments'] = 'Your walking speed is the same as others with your condition'


if result.mean_stride_length>participant_peer_data['msl']:
    sd['pmsl_comments'] = 'Your stride length is longer than average for your condition'
elif result.mean_stride_length<participant_peer_data['mdl']:
    sd['pmsl_comments'] = 'Your stride length is shorter than average for your condition'
else:
    sd['pwsl_comments'] = 'Your stride length is the same as others with your condition'

if result.mean_cadence>participant_peer_data['mc']:
    sd['pmwcad_comments'] = 'Your walking cadence is higher than average for your condition'
elif result.mean_cadence<participant_peer_data['mc']:
    sd['pmwcad_comments'] = 'Your walking cadence is lower than average for your condition'
else:
    sd['pmwcad_comments'] = 'Your walkign cadence is the same as others with your condition'


html = template.render(results=result, pid='100', sd=sd)

# Write the HTML file
with open('report.html', 'w') as f:
    f.write(html)
