from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin


class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    # We store the extracted text, not the PDF itself — later phases only ever
    # need text. LONGTEXT because MySQL's TEXT caps at 64KB.
    extracted_text: Mapped[str] = mapped_column(Text(length=4_294_967_295), nullable=False)
    page_count: Mapped[int] = mapped_column(nullable=False, default=1)
