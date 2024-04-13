import os

import boto3


class S3:
    def __init__(self):
        self._bucket = os.environ["AWS_S3_BUCKET"]
        self._client = None

    @property
    def client(self):
        if not self._client:
            self._client = boto3.client("s3")

        return self._client

    def generate_presigned_url(self, key):
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self.client(), "Key": key}, ExpiresIn=3600
        )
