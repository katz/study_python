from sqlalchemy.orm import registry
from sqlalchemy.orm.decl_api import DeclarativeMeta
import sqlalchemy.types as types
import ulid

mapper_registry = registry()


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True

    # these are supplied by the sqlalchemy2-stubs, so may be omitted
    # when they are installed
    registry = mapper_registry
    metadata = mapper_registry.metadata


class ULIDType(types.TypeDecorator):
    """ULIDをVARCHAR(26)としてデータベースに永続化するためのクラス

    データベースに永続化する際はULIDを文字列化して保存。
    データベースから取り出したものはULIDに変換。
    """

    # データベース側の型はVARCHAR(26)
    impl = types.String(26)

    def process_bind_param(self, value, dialect):
        """ULIDを文字列に変換"""
        if value is None:
            return value
        else:
            return value.str

    def process_result_value(self, value, dialect):
        """文字列からULIDに変換"""
        if value is not None:
            if not isinstance(value, str):
                raise TypeError("value should have str type")
            return ulid.parse(value)
        return value
