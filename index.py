import ast
import os
import subprocess

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
    start = "def fn(arg):\n" \
            f" data = arg['data']\n" \
            f" globals().update({data})\n"
    code = '\n'.join([' ' + line for line in params['code'].splitlines()])
    end = f"\nprint(fn({params}))"
    code = start + code + end
    with open("exec_code.py", "w") as file:
        file.write(code)
    process = subprocess.Popen(["python", "exec_code.py"], stdout=subprocess.PIPE)
    output, error = process.communicate()
    result = output.decode('utf-8')
    print('result')
    print(result)
#     error_result = error.decode('utf-8')
#     print('error_result')
#     print(error_result)
    obj = ast.literal_eval(result)
    return jsonify({ 'resolved': obj })


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=os.environ.get("PORT"), use_reloader=False)
