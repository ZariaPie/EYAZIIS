from collections import Counter

russian = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й',
           'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф',
           'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я']

english = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
           'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
           'w', 'x', 'y', 'z']


def lang(text: str):
    counter = Counter(text.lower())

    russian_count = 0
    for letter in russian:
        russian_count += counter[letter]

    english_count = 0
    for letter in english:
        english_count += counter[letter]

    if russian_count > english_count:
        return "Russian"
    elif russian_count < english_count:
        return "English"
    else:
        return "Unable to recognize"
