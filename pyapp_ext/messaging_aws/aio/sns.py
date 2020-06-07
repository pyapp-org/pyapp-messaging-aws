import logging
from typing import Dict, Any

import botocore.exceptions
from pyapp_ext.aiobotocore import aio_create_client
from pyapp_ext.messaging.aio import MessageSender
from pyapp_ext.messaging.exceptions import QueueNotFound
from .utils import build_attributes


LOGGER = logging.getLogger(__file__)


class SNSBase:
    """
    Base Pub/Sub Queue
    """

    __slots__ = ("topic_arn", "aws_config", "client_args", "_client")

    def __init__(
        self, topic_arn: str, aws_config: str = None, client_args: Dict[str, Any] = None
    ):
        self.topic_arn = topic_arn
        self.aws_config = aws_config
        self.client_args = client_args or {}

        self._client = None

    async def open(self):
        """
        Open queue
        """
        client = await aio_create_client("sns", self.aws_config, **self.client_args)

        self._client = client

    async def close(self):
        """
        Close Queue
        """
        if self._client:
            await self._client.close()
            self._client = None


class SNSSender(SNSBase, MessageSender):
    """
    AIO SNS message publisher.
    """

    __slots__ = ()

    async def send_raw(
        self, body: bytes, *, content_type: str = None, content_encoding: str = None
    ) -> str:
        attributes = build_attributes(
            ContentType=content_type, ContentEncoding=content_type
        )
        response = self._client.publish(
            TopicArn=self.topic_arn, Message=body, MessageAttributes=attributes
        )
        return response["MessageId"]
