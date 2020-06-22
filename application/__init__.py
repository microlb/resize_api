from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask import Flask
from redis import Redis
import rq


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['DEBUG'] = True
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = rq.Queue('api-tasks', connection=app.redis)


from application import routes, models
