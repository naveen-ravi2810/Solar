import boto3
from core.settings import get_settings


class AWSClient:
    def __init__(self, service):
        self.service = service

    def get_client(self):
        return boto3.client(
            self.service,
            aws_access_key_id=get_settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=get_settings.AWS_SECRET_ACCESS_KEY,
        )
