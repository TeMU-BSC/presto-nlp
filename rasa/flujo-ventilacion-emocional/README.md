## Installation

Clone this repository

```bash
git clone git@github.com:TeMU-BSC/presto-nlp.git
```

Create and activate a python 3.8 virtual environment

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the requirements in python3.8

```bash
pip install -r requirements.txt
```


Optionally, to interact with the bot through web interface, install RASA-X locally with the following commands:

```
sudo apt-get install pkg-config libxml2-dev libxmlsec1 libxmlsec1-dev libxmlsec1-openssl
pip install rasa-x --extra-index-url https://pypi.rasa.com/simple
```


## Usage of Vicky

Go to `presto-nlp/rasa/flujo-ventilacion-emocional/` directory.

As we can read in [RASA docs](https://rasa.com/docs/rasa/2.x/command-line-interface):

· To train the current model, use [rasa train](https://rasa.com/docs/rasa/2.x/command-line-interface#rasa-train) (This command might take some time):

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

· To with the bot through RASA-X, use [rasa x](https://legacy-docs-rasa-x.rasa.com/docs/rasa-x/0.42.x/installation-and-setup/install/local-mode/):

```bash
rasa x
```