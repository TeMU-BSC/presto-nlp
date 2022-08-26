# Presto - NLP

Presto NLP

## Installation

Clone this repository

```bash
git clone git@github.com:TeMU-BSC/presto-nlp.git
```

Create and activate a python 3.8 virtual environment

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the requirements

```bash
pip install -r requirements.txt
```

## Usage of Vicky

Go to `presto-nlp/rasa/flujo-ventilacion-emocional/` directory.

As we can read in [RASA docs](https://rasa.com/docs/rasa/2.x/command-line-interface):

· To init a new project (already initialized - we don't need it anymore), use [rasa init](https://rasa.com/docs/rasa/2.x/command-line-interface#rasa-init):

```bash
rasa init
```

· To train changes in the current model, use [rasa train](https://rasa.com/docs/rasa/2.x/command-line-interface#rasa-train) (This command might take some time):

```bash
rasa train
```

· To test and interact with the trained model, use [rasa shell](https://rasa.com/docs/rasa/2.x/command-line-interface#rasa-shell):

```bash
rasa shell
```

· To test and interact only with the NLU trained model, use [rasa shell nlu](https://rasa.com/docs/rasa/2.x/command-line-interface#rasa-shell):

```bash
rasa shell nlu
```