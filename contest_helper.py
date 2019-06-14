#!/usr/bin/env python

import time
import pickle
import datetime
import numpy as np
import pandas as pd
import geopandas as gp

import logging

class NycTaxiAnalyzer:
    first_datetime = None
    last_datetime = None
    taxi_zone_lookup = None
    location_ids = None
    location_num = None
    data = None
    
    def __init__(self):

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        
    def load_shape(self, zone_lookup_csv, shape_of_zones_csv, borough=None):

        # taxi zone lookup
        self.taxi_zone_lookup = pd.read_csv(zone_lookup_csv)
        self.location_ids = self.taxi_zone_lookup[
            self.taxi_zone_lookup['Borough']==borough]['LocationID'].values
        self.location_num = len(self.location_ids)

        # taxi zones shape
        self.taxi_zones_shape = gp.GeoDataFrame.from_file(shape_of_zones_csv)
        self.taxi_zones_shape = self.taxi_zones_shape[self.taxi_zones_shape['borough']==borough]
        #self.taxi_zones_shape.head()

    
    def get_diff_in_mins(self, start_time, end_time, num_of_mins):
        return int((end_time - start_time).total_seconds()//(num_of_mins * 60))

    
    def get_5min_id(self, x):
        return self.get_diff_in_mins(x, self.first_datetime, 5)

    
    def get_15min_id(self, x):
        return self.get_diff_in_mins(x, self.first_datetime, 15)

    
    def get_30min_id(self, x):
        return self.get_diff_in_mins(x, self.first_datetime, 30)

        
    def load_data(self, tripdata_folder, first_datetime=None, last_datetime=None):
        
        self.first_datetime = first_datetime
        self.last_datetime = last_datetime
        
        samples = []
        for m in range(self.first_datetime.month, self.last_datetime.month):
            # call pandas function to read csv from csv file, return variable should be sample
            start = time.time()
            sample = pd.read_csv(f'{tripdata_folder}/yellow_tripdata_2018-0{m}.csv')
            logging.info(f'read_csv 2018-0{m}: {time.time()-start}')

            start = time.time()
            sample = sample[sample['PULocationID'].isin(self.location_ids)]
            logging.info(f'filter PULocationID: {time.time()-start} {sample.shape}')
            
            start = time.time()
            sample['tpep_pickup_datetime'] = pd.to_datetime(sample['tpep_pickup_datetime'])
            logging.info(f'tpep_pickup_datetime: {time.time()-start} {sample.shape}')

            start = time.time()
            sample['tpep_dropoff_datetime'] = pd.to_datetime(sample['tpep_dropoff_datetime'])
            logging.info(f'tpep_dropoff_datetime: {time.time()-start} {sample.shape}')

            start = time.time()
            sample = sample[sample['tpep_pickup_datetime'] >= self.first_datetime]
            logging.info(f'filter tpep_pickup_datetime first_datetime: {time.time()-start} {sample.shape}')
            
            start = time.time()
            sample = sample[sample['tpep_pickup_datetime'] < self.last_datetime]
            logging.info(f'filter tpep_pickup_datetime last_datetime: {time.time()-start} {sample.shape}')

            start = time.time()
            tmp = (sample['tpep_dropoff_datetime'] - sample['tpep_pickup_datetime']).\
                dt.total_seconds().to_frame(name='trip_duration')
            logging.info(f'tpep_dropoff_datetime - tpep_pickup_datetime: {time.time()-start} {tmp.shape}')
            start = time.time()
            sample = sample.merge(tmp, how='left', left_index=True, right_index=True)
            logging.info(f'trip_duration: {time.time()-start} {sample.shape}')

            start = time.time()
            sample.loc[:,'trip_speed'] = sample['trip_distance']/sample['trip_duration']*3600
            logging.info(f'trip_speed: {time.time()-start} {sample.shape}')
            
            start = time.time()
            sample['date'] = sample['tpep_pickup_datetime'].dt.strftime('%Y-%m-%d')
            logging.info(f'filter date: {time.time()-start} {sample.shape}')
        
        
            # append, change and drop columns
            start = time.time()
            sample['store_and_fwd_flag'] = sample['store_and_fwd_flag'].map(lambda x: x == 'N' and 0 or 1)
            logging.info(f'store_and_fwd_flag: {time.time()-start} {sample.shape}')

            start = time.time()
            sample['tpep_pickup_5min_id'] = (sample['tpep_pickup_datetime']-self.first_datetime).dt.total_seconds()//(5*60)
            logging.info(f'tpep_pickup_5min_id: {time.time()-start} {sample.shape}')
            
            start = time.time()
            sample['tpep_pickup_15min_id'] = (sample['tpep_pickup_datetime']-self.first_datetime).dt.total_seconds()//(15*60)
            logging.info(f'tpep_pickup_15min_id: {time.time()-start} {sample.shape}')
            
            start = time.time()
            sample['tpep_pickup_30min_id'] = (sample['tpep_pickup_datetime']-self.first_datetime).dt.total_seconds()//(30*60)
            logging.info(f'tpep_pickup_30min_id: {time.time()-start} {sample.shape}')

            #sample.drop(['tpep_pickup_datetime', 'tpep_dropoff_datetime'], axis=1, inplace=True)  # , 'tpep_pickup_date', 'tpep_dropoff_date'
            #logging.info(f'sample.shape: {time.time()-start} {sample.shape}')

            samples.append(sample)
     
        start = time.time()
        self.data = pd.concat(samples, ignore_index=True)
        logging.info(f'concat: {time.time()-start} {self.data.shape}')

    
    def get_all_index_and_static(self, last_id, id_name):
        start = time.time()
        all_id = np.array([i for i in range(int(last_id)) for _ in range(self.location_num)])
        all_LocationID = np.array([i for _ in range(int(last_id)) for i in self.location_ids])
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