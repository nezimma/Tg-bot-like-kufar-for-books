import sqlite3
#+375445743786
#.execute("SELECT rowid(скрытый парамет с номером)строка FROM таблица")
#.fetchall() выведет все хранящиеся значения в формате [(),()]
#.featchmany() тоже самое, только ограничение по кол-ву
#.featchone() выводит уже кортеж в котором удобно выбирать значения
# table users [name=text, id_users=integer]
# table book [id_user=integer, name_user=text, name=text, autor=text, genre=text, description=text, image=blob, state=TEXT]
# table reading_book [id_user=integer, id_book=integer]
# table review [id_book=integer, id_user=integer, review_text=text]
text = ['Бесконечное лето', 'Советская студия', 'Новелла', '10\\10', 'Семён попадает в детский пионер лагерь и ему предстоит выбраться и вернуться в свое время']
#748256674
conn = sqlite3.connect("TGBOOK.db")
c = conn.cursor()
# with open('img.png', 'rb') as file:
#     image_path = file.read()
# text.append(image_path)
#c.execute("ALTER TABLE book ADD COLUMN state TEXT")
#c.execute("INSERT INTO book (id_user, name_user, name, autor, genre, state, description, image) VALUES (56789, 'kjdsflkjh', ?,?,?,?,?,? )", text )
#c.execute("UPDATE book SET id_user = 748256674 WHERE id_user = 56789")
c.execute("SELECT genre FROM book")
results = c.fetchall()
conn.commit()
# Выводим результаты
print("Результаты из базы данных:")
for row in results:
    print(row)
