import asyncio
import os
import traceback
from dotenv import load_dotenv
from deepclient import DeepClientOptions, DeepClient
from flask import Flask, jsonify, request
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

app = Flask(__name__)
GQL_URN = os.environ.get("GQL_URN", "localhost:3006/gql")
print(f"Using GQL_URN: {GQL_URN}")
GQL_SSL = os.environ.get("GQL_SSL", 0)
print(f"Using GQL_SSL: {GQL_SSL}")
TEMPLATE_CODE = """
{{USER_CODE}}
python_handler_context['result'] = asyncio.run(fn(python_handler_context['args']))
"""

def make_deep_client(token):
    if not token:
        raise ValueError("No token provided")
    url = f"https://{GQL_URN}" if bool(int(GQL_SSL)) else f"http://{GQL_URN}"
    transport = AIOHTTPTransport(url=url, headers={'Authorization': f"Bearer {token}"})
    client = Client(transport=transport, fetch_schema_from_transport=True)
    options = DeepClientOptions(gql_client=client)
    deep_client = DeepClient(options)
    return deep_client

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
        full_code = TEMPLATE_CODE.replace("{{USER_CODE}}", params['code'])
        args = {
            'deep': make_deep_client(params['jwt']),
            'data': params['data'],
        }
        python_handler_context = {'args': args}
        code_object = compile(full_code, 'python_handler', 'exec')
        exec(code_object, globals(), dict(python_handler_context=python_handler_context))
        result = python_handler_context['result']
        print(f"Resolved: {result}")
        return jsonify({'resolved': result})
    except Exception as e:
        print(f"Rejected: {traceback.format_exc()}")
        return jsonify({'rejected': traceback.format_exc()})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=os.environ.get("PORT"), use_reloader=False, threaded=True)
