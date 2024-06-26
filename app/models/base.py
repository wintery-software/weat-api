from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import UUID, asc, desc, func, inspect
from sqlalchemy.orm import mapped_column, Mapped, validates

from app import db
from app.constants import VALID_LOCALES


class BaseModel(db.Model):
    __abstract__ = True

    _fields: List[str] = []

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

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
            print(str(e))
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
        sort: str = "created_at",
        order: str = "asc",
        page: Optional[int] = 0,
        page_size: Optional[int] = 0,
    ):
        order_expr = asc if order == "asc" else desc

        objs = (
            cls
            .query()
            .order_by(order_expr(getattr(cls, sort)).nullslast())
        )

        if page_size:
            return objs.paginate(page=page, per_page=page_size, error_out=False).items
        else:
            return objs.all()
        
    @classmethod
    def list_random(cls, limit: int = 10):
        return cls.query().order_by(func.random()).limit(limit).all()

    @classmethod
    def count(cls):
        return cls.query().count()

    @classmethod
    def query(cls):
        return db.session.query(cls)

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

        return result

    def refresh(self):
        db.session.refresh(self)

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()

    def delete_all(self, objs: List["BaseModel"]):
        for obj in objs:
            db.session.delete(obj)
        db.session.commit()


class TranslationMixin:
    translations: Mapped[List["Translation"]] = []
    TranslationClass = None

    @validates("translations")
    def validate_locales(cls, translations):
        invalid_locales = [
            locale for locale in translations.keys() if locale not in VALID_LOCALES
        ]
        if invalid_locales:
            raise ValueError(f"Invalid locales: {', '.join(invalid_locales)}")
        return translations

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

        for locale, translation_dict in translations.items():
            self.add_translation(locale=locale, **dict(translation_dict))

    def translation_to_dict(
        self, locale: str = None, *args, **kwargs
    ) -> Dict[str, Any]:
        translation = self.get_translation(locale)
        if locale and translation:
            return translation.to_dict()

        return {}


class TranslatableModel(BaseModel, TranslationMixin):
    __abstract__ = True

    @classmethod
    def create(cls, **params):
        translations = params.pop("translations", {})

        obj = super().create(**params)
        obj.update_translations(translations)

        return obj

    def update(self, **params):
        translations = params.pop("translations", {})
        self.update_translations(translations)

        super().update(**params)

    def to_dict(self, locale: str = None, *args, **kwargs):
        result = super().to_dict(locale=locale, *args, **kwargs)
        result.update(self.translation_to_dict(locale=locale))

        return result


class Translation(BaseModel):
    __abstract__ = True

    parent_id: Mapped[uuid.UUID] = None
    locale: Mapped[str] = mapped_column()
