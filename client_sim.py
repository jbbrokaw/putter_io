from __future__ import unicode_literals
import requests
import pusherclient

pusher = pusherclient.Pusher('65be64bbb0dbf33a108e')


def callback(data):
    """Change the state of a controller based on the contents
    of data['messge']"""
    print "Received: ", data


def connect_handler(data):
    channel = pusher.subscribe("controller_channel")
    channel.bind('test_event', callback)  # and appropriate callback

if __name__ == '__main__':
    pusher.connection.bind('pusher:connection_established', connect_handler)
    pusher.connect()
    while True:
        time = raw_input("Enter an x value (0 to 400): ")
        value = raw_input("Enter a y value (0 to 400): ")
        payload = {'time': time, 'value': value}
        r = requests.put("http://ec2-54-148-190-8.us-west-2.compute.amazonaws.com/data", data=payload)
