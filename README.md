# nyc_taxi_requests_prediction
To demonstrate the demand forecast in each grid at 5min, 15min and 30min slot, we use the yellow New York City Taxi and Limousine Commission (TLC) Trip Record Data between Jan 2018 and June 2018 in Manhattan from AWS public datasets as source data (https://registry.opendata.aws/nyc-tlc-trip-records-pds/). We split the dataset into train part (2018.01.01-2018.05.31) and validate part (2018.06.01-2018.06.30). We demonstrate 4 methods to forecast demand: XGBoost, LightGBM, linear regression implemented using sklearn and linear regression implemented using TensorFlow, and evaluate the models using mean absolute error (MAE).

We mainly use linear regression algorithm as the baseline algorithm, and use XGBoost as the main algorithm. XGBoost is an optimized distributed gradient boosting library designed to be highly efficient, flexible and portable. It implements machine learning algorithms under the Gradient Boosting framework. XGBoost provides a parallel tree boosting (also known as GBDT, GBM) that solve many data science problems in a fast and accurate way.

To run this notebook, you have to download trip data from Amazon S3 bucket to nyc-tlc directory in your computer:

## TODO download data and unzip archive file commands [Question 1]

https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2018-01.csv
https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2018-02.csv
https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2018-03.csv
https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2018-04.csv
https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2018-05.csv
https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2018-06.csv
https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
https://s3.amazonaws.com/nyc-tlc/misc/taxi_zones.zip (unzip)
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

