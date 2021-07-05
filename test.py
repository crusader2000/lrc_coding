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
    'ap-northeast-2',
    'ap-northeast-1',
    'ap-southeast-1',]
    s3_conns = [] 

    for loc in regions:
        print("SETTING UP CONNS")
        s3_conns.append(connection_S3(loc))
    

    for i in range(len(regions)):
    # for i in range(1,2):
        for j in range(10):
            print("cachestoregeo"+str(i*10+j))
            try:
                s3_conns[i].delete_bucket(Bucket="cachestoregeo"+str(i*10+j))
            except:
                continue

