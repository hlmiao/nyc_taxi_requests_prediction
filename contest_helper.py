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
    
    def get_all_index_and_static(self, last_id, id_name):
        start = time.time()
        all_id = np.array([i for i in range(int(last_id)) for _ in range(self.manhattan_location_num)])
        all_LocationID = np.array([i for _ in range(int(last_id)) for i in self.manhattan_location_ids])
        print('all_id:', all_id.shape, all_id)
        print('all_LocationID:', all_LocationID.shape, all_LocationID)

        all_index = pd.DataFrame({id_name: all_id, 'LocationID': all_LocationID})
        all_index.set_index([id_name, 'LocationID'], inplace=True)
        print('all_index:', all_index.shape)

        all_static = pd.DataFrame({id_name: all_id, 'LocationID': all_LocationID})
        all_static['tpep_pickup_datetime'] = pd.to_timedelta(all_static[id_name]*5*60, unit='s') + self.first_datetime
        print('tpep_pickup_datetime:', time.time()-start)
        #all_static['tpep_pickup_year'] = all_static['tpep_pickup_datetime'].dt.year
        #print('tpep_pickup_year:', time.time()-start)
        all_static['tpep_pickup_month'] = all_static['tpep_pickup_datetime'].dt.month
        print('tpep_pickup_month:', time.time()-start)
        all_static['tpep_pickup_day'] = all_static['tpep_pickup_datetime'].dt.day
        print('tpep_pickup_day:', time.time()-start)
        all_static['tpep_pickup_hour'] = all_static['tpep_pickup_datetime'].dt.hour
        print('tpep_pickup_hour:', time.time()-start)
        all_static['tpep_pickup_weekday'] = all_static['tpep_pickup_datetime'].dt.weekday
        print('tpep_pickup_weekday:', time.time()-start)
        all_static['is_weekend'] = all_static['tpep_pickup_weekday'].map(lambda x: x >= 5 and 1 or 0)
        print('is_weekend:', time.time()-start)
        all_static['is_morning_peak'] = all_static['tpep_pickup_hour'].map(lambda x: 7 <= x <= 9 and 1 or 0)
        print('is_morning_peak:', time.time()-start)
        all_static['is_evening_peak'] = all_static['tpep_pickup_hour'].map(lambda x: 17 <= x <= 19 and 1 or 0)
        print('is_evening_peak:', time.time()-start)
        all_static.drop(['tpep_pickup_datetime'], axis=1, inplace=True)
        all_static.set_index([id_name, 'LocationID'], inplace=True)
        print('all_static:', all_static.shape)
        
        return all_index, all_static