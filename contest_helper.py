#!/bin/env python


def get_5min_id(x):
    return int((x-first_datetime).total_seconds()//(5*60))

def get_15min_id(x):
    return int((x-first_datetime).total_seconds()//(15*60))

def get_30min_id(x):
    return int((x-first_datetime).total_seconds()//(30*60))


def draw_taxi_zone_shape(pd, gp, zone_lookup, zone_shape):
    # Manhattan taxi zone lookup
    taxi_zone_lookup = pd.read_csv(zone_lookup)
    print('taxi_zone_lookup:', taxi_zone_lookup.shape)
    manhattan_location_ids = taxi_zone_lookup[taxi_zone_lookup['Borough']=='Manhattan']['LocationID'].values
    manhattan_location_num = len(manhattan_location_ids)
    print('manhattan_location_ids:', manhattan_location_ids.shape, manhattan_location_ids)
    print('manhattan_location_num:', manhattan_location_num)

    taxi_zone_lookup.head()

    # Manhattan taxi zones shape
    taxi_zones_shape = gp.GeoDataFrame.from_file(zone_shape)
    taxi_zones_shape = taxi_zones_shape[taxi_zones_shape['borough'] == 'Manhattan']
    taxi_zones_shape.head()

    return taxi_zones_shape



# filter abnormal data: tpep_pickup_datetime, tpep_dropoff_datetime, trip_distance, trip duration, trip_speed, total_amount, etc.
def filter_abnormal_data(sample):
    start = time.time()
    sample_manhattan = sample[sample['PULocationID'].isin(manhattan_location_ids)].copy()
    print('filter PULocationID:', sample_manhattan.shape, time.time()-start)
    sample_manhattan['tpep_pickup_datetime'] = pd.to_datetime(sample_manhattan['tpep_pickup_datetime'])
    print('tpep_pickup_datetime:', time.time()-start)
    sample_manhattan['tpep_dropoff_datetime'] = pd.to_datetime(sample_manhattan['tpep_dropoff_datetime'])
    print('tpep_dropoff_datetime:', time.time()-start)
    sample_manhattan = sample_manhattan[sample_manhattan['tpep_pickup_datetime'] >= first_datetime]
    print('filter tpep_pickup_datetime first_datetime:', sample_manhattan.shape, time.time()-start)
    sample_manhattan = sample_manhattan[sample_manhattan['tpep_pickup_datetime'] < last_datetime]
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