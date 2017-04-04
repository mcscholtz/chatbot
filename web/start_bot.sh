source bin/activate
gunicorn --workers=1 --timeout=300 --bind unix:/tmp/gunicorn.sock chatbot:app
sudo systemctl restart nginx
