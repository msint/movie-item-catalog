#!/usr/bin/env python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Movie

engine = create_engine('sqlite:///MovieCatalog.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create admin user who will be the administrator of this movie catalog
adminUser = User(name="admin", email="maywg89@gmail.com")
session.add(adminUser)
session.commit()

# Dummy movies data
movie1 = Movie(movieName="Princess Agents",
               directorName="Wu Jinyuan",
               category="Historical Fiction",
               description="In a time of civil war, a slave enters the royal \
               household and starts training to become a soldier.",
               userId=1)
session.add(movie1)
session.commit()

# Dummy movies data
movie2 = Movie(movieName="Titanic",
               directorName="James Cameron",
               category="Drama",
               description="Titanic is a romantic drama movie.",
               userId=1)
session.add(movie2)
session.commit()

movie3 = Movie(movieName="The Fast and the Furious",
               directorName="Vin Diesel",
               category="Action",
               description="The Fast and the Furious is an American street \
               racing action film.",
               userId=1)
session.add(movie3)
session.commit()

movie4 = Movie(movieName="A Star is Born",
               directorName="Bradley Cooper",
               category="Romance",
               description="A Star is Born is an romantic drama movie.",
               userId=1)
session.add(movie4)
session.commit()

movie5 = Movie(movieName="The Queens",
               directorName="Annie Yi",
               category="Romance",
               description="The Queens is a romance film.",
               userId=1)
session.add(movie5)
session.commit()

movie6 = Movie(movieName="To the Fore",
               directorName="Dante Lam",
               category="Sport",
               description="To the Fore is a bicycle racing movie.",
               userId=1)
session.add(movie6)
session.commit()

print "Added 6 movie items!"
