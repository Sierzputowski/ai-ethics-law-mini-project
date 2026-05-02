# Human-in-the-Loop Decision Making in AI-Based Robotic Trajectory Planning

**Autor:** Bartek, nr indeksu: do uzupełnienia

**Temat:** własny — *Human-in-the-Loop Decision Making in AI-Based Robotic Trajectory Planning: Risk Analysis and AI Act Compliance*

**Kurs:** Aspekty prawne, społeczne i etyczne w AI, PWr 2025/2026

## Cel projektu

Projekt analizuje, jak różne warianty nadzoru człowieka nad systemem AI planującym trajektorie robota wpływają na ryzyko resztkowe, opóźnienie decyzji i zgodność z wymaganiami AI Act. Mini-projekt nie buduje realnego sterownika robota; tworzy odtwarzalny model analityczny, który pozwala porównać kilka polityk Human-in-the-Loop (HITL) w scenariuszach o różnej gęstości ludzi, prędkości ruchu, okluzji, ładunku i niepewności percepcji.

Główne pytanie badawcze: czy „człowiek w pętli” rzeczywiście zmniejsza ryzyko w planowaniu trajektorii, czy tylko przesuwa odpowiedzialność na operatora?

## Powiązanie z projektem grupowym

Do uzupełnienia po stronie autora, jeśli projekt grupowy dotyczy robotyki, automatyki, systemów bezpieczeństwa lub audytu AI. W obecnej wersji mini-projekt jest samodzielny i wybrany dlatego, że łączy techniczny problem planowania trajektorii z wymaganiami prawnymi dotyczącymi systemów wysokiego ryzyka, nadzoru człowieka, dokumentacji i bezpieczeństwa maszyn.

## Wymagania i uruchomienie

Główna analiza działa na standardowej bibliotece Pythona i nie wymaga kluczy API. Zależności w `pyproject.toml` pozostają przydatne do eksperymentów z notebookami, wykresami Matplotlib i przykładami LLM z szablonu.

```bash
uv sync
uv run python src/main.py
```

Jeśli `uv` nie jest zainstalowane, można uruchomić analizę bezpośrednio:

```bash
python src/main.py
```

Opcjonalne przykłady LLM z `src/example_openai.py`, `src/example_anthropic.py` i `src/example_gemini.py` wymagają skopiowania `.env.example` do `.env` oraz uzupełnienia odpowiednich kluczy API. Główna analiza HITL ich nie używa.

## Co robi skrypt

`src/main.py` generuje 162 deterministyczne scenariusze pracy robota. Każdy scenariusz opisuje środowisko, prędkość, ładunek, niepewność percepcji i nowość sytuacji. Następnie porównuje pięć polityk:

- brak HITL,
- HITL informacyjny,
- prawo weta operatora,
- zatwierdzenie przed ruchem,
- adaptacyjny HITL.

Wyniki są zapisywane do katalogu `wyniki/` jako pliki CSV, SVG i raport Markdown.

## Wyniki

Najważniejsze pliki:

- `wyniki/podsumowanie_polityk.csv` — tabela zbiorcza polityk HITL,
- `wyniki/wyniki_polityk_hitl.csv` — wynik dla każdego scenariusza i polityki,
- `wyniki/macierz_zgodnosci_ai_act.csv` — mapowanie wymagań AI Act na środki projektowe,
- `wyniki/raport_hitl.md` — raport wygenerowany przez skrypt,
- `wyniki/ryzyko_resztkowe_polityki.svg`,
- `wyniki/kompromis_ryzyko_czas.svg`,
- `wyniki/heatmapa_wysokiego_ryzyka.svg`.

Podsumowanie z uruchomienia:

| Polityka | Średnie ryzyko resztkowe | P95 ryzyka | Średni czas decyzji | Odsetek interwencji |
|---|---:|---:|---:|---:|
| Zatwierdzenie przed ruchem | 0.2447 | 0.4217 | 7.4296 s | 46.91% |
| Adaptacyjny HITL | 0.2748 | 0.4708 | 4.9481 s | 37.04% |
| Prawo weta operatora | 0.3155 | 0.5278 | 3.3123 s | 21.60% |
| HITL informacyjny | 0.3541 | 0.6636 | 2.1457 s | 8.64% |
| Brak HITL | 0.3630 | 0.7403 | 1.8000 s | 0.00% |

Najniższe średnie ryzyko daje zatwierdzanie przed ruchem: redukcja średniego ryzyka wobec pełnej autonomii wynosi około 32,6%. Wariant adaptacyjny jest jednak bardziej praktycznym kompromisem, bo zmniejsza ryzyko o około 24,3% przy krótszym średnim czasie decyzji i mniejszym obciążeniu operatora.

## Wnioski merytoryczne

1. Samo dodanie człowieka do procesu nie wystarcza do zgodności z AI Act. Nadzór musi być realny: operator powinien rozumieć powód eskalacji, mieć możliwość przerwania ruchu i działać w czasie, który ma znaczenie dla bezpieczeństwa.
2. Dla planowania trajektorii robota najważniejszy jest kompromis między bezpieczeństwem a opóźnieniem. Zatwierdzanie każdej ryzykownej trajektorii obniża ryzyko, ale może spowolnić system i przeciążyć operatora.
3. Najbardziej uzasadniony model organizacyjny to adaptacyjny HITL: eskalacja następuje przy wysokim ryzyku bazowym albo niskiej pewności AI. To odpowiada logice proporcjonalności z AI Act art. 14.
4. HITL nie może zastąpić funkcji bezpieczeństwa maszyny. W robocie fizycznym nadal potrzebne są ograniczenia prędkości, strefy bezpieczeństwa, detekcja przeszkód, awaryjne zatrzymanie, logowanie decyzji i walidacja zgodności z regulacjami maszynowymi.
5. W ujęciu AI Act system planowania trajektorii używany w środowisku, w którym decyzje mogą wpływać na zdrowie i bezpieczeństwo ludzi, należy traktować co najmniej jako kandydat do szczegółowej oceny ryzyka. Jeśli komponent AI pełni funkcję bezpieczeństwa lub jest częścią maszyny objętej oceną zgodności, wymagania dokumentacyjne i nadzorcze są szczególnie istotne.

## Ograniczenia

Model jest syntetyczny i służy do analizy porównawczej, a nie do certyfikacji robota. Nie korzysta z danych z rzeczywistego manipulatora, cobota ani robota mobilnego. Nie modeluje dynamiki ruchu, mapowania przestrzeni, ograniczeń kinematycznych, awarii sensorów, cyberataków ani ergonomii konkretnego interfejsu operatora. Wdrożenie produkcyjne wymagałoby testów z realnym sprzętem, analizy norm robotycznych, walidacji HMI i pełnej dokumentacji technicznej.

## Źródła

- Regulation (EU) 2024/1689 — AI Act: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- European Commission, AI Act Service Desk, Article 14 Human oversight: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14
- NIST AI Risk Management Framework 1.0: https://www.nist.gov/itl/ai-risk-management-framework
- Regulation (EU) 2023/1230 on machinery: https://eur-lex.europa.eu/eli/reg/2023/1230/oj
- EU-OSHA summary of Regulation 2023/1230/EU: https://osha.europa.eu/en/legislation/directive/regulation-20231230eu-machinery
- ISO/TS 15066:2016, Robots and robotic devices — Collaborative robots: https://www.iso.org/standard/62996.html
