from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # add relationship
    hero_powers = db.relationship('HeroPower', backref='hero', cascade="all, delete-orphan")
    powers = association_proxy('hero_powers', 'power')

    # add serialization rules
    serialize_rules = ('-hero_powers.hero', '-hero_powers.power.hero',)


    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add relationship
    hero_powers = db.relationship('HeroPower', backref='power', cascade="all, delete-orphan")
    heroes = association_proxy('hero_powers', 'hero')


    # add serialization rules
    serialize_rules = ('-hero_powers')

    # add validation
    @validates('description')
    def validate_description(self, key, value):
        if not value or len(value) < 20:
            raise ValueError("Description must be at least 20 characters long.")
        return value

    def to_dict(self, include_hero_powers=False):
        power_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }
        # Only include 'hero_powers' if requested
        if include_hero_powers:
            power_dict['hero_powers'] = [hero_power.to_dict() for hero_power in self.hero_powers]
        return power_dict


    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # add relationships
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))

    # add serialization rules
    serialize_rules = ('-hero.hero_powers', '-power.hero_powers')

    # add validation
    @validates('strength')
    def validate_strength(self, key, value):
        if value not in ['Strong', 'Weak', 'Average']:
            raise ValueError("Strength must be 'Strong', 'Weak', or 'Average'.")
        return value


    def __repr__(self):
        return f'<HeroPower {self.id}>'
