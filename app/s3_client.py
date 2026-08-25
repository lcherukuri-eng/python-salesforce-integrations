import os
import boto3
from dotenv import load_dotenv

load_dotenv()


def upload_file_to_s3(file_name):

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv(
            "AWS_ACCESS_KEY_ID"
        ),
        aws_secret_access_key=os.getenv(
            "AWS_SECRET_ACCESS_KEY"
        ),
        region_name=os.getenv(
            "AWS_REGION"
        )
    )

    bucket_name = os.getenv(
        "AWS_BUCKET_NAME"
    )

    s3.upload_file(
        file_name,
        bucket_name,
        file_name
    )

    return {
        "message": (
            f"{file_name} uploaded "
            "to S3 successfully"
        )
    }