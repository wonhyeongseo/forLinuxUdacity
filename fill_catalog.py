from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Delete all the categories to avoid repetition
# session.query(Category).delete()
# session.commit()

# Delete all the items to avoid repetition
# session.query(Item).delete()
# session.commit()

# Start new entries

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Items for Parkour
category1 = Category(user_id=1, name="Parkour")
session.add(category1)
session.commit()

item1 = Item(user_id=1, title="T-shirt", description="Awesome t-shirt", category=category1)
session.add(item1)
session.commit()

# Items for Swimming
category2 = Category(user_id=1, name="Swimming")
session.add(category2)
session.commit()

item2 = Item(user_id=1, title="Swimming board", description="Sleek swimming board", category=category2)
session.add(item2)
session.commit()

item3 = Item(user_id=1, title="Swimming cap", description="Very wettable", category=category2)
session.add(item3)
session.commit()

# Items for Jujitsu
category3 = Category(user_id=1, name="Jujitsu")
session.add(category3)
session.commit()

item4 = Item(user_id=1, title="Black Belt", description="Challenge the master", category=category3)
session.add(item4)
session.commit()

print("Added items!")
