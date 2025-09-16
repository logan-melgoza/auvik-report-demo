from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column( db.Integer, primary_key=True )
    email = db.Column( db.String(255) , unique=True, nullable=False, index=True )
    password = db.Column( db.String(128), nullable=False )

    def __repr__(self):
        return f"User('{self.email}')"