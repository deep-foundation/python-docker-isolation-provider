import ast
import os
import subprocess
import traceback

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
    try:
        body = request.json
        params = body['params']
        args = {}
        args['data'] = params['data']
        code = f"{params['code']}\nhandlerContext['result'] = fn({args})"
        codeObject = compile(code, 'python_handler', 'exec')
        handlerContext = {}
        exec(codeObject, dict(handlerContext=handlerContext))
        result = handlerContext['result']
        obj = ast.literal_eval(result)
        return jsonify({ 'resolved': obj })
    except Exception as e:
        return jsonify({ 'rejected': traceback.format_exc() })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=os.environ.get("PORT"), use_reloader=False, threaded=True)
