import boto3, uuid

from clnass505_drf.settings import (
    AWS_ACCESS_KEY_ID, 
    AWS_SECRET_ACCESS_KEY, 
    AWS_STORAGE_BUCKET_NAME 
)


class S3Client:
    def __init__(self, access_key, secret_key, AWS_STORAGE_BUCKET_NAME):
        boto3_s3 = boto3.client(
            's3',
            aws_access_key_id     = access_key,
            aws_secret_access_key = secret_key
        )
        self.s3_client   = boto3_s3
        self.bucket_name = AWS_STORAGE_BUCKET_NAME
    
    def upload(self, file, dir):
        try: 
            file_id    = str(uuid.uuid4())
            image_url  = f'{dir}/{file_id}'
            extra_args = {'ContentType' : file.content_type}

            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                image_url,
                ExtraArgs = extra_args
            )
            return f'https://{self.bucket_name}.s3.ap-northeast-2.amazonaws.com/{image_url}'
        except:
            return None

s3_client = S3Client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME)


class FileUpload:
    def __init__(self, client):
        self.client = client
    
    def upload(self, file, dir):
        return self.client.upload(file, dir)