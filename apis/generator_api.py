from glob import glob
from flask import jsonify, request, Blueprint

import math
import random

from itsdangerous import json

generator_api = Blueprint("generator", __name__, url_prefix="/api/generator")

OFFSET = 100
LIMIT = 300000

# Load in file when imported
articles = []
weights = []
count = 0


def load_page_rank(app):
    global articles, count, weights
  
    with open(app.config["PAGERANK_FILE"], encoding="utf-8") as file:
        for line in file:
            (logprob, name) = line.split()
            prob = math.e ** float(logprob)

            articles.append(name)
            weights.append(prob)

            count += 1
            if (count >= LIMIT + OFFSET):
                break

    articles = articles[OFFSET:]
    weights = weights[OFFSET:]
    assert(len(articles) == LIMIT)

@generator_api.get("prompt")
def get_random_prompt():
    if (count == 0):
        return "Prompt generation not setup", 500

    num = int(request.args.get('num_articles', 1))
    difficulty = int(request.args.get('difficulty', 10000))

    if (difficulty >= LIMIT or difficulty < 10):
        return f"Invalid difficulty, should be between 10 and {LIMIT}", 400


    prompts = random.choices(articles[:difficulty], weights[:difficulty], k=num)
    return jsonify(prompts), 200