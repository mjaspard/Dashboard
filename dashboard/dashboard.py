from webapp import app, db
from webapp.models import User, Post, Server

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Server': Server}


