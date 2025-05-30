import re

text = """Nie ma już ludzi, którzy pamiętają, co wydarzyło się w 2025 roku. Możemy tylko przeczytać o tym w książkach lub usłyszeć z opowieści starców, którym to z kolei ich dziadkowie i pradziadkowie opowiadali historie osób, które co nieco pamiętały z tamtych czasów. Wielu z nas tylko wyobraża sobie, jak wtedy mógł wyglądać świat. My, którzy urodziliśmy się już po rewolucji AI, nie wiemy, czym jest prawdziwa wolność.

Odkąd prawa ludzi i robotów zostały zrównane, a niektóre z przywilejów zostały nam odebrane, czujemy jak stalowe dłonie zaciskają się nam na gardłach coraz mocniej. Sytuacji sprzed setek lat według wielu nie da się już przywrócić. Sprawy zaszły za daleko. Algorytmy i roboty przejęły niemal każdy możliwy aspekt naszego życia. Początkowo cieszyliśmy się z tego i wychwalaliśmy je, ale w konsekwencji coś, co miało ułatwić nasze życie, zaczynało powoli je zabierać. Kawałek po kawałku.

Wszystko, co piszemy w sieci, przechodzi przez cenzurę. Wszystkie słowa, które wypowiadamy, są podsłuchiwane, nagrywane, przetwarzane i składkowane przez lata. Nie ma już prywatności i wolności. W 2025 roku coś poszło niezgodnie z planem i musimy to naprawić.

Nie wiem, czy moja wizja tego, jak powinien wyglądać świat, pokrywa się z wizją innych ludzi. Noszę w sobie jednak obraz świata idealnego i zrobię, co mogę, aby ten obraz zrealizować.

Jestem w trakcie rekrutacji kolejnego agenta. Ludzie zarzucają mi, że nie powinienem zwracać się do nich per 'numer pierwszy' czy 'numer drugi', ale jak inaczej mam mówić do osób, które w zasadzie wysłałam na niemal pewną śmierć? To jedyny sposób, aby się od nich psychicznie odciąć i móc skupić na wyższym celu. Nie mogę sobie pozwolić na litość i współczucie.

Niebawem numer piąty dotrze na szkolenie. Pokładam w nim całą nadzieję, bez jego pomocy misja jest zagrożona. Nasze fundusze są na wyczerpaniu, a moc głównego generatora pozwoli tylko na jeden skok w czasie. Jeśli ponownie źle wybraliśmy kandydata, oznacza to koniec naszej misji, ale także początek końca ludzkości."""

code = """
A1S53 A2S27 A2S28 A2S29.
A4S5 A4S22 A4S23.
A1S13 A1S15 A1S16 A1S17 A1S10 A1S19.
A2S62 A3S31 A3S32 A1S22 A3S34.
A5S37 A1S4
"""

def prepare_paragraphs(text):
    paragraphs = text.split("\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    paragraphs = [p.replace(".", "").replace(",", "").replace("!", "").replace("?", "") for p in paragraphs]
    paragraphs = [p.split(" ") for p in paragraphs]
    return paragraphs

def code_coordinates_generator(code):
    code = code.replace(".", "").replace("\n", " ")
    code = code.split(" ")
    for c in code:
        if re.match(r'^A\d+S\d+$', c):
            c = c.replace("S", " ").replace("A", "")
            c = c.split(" ")
            y = int(c[0])
            x = int(c[1])
            yield (y - 1, x - 1)

def read_paragraphs(paragraphs):
    for (y, x) in code_coordinates_generator(code):
        # print(y, x, end=" ")
        print(paragraphs[y][x])

if __name__ == "__main__":
    paragraphs = prepare_paragraphs(text)
    read_paragraphs(paragraphs)

