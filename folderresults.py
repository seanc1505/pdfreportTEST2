import pandas as pd
import math
import os
import json
from datetime import date
from datetime import datetime

# Get a list of subdirectories
def fast_scandir(dirname):
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders

# Class to hold results from a single day folder
class FolderResults:
    def __init__(self):
        self.wb = None
        self.mean_wb_duration = 0
        self.maximum_wb_duration = 0
        self.aggregaged = None
        self.strides = None
        self.start_timestamp = 0
        self.sample_rate = 100
        self.metadata = {}
        self.hourly_speed = {}
        self.total_walking_time = 0
        self.day = ''
    
    def read_folder(self, folder):
        if os.path.exists(folder + '/wb.csv'):
            self.wb = pd.read_csv(folder + '/wb.csv')

        if os.path.exists(folder + '/aggregated.csv'):
            self.aggregated = pd.read_csv(folder + '/aggregated.csv')

        if os.path.exists(folder + '/stride.csv'):
            self.strides = pd.read_csv(folder + '/stride.csv')

        if os.path.exists(folder + '/metadata.json'):
            with open(folder + '/metadata.json') as f:
                self.metadata = json.load(f)
                self.day = self.metadata['session_day']
                self.start_timestamp = self.metadata['session_timestamp']

                # Set the timestamps for the walking bouts etc
        
        
        # Work out actual times for the walking bouts
        if self.wb is not None:
            # Have walking bout data
            starts = self.create_timestamps(self.wb['start'])
            ends = self.create_timestamps(self.wb['end'])
            self.wb['start_times'] = starts
            self.wb['end_times'] = ends
            bout_hours = self.create_hours_of_day(self.wb['start_times'])
            self.wb['bout_hour'] = bout_hours
            self.calculate_hourly_speed()
            self.calculate_total_walking_time()
            self.calculate_mean_walking_bout_duration()
            self.calculate_maximum_walking_bout_duration()
            
    def calculate_total_walking_time(self):
        if self.wb is not None:
            self.total_walking_time = self.wb['duration_s'].sum()
        else:
            self.total_walking_time = 0

    def calculate_maximum_walking_bout_duration(self):
        if self.wb is not None:
            self.maximum_wb_duration = self.wb['duration_s'].max()
        else:
            self.maximum_wb_duration = 0

    def calculate_mean_walking_bout_duration(self):
        if self.wb is not None:
            self.mean_wb_duration = self.wb['duration_s'].mean()
        else:
            self.mean_wb_duration = 0

    def calculate_hourly_speed(self):
        self.hourly_speed = {}
        for i in range(0, 24):
            self.hourly_speed[i] = {
                'strides': 0,
                'sum': 0,
                'count': 0
            }
        
        def do_mean(row):
            hour = row['bout_hour']
            speed = self.hourly_speed[hour]

            bs = row['walking_speed_mps']
            if math.isnan(bs) == False:
                speed['sum'] = speed['sum'] + bs
                speed['count'] = speed['count'] + 1

            strides = row['n_strides']

            if math.isnan(strides)==False:
                speed['strides'] = speed['strides'] + strides

            return row

        self.wb.apply(do_mean, axis=1)
        for i in range(0, len(self.hourly_speed)):
            hr = self.hourly_speed[i]
            if hr['count']!=0:
                hr['mean'] = hr['sum'] / hr['count']

            else:
                hr['mean'] = 0


    
    def create_hours_of_day(self, column):
        def do_hour(x):
            return x.hour
        
        new_column = column.copy().apply(do_hour)
        return new_column
    
    def create_timestamps(self, column):
        def do_timestamp(x):
            dt = datetime.fromtimestamp(((self.start_timestamp) / 1000.0) + (x / 100))
            return dt
            
        new_column = column.copy().apply(do_timestamp)

        return new_column
    

# Contains an aggregated set of results for a list of folders
class AggregatedResults:
    def __init__(self):
        self.results = []
        self.mean_cadence = 0
        self.mean_walking_speed = 0
        self.mean_stride_length = 0
        self.mean_walking_bout_duration = 0
        self.maximum_walking_bout_duration = 0
        self.mean_daily_walking_time = 0
        self.number_sessions = 0
        self.number_of_bouts = 0
        self.all_bouts = None;
        self.all_strides = None;        

    def read_data(self, base_path):
        dirs = fast_scandir(base_path)
        walking_bouts = []
        strides = []
        daily_walking_time = []

        for i in range(0, len(dirs)):
            r = FolderResults()
            r.read_folder(dirs[i])
            self.results.append(r)
            walking_bouts.append(r.wb)
            strides.append(r.strides)
            daily_walking_time.append(r.total_walking_time)

        # Aggregate the walking bouts
        self.number_sessions = len(walking_bouts)
        self.all_bouts = pd.concat(walking_bouts, axis=0)
        self.number_of_bouts = len(self.all_bouts)

        self.mean_cadence = self.all_bouts['cadence_spm'].mean()
        self.mean_stride_length = self.all_bouts['stride_length_m'].mean()
        self.mean_walking_speed = self.all_bouts['walking_speed_mps'].mean()
        self.mean_walking_bout_duration = self.all_bouts['duration_s'].mean()
        self.maximum_walking_bout_duration = self.all_bouts['duration_s'].max()
        self.mean_daily_walking_time = pd.DataFrame(daily_walking_time,columns=['wt'])['wt'].mean()
        
        # Aggregate all of the strides
        self.all_strides = pd.concat(strides, axis=0)
                
    def earliest_day(self):
        earliest = 9999999999999
        earliest_result = None

        for i in range(0, len(self.results)):
            if self.results[i].start_timestamp < earliest:
                earliest = self.results[i].start_timestamp
                earliest_result = self.results[i]

        return earliest_result
    
    def last_day(self):
        latest = 0
        latest_result = None

        for i in range(0, len(self.results)):
            if self.results[i].start_timestamp > latest:
                latest = self.results[i].start_timestamp
                latest_result = self.results[i]

        return latest_result        