To use this project first create a new virtual environment for python:
```bash
virtualenv -p /usr/bin/python2.7 <path/to/new/virtualenv/>
```
Then activate the new environment:
```bash
source bin/activate
```
Then install the required files:
```bash
pip tensorflow-gpu
pip gunicorn
pip flask
```
Next configure nginx to communicate to gunicorn via a unix socket:

```bash
server {
    listen 80;
    server_name hostname.of.server;
    root /path/to/static/content;

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://unix:/tmp/gunicorn.sock;
    }
}
```
Save this file as 'chatbot' in /etc/nginx/sites-available/chatbot

The server can now be started by running the following command:
```bash
./start_bot.sh
```
from the web directory.

This will only work if there is a trained model in the working_dir directory within chatbotcore. To get a pretrained model download this file: https://www.dropbox.com/s/uzgo2ms4an19fti/iteration7.tar.bz2 and extract it into the chatbotcore/working_dir folder. To train a new model see the readme under the chatbotcore directory.
