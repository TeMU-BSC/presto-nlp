import pytest
import pathlib

from rasa.shared.nlu.training_data.message import Message
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.local_model_storage import LocalModelStorage
from rasa.engine.graph import ExecutionContext

from sentiment import SentimentEntityExtractor


@pytest.fixture
def entity_extractor(tmpdir):
    """Generate a sentiment extractor with a tmpdir as the model storage."""
    node_storage = LocalModelStorage(pathlib.Path(tmpdir))
    node_resource = Resource("sparse_feat")
    context = ExecutionContext(node_storage, node_resource)
    return SentimentEntityExtractor(
        config=SentimentEntityExtractor.get_default_config(),
        name=context.node_name,
        resource=node_resource,
        model_storage=node_storage,
    )


@pytest.mark.parametrize(
    "text, expected",
    [("hoy me encuentro mal", ["NEG"]),
     ("hoy me siento en bien", ["POS"]),
     ("mañana iré a hacer la compra", ["NEU"])],
)
def test_sparse_feats_added(entity_extractor, text, expected):
    """Checks if the sizes are appropriate."""
    # Create a message
    msg = Message({"text": text})

    # Process will process a list of Messages
    entity_extractor.process([msg])
    # Check that the message has been processed correctly
    entities = msg.get("entities")
    assert [e["value"] for e in entities] == expected
