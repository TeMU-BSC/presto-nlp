import os
from rasa.engine.graph import GraphComponent  # new in rasa 3.0
from rasa.nlu.extractors.extractor import EntityExtractorMixin
# from rasa.nlu.components import Component
from rasa.nlu import utils
from rasa.engine.storage.resource import Resource  # new in rasa 3.0
from rasa.engine.storage.storage import ModelStorage  # new in rasa 3.0
from rasa.engine.recipes.default_recipe import DefaultV1Recipe  # new in rasa 3.0
# from rasa.nlu.model import Metadata  #not support in rasa 3.0
# from pysentimiento import SentimentAnalyzer  # doesn't seem to work. we try with the component above
from pysentimiento import create_analyzer


@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR], is_trainable=False
    )
class SentimentEntityExtractor(GraphComponent, EntityExtractorMixin):
    """A pre-trained sentiment component"""

    name = "sentiment"
    provides = ["entities"]
    requires = []
    defaults = {}
    language_list = ["es"]
    analyzer = create_analyzer(task="sentiment", lang="es")

    def __init__(self, GraphComponent_config=None):
        super(SentimentEntityExtractor, self).__init__(GraphComponent_config)

    def convert_to_rasa(self, label, score):
        """Convert model output into the Rasa NLU compatible output format."""

        entity = {"value": label,
                  "confidence": score,
                  "entity": "sentiment",
                  "extractor": "sentiment_extractor"}

        return entity

    def process(self, message, **kwargs) -> None:
        """Retrieve the text message, pass it to the classifier
            and append the prediction results to the message class."""
        
        # Skip the training to fix error when executing `rasa train` command
        # TODO: find an alternative to check for the 'text' key and skip training
        try: 
            result = self.analyzer.predict(message.data['text'])  

            label = result.output
            score = round(result.probas[label], 2)

            entity = self.convert_to_rasa(label, score)

            message.set("entities", [entity], add_to_output=True)
        except KeyError:
            entity = None
