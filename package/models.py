from package.app import db


class Trade(db.Model):
    __tablename__ = 'listings'
    id = db.Column(db.Integer, primary_key=True)
    posting_date = db.Column(db.Date)
    building = db.Column(db.String())
    floor = db.Column(db.String())
    unit = db.Column(db.String())
    rent = db.Column(db.Integer)


db.create_all()