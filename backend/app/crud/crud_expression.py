from sqlalchemy.orm import Session
from app.models.expression import Expression
from app.schemas.expression import ExpressionCreate

class CRUDExpression:
    def get(self, db: Session, id: int):
        return db.query(Expression).filter(Expression.id == id).first()

    def create(self, db: Session, *, obj_in: ExpressionCreate) -> Expression:
        db_obj = Expression(
            raw_image_path=obj_in.raw_image_path,
            latex_result=obj_in.latex_result
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

crud_expression = CRUDExpression()
