from chatbot import app, startBot, create_app
from multiprocessing import Process
from chatbotcore.execute import decode

if __name__ == "__main__":
    #startBot()
    #app.run(host='mcscholtz.ddns.net')
    app.run(host='0.0.0.0')
    #app = create_app()

