# nyc_taxi_requests_prediction
To demonstrate the demand forecast in each grid at 5min, 15min and 30min slot, we use the yellow New York City Taxi and Limousine Commission (TLC) Trip Record Data between Jan 2018 and June 2018 in Manhattan from AWS public datasets as source data (https://registry.opendata.aws/nyc-tlc-trip-records-pds/). We split the dataset into train part (2018.01.01-2018.05.31) and validate part (2018.06.01-2018.06.30). We demonstrate 4 methods to forecast demand: XGBoost, LightGBM, linear regression implemented using sklearn and linear regression implemented using TensorFlow, and evaluate the models using mean absolute error (MAE).

We mainly use linear regression algorithm as the baseline algorithm, and use XGBoost as the main algorithm. XGBoost is an optimized distributed gradient boosting library designed to be highly efficient, flexible and portable. It implements machine learning algorithms under the Gradient Boosting framework. XGBoost provides a parallel tree boosting (also known as GBDT, GBM) that solve many data science problems in a fast and accurate way.

To run this notebook, you have to download trip data from Amazon S3 bucket to nyc-tlc directory in your computer:

## TODO download data and unzip archive file commands [Question 1]
<pre>
https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2018-01.csv
https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2018-02.csv
https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2018-03.csv
https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2018-04.csv
https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2018-05.csv
https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2018-06.csv
https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
https://s3.amazonaws.com/nyc-tlc/misc/taxi_zones.zip (unzip)
</pre>

After download, your local directory structure should be:

<pre>
nyc-tlc
├── misc
│   ├── taxi\ _zone_lookup.csv
│   ├── taxi_zones
│   │   ├── taxi_zones.dbf
│   │   ├── taxi_zones.prj
│   │   ├── taxi_zones.sbn
│   │   ├── taxi_zones.sbx
│   │   ├── taxi_zones.shp
│   │   ├── taxi_zones.shp.xml
│   │   └── taxi_zones.shx
│   └── taxi_zones.zip
└── trip\ data
    ├── yellow_tripdata_2018-01.csv
    ├── yellow_tripdata_2018-02.csv
    ├── yellow_tripdata_2018-03.csv
    ├── yellow_tripdata_2018-04.csv
    ├── yellow_tripdata_2018-05.csv
    └── yellow_tripdata_2018-06.csv

3 directories, 15 files
</pre>

### Basic Prepare

We import all useful packages, and set the `first_datetime` to 2018-01-01 00:00:00, and `last_datetime` to 2018-07-01 00:00:00. We split the dataset into two parts: train and validate, by setting the `train_valid_split_datetime` to 2018-06-01 00:00:00.

### Taxi Zones

Since newest NYC Taxi dataset only provides `PULocationID` and `DOLocationID`, instead of `pickup_longitude`, `pickup_latitude`, `dropoff_longitude`, and `dropoff_latitude`, we can only predict requests in each `PULocationID` (zone). We load [taxi _zone_lookup.csv] and [taxi_zones.shp], and use `geopandas` to visualize the zones in Manhattan (69 in total).


### Data Prepare

We load all data from [nyc-tlc/trip data/] between Jan and June 2018, and filter abnormal data. We use `matplotlib` and `geopandas` to visualize some columns and help us to understand the trip data.

## [Question 2] TODO: load Manhattan data: from 2018-01 to 2018-06, call filter_abnormal_data to filter data

## [Question 3.1] TODO: Show first 5 rows of sample_manhattan

## [Question 3.2] TODO: Show statistics of sample_manhattan

### Feature Prepare

We set the `5min_id`, `15min_id` and `30min_id` to represent 5min, 15min and 30min slot. For example, time between 2018-01-01 00:00:00 and 2018-01-01 00:05:00 has a `5min_id` as 0, and time between 2018-01-01 00:05:00 and 2018-01-01 00:10:00 has a `5min_id` as 1, and the similar with `15min_id` and `30min_id`. For each `Xmin_id` (X represents 5, 15 or 30), we predict the requests in all 69 zones. We have some `static features` such as `month`, `day`, `hour`, `weekday`, `is_weekend`, `is_morning_peak`, `is_evening_pick` for all `Xmin_id` and zones. Also we can extend more static features such as weather and zone features. Other `dynamic features` includes requests in `5min ago`, `10min ago`, `15min ago`, `7days ago`, etc. Also we can extend more dynamic features such as total passengers in 5min ago. At last, we generate 34 features for each `Xmin_id` and zone.

## Train and Validate

We split all data into train and validate part. We demonstrate 4 methods to forecast requests: XGBoost, LightGBM, linear regression implemented using sklearn and linear regression implemented using TensorFlow, and evaluate the models using mean absolute error (MAE). We also visualize the prediction results between 2018-01-01 00:00:00 and 2018-01-01 00:05:00 using `geopandas` (the darker the color, the more demand), and we can visualize any time slot using this method.

## [Challenge Question] TODO: Add new prediction algorithm or change parameters of above 4 prediction algorithms