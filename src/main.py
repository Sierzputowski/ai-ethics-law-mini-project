"""
Analiza ryzyka Human-in-the-Loop (HITL) dla planowania trajektorii robota.

Skrypt generuje deterministyczny zestaw scenariuszy pracy robota, porównuje
warianty nadzoru człowieka i zapisuje wyniki w katalogu `wyniki/`.
"""

from __future__ import annotations

import math
import csv
from dataclasses import dataclass
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - zależy od lokalnej instalacji
    plt = None


KATALOG_PROJEKTU = Path(__file__).resolve().parents[1]
KATALOG_WYNIKOW = KATALOG_PROJEKTU / "wyniki"


@dataclass(frozen=True)
class PolitykaHITL:
    """Konfiguracja sposobu nadzoru człowieka nad trajektorią."""

    nazwa: str
    prog_interwencji: float
    prog_niskiej_pewnosci: float
    redukcja_ryzyka: float
    opoznienie_sekundy: float
    obciazenie_operatora: float
    tryb: str


POLITYKI = [
    PolitykaHITL(
        nazwa="Brak HITL",
        prog_interwencji=1.10,
        prog_niskiej_pewnosci=-0.10,
        redukcja_ryzyka=0.00,
        opoznienie_sekundy=0.0,
        obciazenie_operatora=0.00,
        tryb="autonomia",
    ),
    PolitykaHITL(
        nazwa="HITL informacyjny",
        prog_interwencji=0.68,
        prog_niskiej_pewnosci=0.30,
        redukcja_ryzyka=0.18,
        opoznienie_sekundy=4.0,
        obciazenie_operatora=0.25,
        tryb="monitorowanie",
    ),
    PolitykaHITL(
        nazwa="Prawo weta operatora",
        prog_interwencji=0.56,
        prog_niskiej_pewnosci=0.40,
        redukcja_ryzyka=0.43,
        opoznienie_sekundy=7.0,
        obciazenie_operatora=0.55,
        tryb="weto",
    ),
    PolitykaHITL(
        nazwa="Zatwierdzenie przed ruchem",
        prog_interwencji=0.46,
        prog_niskiej_pewnosci=0.52,
        redukcja_ryzyka=0.64,
        opoznienie_sekundy=12.0,
        obciazenie_operatora=0.85,
        tryb="akceptacja",
    ),
    PolitykaHITL(
        nazwa="Adaptacyjny HITL",
        prog_interwencji=0.52,
        prog_niskiej_pewnosci=0.48,
        redukcja_ryzyka=0.55,
        opoznienie_sekundy=8.5,
        obciazenie_operatora=0.62,
        tryb="ryzyko plus niepewność",
    ),
]


def sigmoid(wartosc: float) -> float:
    return 1 / (1 + math.exp(-wartosc))


Rekordy = list[dict[str, object]]


def generuj_scenariusze() -> Rekordy:
    """Tworzy syntetyczny, ale jawny zestaw scenariuszy testowych."""

    srodowiska = {
        "odseparowane": {"gestosc_ludzi": 0.05, "okluzja": 0.10},
        "wspoldzielone": {"gestosc_ludzi": 0.40, "okluzja": 0.35},
        "zatloczone": {"gestosc_ludzi": 0.75, "okluzja": 0.62},
    }
    predkosci = {"niska": 0.25, "srednia": 0.55, "wysoka": 0.85}
    ladunki = {"lekki": 0.20, "sredni": 0.50, "ciezki": 0.82}
    niepewnosci = {"niska": 0.15, "srednia": 0.42, "wysoka": 0.74}
    nowosci = {"znane": 0.10, "rzadkie": 0.45}

    rekordy = []
    identyfikator = 1
    for nazwa_srodowiska, srodowisko in srodowiska.items():
        for nazwa_predkosci, predkosc in predkosci.items():
            for nazwa_ladunku, ladunek in ladunki.items():
                for nazwa_niepewnosci, niepewnosc in niepewnosci.items():
                    for nazwa_nowosci, nowosc in nowosci.items():
                        ciezkosc_skutku = min(
                            1.0,
                            0.20
                            + 0.38 * predkosc
                            + 0.32 * ladunek
                            + 0.22 * srodowisko["gestosc_ludzi"],
                        )
                        prawdopodobienstwo = sigmoid(
                            -3.1
                            + 2.2 * srodowisko["gestosc_ludzi"]
                            + 1.6 * srodowisko["okluzja"]
                            + 1.7 * predkosc
                            + 1.3 * niepewnosc
                            + 0.9 * nowosc
                        )
                        pewnosc_ai = max(
                            0.03,
                            min(
                                0.99,
                                1.02
                                - 0.55 * niepewnosc
                                - 0.30 * nowosc
                                - 0.20 * srodowisko["okluzja"],
                            ),
                        )
                        ryzyko_bazowe = prawdopodobienstwo * ciezkosc_skutku
                        rekordy.append(
                            {
                                "id_scenariusza": f"S{identyfikator:03d}",
                                "srodowisko": nazwa_srodowiska,
                                "predkosc": nazwa_predkosci,
                                "ladunek": nazwa_ladunku,
                                "niepewnosc": nazwa_niepewnosci,
                                "nowosc_sytuacji": nazwa_nowosci,
                                "gestosc_ludzi": srodowisko["gestosc_ludzi"],
                                "okluzja": srodowisko["okluzja"],
                                "pewnosc_ai": round(pewnosc_ai, 3),
                                "prawdopodobienstwo_incydentu": round(
                                    prawdopodobienstwo, 4
                                ),
                                "ciezkosc_skutku": round(ciezkosc_skutku, 4),
                                "ryzyko_bazowe": round(ryzyko_bazowe, 4),
                            }
                        )
                        identyfikator += 1
    return rekordy


def czy_wymaga_interwencji(
    wiersz: dict[str, object], polityka: PolitykaHITL
) -> bool:
    return bool(
        float(wiersz["ryzyko_bazowe"]) >= polityka.prog_interwencji
        or float(wiersz["pewnosc_ai"]) <= polityka.prog_niskiej_pewnosci
    )


def ocen_polityki(scenariusze: Rekordy) -> Rekordy:
    """Porównuje warianty HITL dla wszystkich scenariuszy."""

    wyniki = []
    for scenariusz in scenariusze:
        for polityka in POLITYKI:
            interwencja = czy_wymaga_interwencji(scenariusz, polityka)
            zmeczenie = 0.18 * polityka.obciazenie_operatora if interwencja else 0.0
            skuteczna_redukcja = max(0.0, polityka.redukcja_ryzyka - zmeczenie)
            ryzyko_bazowe = float(scenariusz["ryzyko_bazowe"])
            ryzyko_resztkowe = ryzyko_bazowe * (
                1 - skuteczna_redukcja if interwencja else 1
            )
            czas = 1.8 + (polityka.opoznienie_sekundy if interwencja else 0.0)
            wyniki.append(
                {
                    "id_scenariusza": scenariusz["id_scenariusza"],
                    "polityka": polityka.nazwa,
                    "tryb": polityka.tryb,
                    "interwencja_operatora": interwencja,
                    "czas_decyzji_s": round(czas, 2),
                    "ryzyko_bazowe": ryzyko_bazowe,
                    "ryzyko_resztkowe": round(ryzyko_resztkowe, 4),
                    "redukcja_wzgledna": round(
                        1 - ryzyko_resztkowe / ryzyko_bazowe, 4
                    ),
                    "pewnosc_ai": scenariusz["pewnosc_ai"],
                    "srodowisko": scenariusz["srodowisko"],
                    "predkosc": scenariusz["predkosc"],
                    "ladunek": scenariusz["ladunek"],
                    "niepewnosc": scenariusz["niepewnosc"],
                    "nowosc_sytuacji": scenariusz["nowosc_sytuacji"],
                }
            )
    return wyniki


def srednia(wartosci: list[float]) -> float:
    return sum(wartosci) / len(wartosci)


def kwantyl(wartosci: list[float], q: float) -> float:
    uporzadkowane = sorted(wartosci)
    pozycja = (len(uporzadkowane) - 1) * q
    dol = math.floor(pozycja)
    gora = math.ceil(pozycja)
    if dol == gora:
        return uporzadkowane[int(pozycja)]
    return uporzadkowane[dol] + (uporzadkowane[gora] - uporzadkowane[dol]) * (
        pozycja - dol
    )


def agreguj_wyniki(wyniki: Rekordy) -> Rekordy:
    polityki = sorted({str(wiersz["polityka"]) for wiersz in wyniki})
    agregat = []
    for polityka in polityki:
        podzbior = [w for w in wyniki if w["polityka"] == polityka]
        ryzyka = [float(w["ryzyko_resztkowe"]) for w in podzbior]
        czasy = [float(w["czas_decyzji_s"]) for w in podzbior]
        interwencje = [1.0 if w["interwencja_operatora"] else 0.0 for w in podzbior]
        redukcje = [float(w["redukcja_wzgledna"]) for w in podzbior]
        agregat.append(
            {
                "polityka": polityka,
                "srednie_ryzyko_resztkowe": round(srednia(ryzyka), 4),
                "mediana_ryzyka_resztkowego": round(kwantyl(ryzyka, 0.5), 4),
                "p95_ryzyka_resztkowego": round(kwantyl(ryzyka, 0.95), 4),
                "sredni_czas_decyzji_s": round(srednia(czasy), 4),
                "odsetek_interwencji": round(srednia(interwencje), 4),
                "srednia_redukcja_wzgledna": round(srednia(redukcje), 4),
            }
        )
    return sorted(agregat, key=lambda w: float(w["srednie_ryzyko_resztkowe"]))


def zbuduj_macierz_zgodnosci() -> Rekordy:
    """Mapa wymagań regulacyjnych na konkretne środki projektowe."""

    rekordy = [
        {
            "obszar": "AI Act art. 9",
            "wymaganie": "Ciągły system zarządzania ryzykiem dla systemu wysokiego ryzyka.",
            "implementacja_w_projekcie": "Rejestr scenariuszy, ocena ryzyka bazowego i resztkowego, porównanie środków redukcji.",
            "luka": "W projekcie to prototyp analityczny, nie pełny proces lifecycle z właścicielami ryzyk.",
        },
        {
            "obszar": "AI Act art. 10",
            "wymaganie": "Jakość danych, reprezentatywność i kontrola błędów danych.",
            "implementacja_w_projekcie": "Jawne parametry scenariuszy: środowisko, okluzja, prędkość, ładunek, niepewność i nowość sytuacji.",
            "luka": "Brak danych z rzeczywistego robota i brak audytu biasu domenowego.",
        },
        {
            "obszar": "AI Act art. 11",
            "wymaganie": "Dokumentacja techniczna umożliwiająca ocenę zgodności.",
            "implementacja_w_projekcie": "README, wygenerowany raport, CSV z wynikami i opis założeń modelu.",
            "luka": "Brak pełnej dokumentacji producenta, wersjonowania modelu i specyfikacji HMI.",
        },
        {
            "obszar": "AI Act art. 12",
            "wymaganie": "Rejestrowanie zdarzeń i możliwość śledzenia działania systemu.",
            "implementacja_w_projekcie": "Wyniki per scenariusz zapisane do CSV, w tym decyzja o interwencji i ryzyko resztkowe.",
            "luka": "Brak strumienia logów z robota, czujników i decyzji operatora w czasie rzeczywistym.",
        },
        {
            "obszar": "AI Act art. 13",
            "wymaganie": "Przejrzystość i instrukcje dla wdrażającego.",
            "implementacja_w_projekcie": "Opis progów, trybów nadzoru i interpretacji wyników w README oraz raporcie.",
            "luka": "Trzeba dodać instrukcję stanowiskową dla operatora i procedury eskalacji.",
        },
        {
            "obszar": "AI Act art. 14",
            "wymaganie": "Skuteczny nadzór człowieka, możliwość monitorowania, interpretacji i przerwania działania.",
            "implementacja_w_projekcie": "Porównanie monitorowania, weta, zatwierdzania i adaptacyjnego HITL.",
            "luka": "Projekt nie waliduje ergonomii HMI ani czasu reakcji realnego operatora.",
        },
        {
            "obszar": "AI Act art. 15",
            "wymaganie": "Dokładność, odporność i cyberbezpieczeństwo.",
            "implementacja_w_projekcie": "Niepewność AI i okluzja zwiększają ryzyko, co uruchamia interwencję.",
            "luka": "Brak testów cyberbezpieczeństwa, odporności na spoofing sensorów i awarii sieci.",
        },
        {
            "obszar": "Rozporządzenie maszynowe 2023/1230",
            "wymaganie": "Ocena ryzyka i redukcja ryzyka dla maszyn, w tym autonomii i funkcji bezpieczeństwa.",
            "implementacja_w_projekcie": "Wniosek: HITL jest środkiem organizacyjno-technicznym, ale nie zastępuje funkcji bezpieczeństwa maszyny.",
            "luka": "Do wdrożenia potrzebna byłaby analiza zgodności CE i normy robotyczne.",
        },
    ]
    return rekordy


def tabela_markdown(ramka: Rekordy) -> str:
    naglowki = list(ramka[0].keys())
    wiersze = [[str(wiersz[naglowek]) for naglowek in naglowki] for wiersz in ramka]
    szerokosci = [
        max(len(str(naglowek)), *(len(wiersz[i]) for wiersz in wiersze))
        for i, naglowek in enumerate(naglowki)
    ]

    def formatuj_wiersz(wartosci: list[str]) -> str:
        komorki = [
            wartosc.ljust(szerokosci[i]) for i, wartosc in enumerate(wartosci)
        ]
        return "| " + " | ".join(komorki) + " |"

    separator = "| " + " | ".join("-" * szerokosc for szerokosc in szerokosci) + " |"
    return "\n".join(
        [formatuj_wiersz(naglowki), separator]
        + [formatuj_wiersz(wiersz) for wiersz in wiersze]
    )


def zapisz_svg_slupki(agregat: Rekordy) -> None:
    dane = sorted(agregat, key=lambda w: float(w["srednie_ryzyko_resztkowe"]))
    szerokosc = 900
    wysokosc = 360
    margines_lewy = 220
    maks = max(float(w["srednie_ryzyko_resztkowe"]) for w in dane)
    elementy = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{szerokosc}" height="{wysokosc}" viewBox="0 0 {szerokosc} {wysokosc}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="24" y="34" font-size="20" font-family="Arial">Ryzyko resztkowe według wariantu HITL</text>',
    ]
    for indeks, wiersz in enumerate(dane):
        y = 70 + indeks * 52
        ryzyko = float(wiersz["srednie_ryzyko_resztkowe"])
        dlugosc = 560 * ryzyko / maks
        elementy.append(
            f'<text x="24" y="{y + 18}" font-size="13" font-family="Arial">{wiersz["polityka"]}</text>'
        )
        elementy.append(
            f'<rect x="{margines_lewy}" y="{y}" width="{dlugosc:.1f}" height="26" fill="#2f6f73"/>'
        )
        elementy.append(
            f'<text x="{margines_lewy + dlugosc + 8:.1f}" y="{y + 18}" font-size="13" font-family="Arial">{ryzyko:.4f}</text>'
        )
    elementy.append("</svg>")
    (KATALOG_WYNIKOW / "ryzyko_resztkowe_polityki.svg").write_text(
        "\n".join(elementy), encoding="utf-8"
    )


def zapisz_svg_kompromis(agregat: Rekordy) -> None:
    szerokosc = 900
    wysokosc = 460
    lewy = 90
    prawy = 840
    gora = 60
    dol = 390
    czasy = [float(w["sredni_czas_decyzji_s"]) for w in agregat]
    ryzyka = [float(w["srednie_ryzyko_resztkowe"]) for w in agregat]
    min_x = min(czasy)
    max_x = max(czasy)
    min_y = min(ryzyka)
    max_y = max(ryzyka)

    def sx(x: float) -> float:
        return lewy + (x - min_x) / (max_x - min_x) * (prawy - lewy)

    def sy(y: float) -> float:
        return dol - (y - min_y) / (max_y - min_y) * (dol - gora)

    elementy = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{szerokosc}" height="{wysokosc}" viewBox="0 0 {szerokosc} {wysokosc}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="24" y="34" font-size="20" font-family="Arial">Kompromis: bezpieczeństwo kontra opóźnienie</text>',
        f'<line x1="{lewy}" y1="{dol}" x2="{prawy}" y2="{dol}" stroke="#333"/>',
        f'<line x1="{lewy}" y1="{gora}" x2="{lewy}" y2="{dol}" stroke="#333"/>',
        f'<text x="330" y="440" font-size="14" font-family="Arial">Średni czas decyzji [s]</text>',
        f'<text x="18" y="230" font-size="14" font-family="Arial" transform="rotate(-90 18,230)">Średnie ryzyko resztkowe</text>',
    ]
    for wiersz in agregat:
        x = sx(float(wiersz["sredni_czas_decyzji_s"]))
        y = sy(float(wiersz["srednie_ryzyko_resztkowe"]))
        elementy.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="#c84b31"/>')
        elementy.append(
            f'<text x="{x + 10:.1f}" y="{y - 8:.1f}" font-size="12" font-family="Arial">{wiersz["polityka"]}</text>'
        )
    elementy.append("</svg>")
    (KATALOG_WYNIKOW / "kompromis_ryzyko_czas.svg").write_text(
        "\n".join(elementy), encoding="utf-8"
    )


def zapisz_svg_heatmapa(wyniki: Rekordy) -> None:
    wysokie = [w for w in wyniki if float(w["ryzyko_bazowe"]) >= 0.45]
    srodowiska = ["odseparowane", "wspoldzielone", "zatloczone"]
    polityki = [p.nazwa for p in POLITYKI]
    heatmapa: dict[tuple[str, str], float] = {}
    for srodowisko in srodowiska:
        for polityka in polityki:
            wartosci = [
                float(w["ryzyko_resztkowe"])
                for w in wysokie
                if w["srodowisko"] == srodowisko and w["polityka"] == polityka
            ]
            heatmapa[(srodowisko, polityka)] = (
                round(srednia(wartosci), 3) if wartosci else 0.0
            )
    szerokosc = 980
    wysokosc = 340
    lewy = 150
    gora = 70
    komorka_w = 145
    komorka_h = 58
    maksimum = max(heatmapa.values())
    minimum = min(heatmapa.values())

    def kolor(wartosc: float) -> str:
        udzial = (wartosc - minimum) / (maksimum - minimum)
        r = int(255)
        g = int(245 - 130 * udzial)
        b = int(185 - 145 * udzial)
        return f"rgb({r},{g},{b})"

    elementy = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{szerokosc}" height="{wysokosc}" viewBox="0 0 {szerokosc} {wysokosc}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="24" y="34" font-size="20" font-family="Arial">Ryzyko w scenariuszach wysokiego ryzyka</text>',
    ]
    for j, kolumna in enumerate(polityki):
        elementy.append(
            f'<text x="{lewy + j * komorka_w + 6}" y="60" font-size="11" font-family="Arial" transform="rotate(-20 {lewy + j * komorka_w + 6},60)">{kolumna}</text>'
        )
    for i, indeks in enumerate(srodowiska):
        y = gora + i * komorka_h
        elementy.append(
            f'<text x="24" y="{y + 34}" font-size="13" font-family="Arial">{indeks}</text>'
        )
        for j, kolumna in enumerate(polityki):
            wartosc = heatmapa[(indeks, kolumna)]
            x = lewy + j * komorka_w
            elementy.append(
                f'<rect x="{x}" y="{y}" width="{komorka_w}" height="{komorka_h}" fill="{kolor(wartosc)}" stroke="white"/>'
            )
            elementy.append(
                f'<text x="{x + 48}" y="{y + 34}" font-size="13" font-family="Arial">{wartosc:.3f}</text>'
            )
    elementy.append("</svg>")
    (KATALOG_WYNIKOW / "heatmapa_wysokiego_ryzyka.svg").write_text(
        "\n".join(elementy), encoding="utf-8"
    )


def zapisz_wykresy(agregat: Rekordy, wyniki: Rekordy) -> None:
    zapisz_svg_slupki(agregat)
    zapisz_svg_kompromis(agregat)
    zapisz_svg_heatmapa(wyniki)
    return


def zapisz_raport(
    scenariusze: Rekordy,
    wyniki: Rekordy,
    agregat: Rekordy,
    zgodnosc: Rekordy,
) -> None:
    najlepsza = agregat[0]
    bazowa = next(w for w in agregat if w["polityka"] == "Brak HITL")
    poprawa = 1 - (
        float(najlepsza["srednie_ryzyko_resztkowe"])
        / float(bazowa["srednie_ryzyko_resztkowe"])
    )

    raport = f"""# Raport z analizy HITL dla planowania trajektorii robota

## Zakres

Analiza porównuje {len(POLITYKI)} wariantów nadzoru człowieka na {len(scenariusze)} deterministycznie wygenerowanych scenariuszach. Scenariusze różnią się gęstością ludzi, okluzją, prędkością robota, masą ładunku, niepewnością percepcji i nowością sytuacji.

## Najważniejsze wyniki

- Najniższe średnie ryzyko resztkowe uzyskała polityka **{najlepsza['polityka']}**: {najlepsza['srednie_ryzyko_resztkowe']:.4f}.
- Względem pełnej autonomii daje to redukcję średniego ryzyka o około **{poprawa:.1%}**.
- Koszt bezpieczeństwa to średni czas decyzji **{najlepsza['sredni_czas_decyzji_s']:.2f} s** oraz interwencja operatora w **{najlepsza['odsetek_interwencji']:.1%}** przypadków.
- Najbardziej restrykcyjny wariant nie zawsze jest najlepszy organizacyjnie: mniejsze ryzyko trzeba zestawić z opóźnieniem, obciążeniem operatora i ryzykiem automatyzacyjnej bierności.

## Tabela porównawcza

{tabela_markdown(agregat)}

## Interpretacja

Wyniki wspierają podejście adaptacyjne: człowiek powinien być włączany tam, gdzie ryzyko bazowe albo niepewność modelu przekraczają ustalone progi. Stałe wymaganie zatwierdzania każdej decyzji daje silną redukcję ryzyka, ale podnosi koszt operacyjny i może obniżyć jakość nadzoru przy długiej pracy.

## Macierz zgodności

{tabela_markdown(zgodnosc)}
"""
    (KATALOG_WYNIKOW / "raport_hitl.md").write_text(raport, encoding="utf-8")


def zapisz_csv(sciezka: Path, rekordy: Rekordy) -> None:
    with sciezka.open("w", newline="", encoding="utf-8") as plik:
        writer = csv.DictWriter(plik, fieldnames=list(rekordy[0].keys()))
        writer.writeheader()
        writer.writerows(rekordy)


def main() -> None:
    KATALOG_WYNIKOW.mkdir(exist_ok=True)
    scenariusze = generuj_scenariusze()
    wyniki = ocen_polityki(scenariusze)
    agregat = agreguj_wyniki(wyniki)
    zgodnosc = zbuduj_macierz_zgodnosci()

    zapisz_csv(KATALOG_WYNIKOW / "scenariusze.csv", scenariusze)
    zapisz_csv(KATALOG_WYNIKOW / "wyniki_polityk_hitl.csv", wyniki)
    zapisz_csv(KATALOG_WYNIKOW / "podsumowanie_polityk.csv", agregat)
    zapisz_csv(KATALOG_WYNIKOW / "macierz_zgodnosci_ai_act.csv", zgodnosc)

    zapisz_wykresy(agregat, wyniki)
    zapisz_raport(scenariusze, wyniki, agregat, zgodnosc)

    print("Wygenerowano analizę HITL i zapisano artefakty w katalogu 'wyniki/'.")
    print(tabela_markdown(agregat))


if __name__ == "__main__":
    main()
