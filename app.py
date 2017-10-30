from flask import Flask, request
import flask
import json
from flask_sse import sse


app = Flask(__name__)


@app.route('/subscribe')
def subscribe():
    new_user = sse.add_subscriber('default')
    print(f"Subscribers: {[sse.channels[channel].subscribers for channel in sse.get_channel()]}")
    return flask.Response(sse.stream(new_user), content_type='text/event-stream')


@app.route('/publish', methods=['GET', 'POST'])
def publish():
    channel = sse.get_channel('default')
    data = json.loads(request.data)
    print('User data', data)
    print('Subscribed users: ', channel.subscribers)
    if not data or not data.get('message') or not data.get('message').strip(' '):
        channel.publish("hello")
    else:
        channel.publish(data['message'])
    return "OK"

@app.route('/index')
def index():
    data = """
    <html>
        <body>
        <div>
            <h1> Messages From Others</h1>
            <div id='reply'> </div>
            <span>
                <h1> My message </h1>
                <input type='text' name='text' id='mymessage'>
                <button type='submit' id='send'>Send</button>
            </span>
        </div>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
        <script>
            $(document).ready(function(){
                var source = new EventSource("/subscribe");
                source.addEventListener('default',
                function(notification){
                    var content = $('#reply').html();
                    content += '<h3>' + JSON.parse(notification.data) + '</h3>';
                    $('#reply').html(content);
                });

                $('#send').click(
                    function(){
                        data = {}
                        input = $('#mymessage').val()
                        data['message'] = input
                        console.log(input);
                        var http = new XMLHttpRequest();
                        http.open("POST", "/publish", true);
                        http.send(JSON.stringify(data));
                    }
                );
            });
        </script>
        </body>
    </html>
    """

    return data
