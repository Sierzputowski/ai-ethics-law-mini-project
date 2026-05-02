# Dokumentacja procesu

Ten plik dokumentuje sposób pracy nad mini-projektem: użyte narzędzia AI, prompty, decyzje projektowe, problemy i iteracje.

## Narzędzia AI

| Narzędzie | Do czego użyto |
|---|---|
| Codex / ChatGPT | Zaplanowanie struktury projektu, implementacja skryptu analizy, przygotowanie README i PROCESS, debugowanie uruchomienia lokalnego. |
| Wyszukiwanie web przez asystenta | Sprawdzenie aktualnych źródeł prawnych i regulacyjnych: AI Act 2024/1689, rozporządzenie maszynowe 2023/1230, NIST AI RMF, ISO/TS 15066. |

## Prompty

### Zlecenie główne

```text
wykonaj cały projekt zgodnie z README dla tematu własnego: Human-in-the-Loop Decision Making in AI-Based Robotic Trajectory Planning: Risk Analysis and AI Act Compliance
```

**Kontekst:** Prompt określał temat własny i oczekiwanie wykonania kompletnego mini-projektu zgodnie z szablonem repozytorium.

### Instrukcje repozytorium

```text
Cała dokumentacja, komentarze w kodzie i komunikacja — po polsku.
Nie generuj fałszywych wyników — jeśli analiza wymaga uruchomienia kodu, uruchom go.
Stawiaj na wnioski — kod jest środkiem do celu.
```

**Kontekst:** To były instrukcje z `AGENTS.md`, które ustawiły język, zakres i nacisk na rzetelne wyniki.

## Decyzje

1. **Analiza syntetyczna zamiast sterowania realnym robotem** — mini-projekt ma ograniczony zakres akademicki, więc bezpieczniej i czytelniej jest porównać scenariusze ryzyka niż udawać dane z robota.
2. **Deterministyczne scenariusze** — wyniki są powtarzalne, możliwe do sprawdzenia i nie zależą od losowego ziarna.
3. **Pięć polityk HITL** — zestaw obejmuje pełną autonomię, monitoring, weto, zatwierdzanie przed ruchem i wariant adaptacyjny.
4. **Ryzyko jako iloczyn prawdopodobieństwa i ciężkości skutku** — to prosta, audytowalna reprezentacja zgodna z klasycznym podejściem do oceny ryzyka.
5. **Macierz zgodności z AI Act** — sam wynik techniczny nie wystarcza; trzeba pokazać, jak środki projektowe odpowiadają wymaganiom prawnym.
6. **SVG i CSV jako artefakty** — środowisko lokalne nie miało kompletu bibliotek, więc wykresy generowane są bezpośrednio jako SVG, bez zależności od Matplotlib.

## Co nie zadziałało

1. **`uv` nie był zainstalowany** — komenda `uv run src/main.py` nie mogła zostać wykonana. Obejście: uruchomienie przez `python src/main.py`.
2. **Brak Pandas w lokalnym Pythonie** — pierwsza wersja skryptu używała Pandas, ale środowisko nie miało pakietu. Obejście: przepisanie analizy na standardową bibliotekę Pythona.
3. **Matplotlib był niekompletny** — import Matplotlib kończył się błędem braku pakietu `packaging`. Obejście: generowanie wykresów SVG bez Matplotlib.
4. **Pusta komórka heatmapy dla środowiska odseparowanego** — po filtrowaniu scenariuszy wysokiego ryzyka jedna kombinacja nie miała obserwacji. Obejście: jawna obsługa pustych komórek jako `0.0`.

## Iteracje

1. **v1 — rozpoznanie repozytorium**: sprawdzenie README, PROCESS, `pyproject.toml`, testów i katalogów.
2. **v2 — projekt analizy**: wybór scenariuszy, parametrów ryzyka i polityk nadzoru człowieka.
3. **v3 — pierwsza implementacja**: skrypt z Pandas i Matplotlib.
4. **v4 — wersja odporna środowiskowo**: usunięcie obowiązkowych zależności z głównego skryptu, zapis CSV i SVG przez standardową bibliotekę.
5. **v5 — dokumentacja i wnioski**: uzupełnienie README, PROCESS i raportu w `wyniki/`.

## Czas pracy

Orientacyjnie: 2-3 godziny pracy koncepcyjnej, implementacyjnej, debugowania i dokumentacji.

## Refleksja o użyciu AI

AI przyspieszyła przejście od tematu do działającego prototypu, ale wymagała kontroli: trzeba było zweryfikować źródła prawne, uruchomić kod i poprawić błędne założenie o dostępnych bibliotekach. Najważniejszą wartością nie było samo wygenerowanie kodu, tylko iteracyjne doprowadzenie projektu do stanu, w którym wyniki są odtwarzalne i opisane w kontekście prawnym.
