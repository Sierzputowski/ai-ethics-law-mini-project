"""
Analiza ryzyka Human-in-the-Loop (HITL) dla planowania trajektorii manipulatora
przemysłowego.

Skrypt generuje deterministyczny zestaw scenariuszy pracy robota, porównuje
warianty nadzoru człowieka i zapisuje wyniki w katalogu `wyniki/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


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
    return float(1 / (1 + np.exp(-wartosc)))


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
    return float(np.mean(wartosci))


def kwantyl(wartosci: list[float], q: float) -> float:
    return float(np.quantile(wartosci, q))


def agreguj_wyniki(wyniki: Rekordy) -> Rekordy:
    ramka = pd.DataFrame(wyniki)
    ramka["interwencja_operatora"] = ramka["interwencja_operatora"].astype(float)

    agregat = (
        ramka.groupby("polityka", as_index=False)
        .agg(
            srednie_ryzyko_resztkowe=("ryzyko_resztkowe", "mean"),
            mediana_ryzyka_resztkowego=("ryzyko_resztkowe", "median"),
            p95_ryzyka_resztkowego=(
                "ryzyko_resztkowe",
                lambda seria: seria.quantile(0.95),
            ),
            sredni_czas_decyzji_s=("czas_decyzji_s", "mean"),
            odsetek_interwencji=("interwencja_operatora", "mean"),
            srednia_redukcja_wzgledna=("redukcja_wzgledna", "mean"),
        )
        .round(4)
        .sort_values("srednie_ryzyko_resztkowe")
    )
    return agregat.to_dict("records")


def zbuduj_macierz_zgodnosci() -> Rekordy:
    """Mapa wymagań regulacyjnych na konkretne środki projektowe."""

    rekordy = [
        {
            "obszar": "AI Act art. 9",
            "wymaganie": "Ciągły system zarządzania ryzykiem dla systemu wysokiego ryzyka.",
            "implementacja_w_projekcie": "Rejestr scenariuszy, ocena ryzyka bazowego i resztkowego, porównanie środków redukcji.",
            "luka": "W projekcie to prototyp analityczny, nie pełny proces lifecycle z właścicielami ryzyk, przeglądami i akceptacją ryzyk.",
        },
        {
            "obszar": "AI Act art. 10",
            "wymaganie": "Jakość danych, reprezentatywność i kontrola błędów danych.",
            "implementacja_w_projekcie": "Jawne parametry scenariuszy: środowisko, okluzja, prędkość, ładunek, niepewność i nowość sytuacji.",
            "luka": "Brak logów z realnego manipulatora, brak danych o awariach sensorów i brak walidacji na rozkładzie z hali produkcyjnej.",
        },
        {
            "obszar": "AI Act art. 11",
            "wymaganie": "Dokumentacja techniczna umożliwiająca ocenę zgodności.",
            "implementacja_w_projekcie": "README, wygenerowany raport, CSV z wynikami i opis założeń modelu.",
            "luka": "Brak pełnej dokumentacji producenta, wersjonowania modelu, specyfikacji HMI i formalnego opisu granic systemu.",
        },
        {
            "obszar": "AI Act art. 12",
            "wymaganie": "Rejestrowanie zdarzeń i możliwość śledzenia działania systemu.",
            "implementacja_w_projekcie": "Wyniki per scenariusz zapisane do CSV, w tym decyzja o interwencji i ryzyko resztkowe.",
            "luka": "Brak strumienia logów z robota, czujników, planera trajektorii i decyzji operatora w czasie rzeczywistym.",
        },
        {
            "obszar": "AI Act art. 13",
            "wymaganie": "Przejrzystość i instrukcje dla wdrażającego.",
            "implementacja_w_projekcie": "Opis progów, trybów nadzoru i interpretacji wyników w README oraz raporcie.",
            "luka": "Trzeba dodać instrukcję stanowiskową dla operatora, opis ograniczeń modelu i procedury eskalacji.",
        },
        {
            "obszar": "AI Act art. 14",
            "wymaganie": "Skuteczny nadzór człowieka, możliwość monitorowania, interpretacji i przerwania działania.",
            "implementacja_w_projekcie": "Porównanie monitorowania, weta, zatwierdzania i adaptacyjnego HITL oraz analiza przeciążenia operatora.",
            "luka": "Projekt nie waliduje ergonomii HMI, czasu reakcji realnego operatora ani jakości poprawek trajektorii.",
        },
        {
            "obszar": "AI Act art. 15",
            "wymaganie": "Dokładność, odporność i cyberbezpieczeństwo.",
            "implementacja_w_projekcie": "Niepewność AI i okluzja zwiększają ryzyko, co uruchamia interwencję.",
            "luka": "Brak testów cyberbezpieczeństwa, odporności na spoofing sensorów i awarii sieci.",
        },
        {
            "obszar": "AI Act role operatorów",
            "wymaganie": "Rozróżnienie obowiązków dostawcy, producenta produktu i wdrażającego system AI.",
            "implementacja_w_projekcie": "Wnioski rozdzielają odpowiedzialność: projektant planera, integrator maszyny, organizacja wdrażająca i przeszkolony operator.",
            "luka": "Brak kontraktowej alokacji obowiązków i brak formalnej procedury przekazania systemu do użytkowania.",
        },
        {
            "obszar": "Rozporządzenie maszynowe 2023/1230",
            "wymaganie": "Ocena ryzyka i redukcja ryzyka dla maszyn, w tym autonomii i funkcji bezpieczeństwa.",
            "implementacja_w_projekcie": "Wniosek: HITL jest środkiem organizacyjno-technicznym, ale nie zastępuje osłon, stref, ograniczeń prędkości i awaryjnego zatrzymania.",
            "luka": "Do wdrożenia potrzebna byłaby analiza zgodności CE, ocena ryzyka maszyny i dokumentacja techniczna producenta.",
        },
        {
            "obszar": "ISO/TS 15066 i normy robotyczne",
            "wymaganie": "Dla pracy blisko ludzi trzeba analizować ograniczenia kontaktu, prędkości, siły, separacji i organizacji stanowiska.",
            "implementacja_w_projekcie": "Scenariusze z większą gęstością ludzi i okluzją pokazują, kiedy nadzór człowieka musi być silniejszy.",
            "luka": "Brak pomiarów sił, dystansów, czasów zatrzymania i pełnej walidacji stanowiska.",
        },
    ]
    return rekordy


def zbuduj_rekomendacje_polityk() -> Rekordy:
    """Rekomenduje politykę HITL dla klas sytuacji, nie tylko globalnie."""

    return [
        {
            "sytuacja": "Strefa częściowo odseparowana, znane trajektorie, niska niepewność AI",
            "rekomendowana_polityka": "HITL informacyjny albo prawo weta operatora",
            "uzasadnienie": "Ryzyko dotyczy głównie mienia i przestoju, więc wystarcza monitorowanie z możliwością reakcji bez blokowania każdej trajektorii.",
            "warunek_brzegowy": "Operator musi widzieć powód ostrzeżenia i mieć prostą możliwość zatrzymania albo korekty trajektorii.",
        },
        {
            "sytuacja": "Strefa częściowo odseparowana, wysoka okluzja albo niska pewność percepcji",
            "rekomendowana_polityka": "Adaptacyjny HITL",
            "uzasadnienie": "Eskalacja tylko przy wysokim ryzyku lub niskiej pewności zmniejsza ryzyko bez stałego przeciążania operatora.",
            "warunek_brzegowy": "Progi eskalacji muszą być audytowalne i zapisane w dokumentacji technicznej.",
        },
        {
            "sytuacja": "Rzadkie, nowe lub nietypowe zadanie manipulacyjne",
            "rekomendowana_polityka": "Zatwierdzenie przed ruchem",
            "uzasadnienie": "Przed wykonaniem nieznanej trajektorii operator powinien móc sprawdzić plan i wprowadzić korektę.",
            "warunek_brzegowy": "Nie powinno to być domyślne dla każdej decyzji, bo długotrwale tworzy ryzyko przeciążenia.",
        },
        {
            "sytuacja": "Praca blisko ludzi albo możliwość kolizji z człowiekiem",
            "rekomendowana_polityka": "Adaptacyjny HITL plus niezależne funkcje bezpieczeństwa maszyny",
            "uzasadnienie": "Problem prawny przechodzi z ryzyka produkcyjnego w ryzyko zdrowia i bezpieczeństwa, więc sam człowiek w pętli nie wystarcza.",
            "warunek_brzegowy": "Konieczne są osłony, strefy, ograniczenia prędkości, awaryjne zatrzymanie, walidacja HMI i analiza zgodności maszynowej.",
        },
        {
            "sytuacja": "Jeden operator nadzoruje wiele robotów",
            "rekomendowana_polityka": "Adaptacyjny HITL z limitami obciążenia",
            "uzasadnienie": "Wiele robotów zwiększa liczbę alarmów i decyzji, więc formalny nadzór może stać się pozorny.",
            "warunek_brzegowy": "System powinien mieć limity liczby równoległych eskalacji i procedurę przejęcia przez drugiego operatora.",
        },
    ]


def analizuj_obciazenie_operatora(agregat: Rekordy) -> Rekordy:
    """Porównuje skutki nadzoru jednego manipulatora i wielu manipulatorów."""

    modele = [
        {
            "model_nadzoru": "jeden_operator_jeden_robot",
            "mnoznik_zmeczenia": 1.00,
            "mnoznik_czasu": 1.00,
            "opis": "Operator obserwuje jeden manipulator i ma czas na korektę trajektorii.",
        },
        {
            "model_nadzoru": "jeden_operator_wiele_robotow",
            "mnoznik_zmeczenia": 1.35,
            "mnoznik_czasu": 1.18,
            "opis": "Operator obsługuje kilka manipulatorów, więc rośnie opóźnienie i ryzyko automatyzacyjnej bierności.",
        },
    ]

    wynik = []
    for wiersz in agregat:
        for model in modele:
            odsetek_interwencji = float(wiersz["odsetek_interwencji"])
            przeciazenie = min(
                1.0, odsetek_interwencji * float(model["mnoznik_zmeczenia"])
            )
            kara_ryzyka = 1 + 0.18 * max(0.0, przeciazenie - 0.35)
            wynik.append(
                {
                    "polityka": wiersz["polityka"],
                    "model_nadzoru": model["model_nadzoru"],
                    "opis": model["opis"],
                    "skorygowane_ryzyko": round(
                        float(wiersz["srednie_ryzyko_resztkowe"]) * kara_ryzyka,
                        4,
                    ),
                    "skorygowany_czas_decyzji_s": round(
                        float(wiersz["sredni_czas_decyzji_s"])
                        * float(model["mnoznik_czasu"]),
                        4,
                    ),
                    "indeks_przeciazenia_operatora": round(przeciazenie, 4),
                    "interpretacja": (
                        "wymaga limitów eskalacji"
                        if przeciazenie >= 0.5
                        else "akceptowalne przy przeszkolonym operatorze"
                    ),
                }
            )
    return wynik


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
    dane = pd.DataFrame(agregat).sort_values("srednie_ryzyko_resztkowe")

    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.barh(dane["polityka"], dane["srednie_ryzyko_resztkowe"], color="#2f6f73")
    ax.invert_yaxis()
    ax.set_title("Ryzyko resztkowe według wariantu HITL")
    ax.set_xlabel("Średnie ryzyko resztkowe")
    ax.grid(axis="x", alpha=0.25)
    for indeks, ryzyko in enumerate(dane["srednie_ryzyko_resztkowe"]):
        ax.text(float(ryzyko) + 0.006, indeks, f"{ryzyko:.4f}", va="center")
    fig.tight_layout()
    fig.savefig(KATALOG_WYNIKOW / "ryzyko_resztkowe_polityki.svg")
    plt.close(fig)


def zapisz_svg_kompromis(agregat: Rekordy) -> None:
    dane = pd.DataFrame(agregat)

    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.scatter(
        dane["sredni_czas_decyzji_s"],
        dane["srednie_ryzyko_resztkowe"],
        s=70,
        color="#c84b31",
    )
    for _, wiersz in dane.iterrows():
        ax.annotate(
            str(wiersz["polityka"]),
            (
                float(wiersz["sredni_czas_decyzji_s"]),
                float(wiersz["srednie_ryzyko_resztkowe"]),
            ),
            xytext=(7, 5),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_title("Kompromis: bezpieczeństwo kontra opóźnienie")
    ax.set_xlabel("Średni czas decyzji [s]")
    ax.set_ylabel("Średnie ryzyko resztkowe")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(KATALOG_WYNIKOW / "kompromis_ryzyko_czas.svg")
    plt.close(fig)


def zapisz_svg_heatmapa(wyniki: Rekordy) -> None:
    ramka = pd.DataFrame(wyniki)
    wysokie = ramka[ramka["ryzyko_bazowe"] >= 0.45]
    heatmapa = (
        wysokie.pivot_table(
            index="srodowisko",
            columns="polityka",
            values="ryzyko_resztkowe",
            aggfunc="mean",
        )
        .reindex(index=["odseparowane", "wspoldzielone", "zatloczone"])
        .reindex(columns=[p.nazwa for p in POLITYKI])
        .fillna(0.0)
        .round(3)
    )

    fig, ax = plt.subplots(figsize=(9.8, 3.6))
    obraz = ax.imshow(heatmapa.to_numpy(), cmap="YlOrRd", aspect="auto")
    ax.set_title("Ryzyko w scenariuszach wysokiego ryzyka")
    ax.set_xticks(np.arange(len(heatmapa.columns)), labels=heatmapa.columns)
    ax.set_yticks(np.arange(len(heatmapa.index)), labels=heatmapa.index)
    ax.tick_params(axis="x", labelrotation=20)
    for i in range(len(heatmapa.index)):
        for j in range(len(heatmapa.columns)):
            ax.text(j, i, f"{heatmapa.iloc[i, j]:.3f}", ha="center", va="center")
    fig.colorbar(obraz, ax=ax, label="Średnie ryzyko resztkowe")
    fig.tight_layout()
    fig.savefig(KATALOG_WYNIKOW / "heatmapa_wysokiego_ryzyka.svg")
    plt.close(fig)


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
    rekomendacje: Rekordy,
    obciazenie: Rekordy,
) -> None:
    najlepsza = agregat[0]
    bazowa = next(w for w in agregat if w["polityka"] == "Brak HITL")
    poprawa = 1 - (
        float(najlepsza["srednie_ryzyko_resztkowe"])
        / float(bazowa["srednie_ryzyko_resztkowe"])
    )

    raport = f"""# Raport z analizy HITL dla planowania trajektorii manipulatora przemysłowego

## Zakres

Analiza dotyczy manipulatora przemysłowego pracującego w hali produkcyjnej, w strefie częściowo odseparowanej. AI wybiera trajektorię ramienia robota. Główne szkody w scenariuszu bazowym to uszkodzenie mienia i przestój produkcji, ale analiza wskazuje też, co zmieniłaby praca blisko ludzi.

Analiza porównuje {len(POLITYKI)} wariantów nadzoru człowieka na {len(scenariusze)} deterministycznie wygenerowanych scenariuszach. Scenariusze różnią się gęstością ludzi, okluzją, prędkością robota, masą ładunku, niepewnością percepcji i nowością sytuacji.

## Najważniejsze wyniki

- Najniższe średnie ryzyko resztkowe uzyskała polityka **{najlepsza['polityka']}**: {najlepsza['srednie_ryzyko_resztkowe']:.4f}.
- Względem pełnej autonomii daje to redukcję średniego ryzyka o około **{poprawa:.1%}**.
- Koszt bezpieczeństwa to średni czas decyzji **{najlepsza['sredni_czas_decyzji_s']:.2f} s** oraz interwencja operatora w **{najlepsza['odsetek_interwencji']:.1%}** przypadków.
- Najbardziej restrykcyjny wariant nie zawsze jest najlepszy organizacyjnie: mniejsze ryzyko trzeba zestawić z opóźnieniem, obciążeniem operatora i ryzykiem automatyzacyjnej bierności.

## Tabela porównawcza

{tabela_markdown(agregat)}

## Interpretacja

Wyniki nie prowadzą do jednej uniwersalnej polityki. Dla znanych trajektorii w częściowo odseparowanej strefie wystarczające może być prawo weta albo HITL informacyjny. Dla wysokiej okluzji, niskiej pewności percepcji lub nietypowych zadań uzasadniony jest adaptacyjny HITL albo zatwierdzenie przed ruchem. Jeżeli manipulator pracowałby blisko ludzi, problem zmieniłby charakter: ryzyko zdrowia i bezpieczeństwa wymagałoby nie tylko HITL, ale też niezależnych funkcji bezpieczeństwa maszyny.

Pozorny nadzór człowieka jest realnym ryzykiem etycznym i prawnym. Operator przeszkolony nadal może być przeciążony, szczególnie gdy nadzoruje wiele robotów. Wtedy odpowiedzialność nie może być przerzucana wyłącznie na operatora: dostawca planera, integrator maszyny i organizacja wdrażająca muszą zapewnić interpretowalne alarmy, możliwość korekty trajektorii, limity równoległych interwencji i pełne logowanie decyzji.

## Rekomendacje zależne od sytuacji

{tabela_markdown(rekomendacje)}

## Nadzór jednego i wielu robotów

{tabela_markdown(obciazenie)}

## Macierz zgodności

{tabela_markdown(zgodnosc)}
"""
    (KATALOG_WYNIKOW / "raport_hitl.md").write_text(raport, encoding="utf-8")


def zapisz_csv(sciezka: Path, rekordy: Rekordy) -> None:
    pd.DataFrame(rekordy).to_csv(sciezka, index=False, encoding="utf-8")


def main() -> None:
    KATALOG_WYNIKOW.mkdir(exist_ok=True)
    scenariusze = generuj_scenariusze()
    wyniki = ocen_polityki(scenariusze)
    agregat = agreguj_wyniki(wyniki)
    zgodnosc = zbuduj_macierz_zgodnosci()
    rekomendacje = zbuduj_rekomendacje_polityk()
    obciazenie = analizuj_obciazenie_operatora(agregat)

    zapisz_csv(KATALOG_WYNIKOW / "scenariusze.csv", scenariusze)
    zapisz_csv(KATALOG_WYNIKOW / "wyniki_polityk_hitl.csv", wyniki)
    zapisz_csv(KATALOG_WYNIKOW / "podsumowanie_polityk.csv", agregat)
    zapisz_csv(KATALOG_WYNIKOW / "macierz_zgodnosci_ai_act.csv", zgodnosc)
    zapisz_csv(KATALOG_WYNIKOW / "rekomendacje_polityk.csv", rekomendacje)
    zapisz_csv(KATALOG_WYNIKOW / "analiza_obciazenia_operatora.csv", obciazenie)

    zapisz_wykresy(agregat, wyniki)
    zapisz_raport(scenariusze, wyniki, agregat, zgodnosc, rekomendacje, obciazenie)

    print("Wygenerowano analizę HITL i zapisano artefakty w katalogu 'wyniki/'.")
    print(tabela_markdown(agregat))


if __name__ == "__main__":
    main()
