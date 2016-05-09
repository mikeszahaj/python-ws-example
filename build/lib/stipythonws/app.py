# open browsers
import os
os.system("open -a 'Google Chrome' http://localhost:8888")
os.system("open -a 'Firefox' http://localhost:8888")
os.system("open -a 'Safari' http://localhost:8888")

import tornado.ioloop
import tornado.web
import tornado.websocket

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("""
        <html>
            <head>
            </head>
            <body>
                <h3>Messages</h3>
                <button id="yo">Yo</button>
                <table id="messages">
                </table>
                <script>
                    var ws = new WebSocket("ws://localhost:8888/websocket");
                    //ws.send("Hello, world");
                    window.table = document.getElementById('messages');
                    ws.onmessage = function (evt) {
                        console.log("received evt:", evt);
                        row = document.createElement('tr');
                        cell = document.createElement('td');
                        cell.innerHTML = evt.data ;
                        row.appendChild(cell);
                        window.table.appendChild(row);
                    };
                    document.getElementById('yo').onclick = function(){
                        ws.send("yo");
                    }
                </script>
            </body>
        </html>
        """)

openSockets = []

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
    
def updateCount():
    msg = "Connected users: " + str(len(openSockets))
    print msg
    for openSocket in openSockets:
        openSocket.write_message( msg )



def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/websocket", StiWebSocket)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
