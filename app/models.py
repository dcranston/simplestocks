from app import db, helpers, app
import json


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auth_token = db.Column(db.String(64), nullable=False)
    refresh_token = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return '<Config {}/{}/{}>'.format(self.id, self.auth_token, self.refresh_token)

    @property
    def auth(self):
        return self.auth_token

    @auth.setter
    def auth(self, value):
        self.auth_token = value

    @property
    def refresh(self):
        return self.refresh_token

    @refresh.setter
    def refresh(self, value):
        self.refresh_token = value
        db.session.commit()


class Stock:
    def __init__(self, data):
        self.symbol = data['stock']['symbol']
        self.name = data['stock']['name']
        self.portfolio = data["account_id"]
        self.holdings = int(data['quantity'])
        self.quote = 0.0
        self.quote_timestamp = None
        self.open = float(data['quote']['open'])
        self.since_open = 0.0
        self.prev_close = float(data['quote']['previous_close'])
        self.prev_close_timestamp = data['quote']['previous_closed_at']
        self.since_prev_close = 0.0
        self.since_prev_close_pct = 0.0
        self.total_value = 0.0
        self.set_quote(data['quote']['amount'])

    def set_quote(self, value):
        self.quote = float(value)
        self.update_value()
        self.since_prev_close = self.quote - self.prev_close
        self.since_prev_close_pct = round((self.since_prev_close / self.prev_close) * 100, 2)
        self.since_open = self.quote - self.open

    def update_value(self):
        self.total_value = self.holdings * self.quote

    def to_dict(self):
        v = vars(self)
        v.update({"quote": self.quote})
        return v

    def __repr__(self):
        return '<Stock %r>' % self.symbol


class Portfolio:
    def __init__(self, account_id):
        self.id = account_id
        self.positions = []
        pass

    def __repr__(self):
        return f'<Portfolio {self.id}>'

    @property
    def value(self):
        v = 0.0
        for pos in self.positions:
            v += pos.total_value
        return v

    def to_dict(self):
        self.positions = [s.to_dict() for s in self.positions]
        d = vars(self)
        d.update({"value": self.value})
        return d


class Quote(db.Model):
    __tablename__ = "quotes"
    __table_args__ = (db.UniqueConstraint('symbol', 'timestamp', name="uniq_sym_time"),)
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Quote %r>' % self.symbol

    def to_dict(self):
        return dict({
            "id": self.id,
            "symbol": self.symbol,
            "timestamp": self.timestamp.ctime(),
            "value": self.value
            })

    def to_json(self):
        return json.dumps(self.to_dict())


db.create_all()
