from rasa.nlu.components import Component
from rasa.nlu import utils
from rasa.nlu.model import Metadata
from pysentimiento import SentimentAnalyzer, analyzer
import os


class SentimentAnalyzer(Component):
    """A pre-trained sentiment component"""

    name = "sentiment"
    provides = ["entities"]
    requires = []
    defaults = {}
    language_list = ["es"]
    analyzer = SentimentAnalyzer(lang="es")

    def __init__(self, component_config=None):
        super(SentimentAnalyzer, self).__init__(component_config)

    def train(self, training_data, cfg, **kwargs):
        """Not needed, because the the model is pretrained"""
        pass

    def convert_to_rasa(self, label, score):
        """Convert model output into the Rasa NLU compatible output format."""

        entity = {"value": label,
                  "confidence": score,
                  "entity": "sentiment",
                  "extractor": "sentiment_extractor"}

        return entity

    def process(self, message, **kwargs):
        """Retrieve the text message, pass it to the classifier
            and append the prediction results to the message class."""

        result = self.analyzer.predict(message)
        label = result.output
        score = result.probas[label]

        entity = self.convert_to_rasa(label, score)

        message.set("entities", [entity], add_to_output=True)

    def persist(self, *args):
        """Pass because a pre-trained model is already persisted"""
        pass
