Following the instructions here:

Download and run the install script: 
```
  curl -sSL -o install.sh https://storage.googleapis.com/rasa-x-releases/1.0.1/install.sh
  sudo bash ./install.sh
```

Copy the following files to `/etc/rasa/`:
```
  sentiment.py
  requirements.txt
  CustomDockerfile
  docker-compose.override.yml
```

run the following commands (replace <some password here> with an acutal password):
```
  cd /etc/rasa
  sudo docker build -f CustomDockerfile . -t presto-nlp/rasa:2.8.15
  sudo docker-compose up -d
  sudo python3 rasa_x_commands.py create --update admin admin <some password here>
```