import pickle
import boto3


access_key_id = 'AKIAXJULJPQNZCGYW7H7'
secret_access_key = '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'
 

def connection_S3(loc):
    s3 = boto3.client('s3',aws_access_key_id = access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=loc)
    return s3

if __name__ == '__main__':

    regions = ['ap-south-1',
    'ap-northeast-1',
    'ap-southeast-1',]
    
    # database
    db_upload = {
        "locations" : {
            "test" : "location_none"
        },
        "upload_requests" : [["Time","File Name","Time To Encode (in microseconds)",
        "Time To Upload (in microseconds)","Total Time Taken (in microseconds)"]],
        "upload_vanilla" : [["Time","File Name","Time Taken (in microseconds)"]],
        "cache_requests": [["Time","File Name","Cache Hit","Time Taken (in microseconds)"]],
        "aws_regions" : regions,
        "buckets" : [],
        "bucket_space" : [0 for i in range(len(regions)*10)],
        "bucket_score" : [0 for i in range(len(regions)*10)]
    }

    db_download = {
        "download_requests" : [["Time","File Name","Files Downloaded","Num Global Blocks","Num Local Parity","Time To Download (in microseconds)","Time To Decode (in microseconds)","Total Time Taken (in microseconds)","Size"]],
        "download_vanilla" : [["Time","File Name","Time Taken (in microseconds)"]],
    }

    s3_conns = [] 

    for loc in regions:
        s3_conns.append(connection_S3(loc))

    for i in range(len(regions)):
        for j in range(10):
            db_upload["buckets"].append(["cachestoregeo"+str(i*10+j),i])
            print("BUCKET - "+"cachestoregeo"+str(i*10+j))
            res = s3_conns[i].list_objects(Bucket = "cachestoregeo"+str(i*10+j))
            try:
                delete_items = []
                for x in res['Contents']:
                    # print(x['Key'])
                    delete_items.append({'Key':x['Key']})
                print(delete_items)
                s3_conns[i].delete_objects(Bucket="cachestoregeo"+str(i*10+j), Delete={'Objects':delete_items})
            except:
                pass
    

    # Its important to use binary mode
    dbfile = open('pckl_upload', 'wb')
    pickle.dump(db_upload, dbfile)
    dbfile.close()

    dbfile = open('pckl_download', 'wb')
    pickle.dump(db_download, dbfile)
    dbfile.close()
