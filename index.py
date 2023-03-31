import ast
import io
import sys

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({})


@app.route('/init', methods=['POST'])
def init():
    return jsonify({})


@app.route('/call', methods=['POST'])
def call():
    body = request.json
    params = body['params']
    data = params['data']
    locals().update(data)
    start = "def fn():\n" \
            f" globals().update({data})\n"
    code = params['code']
    code = '\n'.join([' ' + line for line in code.splitlines()])
    end = f"\nresult = fn()" \
          f"\nprint(result)"
    output = io.StringIO()
    sys.stdout = output
    exec(start + code + end)
    result = output.getvalue()
    obj = ast.literal_eval(result)
    print(obj)
    return jsonify(obj)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
