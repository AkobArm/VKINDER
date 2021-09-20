import json

import sqlalchemy

from functions import *
from models import User, ProfUrls, create_db
from secret import my_token, comm_token, DSN
from vk_class import Kinder, Talk


def search_result_processing(id_, k):
    raw_u = k.users_get(id_)[0]  # полный профиль из результатов поиска
    if check_user(raw_u):
        # новый объект профиля
        new_u = User(user_id=raw_u['id'],
                     first_name=raw_u['first_name'],
                     last_name=raw_u['last_name'],
                     sex=raw_u['sex'],
                     bdate=raw_u['bdate'],
                     city=raw_u['city']['title'])

        # новый объект фоток
        pu = [ProfUrls(user_id=new_u.user_id, url=one_url) for one_url in get_best_prof_photos(k, new_u.user_id)]

        return {'u': new_u, 'pu': pu}
    else:
        return False  # профиль не валидный


def go_go(k, session_maker):
    hi = k.read_msg()
    new_client = hi.user_id
    t = Talk(k, new_client)
    t.write('Привет!')

    resp = k.users_get(new_client)  # профиль пользователя, которому надо найти пару

    u = resp[0]
    t.write(f"Ищем пару для {u['first_name']} {u['last_name']}")
    res = make_search(k, u, t)  # итератор с результатами поиска
    dump_list = []
    for r in res:
        # по айти запрашивает полный профиль, и если он валидный, то добавляет в базу и выводит результат
        if session_maker:
            # если есть доступ к базе - запрос, чтобы избежать повтор
            already_in_db = session_maker().query(User).filter(User.user_id == r['id']).first()
        else:
            already_in_db = False

        if not already_in_db:
            new_id = search_result_processing(r['id'], k)  # запрос инфы нового айди
            if not new_id:  # невалидный результат - пробуем следующий
                continue
            else:
                print(f"Вот, например, {new_id['u']}")  # вывод результатов в консоль
                [print(item) for item in new_id['pu']]

                t.write(f"Вот, например, {new_id['u']}")  # вывод результатов в чат
                [t.write(item) for item in new_id['pu']]

                dump_it(session_maker, new_id['u'], new_id['pu']) # запись в базу, если доступно
                dump_list += [new_id['u'].mk_dict()]

                t.write(f"Выберите 'q' для выхода или 'n' для продолжения")
                q = t.read()
                if q == 'q':
                    t.write(f"Пока, {u['first_name']} {u['last_name']}!")
                    break

    if not session_maker:  # если база недоступна - дамп в файл
        with open("dump_file.json", "a", encoding='utf-8') as f:
            json.dump(dump_list, f)


if __name__ == '__main__':
    try:
        Session = create_db(DSN)
    except sqlalchemy.exc.OperationalError as error_msg:
        print(error_msg)
        Session = False

    kinder = Kinder(token=my_token, c_token=comm_token)
    go_go(kinder, Session)
