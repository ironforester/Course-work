import requests
import time
import json
import datetime
from pprint import pprint
from datetime import datetime
from tqdm import tqdm


def get_biggest_photos():
    '''Функция получения отсортированного по размеру списка с фото'''
    with open('tokenvk.txt', 'r') as f, open('vk_id.txt', 'r') as v:
        access_token = f.read().strip()
        user_id = v.read().strip()
    URL = 'https://api.vk.com/method/photos.get'
    params = {
        'user_ids': user_id,
        'access_token': access_token,
        'v': '5.131',
        'owner_id': '739837048',
        'album_id': '291838858',
        'extended': '1',
        'photo_sizes': '1',
        'count': '5'
    }
    res = requests.get(URL, params=params)
    dic = res.json()['response']['items']
    selected_photos = []
    for photos_info in dic:
        photos_dic = {}
        photos_dic.update(dict(id=photos_info['id'], likes=photos_info['likes']['count'], sizes=photos_info['sizes'],
                               date=photos_info['date']))
        sorted_size = sorted(photos_dic['sizes'], key=lambda x: x['height'])
        del photos_dic['sizes']
        photos_dic.setdefault('url', sorted_size[-1]['url'])
        photos_dic.setdefault('size', sorted_size[-1]['type'])
        selected_photos.append(photos_dic)
    return selected_photos


def date_name_converse():
    '''Функция перевода даты в читабельный формат, присвоения имени фотографии, записи json файла. Поскольку все фото
    были загружены единовременно для целей данной курсовой, а лайков почти нет, добавил последние 2 цифры id фотографии
    к имени'''
    selected_photos = get_biggest_photos()
    json_list = []
    for unix_dates in selected_photos:
        unix_date = int(unix_dates['date'])
        norm_date = str(datetime.fromtimestamp(unix_date))
        unix_dates['date'] = norm_date
    names_list = []
    for name in selected_photos:
        name['file_name'] = str(name['likes']) + '.jpeg'
        names_list.append(name['file_name'])
        if names_list.count(name['file_name']) > 1:
            name['file_name'] = str(name['likes']) + '_' + name['date'][0:10] + '_' + str(name['id'])[-2:] + '.jpeg'
        json_list.append({'file_name': name['file_name'], 'size': name['size']})
    with open('VK_photo.txt', 'w') as outfile:
        json.dump(json_list, outfile)
    return selected_photos


def folder_create (folder_name):
    '''Функция создания папки на ЯД для загрузки фото'''
    with open('tokenyandex.txt', 'r') as f:
        tokenyandex = f.read().strip()
        fold_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': folder_name, "overwrite": "true"}
        headers = {'Content-Type': 'application/json', 'Authorization': tokenyandex}
        folder = requests.put(url=fold_url, headers=headers, params=params)
        if folder.status_code == 201:
            print(f'Папка {folder_name}успешно создана')
        elif folder.status_code == 409:
            print(f'Папка с именем {folder_name} уже существует')
        return folder_name

def photos_upload():
    '''Функция загрузки фотографий на ЯД'''
    selected_photos = date_name_converse()
    folder_name = folder_create('vk_pictures')
    with open('tokenyandex.txt', 'r') as f:
        tokenyandex = f.read().strip()
    headers = {'Content-Type': 'application/json', 'Authorization': tokenyandex}
    upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    for photo in tqdm(selected_photos, desc='Photos loading progress', colour='green', leave=False):
        par = {'path': folder_name+'/'+photo['file_name'], 'url': photo['url'], 'overwrite': 'true'}
        result = requests.post(url=upload_url, headers=headers, params=par)
        result.raise_for_status()
    if result.status_code == 202:
        print('Загрузка проведена успешно')
    else:
        print(f'Ошибка при выполнении загрузки {result.status_code}')
photos_upload()
