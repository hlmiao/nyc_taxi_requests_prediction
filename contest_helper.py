#!/usr/bin/env python

import time
import pickle
import datetime
import numpy as np
import pandas as pd
import geopandas as gp


class NycTaxiAnalyzer:
    first_datetime = None
    last_datetime = None
    taxi_zone_lookup = None
    manhattan_location_ids = None
    manhattan_location_num = None
    
    def __init__(self, zone_lookup_csv, shape_of_zones_csv, first_datetime=None, last_datetime=None):
        self.first_datetime = first_datetime
        self.last_datetime = last_datetime
        
        # Manhattan taxi zone lookup
        self.taxi_zone_lookup = pd.read_csv(zone_lookup_csv)
        self.manhattan_location_ids = self.taxi_zone_lookup[self.taxi_zone_lookup['Borough']=='Manhattan']['LocationID'].values
        self.manhattan_location_num = len(self.manhattan_location_ids)
        # Manhattan taxi zones shape
        self.taxi_zones_shape = gp.GeoDataFrame.from_file(shape_of_zones_csv)
        self.taxi_zones_shape = self.taxi_zones_shape[self.taxi_zones_shape['borough'] == 'Manhattan']
        self.taxi_zones_shape.head()

        
    def get_5min_id(self, x):
        return int((x-self.first_datetime).total_seconds()//(5*60))

    
    def get_15min_id(self, x):
        return int((x-self.first_datetime).total_seconds()//(15*60))

    
    def get_30min_id(self, x):
        return int((x-self.first_datetime).total_seconds()//(30*60))

    
    def describe(self):
        print('taxi_zone_lookup:', self.taxi_zone_lookup.shape)
        print('manhattan_location_ids:', self.manhattan_location_ids.shape, self.manhattan_location_ids)
        print('manhattan_location_num:', self.manhattan_location_num)

        self.taxi_zone_lookup.head()
        
        self.taxi_zones_shape.plot()


    # filter abnormal data: tpep_pickup_datetime, tpep_dropoff_datetime, trip_distance, trip duration, trip_speed, total_amount, etc.
    def filter_abnormal_data(self, sample):
        start = time.time()
        sample_manhattan = sample[sample['PULocationID'].isin(self.manhattan_location_ids)].copy()
        print('filter PULocationID:', sample_manhattan.shape, time.time()-start)
        sample_manhattan['tpep_pickup_datetime'] = pd.to_datetime(sample_manhattan['tpep_pickup_datetime'])
        print('tpep_pickup_datetime:', time.time()-start)
        sample_manhattan['tpep_dropoff_datetime'] = pd.to_datetime(sample_manhattan['tpep_dropoff_datetime'])
        print('tpep_dropoff_datetime:', time.time()-start)
        sample_manhattan = sample_manhattan[sample_manhattan['tpep_pickup_datetime'] >= self.first_datetime]
        print('filter tpep_pickup_datetime first_datetime:', sample_manhattan.shape, time.time()-start)
        sample_manhattan = sample_manhattan[sample_manhattan['tpep_pickup_datetime'] < self.last_datetime]
        print('filter tpep_pickup_datetime last_datetime:', sample_manhattan.shape, time.time()-start)
        sample_manhattan = sample_manhattan[sample_manhattan['trip_distance'] > 0]
        print('filter trip_distance:', sample_manhattan.shape, time.time()-start)
        sample_manhattan['trip_duration'] = (sample_manhattan['tpep_dropoff_datetime']-sample_manhattan['tpep_pickup_datetime']).dt.total_seconds()
        print('trip_duration:', time.time()-start)
        sample_manhattan = sample_manhattan[sample_manhattan['trip_duration'] > 0]
        print('filter trip_duration:', sample_manhattan.shape, time.time()-start)
        sample_manhattan['trip_speed'] = sample_manhattan['trip_distance']/sample_manhattan['trip_duration']*3600
        print('trip_speed:', time.time()-start)
        sample_manhattan = sample_manhattan[sample_manhattan['trip_speed'] > 0]
        sample_manhattan = sample_manhattan[sample_manhattan['trip_speed'] <= 200]
        print('filter trip_speed:', sample_manhattan.shape, time.time()-start)
        sample_manhattan = sample_manhattan[sample_manhattan['total_amount'] > 0]
        print('filter total_amount:', sample_manhattan.shape, time.time()-start)

        return sample_manhattan