# Human-in-the-Loop Decision Making in AI-Based Robotic Trajectory Planning

**Autor:** Bartosz Sierzputowski, nr indeksu: 266599

**Temat:** temat własny, potwierdzony z prowadzącym: *Human-in-the-Loop Decision Making in AI-Based Robotic Trajectory Planning: Risk Analysis and AI Act Compliance*

**Kurs:** Aspekty prawne, społeczne i etyczne w AI, Politechnika Wrocławska, semestr letni 2025/2026

## Cel projektu

Projekt analizuje, jak różne warianty nadzoru człowieka nad systemem AI wybierającym trajektorię manipulatora przemysłowego wpływają na ryzyko resztkowe, opóźnienie decyzji, obciążenie operatora i zgodność z wymaganiami AI Act. Scenariuszem bazowym jest ramię robota pracujące w hali produkcyjnej, w strefie częściowo odseparowanej od ludzi.

Mini-projekt nie buduje realnego sterownika robota. Tworzy odtwarzalny model analityczny, który porównuje polityki Human-in-the-Loop (HITL) w syntetycznych scenariuszach o różnej gęstości ludzi, prędkości ruchu, okluzji, ładunku, niepewności percepcji i nowości sytuacji.

Główne pytanie badawcze brzmi: w jakich sytuacjach dana polityka HITL jest uzasadniona prawnie i etycznie, a kiedy „człowiek w pętli” staje się tylko formalnym przeniesieniem odpowiedzialności na operatora?

## Powiązanie z projektem grupowym

Projekt grupowy dotyczy wyznaczania ścieżek dla robotów przemysłowych. Mini-projekt wspiera go przez analizę możliwych ograniczeń prawnych i etycznych dla systemu AI planującego trajektorie manipulatora. Najważniejsze powiązanie nie polega na poprawie algorytmu planowania, ale na sprawdzeniu, kiedy taki algorytm wymaga nadzoru człowieka, dokumentacji, logowania, oceny ryzyka i zgodności z regulacjami dotyczącymi systemów AI oraz maszyn.

## Wymagania

Projekt jest zarządzany przez `uv` i wymaga Pythona 3.11 lub nowszego. Zależności są opisane w `pyproject.toml`, a ich wersje są blokowane w `uv.lock`.

Główne biblioteki użyte w analizie:

- `numpy` - obliczenia numeryczne, funkcja sigmoid, średnie i kwantyle,
- `pandas` - tabele wyników, agregacje, zapis plików CSV i przygotowanie heatmapy,
- `matplotlib` - generowanie wykresów SVG w katalogu `wyniki/`.

Główna analiza HITL nie wymaga kluczy API. Plik `.env.example` pochodzi z szablonu i dotyczy opcjonalnych przykładów LLM.

## Uruchomienie

Instalacja zależności:

```bash
uv sync
```

Uruchomienie pełnej analizy i wygenerowanie artefaktów:

```bash
uv run python src/main.py
```


Opcjonalne uruchomienie notebooków:

```bash
uv sync --extra notebooks
uv run jupyter notebook
```

## Co robi skrypt

`src/main.py` generuje 162 deterministyczne scenariusze pracy manipulatora. Każdy scenariusz opisuje środowisko, prędkość, ładunek, niepewność percepcji, okluzję i nowość sytuacji. Następnie porównuje pięć polityk:

- brak HITL,
- HITL informacyjny,
- prawo weta operatora,
- zatwierdzenie przed ruchem,
- adaptacyjny HITL.

Operator jest traktowany jako osoba przeszkolona. W analizie zakładam, że może nie tylko zaakceptować albo odrzucić trajektorię, ale także ją poprawić. Dodatkowy moduł porównuje dwa modele organizacyjne: jeden operator nadzoruje jeden manipulator oraz jeden operator nadzoruje wiele manipulatorów.

## Wyniki

Po uruchomieniu `uv run python src/main.py` powstają następujące pliki:

- `wyniki/scenariusze.csv` - wejściowe scenariusze syntetyczne,
- `wyniki/wyniki_polityk_hitl.csv` - wynik dla każdego scenariusza i polityki,
- `wyniki/podsumowanie_polityk.csv` - tabela zbiorcza polityk HITL,
- `wyniki/rekomendacje_polityk.csv` - rekomendacje zależne od sytuacji,
- `wyniki/analiza_obciazenia_operatora.csv` - porównanie nadzoru jednego i wielu robotów,
- `wyniki/macierz_zgodnosci_ai_act.csv` - mapowanie wymagań AI Act i regulacji maszynowych na środki projektowe,
- `wyniki/raport_hitl.md` - raport generowany przez skrypt,
- `wyniki/ryzyko_resztkowe_polityki.svg`,
- `wyniki/kompromis_ryzyko_czas.svg`,
- `wyniki/heatmapa_wysokiego_ryzyka.svg`.

Notebooki:

- `notebooks/run.ipynb` - odtworzenie wyników przez uruchomienie skryptu,
- `notebooks/analyse.ipynb` - opisowa analiza wyników, wykresów i konsekwencji prawno-etycznych.

Podsumowanie z aktualnego uruchomienia:

| Polityka | Średnie ryzyko resztkowe | P95 ryzyka | Średni czas decyzji | Odsetek interwencji |
|---|---:|---:|---:|---:|
| Zatwierdzenie przed ruchem | 0.2447 | 0.4217 | 7.4296 s | 46.91% |
| Adaptacyjny HITL | 0.2748 | 0.4708 | 4.9481 s | 37.04% |
| Prawo weta operatora | 0.3155 | 0.5278 | 3.3123 s | 21.60% |
| HITL informacyjny | 0.3541 | 0.6636 | 2.1457 s | 8.64% |
| Brak HITL | 0.3630 | 0.7403 | 1.8000 s | 0.00% |

## Interpretacja wyników

Nie ma jednej najlepszej polityki dla wszystkich sytuacji. Zatwierdzenie przed ruchem daje najniższe średnie ryzyko, ale wymaga interwencji w prawie połowie przypadków. Dla pracy rutynowej w częściowo odseparowanej hali może to być zbyt kosztowne organizacyjnie i może prowadzić do przeciążenia operatora.

Najbardziej praktyczny wniosek jest sytuacyjny:

- dla znanych trajektorii, niskiej niepewności i ryzyka głównie produkcyjnego wystarczy HITL informacyjny albo prawo weta;
- dla wysokiej okluzji, niskiej pewności AI lub nietypowych zadań najlepszym kompromisem jest adaptacyjny HITL;
- dla rzadkich i nowych trajektorii uzasadnione jest zatwierdzenie przed ruchem;
- dla pracy blisko ludzi sam HITL nie wystarczy i musi być połączony z funkcjami bezpieczeństwa maszyny;
- przy jednym operatorze nadzorującym wiele robotów trzeba ograniczać liczbę równoległych eskalacji, bo nadzór może stać się pozorny.

## Wnioski prawno-etyczne

1. Samo dodanie człowieka do procesu nie wystarcza do zgodności z AI Act. Nadzór musi być realny: operator powinien rozumieć powód eskalacji, mieć możliwość zatrzymania lub korekty trajektorii i działać w czasie, który ma znaczenie dla bezpieczeństwa.
2. W strefie częściowo odseparowanej, gdzie podstawowe szkody dotyczą mienia i przestoju, system nie musi automatycznie być traktowany tak samo jak robot pracujący bezpośrednio obok ludzi. Nadal wymaga jednak zarządzania ryzykiem, dokumentacji, logowania i jasnego podziału odpowiedzialności.
3. Jeżeli manipulator pracowałby blisko ludzi albo planowanie trajektorii wpływałoby na funkcję bezpieczeństwa maszyny, problem prawny byłby poważniejszy. System należałoby traktować jako kandydata do szczegółowej oceny pod kątem AI Act, rozporządzenia maszynowego 2023/1230 i norm robotycznych.
4. HITL nie może zastąpić funkcji bezpieczeństwa maszyny. Potrzebne są osłony, strefy bezpieczeństwa, ograniczenia prędkości, awaryjne zatrzymanie, walidacja HMI, testy czasu reakcji i dokumentacja techniczna.
5. Odpowiedzialność nie powinna być przerzucana wyłącznie na operatora. Dostawca planera trajektorii odpowiada za projekt systemu i dokumentację, integrator za włączenie go do maszyny, organizacja wdrażająca za procedury i szkolenia, a operator za decyzje w granicach realnie dostępnych informacji i narzędzi.
6. Największe ryzyko etyczne to pozorny nadzór: system formalnie ma człowieka w pętli, ale operator ma za dużo alarmów, za mało czasu albo za mało wyjaśnień, żeby skutecznie zareagować.

## Ograniczenia

Model jest syntetyczny i służy do analizy porównawczej, a nie do certyfikacji robota. Projekt nie korzysta z danych realnego manipulatora, ponieważ takich danych nie było w projekcie grupowym i trudno je pozyskać w ramach mini-projektu akademickiego.

Projekt nie modeluje pełnej dynamiki manipulatora, ograniczeń kinematycznych, rzeczywistych mas elementów robota, dokładnych czasów zatrzymania, awarii sensorów, cyberataków ani ergonomii konkretnego interfejsu operatora. Masa robota, energia ruchu, typ chwytaka, rodzaj ładunku, dystans do ludzi i czasy zatrzymania mogłyby zmienić ocenę prawną, bo wpływają na potencjalną ciężkość szkody i zakres wymagań maszynowych.

Do dalszego rozwoju potrzebne byłyby: logi z realnego robota, dane o trajektoriach, pomiary odległości i prędkości, testy HMI z operatorami, symulacja w ROS lub podobnym środowisku, analiza awarii sensorów, testy cyberbezpieczeństwa oraz pełniejsza ocena zgodności z rozporządzeniem maszynowym.

## Źródła

- Regulation (EU) 2024/1689 - AI Act: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- European Commission, AI Act Service Desk, Article 14 Human oversight: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14
- NIST AI Risk Management Framework 1.0: https://www.nist.gov/itl/ai-risk-management-framework
- Regulation (EU) 2023/1230 on machinery: https://eur-lex.europa.eu/eli/reg/2023/1230/oj
- EU-OSHA summary of Regulation 2023/1230/EU: https://osha.europa.eu/en/legislation/directive/regulation-20231230eu-machinery
- ISO/TS 15066:2016, Robots and robotic devices - Collaborative robots: https://www.iso.org/standard/62996.html

## Sprawdzenie

Projekt został sprawdzony poleceniami:

```bash
uv run python src/main.py
uv run python -m unittest discover -s tests
```

Wynik: analiza wygenerowała artefakty w `wyniki/`, a 3 testy jednostkowe zakończyły się poprawnie.
