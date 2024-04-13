import os

import boto3


class S3:
    def __init__(self):
        self._bucket = os.environ["AWS_S3_BUCKET"]

        self._client = None

    @property
    def client(self):
        if not self._client:
            self._client = boto3.client(
                "s3",
                aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
            )

        return self._client

    def generate_presigned_url(self, key):
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self._bucket, "Key": key}, ExpiresIn=3600
        )
