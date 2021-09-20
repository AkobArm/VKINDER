def dump_it(session_maker, new_u, pu):
    res = False
    if session_maker:
        session = session_maker()
        session.add(new_u)
        for p in pu:
            session.add(p)
        session.commit()
        res = True
    return res


def make_search(k, u, t):
    sex = make_sex(u['sex'], t)
    birth_year = make_birth_year(u, t)
    city = u['city']['id']

    search_params = {'sort': 0,
                     'is_closed': False,
                     'has_photo': 1,
                     'sex': sex,
                     'birth_year': birth_year,
                     'city': city,
                     'status': 1}

    res = k.search(search_params)

    return res


def check_user(u):
    if u['is_closed']:
        return False
    param_list = ['id', 'first_name', 'last_name', 'sex', 'bdate', 'city']
    for ii in param_list:
        if ii not in u.keys():
            return False
    return True


def best_size(sizes_list):
    type_ = ['s', 'm', 'x', 'o', 'p', 'q', 'r', 'y', 'z', 'w']
    size_ = range(1, len(type_) + 1)
    sizes_rating = dict(zip(type_, size_))
    top_size = sorted(sizes_list, key=(lambda item: sizes_rating[item['type']]), reverse=True)[0]
    return top_size


def get_best_prof_photos(k, id_):
    r = k.get_prof_photos(id_)
    top_3_links = None
    if 'items' in r.keys():
        res = k.get_prof_photos(id_)['items']
        res.sort(key=lambda item: item['likes']['count'], reverse=True)
        top_3 = res[0: min(3, len(res))]
        top_3_links = [best_size(item['sizes'])['url'] for item in top_3]

    return top_3_links


def make_sex(sex, t):
    if sex != 0:
        sex = 3 - sex
    else:
        while sex != 1 or sex != 1:
            sex = int(t.read('какой пол искать? (1 - женский, 2 - мужской)'))
    return sex


def make_birth_year(u, t):
    if 'bdate' not in u.keys():
        birth_year = None
        while not (isinstance(birth_year, int) and 1900 < birth_year < 2021):
            birth_year = int(t.read('Какой год рождения?'))
    elif len(u['bdate'].split('.')) != 3:
        birth_year = None
        while not (isinstance(birth_year, int) and 1900 < birth_year < 2021):
            birth_year = int(t.read('Какой год рождения?'))
    else:
        birth_year = u['bdate'].split('.')[-1]

    return birth_year
