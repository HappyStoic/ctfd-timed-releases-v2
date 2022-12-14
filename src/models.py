from CTFd.models import db


class TimedReleases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chalid = db.Column(db.Integer, db.ForeignKey('challenges.id', ondelete="CASCADE"), nullable=False)
    release = db.Column(db.DateTime, nullable=False)

    def __init__(self, chalid, release):
        self.chalid = chalid
        self.release = release

    def __repr__(self):
        return '<timed-release {}, {}>'.format(self.chalid, self.release)
