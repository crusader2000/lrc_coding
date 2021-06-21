import pickle
import boto3

access_key_id = ""
secret_access_key = ""

def connection_S3(loc):
    s3 = boto3.client('s3',aws_access_key_id = access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=loc)
    return s3

if __name__ == '__main__':


    region = 'ap-south-1'
    s3 = connection_S3(region)

    for i in range(20):
        try:
            location = {'LocationConstraint': region}
            s3.create_bucket(Bucket="cachestore"+str(i),
                                    CreateBucketConfiguration=location)
        except ClientError as e:
            print(e)
            continue
    
    # database
    db = {
        "locations" : {
            "test" : "location_none"
        },
        "upload_requests" : [["Time","File Name","Time Taken (in microseconds)"]],
        "download_requests" : [["Time","File Name","Num Global","Num Parity","Time Taken (in microseconds)"]],
        "aws_region" : region,
        "buckets" : ["cachestore"+str(i) for i in range(20)],
        "bucket_space" : [0 for i in range(20)]
    }

    # Its important to use binary mode
    dbfile = open('pckl', 'wb')
    pickle.dump(db, dbfile)
    dbfile.close()