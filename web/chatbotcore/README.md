Code was originally from here: https://github.com/suriyadeepan/easy_seq2seq

I have updated it to work with the new version of tensorflow 1.0 and made other minor changes to make it suit my project better.



See the data directory for how to obtain training data. After the training data have been obtained put the data in the web/chatbotcore/data folder. Then configure the seq2seq.ini file according as you see fit.

## Training

```bash
# edit seq2seq.ini file to set 
#		mode = train
python execute.py
```

## Testing

```bash
# edit seq2seq.ini file to set 
#		mode = test
python execute.py
```
