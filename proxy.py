# set async_mode to 'threading', 'eventlet', 'gevent' or 'gevent_uwsgi' to
# force a mode else, the best mode is selected automatically from what's
# installed

async_mode = 'threading'

from flask import Flask, render_template
from socketio import server, client, WSGIApp

sio = server.Server(async_mode=async_mode)
app = Flask(__name__)
app.wsgi_app = WSGIApp(sio, app.wsgi_app)


# @app.route('/')
# def index():
#     return render_template('latency.html')


@sio.event
def cmd_from_client(sid, data):
    print('Received data: {}'.format(data))
    cli = client.Client()

    def send_cmd():
        cli.emit('execute_cmd', data)

    @cli.event
    def connect():
        print('connected to device')
        send_cmd()

    @cli.event()
    def output_from_device(message):
        print('message from device: {}'.format(message))
        sio.emit('cmd_from_server', message)

    cli.connect('http://192.168.29.17:9000')
    # cli.connect('http://0.0.0.0:9000')
    cli.wait()

if __name__ == '__main__':
    if sio.async_mode == 'threading':
        # deploy with Werkzeug
        app.run(threaded=True, host='0.0.0.0', port=8000)
    elif sio.async_mode == 'eventlet':
        # deploy with eventlet
        import eventlet
        import eventlet.wsgi
        eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
    elif sio.async_mode == 'gevent':
        # deploy with gevent
        from gevent import pywsgi
        try:
            from geventwebsocket.handler import WebSocketHandler
            websocket = True
        except ImportError:
            websocket = False
        if websocket:
            pywsgi.WSGIServer(('', 5000), app,
                              handler_class=WebSocketHandler).serve_forever()
        else:
            pywsgi.WSGIServer(('', 5000), app).serve_forever()
    elif sio.async_mode == 'gevent_uwsgi':
        print('Start the application through the uwsgi server. Example:')
        print('uwsgi --http :5000 --gevent 1000 --http-websockets --master '
              '--wsgi-file latency.py --callable app')
    else:
        print('Unknown async_mode: ' + sio.async_mode)
