from flask import Flask, jsonify

from api import catalog, criteria, evaluations, rankings
from api.errors import register_error_handlers

app = Flask(__name__)
app.register_blueprint(catalog.bp)
app.register_blueprint(criteria.bp)
app.register_blueprint(evaluations.bp)
app.register_blueprint(rankings.bp)
register_error_handlers(app)


@app.get("/health")
def health():
    return jsonify(success=True, data={"status": "ok"})
