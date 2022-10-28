# Deployment of Vicky bot with RASA-X using docker compose

Tested on system:

OS:
Centos 7
Intance details:
t2.medium
SecurityGroup - Open ports:
ssh, http, https
Storage:
100gb

## FIRST INSTALL

Download and run the install script: 
```
  sudo yum install wget
  curl -sSL -o install.sh https://storage.googleapis.com/rasa-x-releases/1.0.1/install.sh
  sudo bash ./install.sh
```

Grant acess to github:
```
  ssh-keygen -t ed25519 -C "your_email@example.com"
  eval "$(ssh-agent -s)"
  ssh-add ~/.ssh/id_ed25519
  cat ~/.ssh/id_ed25519.pub

```
Open github and create a new deploy key on the repo using the result of the previous command


Clone the repo and start docker:
```
  sudo yum install git
  git clone -b rasa-x-model --single-branch git@github.com:TeMU-BSC/presto-nlp.git
  cp presto-nlp/docker-compose.override.yml /etc/rasa/docker-compose.override.yml

  sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
  cd /etc/rasa
  sudo docker-compose up -d
  sudo python3 rasa_x_commands.py create --update admin admin <some password here>
```

## UPDATING

Pull the latest repo:
```
  sudo docker-compose down
  cd presto-nlp
  git pull
  cd ../
  sudo docker-compose up -d --build
```
