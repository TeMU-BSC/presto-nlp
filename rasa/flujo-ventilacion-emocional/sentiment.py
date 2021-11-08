from rasa.nlu.components import Component
from rasa.nlu import utils
from rasa.nlu.model import Metadata
from rasa.nlu.classifiers.classifier import IntentClassifier
from pysentimiento import SentimentAnalyzer
import os


class IntentSentimentAnalyzer(IntentClassifier):
    """A pre-trained sentiment component"""

    name = "sentiment"
    provides = ["intent"]
    requires = []
    defaults = {}
    language_list = ["es"]
    analyzer = SentimentAnalyzer(lang="es")

    def __init__(self, component_config=None):
        super(IntentSentimentAnalyzer, self).__init__(component_config)

    def train(self, training_data, cfg, **kwargs):
        """Not needed, because the the model is pretrained"""
        pass

    def convert_to_rasa(self, label, score):
        """Convert model output into the Rasa NLU compatible output format."""

        intent = {"name": label,
                  "confidence": score}

        return intent

    def process(self, message, **kwargs):
        """Retrieve the text message, pass it to the classifier
            and append the prediction results to the message class."""

        result = self.analyzer.predict(message.data['text'])

        label = result.output
        score = round(result.probas[label], 2)

        intent = self.convert_to_rasa(label, score)

        message.set("intent", intent, add_to_output=True)

    def persist(self, *args):
        """Pass because a pre-trained model is already persisted"""
        pass
