from flask import Flask, request
from flask.ext import restful
from flask.ext.restful import reqparse, abort
import io
import os
import pusher


app = Flask(__name__)
api = restful.Api(app)

data = [
    {'id': 0, 'time': 0, 'value': 1}]

controller_state = {'id': 0,
                    'power': 'ON', }

p = pusher.Pusher(
    app_id='97440',
    key='65be64bbb0dbf33a108e',
    secret=os.environ['PUSHER_KEY']
)


def abort_if_record_doesnt_exist(record_id):
    if (record_id < 0) or (record_id >= len(data)):
        abort(404, message="Record {} doesn't exist".format(record_id))

parser = reqparse.RequestParser()
parser.add_argument('time', type=int, help='Time data recorded')
parser.add_argument('value', type=int, help='A recorded data point')

controller_parser = reqparse.RequestParser()
controller_parser.add_argument('power', type=str, help='power ON or OFF')


@app.route('/')
def main_page():
    with io.open('testpage.html', 'rb') as template:
        return template.read()


class Data(restful.Resource):
    def get(self):
        return data

    def put(self):
        args = parser.parse_args()
        record_id = len(data)
        data.append({'id': record_id,
                     'time': args['time'],
                     'value': args['value']})
        # p['test_channel'].trigger('my_event', {'message': 'refresh'})
        return data[record_id], 201


class Record(restful.Resource):
    def get(self, record_id):
        abort_if_record_doesnt_exist(record_id)
        return data[record_id]

    def put(self, record_id):
        abort_if_record_doesnt_exist(record_id)
        print "Updating", record_id
        print "As", request.json
        args = parser.parse_args()
        data[record_id] = {'id': record_id,
                           'time': args['time'],
                           'value': args['value']}
        return data[record_id], 201

    def delete(self, record_id):
        abort_if_record_doesnt_exist(record_id)
        data[record_id] = {}
        return '', 204


class Controller(restful.Resource):
    def get(self):
        return controller_state

    def put(self):
        print "Updating the controller"
        print "As", request.json
        args = controller_parser.parse_args()
        controller_state['power'] = args['power']
        p['controller_channel'].trigger('test_event',
                                        {'message': 'turn %s' %
                                                    controller_state})
        return controller_state

api.add_resource(Data, '/data')
api.add_resource(Record, '/data/<int:record_id>')
api.add_resource(Controller, '/controller')

if __name__ == '__main__':
    app.run(debug=True)
