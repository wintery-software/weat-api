from datetime import datetime
from typing import Any, Dict, List, Union
import uuid

from sqlalchemy import UUID, BinaryExpression, UnaryExpression, func, inspect
from sqlalchemy.orm import mapped_column, Mapped


from app import db


class TranslationMixin:
    translations: Mapped[List["Translation"]] = []
    TranslationClass = None

    def get_translation(self, locale: str) -> "Translation":
        for translation in self.translations:
            if translation.locale == locale:
                return translation
        return None

    def add_translation(self, locale: str, *args, **kwargs):
        translation = self.get_translation(locale)
        if translation:
            translation.update(**kwargs)
        else:
            translation = self.TranslationClass.create(
                parent_id=self.id, locale=locale, **kwargs
            )
        return translation

    def remove_translation(self, locale: str):
        translation = self.get_translation(locale)
        if translation:
            translation.delete()

    def update_translations(self, translations):
        self.delete_all(self.translations)

        for translation_dict in translations:
            self.add_translation(**translation_dict)

    def translation_to_dict(
        self, locale: str = None, *args, **kwargs
    ) -> Dict[str, Any]:
        translation = self.get_translation(locale)
        if locale and translation:
            return translation.to_dict()

        return {}


class BaseModel(db.Model, TranslationMixin):
    __abstract__ = True

    _fields: List[str] = []

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    def validate_not_blank(self, key, value):
        if not value or not value.strip():
            raise ValueError(f"Field {key} cannot be blank")
        return value

    @classmethod
    def create(cls, **params):
        obj = cls(**params)

        db.session.add(obj)
        db.session.commit()
        db.session.refresh(obj)

        return obj

    def update(self, **params):
        for key, value in params.items():
            setattr(self, key, value)

        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get(cls, **params):
        try:
            obj = db.session.query(cls).filter_by(**params).first()

            if obj is None:
                return None

            return obj
        except Exception as e:
            return None

    @classmethod
    def get_or_create(cls, **params):
        obj = cls.get(**params)
        created = False

        if obj is None:
            obj = cls.create(**params)
            created = True

        return obj, created

    @classmethod
    def list(
        cls,
        filter_by: Union[UnaryExpression, BinaryExpression] = None,
        order_by: Union[UnaryExpression, BinaryExpression] = None,
    ):
        if filter_by is None:
            filter_by = True
        if order_by is None:
            order_by = cls.created_at

        objs = db.session.query(cls).filter(filter_by).order_by(order_by).all()

        return objs

    def to_dict(self, *args, **kwargs):
        result = {}

        for field in self._fields:
            value = getattr(self, field)

            if field in inspect(self.__class__).relationships:
                # For one-to-many relationships
                if isinstance(value, list):
                    result[field] = [v.to_dict(*args, **kwargs) for v in value]
                # For one-to-one or many-to-one relationships
                elif value is not None:
                    result[field] = value.to_dict(*args, **kwargs)
                # For others
                else:
                    result[field] = None
            else:
                result[field] = value

        result.update(self.translation_to_dict(*args, **kwargs))

        return result

    def refresh(self):
        db.session.refresh(self)
        return self

    def delete_all(self, objs: List["BaseModel"]):
        for obj in objs:
            db.session.delete(obj)
        db.session.commit()


class Translation(BaseModel):
    __abstract__ = True

    parent_id: Mapped[uuid.UUID] = None
    locale: Mapped[str] = mapped_column()
