# Проект Yatube 

Данный проект - это реализация блога с возможностью написать, скорректировать и читать пост, а также подписаться на понравившихся блогеров.

## Установка 

Для корректной работы проекта необходимо: 

*  python версии 3.7. Для его установки в виртуальное окружение, выполните команду:

 ``` 

sudo apt install python3.7-venv 

``` 

* разверните виртуальное окружение 

### * ! не забудьте его активировать 

* установите все зависимости

``` 

pip install -r requirements.txt 

``` 

* Проведите все миграции 

``` 

python3 manage.py migrate 

``` 

* Готово! Теперь можно запустить проект. 

``` 

python3 manage.py runserver 

``` 

## Что может данный проект 

На главной странице - отображает все посты всех авторов.
Возможна регистрация новых пользователей через двойную аутентификацию (через е-мейл).
Дла зарегистрированных пользователей доступна возможность создавать посты и относить их к (тематической) группе постов, а также - подписываться на других авторов. Помимо основной ленты, где отображаются все новые посты во всех блогах, авторизированным пользователям доступна лента подписок: посты только от тех пользователей, на кого они подписались.
Данный проект был создан в целях изучения фреймворка Django.
На нём специально была убрана папка static из гитигнора для того, чтобы развернуть проект с работающей статикой на удаленном сервере.

## Автор проекта
https://github.com/Aenika 