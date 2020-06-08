# Credentials for localstack
AWS_CREDENTIALS = {
    "default": {
        "region": "ap-southeast-2",
        "aws_access_key_id": "123",
        "aws_secret_access_key": "123",
        # "aws_session_token": None,
    }
}


SEND_MESSAGE_QUEUES = {
    "sqs": (
        "pyapp_ext.messaging_aws.aio.SQSSender",
        {
            "queue_name": "queue1",
            "client_args": {"endpoint_url": "http://localhost:4566/"},
        },
    ),
    "sns": (
        "pyapp_ext.messaging_aws.aio.SNSSender",
        {
            "topic_name": "topic1",
            "client_args": {"endpoint_url": "http://localhost:4566"},
        },
    ),
}

RECEIVE_MESSAGE_QUEUES = {
    "sqs": (
        "pyapp_ext.messaging_aws.aio.SQSReceiver",
        {
            "queue_name": "queue1",
            "client_args": {"endpoint_url": "http://localhost:4566/"},
        },
    ),
    "sns": (
        "pyapp_ext.messaging_aws.aio.SNSReceiver",
        {
            "topic_name": "topic1",
            "client_args": {"endpoint_url": "http://localhost:4566/"},
        },
    ),
}
