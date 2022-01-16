# Noise Crypter
## Введение
Это имплементация моего собственного симметричного алгоритма шифрации на основе генератора псевдо-случайных чисел (ГПСЧ).

Сам алгоритм я придумал лет 10-12 назад и первая реализация была написана на Java. Однако она к сожалению не сохранилась.
Единственное что я нашёл - более поздние наработки под C# и документ с попыткой анализа криптографической стойкости:
[документ](https://docs.google.com/document/d/1MI2j9nXyF6v-li8H46Dzcm_RTsFH2muz8ekCamvwotg/edit)

Кода на C# тоже не нашёл :( Но это не важно, потому что я всегда могу написать новый :)


## Алгоритм
В основе алгоритма лежит идея синхронных ГПСЧ - при шифрации и дешифрации используется один и тот же ГПСЧ инициализируемый одним и тем же значением, которое в данном алгоритме является ключом. Назовём этот генератор ключевым. Так же при шифрации используется второй ГПСЧ, инициализируемый случайным значением (например текущим временем). Он используется для создания зашумления, благодаря чему каждый шифротекст оказывается уникальным. Назовём его зашумляющим.

В качестве ГПСЧ я рекомендую [вихри Мерсенна](https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D1%85%D1%80%D1%8C_%D0%9C%D0%B5%D1%80%D1%81%D0%B5%D0%BD%D0%BD%D0%B0). Хоть в общем случае они не являются криптостойкими, но для получения ключа ГПСЧ нужно получить значительное колличество сгенерированных ГПСЧ чисел, которые в шифротексте созданном данным алгоритмом получить невозможно.
Кроме того в питоне модуль Random работает именно на вихрях Мерсенна, что так же облегчает задачу написания алгоритма.

Шифротекст представляет собой последовательность кадров произвольной длинны, состоящих из N бит заголовка и K бит тела. Число K записывается в заголовке. Соответственно длинна тела ограничена длинной заголовка.
Пример битовых записей с заголовком из 2 бит:

[01] [x]

[10] [xx]

[11] [xxx]

Здесь x - биты данных.

Как происходит шифрация:
1. Ключевой ГПСЧ инициализируется ключом
2. Зашумляющий ГПСЧ инициализируется случайным значением
3. Входное сообщение разбивается на поток отдельных битов.
4. Ключевой ГПСЧ генерирует длинну заголовка в битах K. В текущей реализации от 2 до 7 по умолчанию.
5. Зашумляющий ГПСЧ генерирует длинну тела в битах K. В текущей реализации не менее 1 (но возможно стоит сделать от 0)
6. В шифротекст записывается заголовок из N бит, содержащих бинарное представление числа K
7. В шифротекст последовательно записывается K бит исходного сообщения
    1. Каждый бит перед записью подвергается XOR операции с битом, сгенерированным ключевым ГПСЧ
8. пока во входном потоке есть биты - повторяются шаги 4-7
9. по завершении входного сообщения в шифротекст дописывается заголовок в K бит с нулевым значением.
10. оставшиеся биты так же заполняются нулями до достижения конца байта

Как происходит дешифрация:
1. Ключевой ГПСЧ инициализируется ключом
2. Входной шифротекст разбивается на поток отдельных битов.
3. Ключевой ГПСЧ генерирует длинну заголовка в битах K.
4. Из шифротекста читается K бит, которые являются длинной тела K.
5. Если K равно 0, то сообщение закончено.
6. Из шифротекста последовательно читается K бит
    1. Каждый бит подвергается XOR операции с битом, сгенерированным ключевым ГПСЧ, после чего добавляется к расшифрованному сообщению.
7. пока во входном потоке есть биты и заголовок не равен нулю - повторяются шаги 4-6

Успешная расшифровка сообщения упирается именно в сонхронность: значения из ключевого ГПСЧ при шифрации и дешифрации должны браться в одинаковом порядке.


## Свойства алгоритма
Главным свойством алгоритма является то, что шифротексты, созданные с его помощью, будут разными даже при одинаковом сообщении и ключе. По факту зашифрованные сооющения выглядят как поток случайных битов. Что так же можно использовать для их маскировки (хотя это наверное применимо к любым шифровкам)

Однако такие эффекты достигаются ценой увеличения длинны сообщения. В зависимости от настроек это уведичение может достигать 200%, что может быть не всегда приемлемо.

Алгоритм является симметричным - для дешифрации нужен тот же ключ что и для шифрации. Следовательно передающая и принимающая стороны должны предварительно получить общий ключ используя безопасные каналы связи.


## Дополнения
В текущей версии отсутствует XOR-шифрация битов заголовка, однако её можно ввести для большей надёжности.

Длинна ключа, которая в вихре Мерсенна может быть очень болшьшой, может быть неограниченно увеличена путём добавления нескольких ключевых ГПСЧ, которые будут использоваться поочерёдно в процессе шифрации. При этом биты ключа будут использоваться при шифрации равномерно, что так же положительно скажется на стойкости алгоритма (нельзя подобрать только ЧАСТЬ ключа)


## Безопасность
Криптостойкость алгоритма я уже рассматривал в [документе](https://docs.google.com/document/d/1MI2j9nXyF6v-li8H46Dzcm_RTsFH2muz8ekCamvwotg/edit) выше, пока не вижу смысла переписывать те же рассуждения сюда.









