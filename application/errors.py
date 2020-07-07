from flask import jsonify, make_response
from application import app, db


@app.errorhandler(405)
def not_found(error):
    return make_response(jsonify({'error': 'Method not found'}), 405)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def not_found(error):
    db.session.rollback()
    return make_response(jsonify({'error': 'An unexpected error'}), 500)

