from sqlalchemy import Table, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from dataclasses import dataclass, field

import ulid
from . import ULIDType, mapper_registry
from ulid import ULID
from typing import List, NewType

UserID = NewType("UserID", ULID)


@dataclass
class Email:
    id: ULID = field(
        init=False,
        default_factory=ulid.new,
    )
    user_id: UserID = field(init=False)
    email_address: str = field(default="")


@dataclass
class User:
    id: UserID = field(
        init=False,
        default_factory=ulid.new,
    )
    fullname: str = field(default="")
    emails: List[Email] = field(default_factory=list)


user_table = Table(
    "user",
    mapper_registry.metadata,
    Column("id", ULIDType, primary_key=True),
    Column("fullname", String(255), nullable=False),
    schema="my_schema",
)

email_table = Table(
    "email",
    mapper_registry.metadata,
    Column("id", ULIDType, primary_key=True),
    Column("user_id", ULIDType, ForeignKey("my_schema.user.id")),
    Column("email_address", String(255), nullable=False),
    schema="my_schema",
)

mapper_registry.map_imperatively(
    User,
    user_table,
    properties={
        "id": user_table.c.id,
        "fullname": user_table.c.fullname,
        "emails": relationship("Email"),
    },
    column_prefix="_db_column_",
)
mapper_registry.map_imperatively(
    Email,
    email_table,
    properties={
        "id": email_table.c.id,
        "user_id": email_table.c.user_id,
        "email_address": email_table.c.email_address,
    },
    column_prefix="_db_column_",
)
