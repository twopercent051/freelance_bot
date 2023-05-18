from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class AdminInlineKeyboard(InlineKeyboardMarkup):
    """Клавиатуры админа"""

    @classmethod
    def home_kb(cls) -> InlineKeyboardMarkup:
        """Кнопка домой"""
        keyboard = [[InlineKeyboardButton(text='🏡 Домой', callback_data='home')]]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def projects_kb(cls, projects_list: list) -> InlineKeyboardMarkup:
        """Главное меню"""
        keyboard = []
        for project in projects_list:
            project_id = project['id']
            project_title = project['title']
            keyboard.append([InlineKeyboardButton(text=f'ID: {project_id} || {project_title}',
                                                  callback_data=f'project_id:{project_id}')])
        keyboard.append([InlineKeyboardButton(text='🕺 Новый проект', callback_data='new_project')])
        keyboard.append([InlineKeyboardButton(text='📋 Список проектов', callback_data='excel_list')])
        keyboard.append([InlineKeyboardButton(text='🔎 Поиск по ID', callback_data='search_project')])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def profile_kb(cls, project_id: int, is_finished: bool):
        """Клавиатура проекта"""
        keyboard = [[InlineKeyboardButton(text='⏳ Рабочее время', callback_data=f'worktime:{project_id}')]]
        if not is_finished:
            keyboard.append([InlineKeyboardButton(text='💵 Завершить проект',
                                                  callback_data=f'finish_project:{project_id}')])
        keyboard.append([InlineKeyboardButton(text='🏡 Домой', callback_data='home')])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard
