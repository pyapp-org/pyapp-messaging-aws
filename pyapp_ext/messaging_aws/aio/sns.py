"""
AWS SNS Interfaces
~~~~~~~~~~~~~~~~~~

"""
import logging
from typing import Dict, Any, AsyncGenerator

import botocore.exceptions
from pyapp_ext.aiobotocore import aio_create_client, create_client
from pyapp_ext.messaging.aio import MessageSender, MessageReceiver, Message
from pyapp_ext.messaging.exceptions import ClientError

from .sqs import SQSReceiver
from .utils import build_attributes, parse_attributes

LOGGER = logging.getLogger(__name__)


class SNSSender(MessageSender):
    """
    AIO SNS message publisher.
    """

    __slots__ = ("topic_name", "aws_config", "client_args", "_client", "_topic_arn")

    def __init__(
        self, topic_name: str, aws_config: str = None, client_args: Dict[str, Any] = None
    ):
        self.topic_name = topic_name
        self.aws_config = aws_config
        self.client_args = client_args or {}

        self._client = None
        self._topic_arn = None

    def __repr__(self):
        return f"{type(self).__name__}(topic_name={self.topic_name!r})"

    async def open(self):
        """
        Open queue
        """
        client = await aio_create_client("sns", self.aws_config, **self.client_args)

        if self.topic_name.startswith("arn:"):
            self._topic_arn = self.topic_name

        else:
            # Use create topic to get the Topic ARN
            try:
                response = await client.create_topic(Name=self.topic_name)

            except botocore.exceptions.ClientError as ex:
                await client.close()
                error_code = ex.response["Error"]["Code"]
                raise ClientError(error_code) from ex

            except Exception:
                await client.close()
                raise

            self._topic_arn = response["TopicArn"]

        self._client = client

    async def close(self):
        """
        Close Queue
        """
        if self._client:
            await self._client.close()
            self._client = None

        self._topic_arn = None

    async def send_raw(
        self, body: bytes, *, content_type: str = None, content_encoding: str = None
    ) -> str:
        attributes = build_attributes(
            ContentType=content_type, ContentEncoding=content_type
        )
        response = await self._client.publish(
            TopicArn=self._topic_arn, Message=body, MessageAttributes=attributes
        )
        return response["MessageId"]


class SNSReceiver(SQSReceiver, MessageReceiver):
    """
    AIO SQS message receiver, subscribed to SNS topic.
    """

    __slots__ = ("topic_name",)

    def __init__(self, *, topic_name: str, queue_name: str = None, **kwargs):
        self.topic_name = topic_name

        super().__init__(queue_name=queue_name or topic_name, **kwargs)

    def __repr__(self):
        return f"{type(self).__name__}(topic_name={self.topic_name!r}, queue_name={self.queue_name!r})"

    async def _get_topic_arn(self, client):
        if self.topic_name.startswith("arn:"):
            return self.topic_name
        else:
            response = await client.create_topic(Name=self.topic_name)
            return response["TopicArn"]

    async def receive_raw(self) -> AsyncGenerator[Message, None]:
        async for message in super().receive_raw():
            # Unwrap envelope
            envelope = message.content
            try:
                attrs = parse_attributes(
                    envelope.pop("MessageAttributes")
                )
            except KeyError:
                attrs = {}

            yield Message(
                envelope.pop("Message"),
                attrs.get("ContentType"),
                attrs.get("ContentEncoding"),
                message,
                self
            )

    async def delete(self, message: Message):
        await super().delete(message.raw)

    async def configure(self):
        """
        Define any send queue and subscribe to SNS topic
        """
        async with create_client("sns", self.aws_config, **self.client_args) as sns_client:
            async with create_client("sqs", self.aws_config, **self.client_args) as sqs_client:
                topic_arn = await self._get_topic_arn(sns_client)
                LOGGER.info("Topic ARN queue %s", topic_arn)

                # Create the queue
                response = await sqs_client.create_queue(QueueName=self.queue_name)
                queue_url = response["QueueUrl"]
                LOGGER.info("Created queue %s", queue_url)

                # Get queue Arn
                response = await sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["QueueArn"])
                queue_arn = response["Attributes"]["QueueArn"]
                LOGGER.info("Queue ARN %s", queue_arn)

                # Subscribe
                response = await sns_client.subscribe(TopicArn=topic_arn, Endpoint=queue_arn, Protocol="sqs")
                subscription_arn = response["SubscriptionArn"]
                LOGGER.info("Subscription ARN %s", subscription_arn)

                return subscription_arn
