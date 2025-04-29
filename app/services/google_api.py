from copy import deepcopy
from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings

COLUMNS = 3
ROWS = 100
TABLE_HEADER_TEMPLATE = [
    ["Отчет от {report_date}"],
    ["Топ проектов по скорости закрытия"],
    ["Название проекта", "Время сбора", "Описание"],
]
SPREADSHEET_BODY_TEMPLATE = dict(
    properties=dict(
        title="",
        locale="ru_RU",
    ),
    sheets=[
        dict(
            properties=dict(
                sheetType="GRID",
                sheetId=0,
                title="Отчет",
                gridProperties=dict(rowCount=ROWS, columnCount=COLUMNS),
            )
        )
    ],
)


async def spreadsheets_create(
    wrapper_services: Aiogoogle,
    spreadsheet_template: dict = SPREADSHEET_BODY_TEMPLATE,
) -> tuple[str, str]:
    service = await wrapper_services.discover("sheets", "v4")
    spreadsheet_body = deepcopy(spreadsheet_template)
    spreadsheet_body["properties"]["title"] = (
        f"Отчет от {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}"
    )
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response["spreadsheetId"]
    spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    return spreadsheet_id, spreadsheet_url


async def set_user_permissions(
    spreadsheet_id: str,
    wrapper_services: Aiogoogle,
) -> None:
    permissions_body = {
        "type": "user",
        "role": "writer",
        "emailAddress": settings.email,
    }
    service = await wrapper_services.discover("drive", "v3")
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id",
        )
    )


async def spreadsheets_update_value(
    spreadsheetid: str,
    projects: list,
    wrapper_services: Aiogoogle,
) -> None:
    service = await wrapper_services.discover("sheets", "v4")
    table_header = deepcopy(TABLE_HEADER_TEMPLATE)
    table_header[0][0] = table_header[0][0].format(
        report_date=datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    )
    table_values = [
        *table_header,
        *[
            [
                project.name,
                str(project.close_date - project.create_date),
                project.description,
            ]
            for project in projects
        ],
    ]
    num_rows = len(table_values)
    num_cols = max(len(row) for row in table_values)
    if num_rows > ROWS or num_cols > COLUMNS:
        raise ValueError(
            f"Размер таблицы {num_rows}x{num_cols} "
            f"превышает лимит: {ROWS}x{COLUMNS}"
        )
    update_body = {"majorDimension": "ROWS", "values": table_values}
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range=f"R1C1:R{num_rows}C{num_cols}",
            valueInputOption="USER_ENTERED",
            json=update_body,
        )
    )
