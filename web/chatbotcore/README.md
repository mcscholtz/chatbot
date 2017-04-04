Code was originally from here: https://github.com/suriyadeepan/easy_seq2seq

I have updated it to work with the new version of tensorflow 1.0 and made other minor changes to make it suit my project better.



See the data directory for how to obtain training data. After the training data have been obtained put the data in the web/chatbotcore/data folder. Then configure the seq2seq.ini file according as you see fit.

## Training

Edit seq2seq.ini file. Set mode = train
```bash
python execute.py
```

## Testing

Edit seq2seq.ini file. Set mode = test
```bash
python execute.py
```
