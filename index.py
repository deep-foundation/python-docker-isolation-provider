import ast
import asyncio
import os
import subprocess
import traceback
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from flask import Flask, jsonify, request

app = Flask(__name__)

GQL_URN = os.environ.get("GQL_URN", "3006-deepfoundation-dev-adxmoff7bpv.ws-eu103.gitpod.io/gql")
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
    body = request.json
    params = body['params']
    data = params['data']
    locals().update(data)
    imports = ('from gql.transport.aiohttp import AIOHTTPTransport\n'
               'import asyncio\n'
               'from gql import gql, Client\n'
               'from deepclient import DeepClient, DeepClientOptions\n'
               'async def make_deep_client(token):\n'
               ' if not token:\n'
               '  raise ValueError("No token provided")\n'
               ' url = "https://3006-deepfoundation-dev-adxmoff7bpv.ws-eu103.gitpod.io/gql"\n'
               ' transport = AIOHTTPTransport(url=url, headers={ \'Authorization\': f"Bearer {token}" })\n'
               ' client = Client(transport=transport, fetch_schema_from_transport=True)\n'
               ' options = DeepClientOptions(gql_client=client)\n'
               ' deep_client = DeepClient(options)\n'
               ' return deep_client\n')
    start = "async def fn(arg):\n" \
            f" data = arg['data']\n" \
            f" deep = await make_deep_client(arg['jwt'])\n" \
            f" globals().update({data})\n" \
            # f" gql = arg['gql']\n" \
            # f" newLink = arg['newLink']\n"
    code = '\n'.join([' ' + line for line in params['code'].splitlines()])
    end = f"\nprint(asyncio.run(fn({params})))"
    code = imports + start + code + end
    with open("exec_code.py", "w") as file:
        file.write(code)
    python_path = "C:\\Coding\\python-docker-isolation-provider\\venv\\Scripts\\python.exe"

    process = subprocess.Popen([python_path, "exec_code.py"], stdout=subprocess.PIPE)
    output, error = process.communicate()
    result = output.decode('utf-8')
    print(result)
    # obj = ast.literal_eval(result)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=os.environ.get("PORT"), use_reloader=False, threaded=True)
