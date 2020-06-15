from unittest import mock

import pytest

from pyapp_ext.messaging.exceptions import ClientError
from pyapp_ext.messaging_aws.aio import sns


class TestSNSSender:
    @pytest.mark.asyncio
    async def test_open(self, monkeypatch):
        mock_client = mock.AsyncMock(
            create_topic=mock.AsyncMock(return_value={"TopicArn": "arn:sns:...:my_topic"})
        )
        mock_factory = mock.AsyncMock(return_value=mock_client)
        monkeypatch.setattr(sns, "aio_create_client", mock_factory)

        target = sns.SNSSender(topic_name="my_topic", aws_config="my_config")

        await target.open()

        mock_factory.assert_awaited_with("sns", "my_config")
        mock_client.create_topic.assert_awaited_with(Name="my_topic")
        mock_client.close.assert_not_called()
        assert target._client is mock_client
        assert target._topic_arn == "arn:sns:...:my_topic"

    @pytest.mark.asyncio
    async def test_open__with_arn(self, monkeypatch):
        mock_client = mock.AsyncMock()
        mock_factory = mock.AsyncMock(return_value=mock_client)
        monkeypatch.setattr(sns, "aio_create_client", mock_factory)

        target = sns.SNSSender(topic_name="arn:sns:...:my_topic", aws_config="my_config")

        await target.open()

        mock_factory.assert_awaited_with("sns", "my_config")
        mock_client.create_topic.assert_not_called()
        mock_client.close.assert_not_called()
        assert target._client is mock_client
        assert target._topic_arn == "arn:sns:...:my_topic"

    @pytest.mark.asyncio
    async def test_open__client_error(self, monkeypatch):
        mock_client = mock.AsyncMock(
            create_topic=mock.AsyncMock(
                side_effect=ClientError({
                    "Error": {"Code": "AWS.SimpleQueueService.QueueDeletedRecently"}
                }, "getQueueUrl")
            ),
        )
        mock_factory = mock.AsyncMock(return_value=mock_client)
        monkeypatch.setattr(sns, "aio_create_client", mock_factory)

        target = sns.SNSSender(topic_name="my_topic", aws_config="my_config")

        with pytest.raises(ClientError):
            await target.open()

        mock_factory.assert_awaited_with("sns", "my_config")
        mock_client.create_topic.assert_awaited_with(Name="my_topic")
        mock_client.close.assert_called()
