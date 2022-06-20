import pprint
import requests
import re
import numpy as np

DOMAIN = 'https://api.hh.ru/'

url_vacancies = f'{DOMAIN}vacancies'

PROFF = str(input('Введите название вакансии для поиска:'))
AREA = str(input('Введите название города для поиска:'))
# Задаем списки и переменные
# Список требований к профессиям
list_of_req = []
# Список зарплат
payment = []
# Курс доллараб при желании можно добавить и другие валюты
usd_course = 60
# Параметры поиска профессия и город
params = {
        'text': f'{PROFF} AND {AREA}'
}
# Результат запроса на языке джсон
result = requests.get(url_vacancies, params = params).json()

# Переменная для определения количества вакансий по запросу, для последующего принта
quant_of_vac = result['found']
print(f'Количество вакансий по вашему запросу - {quant_of_vac}')

# Цикл по страницам
for p in range(result['pages']):
    PAGE = f'{p}'
    # Задаем новые параметры для прохода по страницам
    params = {
        'text': f'{PROFF} AND {AREA}',
        'page': f'{PAGE}'
    }
    # Новый резалт с постраничной проходкой
    result = requests.get(url_vacancies, params=params).json()
    # Принтю прогресс, чтобы видеть что ничего не зависло, а программа работает
    print(result['page'] + 1, ' страница просмотрена...')
    # Цикл для прохода по элементам на странице
    for p in range(len(result['items'])):
        # Словарь из нескольких уровней - добираемся до нужных
        items = result['items']

        item_iter = items[p]
        #Переменная для цикла по требованиям
        requirement = item_iter['snippet']['requirement']
        # Переменная для цикла по зарплатам
        salary = item_iter['salary']
        # цикл по зп - часто выдает ошибку о типе объекта зп - тк не у всех зп написана, поэтому если зп не написана - пропускаем
        if salary != None:
            # Цикл по рублю - для доллара еще имеется ниже, при желании можно добавить другие валюты
            if salary['currency'] == 'RUR':
                # не во всех вакансиях указаны суммы от или до - поэтому цикл разделен на части - сильно с математикой не усложнял
                if salary['to'] is None:
                    payment.append(int(salary['from']))
                elif salary['from'] is None:
                    payment.append(int(salary['to']))
                elif salary['from'] is not None and salary['to'] is not None:
                    value_av_one_vac = (salary['to'] + salary['from'])/2
                    payment.append(int(value_av_one_vac))
                else:
                    continue
            # Цикл по доллару, все тоже самое что и у рубля только умножаем на курс валюты установленный в начале
            if salary['currency'] == 'USD':
                if salary['to'] is None:
                    payment.append(int(salary['from'])*usd_course)
                elif salary['from'] is None:
                    payment.append(int(salary['to'])*usd_course)
                elif salary['from'] is not None and salary['to'] is not None:
                    value_av_one_vac = (salary['to'] + salary['from']) / 2
                    payment.append(int(value_av_one_vac)*usd_course)
                else:
                    continue
        # Цикл по требованиям - не у всех требований формат строки - поэтому выдает ошибку иногда, поэтому если не строка - пропускаем
        if type(requirement) == str:
            # разделяем полученную строку по разделителям "." и ","
            list_of_req_split = re.split(",|\.", requirement)
            # Добавляем в один большой список все требования для дальнейшей работы
            for item in range(len(list_of_req_split)):
                list_of_req.append(list_of_req_split[item])
        else:
            continue
# Считаем среднюю зп и принтим ее
avarage_payment = sum(payment)/len(payment)
print(f'Средняя заработная плата по вашему запросу: {avarage_payment} рублей в месяц')
# Удаляем лишние элементы в списке, которые нам мешают выводить корректную информацию по требованиям
# Возможно стоит поместить в циклы для проверки есть ли данные элементы в списке требований, но и так работает
lst1, lst2 = np.unique(list_of_req, return_counts = True)
lst1 = list(lst1)
lst2 = list(lst2)

lst2.pop(lst1.index(''))
lst1.remove('')

lst2.pop(lst1.index(' '))
lst1.remove(' ')

lst2.pop(lst1.index(')'))
lst1.remove(')')

lst2.pop(lst1.index(' Опыт работы с'))
lst1.remove(' Опыт работы с')
# Принтим самое частое требование циклом и удалям только что выведенное на экран из списка, чтобы вывести другие
print('Самые требуемые навыки по вашей вакансии:')

for i in range(5):
    index, max_value = max(enumerate(lst2), key=lambda i_v: i_v[1])
    print(lst1[index], '- встречается в',max_value, 'вакансиях')
    lst1.pop(index)
    lst2.pop(index)

#Возможно стоит




