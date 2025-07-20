import asyncio
import sqlite3
import logging
import io
from aiogram import Dispatcher, Bot, types, F
from aiogram.filters.command import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from aiogram.fsm.context import FSMContext



logging.basicConfig(level=logging.INFO)
bot = Bot(token="6390375163:AAE8DxzAuLz3WJCHvo4_3uZXORIYSD7EyLE")
dp = Dispatcher()
shablon = FSInputFile("img.png")
conn = sqlite3.connect("TGBOOK.db")
c = conn.cursor()
last_messages = {}

class Bookimage(StatesGroup):
    user_send_message = State()
    current_index_book = State()
    waiting_book_name = State()
    waiting_book_autor = State()
    waiting_book_genre = State()
    waiting_uppdate_text = State()
    waiting_uppdate_img = State()
    waiting_review = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [[types.KeyboardButton(text="Зарегистрироваться", request_contact=True)]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True

    )
    await message.answer("Добро пожаловать в телеграм бот для обмена книгами.\n"
                         "Здесь вы сможете найти литературу которую хотели давно почитать и предложить свой книжный вкус остальным.",
                         reply_markup=keyboard)

@dp.message(F.contact)
async def print_nomber(message:types.Message):
    if message.contact is not None:
        await message.answer("Регистрация прошла успешно")
        phone = str(message.contact.phone_number)
        user_id = int(message.from_user.id)
        
        c.execute("INSERT INTO users (name, id_users) VALUES (?, ?)", (phone, user_id))
        conn.commit()
        kb = [
            [types.KeyboardButton(text="Добавить книгу", callback_data='add_book'),
             types.KeyboardButton(text='Мои книги', callback_data="my_book")],
            [types.KeyboardButton(text="Поиск книги", callback_data='search_book'),
             types.KeyboardButton(text="Избранное", callback_data='reader')]
        ]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True

        )
        await message.answer("🎉 Добро пожаловать в наш бот! 🎉\n\n"
                             "Вы успешно зарегистрированы! Теперь вы можете обмениваться книгами с другими пользователями.\n"
                             "Приятного использования 😊", reply_markup=keyboard)

@dp.message(F.text.lower() == "главное меню")
async def main_menu(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Добавить книгу", callback_data='add_book'),
         types.KeyboardButton(text='Мои книги', callback_data="my_book")],
        [types.KeyboardButton(text="Поиск книги", callback_data='search_book'),
         types.KeyboardButton(text="Избранное", callback_data='reader')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True

    )
    conn.commit()
    await message.answer("Здесь вы сможете найти литературу которую хотели давно почитать и предложить свой книжный вкус остальным.", reply_markup=keyboard)

@dp.message(F.text.lower() == "поиск")
async def search(message: types.Message):
    marup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Название", callback_data="name_book"),
        InlineKeyboardButton(text="Автор", callback_data="autor_book"),
        InlineKeyboardButton(text="Жанр", callback_data="genre_book")
    ]])
    await message.answer("Выберите критерий по которому желаете найти книгу", reply_markup=marup)

@dp.callback_query(lambda call: call.data == "name_book")
async def search_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите название книги")
    await state.set_state(Bookimage.waiting_book_name)

@dp.message(Bookimage.waiting_book_name)
async def waiting_name(message: types.Message, state:FSMContext):
    book_name = message.text
    c.execute('SELECT rowid, name FROM book')
    len_book_name = c.fetchall()
    h = 0
    for i in range(len(len_book_name)):
        if len_book_name[i][1].lower() == book_name.lower():
            await show_book_for_search(message.chat.id, int(len_book_name[i][0]))
            h+=1
    if h == 0:
        await message.answer("Книга с данным названием не найдена")
    await state.clear()

@dp.callback_query(lambda call: call.data == "autor_book")
async def search_autor(call: types.CallbackQuery, state: FSMContext):
    # await call.answer()
    await call.message.answer("Введите автора книги")
    await state.set_state(Bookimage.waiting_book_autor)


@dp.message(Bookimage.waiting_book_autor)
async def waiting_autor(message: types.Message, state:FSMContext):
    book_name = message.text
    c.execute('SELECT rowid, autor FROM book')
    len_book_name = c.fetchall()
    h = 0
    for i in range(len(len_book_name)):
        if len_book_name[i][1].lower() == book_name.lower():
            await show_book_for_search(message.chat.id, int(len_book_name[i][0]))
            h += 1
    if h == 0:
        await message.answer("Книга с данным автором не найдена")
    await state.clear()

@dp.callback_query(lambda call: call.data == "genre_book")
async def search_genre(call: types.CallbackQuery, state: FSMContext):
    # await call.answer()
    await call.message.answer("Введите жанр книги")
    await state.set_state(Bookimage.waiting_book_genre)


@dp.message(Bookimage.waiting_book_genre)
async def waiting_genre(message: types.Message, state:FSMContext):
    book_name = message.text
    c.execute('SELECT rowid, genre FROM book')
    len_book_name = c.fetchall()
    h = 0
    for i in range(len(len_book_name)):
        if len_book_name[i][1].lower() == book_name.lower():
            await show_book_for_search(message.chat.id, int(len_book_name[i][0]))
            h += 1
    if h == 0:
        await message.answer("Книга с данным жанром не найдена")
    await state.clear()


@dp.message(F.text.lower() == "добавить книгу")
async def add_book(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Опубликовать", callback_data='public')],
        [types.KeyboardButton(text="Главное меню")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True

    )
    marup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Проверить описание", callback_data="chek_message")]])
    await message.answer("Введите данные о вашей книге по следующему примеру:\nНазвание книги\nАвтор\nЖанр\nСостояние книги\nКраткое описание",
                         reply_markup=keyboard)
    await bot.send_photo(chat_id=message.chat.id, photo=shablon)

@dp.message(F.text.lower() == "опубликовать")
async def public(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    mes = str(last_messages.get(user_id))
    chek_mess = mes.split("\n")
    if len(chek_mess) == 5:
        await message.answer("отправте фото книги")
        await state.set_state(Bookimage.user_send_message)
    else:
        await message.answer("Пожалуйста, заполните данные по шаблону")

@dp.callback_query(lambda call:call.data == "chek_message")
async def chek_shablon(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    mes = str(last_messages.get(user_id))
    chek_mess = mes.split("\n")
    if len(chek_mess) == 5:
        await call.message.answer("отправте фото книги")
        await state.set_state(Bookimage.user_send_message)
    else: await call.message.answer("Пожалуйста, заполните данные по шаблону")

@dp.message(Bookimage.user_send_message, F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = last_messages.get(user_id).split("\n")
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    image_data = await bot.download_file(file.file_path)
    blob_data = image_data.read()
    text.insert(0, message.from_user.id)
    c.execute("SELECT name FROM users WHERE id_users = ?", (user_id,))
    text.insert(1, c.fetchone()[0])
    text.insert(7, blob_data)
    c.execute(
        "INSERT INTO book (id_user, name_user, name, autor, genre, state, description, image) VALUES (?, ?, ?,?,?,?,?,? )",
        text)
    await message.answer("Благодарим за публикацию")
    await state.clear()

@dp.message(F.text.lower() == "поиск книги")
async def search_book(message: types.Message, state: FSMContext):
    await state.set_state(Bookimage.current_index_book)
    kb = [
        [types.KeyboardButton(text="Предыдущая"), types.KeyboardButton(text="Следующая")],
        [types.KeyboardButton(text="Поиск")],
        [types.KeyboardButton(text="Главное меню")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard = kb,
        resize_keyboard = True
    )
    await message.answer("Найдите интересующую вас книгу", reply_markup=keyboard)
    await show_book(message.chat.id, 0)

async def show_book_for_search(chat_id, index):
    c.execute("SELECT rowid, * FROM book")
    show_kniga = c.fetchall()
    book_data = []
    for i in range(len(show_kniga)):
        if show_kniga[i][0] == index:
            book_data = show_kniga[i]
    image_file = io.BytesIO(book_data[7])
    caption = f"Название: {book_data[3]}\nАвтор: {book_data[4]}\nЖанр: {book_data[5]}\nСостояние: {book_data[8]}\nОписание: {book_data[6]}"
    marup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Связаться", url=f"tg://user?id={book_data[1]}"),InlineKeyboardButton(text="В избранное", callback_data=f"AddReadingBook_{book_data[0]}"), InlineKeyboardButton(text="Отзывы", callback_data=f"review_{book_data[0]}")]])
    await bot.send_photo(photo=BufferedInputFile(image_file.read(), filename='screenshot.png'), caption=caption, chat_id=chat_id, reply_markup=marup)
async def show_book(chat_id, index):
    c.execute("SELECT rowid, * FROM book")
    book_data = c.fetchall()[index]
    image_file = io.BytesIO(book_data[7])
    caption = f"Название: {book_data[3]}\nАвтор: {book_data[4]}\nЖанр: {book_data[5]}\nСостояние: {book_data[8]}\nОписание: {book_data[6]}"
    marup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Связаться", url=f"tg://user?id={book_data[1]}"),InlineKeyboardButton(text="В избранное", callback_data=f"AddReadingBook_{book_data[0]}"), InlineKeyboardButton(text="Отзывы", callback_data=f"review_{book_data[0]}")]])
    await bot.send_photo(photo=BufferedInputFile(image_file.read(), filename='screenshot.png'), caption=caption, chat_id=chat_id, reply_markup=marup)

@dp.callback_query(lambda call: call.data.startswith("review_"))
async def book_review(call: types.CallbackQuery):
    review_data = call.data.split("_")[1]
    c.execute("SELECT review_text FROM review WHERE id_book = ?", (review_data,))
    text = c.fetchall()
    if len(text) != 0:
        for i in range(len(text)):
            await call.message.answer(f"Отзыв №{i+1}:\n{text[i][0]}")
    else: await call.message.answer("У данный публикации нет отзывов")


@dp.callback_query(lambda call: call.data.startswith("AddReadingBook_"))
async def reading_book(call:types.CallbackQuery):
    id_book = call.data.split("_")[1]
    id_user = call.from_user.id
    c.execute("INSERT INTO reading_book (id_user, id_book) VALUES (?, ?)", (id_user, id_book))
    await call.message.answer("Книга добавлена в избранное")

@dp.message(F.text.lower() == "следующая")
async def next_book(message: types.Message, state: FSMContext):
    c.execute("SELECT * FROM book")
    book_data = c.fetchall()
    state_data = await state.get_data()
    current_index = state_data.get('current_index', 0)

    if current_index < len(book_data) - 1:
        current_index += 1
        await state.update_data(current_index=current_index)
        await show_book(message.chat.id, current_index)
    else:
        await message.answer("Это последняя книга.")

@dp.message(F.text.lower() == "предыдущая")
async def previous_book(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    current_index = state_data.get('current_index', 0)

    if current_index > 0:
        current_index -= 1
        await state.update_data(current_index=current_index)
        await show_book(message.chat.id, current_index)
    else:
        await message.answer("Это первая книга.")

@dp.message(F.text.lower() == "мои книги")
async def my_book(message: types.Message):
    chat_id = message.chat.id
    kb = [[types.KeyboardButton(text="Главное меню")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    await message.answer("Просмотрите опубликованные вами книги", reply_markup=keyboard)
    c.execute("SELECT rowid, * FROM book WHERE id_user = ?", (chat_id,))
    book_data = c.fetchall()
    for i in range(len(book_data)):
        image_file = io.BytesIO(book_data[i][7])
        caption = f"Название: {book_data[i][3]}\nАвтор: {book_data[i][4]}\nЖанр: {book_data[i][5]}\nСостояние: {book_data[i][8]}\nОписание: {book_data[i][6]}"
        marup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Удалить", callback_data=f"replace_{book_data[i][0]}"),
             InlineKeyboardButton(text="Редактировать", callback_data=f"refactor_{book_data[i][0]}")]])
        await bot.send_photo(photo=BufferedInputFile(image_file.read(), filename='screenshot.png'), caption=caption,
                             chat_id=chat_id, reply_markup=marup)

@dp.callback_query(lambda call: call.data.startswith("refactor_"))
async def refactor_book(call: types.CallbackQuery):
    book_rewiev = call.data.split("_")[1]
    marup = InlineKeyboardMarkup(inline_keyboard=([[InlineKeyboardButton(text="Текст", callback_data=f"RefactorBookText_{book_rewiev}"),InlineKeyboardButton(text="Фото", callback_data=f"RefactorBookImg_{book_rewiev}")]]))
    await call.message.answer("Что вы желаете исправить?", reply_markup=marup)

@dp.callback_query(lambda call: call.data.startswith("replace_"))
async def replace_book(call:types.CallbackQuery):
    book_replace = call.data.split("_")[1]
    marup = InlineKeyboardMarkup(inline_keyboard=([[InlineKeyboardButton(text="Да", callback_data=f"YesReplace_{book_replace}")]]))
    await call.message.answer("Вы уверены, что желаете удалить публикацию?",reply_markup=marup)

@dp.callback_query(lambda call: call.data.startswith("YesReplace_"))
async def YesReplace(call:types.CallbackQuery):
    id_delete = call.data.split("_")[1]
    c.execute("DELETE FROM book WHERE rowid = ?", (id_delete,))
    await call.message.answer("Ваша публикация успешно удалена")

@dp.callback_query(lambda call: call.data.startswith("RefactorBookText_"))
async def refactor_book_text(call: types.CallbackQuery, state: FSMContext):
    book_text = call.data.split("_")[1]
    await state.update_data(book_text=book_text)
    await call.message.answer(
        "Введите данные о вашей книге по следующему примеру:\nНазвание книги\nАвтор\nЖанр\nСостояние книги\nКраткое описание")
    await state.set_state(Bookimage.waiting_uppdate_text)

@dp.message(Bookimage.waiting_uppdate_text)
async def waiting_name(message: types.Message, state:FSMContext):
    mes = message.text
    data = await state.get_data()
    book_text = data.get('book_text')
    chat_id = message.from_user.id
    chek_mess = mes.split("\n")
    if len(chek_mess) != 5:
        await message.answer("Пожалуйста, заполните данные по шаблону")
    else:
        c.execute("UPDATE book SET name = ?, autor = ?, genre = ?, state = ?, description = ? WHERE rowid = ?" , (chek_mess[0],chek_mess[1],chek_mess[2],chek_mess[3],chek_mess[4], book_text))
        conn.commit()
        await message.answer("Данные о вашей книге были успешно обновлены")
        c.execute("SELECT name, autor, genre, state, description, image FROM book WHERE rowid = ?", (book_text,))
        book_data = c.fetchall()
        image_file = io.BytesIO(book_data[0][5])
        marup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Удалить", callback_data=f"replace_{book_text}"),
             InlineKeyboardButton(text="Редактировать", callback_data=f"refactor_{book_text}")]])
        caption = f"Название: {book_data[0][0]}\nАвтор: {book_data[0][1]}\nЖанр: {book_data[0][2]}\nСостояние: {book_data[0][3]}\nОписание: {book_data[0][4]}"
        await bot.send_photo(photo=BufferedInputFile(image_file.read(), filename='screenshot.png'), caption=caption,
                             chat_id=chat_id, reply_markup=marup)
    await state.clear()

@dp.callback_query(lambda call: call.data.startswith("RefactorBookImg_"))
async def refactor_book_text(call: types.CallbackQuery, state: FSMContext):
    book_img = call.data.split("_")[1]
    await state.update_data(book_img=book_img)
    await call.message.answer("Отправте фото вашей книги")
    await state.set_state(Bookimage.waiting_uppdate_img)

@dp.message(Bookimage.waiting_uppdate_img)
async def waiting_name(message: types.Message, state:FSMContext):
    photo = message.photo[-1]
    chat_id = message.chat.id
    data = await state.get_data()
    book_img = data.get('book_img')
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    image_data = await bot.download_file(file.file_path)
    blob_data = image_data.read()
    c.execute("UPDATE book SET image = ? WHERE rowid = ?", (blob_data, book_img))
    await message.answer("Фото книги было успешно обновлено")
    c.execute("SELECT name, autor, genre, state, description, image FROM book WHERE rowid = ?", (book_img,))
    book_data = c.fetchall()
    image_file = io.BytesIO(book_data[0][5])
    marup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Удалить", callback_data=f"replace_{book_img}"),
         InlineKeyboardButton(text="Редактировать", callback_data=f"refactor_{book_img}")]])
    caption = f"Название: {book_data[0][0]}\nАвтор: {book_data[0][1]}\nЖанр: {book_data[0][2]}\nСостояние: {book_data[0][3]}\nОписание: {book_data[0][4]}"
    await bot.send_photo(photo=BufferedInputFile(image_file.read(), filename='screenshot.png'), caption=caption,
                         chat_id=chat_id, reply_markup=marup)
    await state.clear()

@dp.message(F.text.lower() == "избранное")
async def reading(message: types.Message):
    chat_id = message.chat.id
    c.execute("SELECT rowid, * FROM book")
    kb = [[types.KeyboardButton(text="Главное меню")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    await message.answer("Просмотрите прочитанные вами книги", reply_markup=keyboard)
    c.execute("SELECT rowid, * FROM reading_book WHERE id_user = ?", (chat_id,))
    reading_book_data = c.fetchall()
    for i in range(len(reading_book_data)):
        c.execute("SELECT rowid, * FROM book WHERE rowid = ?", (reading_book_data[i][2],))
        book_data = c.fetchall()
        marup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Связаться", url=f"tg://user?id={book_data[0][1]}"),
        InlineKeyboardButton(text="Оставить отзыв", callback_data=f"AddReview_{book_data[0][0]}_{book_data[0][1]}"),
        InlineKeyboardButton(text="Удалить", callback_data=f"delete_{reading_book_data[i][0]}")
        ]])
        image_file = io.BytesIO(book_data[0][7])
        caption = f"Название: {book_data[0][3]}\nАвтор: {book_data[0][4]}\nЖанр: {book_data[0][5]}\nСостояние: {book_data[0][8]}\nОписание: {book_data[0][6]}"
        await bot.send_photo(photo=BufferedInputFile(image_file.read(), filename='screenshot.png'), caption=caption,
                             chat_id=chat_id, reply_markup=marup)

@dp.callback_query(lambda call: call.data.startswith("delete_"))
async def delete_from_star(call: types.CallbackQuery):
    delete = call.data.split("_")[1]
    marup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Удалить", callback_data=f"YesDelete_{delete}")]])
    await call.message.answer("Вы уверены, что желаете удалить книгу из избранных?", reply_markup=marup)

@dp.callback_query(lambda call: call.data.startswith("YesDelete_"))
async def YesDelete(call: types.CallbackQuery):
    delete = call.data.split("_")[1]
    c.execute("DELETE FROM reading_book WHERE rowid = ?", (delete,))

    await call.message.answer("Публикация удалена из избранных")

@dp.callback_query(lambda call: call.data.startswith("AddReview_"))
async def add_review(call:types.CallbackQuery, state: FSMContext):
    id_book = call.data.split("_")[1]
    id_user = call.data.split("_")[2]
    await state.update_data(id_book=id_book)
    await state.update_data(id_user=id_user)
    await call.message.answer("Напишите ваш отзыв к книге")
    await state.set_state(Bookimage.waiting_review)

@dp.message(Bookimage.waiting_review)
async def waiting_review(message:types.Message, state: FSMContext):
    review_text = message.text
    data = await state.get_data()
    id_book = data.get('id_book')
    data = await state.get_data()
    id_user = data.get('id_user')
    c.execute("INSERT INTO review(id_book, id_user, review_text) VALUES (?,?,?)", (id_book, id_user, review_text))
    await message.answer("Ваш комментарий добавлен")


@dp.message()
async def save_last_message(message: types.Message):
    # Сохраняем последнее сообщение пользователя
    last_messages[message.from_user.id] = message.text

@dp.callback_query()
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


