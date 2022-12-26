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
        topicArns,
    ) -> None:
        self.snsClient = boto3.client('sns')
        self.topicArns = topicArns

    @classmethod
    async def from_endpoint_config(cls, config) -> "SNSEventBroker":        
        """Creates broker. See the parent class for more information."""
        return cls(topicArns=config.url, **config.kwargs)

    def publish(self, event: Dict[Text, Any]) -> None:
        logger.info(event)
        stage = event.get('sender_id').split('@')[1]
        topicArn = self.topicArns.get(stage)
        if topicArn:
            self.snsClient.publish(
                TopicArn=topicArn,
                Message=json.dumps(event),
            )
