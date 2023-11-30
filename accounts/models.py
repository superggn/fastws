from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from fastws.base import Base


class User(Base):
    __tablename__ = "account_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    # lowercase
    username: Mapped[str] = mapped_column(String(30), unique=True)
    # sha256 password
    password: Mapped[str] = mapped_column(String(64))

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


from hashlib import sha256

s = b'ajahduiqhweiiadniasjdoajeoiqwjeomodijaadssd'
res2 = sha256(s).hexdigest()

# class Address(Base):
#     __tablename__ = "account_address"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     email_address: Mapped[str] = mapped_column(String(100))
#     user_id: Mapped[int] = mapped_column(ForeignKey("account_user.id"))
#     user: Mapped["User"] = relationship(back_populates="addresses")
#
#     def __repr__(self) -> str:
#         return f"Address(id={self.id!r}, email_address={self.email_address!r})"
