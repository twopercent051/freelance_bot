import os
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.filters.state import StateFilter

from create_bot import bot
from tgbot.filters.admin import AdminIdFilter
from tgbot.keyboards.inline import AdminInlineKeyboard as inline_kb
from tgbot.misc.excel_create import create_excel
from tgbot.misc.states import AdminFSM
from tgbot.models.sql_connector import MyProjectsDAO

router = Router()
router.message.filter(AdminIdFilter())
router.callback_query.filter(AdminIdFilter())


async def project_profile(project_id: int) -> str:
    """Функция создания карточки проекта"""
    profile = await MyProjectsDAO.get_one_or_none(project_id=project_id)
    if profile:
        text = [
            f"<b># {profile['id']} {profile['title']}</b>\n",
            f"Гонорар: <i>{profile['royalty']} ₽</i>",
            f"Дата старта: <i>{profile['start_date'].strftime('%d-%m-%Y')}</i>",
            f"Дата окончания: <i>{profile['finish_date'].strftime('%d-%m-%Y') if profile['finish_date'] else '--'}</i>",
            f"Время работы: <i>{profile['worktime'] // 60} час {profile['worktime'] % 60} мин</i>",
            f"Статус: <i>{'Завершён' if profile['is_finished'] else 'В работе'}</i>",
            f"Оплата в час: <i>{'' if profile['worktime'] == 0 else (60 * profile['royalty']) / profile['worktime']}</i>"
        ]
        kb = inline_kb.profile_kb(project_id=project_id, is_finished=profile['is_finished'])
        return '\n'.join(text), kb
    else:
        kb = inline_kb.home_kb()
        return "Проект не найден", kb


@router.message(Command('start'), StateFilter('*'))
async def admin_start_msg(message: Message, state: FSMContext):
    project_list = await MyProjectsDAO.get_all(all_projects=False)
    text = "Действующие проекты"
    kb = inline_kb.projects_kb(projects_list=project_list)
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == 'home', StateFilter('*'))
async def admin_start_clb(callback: CallbackQuery, state: FSMContext):
    project_list = await MyProjectsDAO.get_all(all_projects=False)
    text = "Действующие проекты"
    kb = inline_kb.projects_kb(projects_list=project_list)
    await state.set_state(AdminFSM.home)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == "new_project")
async def create_project(callback: CallbackQuery, state: FSMContext):
    """НАЧАЛО СОЗДАНИЯ ПРОЕКТА"""
    text = "Введите название проекта"
    kb = inline_kb.home_kb()
    await state.set_state(AdminFSM.title)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.title)
async def get_title(message: Message, state: FSMContext):
    text = "Укажите предполагаемый гонорар"
    kb = inline_kb.home_kb()
    await state.update_data(title=message.text)
    await state.set_state(AdminFSM.royalty_create)
    await message.answer(text, reply_markup=kb)


@router.message(F.text, AdminFSM.royalty_create)
async def get_royalty(message: Message, state: FSMContext):
    if message.text.isdigit():
        text = "Проект создан"
        state_data = await state.get_data()
        title = state_data['title']
        today = datetime.now().date()
        await MyProjectsDAO.create(title=title, royalty=int(message.text), start_date=today)
        await state.set_state(AdminFSM.home)
    else:
        text = "Нужно ввести целое число"
    kb = inline_kb.home_kb()
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == 'excel_list')
async def get_excel(callback: CallbackQuery):
    """Таблица с проектами"""
    projects_list = await MyProjectsDAO.get_all(all_projects=True)
    await create_excel(projects_list=projects_list)
    kb = inline_kb.home_kb()
    file = FSInputFile(path=f'{os.getcwd()}/all_projects.xlsx', filename="all_projects.xlsx")
    await bot.send_document(chat_id=callback.from_user.id, document=file, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == "search_project")
async def search_project(callback: CallbackQuery, state: FSMContext):
    """Поиск проекта"""
    text = "Введите ID проекта"
    kb = inline_kb.home_kb()
    await state.set_state(AdminFSM.project_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.project_id)
async def project_profile_msg(message: Message):
    """Поиск по вводу"""
    if message.text.isdigit():
        project_id = int(message.text)
        text, kb = await project_profile(project_id=project_id)
    else:
        text = "Нужно ввести целое число"
        kb = inline_kb.home_kb()
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "project_id")
async def project_profile_clb(callback: CallbackQuery):
    """Поиск по кнопке"""
    project_id = int(callback.data.split(":")[1])
    text, kb = await project_profile(project_id=project_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "worktime")
async def request_worktime(callback: CallbackQuery, state: FSMContext):
    """Запрос рабочего времени"""
    project_id = int(callback.data.split(":")[1])
    text = "Укажите рабочее время в минутах"
    kb = inline_kb.home_kb()
    await state.set_state(AdminFSM.worktime)
    await state.update_data(project_id=project_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.worktime)
async def set_worktime(message: Message, state: FSMContext):
    """Запись рабочего времени"""
    if message.text.replace("-", "").isdigit():
        state_data = await state.get_data()
        project_id = int(state_data['project_id'])
        text = f"Рабочее время проекта # {project_id} обновлено"
        await MyProjectsDAO.change_worktime(project_id=project_id, worktime=int(message.text))
        await state.set_state(AdminFSM.home)
    else:
        text = "Нужно ввести целое число"
    kb = inline_kb.home_kb()
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "finish_project")
async def finish_project(callback: CallbackQuery, state: FSMContext):
    """Завершение проекта старт"""
    project_id = int(callback.data.split(":")[1])
    text = "Укажите окончательный размер гонорара"
    kb = inline_kb.home_kb()
    await state.set_state(AdminFSM.royalty_update)
    await state.update_data(project_id=project_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.royalty_update)
async def finish_project(message: Message, state: FSMContext):
    """Завершение проекта финал"""
    if message.text.isdigit():
        state_data = await state.get_data()
        project_id = int(state_data['project_id'])
        text = f"Проект # {project_id} завершён"
        await MyProjectsDAO.change_data(
            project_id=project_id,
            royalty=int(message.text),
            finish_date=datetime.now().date(),
            is_finished=True
        )
        await state.set_state(AdminFSM.home)
    else:
        text = "Нужно ввести целое число"
    kb = inline_kb.home_kb()
    await message.answer(text, reply_markup=kb)
