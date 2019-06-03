import boto3

client = boto3.client('sagemaker-runtime')

custom_attributes = "c000b4f9-df62-4c85-a0bf-7c525f9104a4"  # An example of a trace ID.
endpoint_name = "nyc-taxi-requests-prediction-xgboost-5min-endpoint"                                       # Your endpoint name.
content_type = "text/csv;label_size=0"                                        # The MIME type of the input data in the request body.
accept = "text/json"                                              # The desired MIME type of the inference in the response.
payload = "6,1,0,4,0,0,0,1.0,3.0,4.0,2.0,6.0,2.0,8.0,1.0,9.0,0.0,9.0,8.0,11.0,19.0,11.0,30.0,7.0,37.0,9.0,46.0,7.0,53.0,2.0,2.0,3.0,3.0,5.0"                                             # Payload for inference.
 
response = client.invoke_endpoint(
    EndpointName=endpoint_name, 
    CustomAttributes=custom_attributes, 
    ContentType=content_type,
    Accept=accept,
    Body=payload
    )

print(response)
print(response['Body'].read())
 