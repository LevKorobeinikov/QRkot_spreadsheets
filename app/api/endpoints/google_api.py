from aiogoogle import Aiogoogle
from aiogoogle.excs import HTTPError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.services.google_api import (
    set_user_permissions,
    spreadsheets_create,
    spreadsheets_update_value,
)

router = APIRouter()


@router.post(
    "/",
    response_model=dict[str, str],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service),
):
    """
    Только для суперюзеров.
    Возвращает ссылку на созданный отчёт в Google Таблицах.
    """
    projects = await charity_project_crud.get_projects_by_completion_rate(
        session,
    )
    spreadsheet_id, spreadsheet_url = await spreadsheets_create(
        wrapper_services,
    )
    await set_user_permissions(
        spreadsheet_id,
        wrapper_services,
    )
    try:
        await spreadsheets_update_value(
            spreadsheet_id,
            projects,
            wrapper_services,
        )
        return {"url": spreadsheet_url}
    except HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении Google таблицы: {error}",
        )
