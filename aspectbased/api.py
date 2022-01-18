from typing import Union, Dict, Tuple, List

import json
from flask import Response, request

from logos.logos.api import app, http_get_transcript, bad_request

import predict_sentiment


@app.route('/api/models/sentiment/transcript', methods=['POST'])
def predict_sentiment_transcript() -> Response:
    """"""
    req_data = request.get_json()
    aspects = req_data["aspects"]
    print(aspects)
    valid, transcript = http_get_transcript({'transcript': req_data})
    print(valid)
    if not valid:
        app.logger.error("Invalid request format.")
        return bad_request
    try:
        pred = predict_sentiment.predict(transcript, aspects)
        js_data = json.dumps(pred, indent=4, sort_keys=True)
        resp = Response(js_data, status=200, mimetype='application/json')
    except Exception as e:
        app.logger.error(f"{e}")
        return bad_request

    return resp


# @app.route('/api/models/sentiment/text', methods=['POST'])
# def predict_sentiment_text() -> Response:
#     """"""
#     req_data = request.get_json()
#     valid, texts = http_get_texts(req_data)
#     if not valid:
#         app.logger.error("Invalid request format.")
#         return bad_request
#
#     try:
#         pred = predict_sentiment.predict_sentiment(texts)
#         js_data = json.dumps(pred, indent=4, sort_keys=True)
#         resp = Response(js_data, status=200, mimetype='application/json')
#     except Exception as e:
#         app.logger.error(f"{e}")
#         return bad_request
#
#     return resp


# def http_get_texts(req_data: Dict) -> Tuple[bool, Union[List[str], None]]:
#     """"""
#     valid = False
#     texts = None
#     try:
#         texts = req_data['texts']
#         valid = all([isinstance(text, str) for text in texts])
#     except Exception as e:
#         app.logger.error(f"{e}")
#     return valid, texts


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5031, debug=False)
