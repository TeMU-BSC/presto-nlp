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

## Usage of Vicky

Go to `presto-nlp/vickyboy/` directory.

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

## Build rasa docker image

· To build rasa docker image use: 

```bash
docker build -t bsctemu/presto-vickybot:latest -t bsctemu/presto-vickybot:<YOUR_VERSION> .
```

· Then, push the image to docker hub:

```bash
docker push bsctemu/presto-vickybot --all-tags 
```

## Build custom actions docker image (action server)

If you made any changes to the custom actions, then build the image with:
``` bash
docker build -t bsctemu/presto-vickybot-actions-server:latest -t bsctemu/presto-vickybot-actions-server:<YOUR_VERSION> -f DockerfileActions .
docker push bsctemu/presto-vickybot-actions-server --all-tags 
```

## Deploy via docker compose (using Rasa X)

Download and run Rasa X install script
```bash
curl -sSL -o install.sh https://storage.googleapis.com/rasa-x-releases/1.1.4/install.sh
sudo bash ./install.sh
```

Clone this repo
```bash
git clone https://github.com/TeMU-BSC/presto-nlp
```

Copy docker-compose.override.yml to Rasa X folder
```bash
sudo cp presto-nlp/vickyboy/rasax/docker-compose.override.yml /etc/rasa/
```

Start Rasa X and create new user for Rasa X admin panel 
```bash
cd /etc/rasa
docker compose up -d
sudo python3 rasa_x_commands.py create --update admin admin <some password here>
```