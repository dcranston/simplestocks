from app import db
import json


class Quote(db.Model):
    __tablename__ = "quotes"
    __table_args__ = (db.UniqueConstraint('symbol', 'timestamp', name="uniq_sym_time"),)
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Quote %r>' % self.symbol

    def to_json(self):
        return json.dumps({
            self.symbol: {
                "id": self.id,
                "symbol": self.symbol,
                "timestamp": self.timestamp.ctime(),
                "value": self.value
            }
        })

db.create_all()
