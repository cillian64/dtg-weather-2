#!/usr/bin/python3

from flask import Flask
app = Flask(__name__)
from flask import jsonify
import json
import numpy as np
import os

@app.route("/gimme.json")
def gimme_json():
    xs = np.linspace(0, 2*np.pi, 100)
    ys = np.sin(xs)
    return jsonify({'results': list(zip(list(xs), list(ys)))})

    



if __name__ == "__main__":
    app.run()
