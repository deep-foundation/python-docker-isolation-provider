import asyncio
import os
import traceback
from dotenv import load_dotenv
from deepclient import DeepClient, DeepClientOptions
from flask import Flask, jsonify, request
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from asgiref.wsgi import WsgiToAsgi
import uvicorn

app = Flask(__name__)
GQL_URN = os.environ.get("GQL_URN", "localhost:3006/gql")
GQL_SSL = os.environ.get("GQL_SSL", 0)
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


def separate_imports(code_str):
    import_lines = []
    other_lines = []

    for line in code_str.split('\n'):
        stripped_line = line.strip()
        if stripped_line.startswith(('import', 'from')):
            import_lines.append(line)
        else:
            other_lines.append(line)

    return '\n'.join(import_lines), '\n'.join(other_lines)


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
        import_section, code_section = separate_imports(full_code)
        exec(import_section, globals())
        args = {
            'deep': make_deep_client(params['jwt']),
            'data': params['data'],
        }
        python_handler_context = {'args': args}
        code_object = compile(code_section, 'python_handler', 'exec')
        exec(code_object, globals(), dict(python_handler_context=python_handler_context))
        result = python_handler_context['result']
        print(f"Resolved: {result}")
        return jsonify({'resolved': result})
    except Exception as e:
        print(f"Rejected: {traceback.format_exc()}")
        return jsonify({'rejected': traceback.format_exc()})

if __name__ == '__main__':
    asgi_app = WsgiToAsgi(app)
    uvicorn.run(asgi_app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), log_level="info", reload=False)
