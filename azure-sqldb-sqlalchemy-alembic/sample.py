from model.user import User, Email
import pprint
import random
from logging import getLogger
from sqldb import get_engine
from sqlalchemy.orm import sessionmaker


logger = getLogger(__name__)

# INSERTのテスト用データ作る
email1 = Email(email_address="test{}@example.com".format(random.randint(1, 10000)))
email2 = Email(email_address="test{}@example.com".format(random.randint(1, 10000)))
u = User(fullname="テスト太郎{}".format(random.randint(1, 10000)))
u.emails.append(email1)
u.emails.append(email2)

# INSERTする
engine = get_engine()
Session = sessionmaker(bind=engine)
session = Session()
session.add(u)
session.commit()

# SELECTして取ってくる
all_user = session.query(User).all()

pprint.pprint(all_user)
