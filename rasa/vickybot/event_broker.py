import json
import logging
from typing import Any, Dict, Text

import boto3

from rasa.core.brokers.broker import EventBroker
from rasa.utils.endpoints import EndpointConfig

logger = logging.getLogger(__name__)


class SNSEventBroker(EventBroker):

    def __init__(
        self,
        topicArn,
    ) -> None:
        self.snsClient = boto3.client('sns')
        self.topicArn = topicArn

    @classmethod
    async def from_endpoint_config(cls, config) -> "SNSEventBroker":        
        """Creates broker. See the parent class for more information."""
        return cls(topicArn=config.url, **config.kwargs)

    def publish(self, event: Dict[Text, Any]) -> None:
        self.snsClient.publish(
            TopicArn=self.topicArn,
            Message=json.dumps(event),
        )
