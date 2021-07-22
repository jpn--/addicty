
import gzip
import io
import yaml
from .addict import Dict

try:
    import boto3
except ImportError:
    boto3 = None
    client = None
else:
    client = boto3.client('s3')


def to_s3(d, bucket, key, **kwargs):
    global client, boto3
    if boto3 is None:
        raise ModuleNotFoundError("boto3")
    assert isinstance(d, Dict)
    payload = io.BytesIO(gzip.compress(d.dump(**kwargs).encode()))
    payload.seek(0)
    client.upload_fileobj(payload, bucket, key)


def from_s3(cls, bucket, key, freeze=False, loader=yaml.SafeLoader):
    global client, boto3
    if boto3 is None:
        raise ModuleNotFoundError("boto3")
    with io.BytesIO() as data:
        client.download_fileobj(bucket, key, data)
        content = gzip.decompress(data.getvalue())
        result = cls(yaml.load(content, Loader=loader))
        if freeze:
            result.freeze(True)
        return result

