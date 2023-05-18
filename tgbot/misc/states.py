from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    home = State()
    title = State()
    royalty_create = State()
    project_id = State()
    worktime = State()
    royalty_update = State()
