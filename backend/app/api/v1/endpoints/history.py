import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_history import crud_history
from app.schemas.history import EquationHistoryPage

router = APIRouter()


@router.get("", response_model=EquationHistoryPage)
def list_history(
    search: str = Query(default="", max_length=200),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(deps.get_db),
) -> EquationHistoryPage:
    items, total = crud_history.get_page(
        db,
        search=search.strip(),
        page=page,
        page_size=page_size,
    )
    total_pages = max(1, math.ceil(total / page_size)) if total else 1

    return EquationHistoryPage(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(
    history_id: int,
    db: Session = Depends(deps.get_db),
) -> None:
    deleted = crud_history.delete(db, id=history_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History item not found.",
        )
