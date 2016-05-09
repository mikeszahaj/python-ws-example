# open browsers
import os
from threading import Thread, Lock
import redis
import time
import tornado.ioloop
import tornado.web
import tornado.websocket

r = redis.Redis()
openSockets = []

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("""
        <html>
            <head>
            </head>
            <body>
                <h3>Messages</h3>
                <button id="hi">hi</button>
                <table id="messages">
                </table>
                <script>
                    window.wsEstablished = false;
                    function establishConnection(){
                        if(window.wsEstablished) return false;
                        var ws = new WebSocket("ws://" + document.location.host + "/websocket");
                        window.table = document.getElementById('messages');
                        ws.onmessage = function (evt) {
                            console.log("received evt:", evt);
                            row = document.createElement('tr');
                            cell = document.createElement('td');
                            cell.innerHTML = evt.data ;
                            row.appendChild(cell);
                            window.table.appendChild(row);
                        };
                        ws.onopen = function(){
                            window.wsEstablished = true;
                            if(window.wsInterval != undefined || window.wsInterval != null){
                                clearInterval(window.wsInterval);
                                window.wsInterval = null;
                            }
                        }
                        ws.onclose = function(){
                            if(window.wsEstablished) window.wsInterval = setInterval(establishConnection, 5000);
                            window.wsEstablished = false;
                        };
                        window.ws = ws;
                    }
                    
                    establishConnection();
                    document.getElementById('hi').onclick = function(){
                        ws.send("hi");
                    }
                </script>
            </body>
        </html>
        """)

class StiWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        if self not in openSockets:
            openSockets.append(self)
        updateCount()

    def on_message(self, message):
        for openSocket in openSockets:
            openSocket.write_message(message)

    def on_close(self):
        if self in openSockets:
            openSockets.remove(self)
        updateCount()
        
def listen():
    while True:
        response = r.blpop('stipythonws', 5)
        if response is not None:
            sendMessage(response[1])

def write():
    while True:
        time.sleep(7)
        r.rpush('stipythonws', "Message from Redis")
            
def updateCount():
    msg = "Connected users: " + str(len(openSockets))
    print msg
    sendMessage(msg)

def sendMessage(msg):
    for openSocket in openSockets:
        openSocket.write_message( msg )


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/websocket", StiWebSocket)
    ])

if __name__ == "__main__":
    redis_thread = Thread(target=listen)
    redis_thread.start()
    
    other_redis_thread = Thread(target=write)
    other_redis_thread.start()
    
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
