import pickle
import boto3


access_key_id = ''
secret_access_key = '' 

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
        except:
            continue
    
    # database
    db_upload = {
        "locations" : {
            "test" : "location_none"
        },
        "upload_requests" : [["Time","File Name","Time To Encode (in microseconds)",
        "Time To Upload (in microseconds)","Total Time Taken (in microseconds)"]],
        "upload_vanilla" : [["Time","File Name","Time Taken (in microseconds)"]],
        "cache_requests": [["Time","File Name","Cache Hit","Time Taken (in microseconds)"]],
        "aws_region" : region,
        "buckets" : ["cachestore"+str(i) for i in range(20)],
        "bucket_space" : [0 for i in range(20)]
    }

    db_download = {
        "download_requests" : [["Time","File Name","Files Downloaded","Num Global Blocks","Num Local Parity","Time To Download (in microseconds)","Time To Decode (in microseconds)","Total Time Taken (in microseconds)"]],
        "download_vanilla" : [["Time","File Name","Time Taken (in microseconds)"]],
    }

    # Its important to use binary mode
    dbfile = open('pckl_upload', 'wb')
    pickle.dump(db_upload, dbfile)
    dbfile.close()

    dbfile = open('pckl_download', 'wb')
    pickle.dump(db_download, dbfile)
    dbfile.close()
