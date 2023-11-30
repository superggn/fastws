from sqlalchemy import create_engine

from fastws.constants import SQLALCHEMY_URL

# url_object = URL.create(
#     "mysql+pymysql",
#     username="root",
#     password="123456",  # plain (unescaped) text
#     host="127.0.0.1",
#     database="fastws",
# )

engine = create_engine(SQLALCHEMY_URL)
