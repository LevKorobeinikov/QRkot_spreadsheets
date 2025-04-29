from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Integer,
    text,
)

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

    __table_args__ = (
        CheckConstraint(
            text("full_amount > 0"),
            name="check_full_amount_positive",
        ),
        CheckConstraint(
            text(
                "(full_amount - invested_amount) >= 0 AND invested_amount >= 0"
            ),
            name="check_invested_amount_valid",
        ),
    )

    def __repr__(self):
        return (
            f"{type(self).__name__}("
            f"id={self.id}, "
            f"{self.full_amount=}, "
            f"{self.invested_amount=}, "
            f"{self.fully_invested=}, "
            f"{self.create_date=}, "
            f"{self.close_date=})"
        )
