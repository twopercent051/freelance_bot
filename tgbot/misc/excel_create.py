from openpyxl import Workbook
from openpyxl.styles import Font
import os


async def create_excel(projects_list: list):
    wb = Workbook()
    ws = wb.active
    ws.append(
        (
            'Номер',
            'Название',
            'Гонорар',
            'Дата начала',
            'Дата завершения',
            'Отработано минут',
            'Статус',
            'Оплата в час',
        )
    )
    ft = Font(bold=True)
    for row in ws['A1:T1']:
        for cell in row:
            cell.font = ft

    for project in projects_list:
        ws.append(
            (
                project['id'],
                project['title'],
                project['royalty'],
                project['start_date'].strftime('%d-%m-%Y'),
                project['finish_date'].strftime('%d-%m-%Y') if project['finish_date'] else '--',
                f"{project['worktime'] // 60} час {project['worktime'] % 60} мин",
                "Завершён" if project['is_finished'] else "В работе",
                '' if project['worktime'] == 0 else (60 * project['royalty']) / project['worktime'],
            )
        )

    wb.save(f'{os.getcwd()}/all_projects.xlsx')
