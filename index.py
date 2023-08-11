import ast
import asyncio
import os
import subprocess
import traceback
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from flask import Flask, jsonify, request

app = Flask(__name__)

GQL_URN = os.environ.get("GQL_URN", "localhost:3006/gql")
GQL_SSL = os.environ.get("GQL_SSL", 0)

async def execute_handler(code, args):
    python_handler_context = { 'args': args }
    generated_code = f"{code}\npython_handler_context['result'] = fn(python_handler_context['args'])"
    code_object = compile(generated_code, 'python_handler', 'exec')
    exec(code_object, dict(python_handler_context=python_handler_context))
    result = python_handler_context['result']
    return result

async def make_deep_client(token):
    if not token:
        raise ValueError("No token provided")
    url = bool(int(GQL_SSL)) if f"https://{GQL_URN}" else f"http://{GQL_URN}"
    transport = AIOHTTPTransport(url=url, headers={ 'Authorization': token })
    deep_client = Client(transport=transport, fetch_schema_from_transport=True)
    return deep_client

@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({})

@app.route('/init', methods=['POST'])
def init():
    return jsonify({})

@app.route('/call', methods=['POST'])
async def call():
    try:
        body = request.json
        params = body['params']
        args = {
            'deep':  await make_deep_client(params['jwt']),
            'data': params['data'],
            'gql': gql
        }
        result = await execute_handler(params['code'], args)
        return jsonify({ 'resolved': result })
    except Exception as e:
        return jsonify({ 'rejected': traceback.format_exc() })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=os.environ.get("PORT"), use_reloader=False, threaded=True)
