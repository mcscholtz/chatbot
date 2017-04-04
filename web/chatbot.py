import os, re
from multiprocessing import Process, Queue
from chatbotcore.execute import decode
from flask import Flask, request, render_template, jsonify

session_count = 0
bot_status = 0
query_q = Queue()
resp_q = Queue()
ctl_q = Queue()

def startBot():
    global bot_status
    print 'Starting bot'
    proc = Process(target=decode, args=(query_q, resp_q, ctl_q,))
    proc.start()
    #Wait till the bot is ready
    while ctl_q.get() != "READY":
        pass
    ctl_q.put('START')
    print 'Bot is ready to communicate...'
    bot_status = 1

def create_app():
    startBot()
    app = Flask(__name__)
    print "Flask application started..."
    return app

app = create_app()

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    if bot_status ==0:
        print "Bot has not started"
    if request.method == 'POST':
        if request.form['msg'] != '':
            #print 'session: '+ str(request.form['sess'])
            #print request.form['msg']
            query_q.put(request.form['msg'])
            msg = resp_q.get()
            #print msg
            if re.search('_UNK', msg):
                msg = '...does not compute'
        else:
            return jsonify({'failure':'Empty Message'}), 400, {'ContentType':'application/json'}
    return jsonify({"msg": msg}), 200, {'ContentType':'application/json'}

@app.route('/start-session', methods=['POST'])
def session():
    global session_count
    sess = session_count
    session_count += 1
    #print 'Issued session id:'+str(sess)
    return jsonify({"sess": sess}), 201, {'ContentType':'application/json'}

@app.route('/save', methods=['POST'])
def save():
    if request.method == 'POST':
        folder = os.path.join('chatbotcore', 'feedback')
        if request.form['query'] != '':
            if request.form['status'] == 'rejected':
                with open(os.path.join(folder, 'rejected'), "ab") as rejected:
                    rejected.write(request.form['query'].strip() + '\t\t' + request.form['response'].strip()+'\n')
            elif request.form['status'] == 'approved':
                with open(os.path.join(folder, 'approved'), "ab") as rejected:
                    rejected.write(request.form['query'].strip() + '\t\t' + request.form['response'].strip()+'\n')
            elif request.form['status'] == 'suggestion':
                with open(os.path.join(folder, 'suggestion'), "ab") as rejected:
                    rejected.write(request.form['query'].strip() + '\t\t' + request.form['response'].strip()+'\n')
            else:
                return jsonify({'failure':'Incorrect status type'}), 400, {'ContentType':'application/json'} 
        else:
            return jsonify({'failure':'Empty Query'}), 400, {'ContentType':'application/json'}
    return jsonify({'success':True}), 200, {'ContentType':'application/json'}


#if __name__ == "__main__":
#    startBot()
#    app.run(host='0.0.0.0')

