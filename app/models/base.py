from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
)

from app.constants import FULL_AMOUNT_SUM, INVESTED_AMOUNT
from app.core.db import Base


class BaseModel(Base):
    """
    Абстрактная базовая модель для моделей.
    """

    __abstract__ = True

    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, nullable=False, default=0)
    fully_invested = Column(Boolean, nullable=False, default=False)
    create_date = Column(DateTime, index=True, default=datetime.now)
    close_date = Column(DateTime, index=True)

    def validate_investment(self):
        if self.full_amount <= 0:
            raise ValueError(FULL_AMOUNT_SUM)
        if not (self.full_amount >= self.invested_amount >= 0):
            raise ValueError(INVESTED_AMOUNT)

    def save(self, *args, **kwargs):
        self.validate_investment()
        super().save(*args, **kwargs)

    def __repr__(self):
        return (
            f"{type(self).__name__}("
            f"{self.id=}, "
            f"{self.full_amount=}, "
            f"{self.invested_amount=}, "
            f"{self.fully_invested=}, "
            f"{self.create_date=}, "
            f"{self.close_date=})"
        )
