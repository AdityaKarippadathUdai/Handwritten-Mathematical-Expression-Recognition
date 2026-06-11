from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.history import EquationHistory
from app.schemas.history import EquationHistoryCreate


class CRUDEquationHistory:
    def create(self, db: Session, *, obj_in: EquationHistoryCreate) -> EquationHistory:
        db_obj = EquationHistory(
            image_path=obj_in.image_path,
            latex_output=obj_in.latex_output,
            confidence=obj_in.confidence,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_page(
        self,
        db: Session,
        *,
        search: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[EquationHistory], int]:
        query = db.query(EquationHistory)

        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    EquationHistory.latex_output.ilike(pattern),
                    EquationHistory.image_path.ilike(pattern),
                )
            )

        total = query.count()
        offset = (page - 1) * page_size
        items = (
            query.order_by(EquationHistory.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return items, total

    def delete(self, db: Session, *, id: int) -> bool:
        db_obj = db.query(EquationHistory).filter(EquationHistory.id == id).first()
        if db_obj is None:
            return False

        db.delete(db_obj)
        db.commit()
        return True


crud_history = CRUDEquationHistory()
