from typing import Any, Text, Dict, List

from collections import Counter

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        prova = tracker.events
        for i, item in enumerate(prova):
            if item["event"] == "user":
                text = str(item["parse_data"]["intent"]["name"])
                dispatcher.utter_message(text)
            if item["event"] == "slot" and item["name"] == "sentiment":
                #  text = item["value"]
                text = str(item["value"])

                dispatcher.utter_message(text)
            if item["event"] == "bot":
                text = item.get("metadata", "no hi ha metadata").get("utter_action", "no hi ha action")

                dispatcher.utter_message(text)


def create_my_events_list(self, events):
    my_events_list = []
    for event in events:
        if event["event"] == "user":
            my_events_list.append(event["parse_data"]["intent"]["name"])

        elif event["event"] == "slot" and event["name"] == "sentiment":
            my_events_list.append(event["value"])
        elif event["event"] == "bot":
            try:
                action = event["metadata"]["utter_action"]
            except:
                action = "no_action"
            my_events_list.append(action)
    return my_events_list


def find_last_action(self, intents_list, emotions_list, my_events_list):
    for i, item in enumerate(my_events_list[:-2]):
        if item in intents_list and my_events_list[i + 1] in emotions_list:
            interaction = i
    try:
        last_action = my_events_list[interaction + 2]
    except:
        last_action = "not_found"
    return last_action


def find_main_distortion(self, my_events_list, distortions_list):
    distortions_track = [event for event in my_events_list if event in distortions_list]
    count_dict = dict(Counter(distortions_track).items())
    sorted_dict = dict(sorted(count_dict.items(), key=lambda x: x[1], reverse=True))
    c = sorted_dict[list(sorted_dict.keys())[0]]
    short_list = [item for item in sorted_dict.keys() if sorted_dict[item] == c]
    if len(short_list) == 1:
        main_distortion = short_list[0]
    else:
        for item in reversed(distortions_track):
            if item in short_list:
                main_distortion = item
                break
    return main_distortion


class NegativeEmotion(Action):
    def name(self) -> Text:
        return "action_negative_emotion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intents_list = ["nlu_fallback", "inform_sentiment"]
        emotions_list = ["NEG"]

        my_events_list = create_my_events_list(self, tracker.events)
        last_action = find_last_action(self, intents_list, emotions_list, my_events_list)

        if last_action == "utter_sentiment_NEG":
            new_action = "utter_ask_tell_more_NEG"
        elif last_action == "utter_ask_tell_more_NEG":
            new_action = "utter_selector_NEG_last"
        else:
            new_action = "utter_sentiment_NEG"

        dispatcher.utter_message(response=new_action)
        return []


class PositiveEmotion(Action):

    def name(self) -> Text:
        return "action_positive_emotion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intents_list = ["nlu_fallback", "inform_sentiment"]
        emotions_list = ["POS"]

        my_events_list = create_my_events_list(self, tracker.events)
        last_action = find_last_action(self, intents_list, emotions_list, my_events_list)

        if last_action == "utter_sentiment_POS":
            dispatcher.utter_message(response="utter_sentiment_POS2")
            new_action = "utter_ask_tell_more_POS"
        elif last_action == "utter_sentiment_POS2":
            new_action = "utter_selector_POS_last"
        else:
            new_action = "utter_sentiment_POS"

        dispatcher.utter_message(response=new_action)
        return []


class Distortion(Action):

    def name(self) -> Text:
        return "action_distortion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intents_list = ["sobregeneralizacion", "etiquetado", "deberias", "lectordementes", "pensamientoabsolutista",
                        "adivinacion", "catastrofismo"]
        emotions_list = ["POS", "NEG", "NEU"]

        my_events_list = create_my_events_list(self, tracker.events)
        last_action = find_last_action(self, intents_list, emotions_list, my_events_list)

        if last_action in ["utter_sentiment_NEG", "utter_sentiment_POS", "utter_sentiment_NEU"]:
            new_action = "utter_flecha_descendiente_1"
        elif last_action == "utter_flecha_descendiente_1":
            new_action = "utter_flecha_descendiente_2"
        elif last_action == "utter_flecha_descendiente_2":
            dispatcher.utter_message(response="utter_psico_edu_general")
            new_action = "utter_selector_psico_edu_general"
        else:
            emotion = my_events_list[-1]
            if emotion == "POS":
                new_action = "utter_sentiment_POS"
            elif emotion == "NEU":
                new_action = "utter_sentiment_NEU"
            else:
                new_action = "utter_sentiment_NEG"

        dispatcher.utter_message(response=new_action)
        return []


class PsicoEdu(Action):

    def name(self) -> Text:
        return "action_psico_edu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        my_events_list = create_my_events_list(self, tracker.events)
        distortions_list = ["sobregeneralizacion", "etiquetado", "deberias", "lectordementes", "pensamientoabsolutista",
                            "adivinacion", "catastrofismo"]

        distortions_dict = {"sobregeneralizacion": ["utter_psico_edu_sobre", "utter_selector_psico_edu_sobre"],
                            "etiquetado": ["utter_psico_edu_etiquetado", "utter_selector_psico_edu_etiquetado"],
                            "deberias": ["utter_psico_edu_deberias", "utter_selector_psico_edu_deberias"],
                            "lectordementes": ["utter_psico_edu_lectordementes",
                                               "utter_selector_psico_edu_lectordementes"],
                            "pensamientoabsolutista": ["utter_psico_edu_pensamientoabsolutista",
                                                       "utter_selector_psico_edu_pensamientoabsolutista"],
                            "adivinacion": ["utter_psico_edu_adivinacion", "utter_selector_psico_edu_adivinacion"],
                            "catastrofismo": ["utter_psico_edu_catastrofismo",
                                              "utter_selector_psico_edu_catastrofismo"]}
        main_distortion = find_main_distortion(self, my_events_list, list(distortions_dict.keys()))

        dispatcher.utter_message(response=distortions_dict[main_distortion][0])
        dispatcher.utter_message(response=distortions_dict[main_distortion][1])

        return []
