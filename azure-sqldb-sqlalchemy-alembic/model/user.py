from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from dataclasses import dataclass, field
from typing import List

import ulid
from . import mapper_registry, ULIDType
from ulid import ULID


@mapper_registry.mapped
@dataclass
class Email:
    __tablename__ = "email"
    __table_args__ = {"schema": "my_schema"}
    __sa_dataclass_metadata_key__ = "sa"

    id: ULID = field(
        init=False,
        default_factory=ulid.new,
        metadata={"sa": Column(ULIDType, primary_key=True)},
    )
    user_id: ULID = field(
        init=False, metadata={"sa": Column(ULIDType, ForeignKey("my_schema.user.id"))}
    )
    email_address: str = field(default=None, metadata={"sa": Column(String(255))})


@mapper_registry.mapped
@dataclass
class User:
    __tablename__ = "user"
    __table_args__ = {"schema": "my_schema"}
    __sa_dataclass_metadata_key__ = "sa"

    id: ULID = field(
        init=False,
        default_factory=ulid.new,
        metadata={"sa": Column(ULIDType, primary_key=True)},
    )
    fullname: str = field(
        default="", metadata={"sa": Column(String(255), nullable=False)}
    )
    emails: List[Email] = field(
        default_factory=list, metadata={"sa": relationship("Email")}
    )
