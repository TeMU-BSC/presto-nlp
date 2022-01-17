from rasa.nlu.components import Component
from rasa.nlu import utils
from rasa.nlu.model import Metadata
from pysentimiento import SentimentAnalyzer
import os


class SentimentEntityExtractor(Component):
    """A pre-trained sentiment component"""

    name = "sentiment"
    provides = ["entities"]
    requires = []
    defaults = {}
    language_list = ["es"]
    analyzer = SentimentAnalyzer(lang="es")

    def __init__(self, component_config=None):
        super(SentimentEntityExtractor, self).__init__(component_config)

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
        print(message.data)
        result = self.analyzer.predict(message.data['text'])

        label = result.output
        score = round(result.probas[label], 2)

        entity = self.convert_to_rasa(label, score)

        message.set("entities", [entity], add_to_output=True)
