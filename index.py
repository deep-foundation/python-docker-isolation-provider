import json
from functools import lru_cache
from deep_foundation.hasura.client import generate_apollo_client
from deep_foundation.deeplinks.client import DeepClient, parse_jwt
from flask import Flask, jsonify, request

GQL_URN = os.environ.get("GQL_URN", "localhost:3006/gql")
GQL_SSL = os.environ.get("GQL_SSL", 0)

def to_json(data):
    return json.dumps(data, default=lambda x: x.__dict__, indent=2)

@lru_cache()
def make_function(code):
    fn = eval(code)
    if not callable(fn):
        raise ValueError("Executed handler's code didn't return a function.")
    return fn

def make_deep_client(token):
    if not token:
        raise ValueError("No token provided")
    decoded = parse_jwt(token)
    link_id = decoded.user_id
    apollo_client = generate_apollo_client(
        path=GQL_URN, ssl=bool(int(GQL_SSL)), token=token
    )
    deep_client = DeepClient(apollo_client=apollo_client, link_id=link_id, token=token)
    return deep_client

app = Flask(__name__)

@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({})

@app.route('/init', methods=['POST'])
def init():
    return jsonify({})

@app.route('/call', methods=['POST'])
def call():
    try:
        body = request.json
        params = body['params']
        jwt = params['jwt']
        code = params['code']
        data = params['data']
        fn = makeFunction(code)
        deep = makeDeepClient(jwt)
        result = await fn({ data, deep, gql, require })
        return jsonify({ resolved: result })
    except rejected:
        processedRejection = JSON.parse(toJSON(rejected))
        return jsonify({ rejected: processedRejection })

@app.route('/http-call', methods=['POST'])
def http_call():
    try:
        options = request.headers['deep-call-options']
        jwt = options['jwt']
        code = options['code']
        data = options['data']
        fn = makeFunction(code)
        deep = makeDeepClient(jwt)
        await fn(request, response, next, { data, deep, gql, require })
    except rejected:
        processedRejection = JSON.parse(toJSON(rejected))
        return jsonify({ rejected: processedRejection })

if __name__ == "__main__":
    app.run(port=process.env.PORT)
    print(f"Listening on port {process.env.PORT}")
