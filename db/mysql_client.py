from sqlalchemy import create_engine, URL


class MySQLClient:
    engine = None

    @classmethod
    def get_engine(cls):
        if cls.engine:
            return cls.engine
        url_object = URL.create(
            "mysql+pymysql",
            username="root",
            password="123456",  # plain (unescaped) text
            host="127.0.0.1",
            database="fastws",
        )
        cls.engine = create_engine(url_object)
        # cls.conn = happybase.Connection(settings.HBASE_HOST)
        return cls.engine
