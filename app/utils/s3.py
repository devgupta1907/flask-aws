import boto3
from flask import current_app
import uuid

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['S3_REGION']
    )


def upload_resume_to_s3(file, email):
    s3_client = get_s3_client()
    filename = f"resumes/{email}_resume.pdf"
    
    s3_client.upload_fileobj(file, 
                            current_app.config['AWS_S3_BUCKET_NAME'], 
                            filename,
                            ExtraArgs={
                                'ContentType': 'application/pdf'
                            })
        

    return filename


def generate_resume_url(s3_key):
    s3 = get_s3_client()

    url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': current_app.config['S3_BUCKET'],
            'Key'   : s3_key
        },
        ExpiresIn=3600
    )

    return url

def delete_resume_from_s3(s3_key):
    s3 = get_s3_client()
    s3.delete_object(
        Bucket=current_app.config['S3_BUCKET'],
        Key=s3_key
    )