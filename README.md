# TreesLeaves

Для работы необходимы [Python 3.7](https://www.python.org/downloads/) и [MongoDB 4](https://docs.mongodb.com/manual/installation/)

##### Установка зависимостей
```
pip3 install -r requirements.txt
```

##### Настройки
Файл настроек - app/config.py.

##### Старт
```
python3 start.py
```

## API
#### New
> Добавляет новый документ в базу данных и возвращает строковое представление ObjectId
```
GET /new
```

Поддерживает следующие параметры (можно использовать несколько):

###### Text [**required**]
```
GET /new?text=test
```

###### Parent
```
GET /new?text=testNumTwo&parent=5cc05cee9202caf5752bd7db
```
#### Search
> Производит полнотекстовый поиск по документам. Возвращает документы с полем *parents*, содержащим ObjectId всех элементов родителей
```
GET /search
```

Поддерживает следующие параметры:

###### Text [**required**]
```
GET /search?text=test
```

#### Get
> Возвращает документ с полем *parents*, содержащим ObjectId всех элементов родителей
```
GET /get
```

Поддерживает следующие параметры:

###### id [**required**]
```
GET /get?id=5cc05cee9202caf5752bd7db
```
