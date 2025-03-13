from package.app import db


class Listing(db.Model):
    __tablename__ = 'listings'
    id = db.Column(db.Integer, primary_key=True)
    initial_posting_date = db.Column(db.Date)
    last_updated = db.Column(db.Date)
    update_time = db.Column(db.String())
    building = db.Column(db.String())
    floor = db.Column(db.String())
    unit = db.Column(db.String())
    initial_rent = db.Column(db.Integer)
    rent_change = db.Column(db.Integer)
    current_rent = db.Column(db.Integer)
    days_listed = db.Column(db.Integer)
    status = db.Column(db.String())


db.create_all()