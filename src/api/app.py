from flask import Flask, Response, request

import geo
import tools
import json

app = Flask(__name__, static_url_path='/static')

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response

app.after_request(add_cors_headers)

@app.route('/get_near_points', methods=['GET'])
def files():
    longitude = float(request.args.get('longitude'))
    latitude = float(request.args.get('latitude'))
    mode = request.args.get('mode')
    head = int(request.args.get('head'))
    near_points = geo.nearest_response(longitude, latitude, mode, head)
    response = tools.format_response(longitude, latitude, mode, head, near_points)
    text_response = json.dumps(response).replace('": NaN','": "NaN"')
    return Response(text_response, mimetype='application/json')


if __name__ == '__main__':
    app.after_request(add_cors_headers)
    app.run(threaded=True, host='0.0.0.0', debug=True)
