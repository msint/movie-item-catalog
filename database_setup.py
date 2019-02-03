#!/usr/bin/env python
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# class to store user info
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    provider = Column(String(30))


# class to store Movie info
class Movie(Base):
    __tablename__ = "movie"

    id = Column(Integer, primary_key=True)
    movieName = Column(String(250), nullable=False)
    directorName = Column(String(250), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(), nullable=False)
    userId = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # return movie data in serializable format
        """Return movie object data in easily serializeable format"""
        return {
            'id': self.id,
            'movieName': self.movieName,
            'directorName': self.directorName,
            'category': self.category,
            'description': self.description
        }

engine = create_engine('sqlite:///MovieCatalog.db')
Base.metadata.create_all(engine)
