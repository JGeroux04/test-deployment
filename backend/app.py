from flask import Flask
from flask_cors import CORS
from db.mongo import init_db
from routes.predict import predict_blueprint
from routes.register import register_blueprint
from routes.analyze import analyze_blueprint
from routes.login_face import login_face_blueprint
from routes.demo_compare import demo_blueprint

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize database
init_db(app)

# Register routes
app.register_blueprint(predict_blueprint, url_prefix='/api')
app.register_blueprint(register_blueprint, url_prefix='/api')
app.register_blueprint(analyze_blueprint, url_prefix='/api')
app.register_blueprint(login_face_blueprint, url_prefix='/api')
app.register_blueprint(demo_blueprint, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)