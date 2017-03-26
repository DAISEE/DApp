# #/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Flask, render_template, jsonify
import fct


app = Flask(__name__)
app.debug = True

@app.route("/")
def init():
    data = fct.getconfig()
    return render_template('index.html', name=data['name'], typ=data['typ'])


@app.route("/getconfig/")
def getconfig():
    data = fct.getconfig()
    return jsonify(result=data)

if __name__ == "__main__":
    app.run()
