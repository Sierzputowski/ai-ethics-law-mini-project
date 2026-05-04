# Dokumentacja procesu

Ten plik dokumentuje sposób pracy nad mini-projektem: użyte narzędzia AI, prompty, decyzje projektowe, problemy i iteracje.

## Narzędzia AI

| Narzędzie | Do czego użyto |
|---|---|
| Codex / ChatGPT | Zaplanowanie struktury projektu, implementacja i rozszerzenie skryptu analizy, przygotowanie README, PROCESS, notebooków, raportu i artefaktów wynikowych. |
| Codex / ChatGPT z wyszukiwaniem web | Sprawdzenie aktualnych źródeł regulacyjnych: AI Act 2024/1689, AI Act art. 14, rozporządzenie maszynowe 2023/1230, NIST AI RMF, ISO/TS 15066. |

Nie używano innych narzędzi AI, takich jak Claude, Cursor, GitHub Copilot, Gemini albo Perplexity.

## Prompty

### Zlecenie główne

```text
wykonaj cały projekt zgodnie z README dla tematu własnego: Human-in-the-Loop Decision Making in AI-Based Robotic Trajectory Planning: Risk Analysis and AI Act Compliance
```

**Kontekst:** Prompt określał temat własny i oczekiwanie wykonania kompletnego mini-projektu zgodnie z szablonem repozytorium.

### Doprecyzowanie wymagań

```text
przeczytaj miniprojekt zasady.docx i dokładnie opisz wymagania jakie muszą być spełnione dla mini projektu o temacie: Human-in-the-Loop Decision Making in AI-Based Robotic Trajectory Planning: Risk Analysis and AI Act Compliance
skorzystaj z opisów w README, możesz też zobaczyć przykłady w przykłady.docx (jednak mają one krótkie opisy ja oczekuje dłuższego)
wymagania zapisz w pliku "wymagania"
```

**Kontekst:** Prompt służył do przełożenia zasad oceny i przykładowych tematów na konkretną checklistę dla tego mini-projektu.

### Pytania uzupełniające

```text
napisz plik 'doprecyzowania' który będzie zawieriał pytania do mnie na temat rzeczy które muszę doprecyzować abyś miał całą wiedzę potrzebną do pełnego stworzenia projektu
```

**Kontekst:** Na podstawie tego promptu powstał plik z pytaniami o dane formalne, projekt grupowy, typ robota, zakres prawny, sposób nadzoru operatora i oczekiwaną formę końcową.

### Finalne dopracowanie

```text
odpowiedziałem na pytania w doprecyzowania dokończ projekt na ich podstawie
```

**Kontekst:** Po odpowiedziach projekt został doprecyzowany jako analiza manipulatora przemysłowego w hali produkcyjnej, powiązana z projektem grupowym o wyznaczaniu ścieżek dla robotów przemysłowych.

### Instrukcje repozytorium

```text
Cała dokumentacja, komentarze w kodzie i komunikacja — po polsku.
Nie generuj fałszywych wyników — jeśli analiza wymaga uruchomienia kodu, uruchom go.
Stawiaj na wnioski — kod jest środkiem do celu.
```

**Kontekst:** To były instrukcje z `AGENTS.md`, które ustawiły język, zakres i nacisk na rzetelne wyniki.

## Decyzje

1. **Manipulator przemysłowy jako przypadek bazowy** — projekt grupowy dotyczy wyznaczania ścieżek dla robotów przemysłowych, więc mini-projekt analizuje ramię robota w hali produkcyjnej.
2. **Strefa częściowo odseparowana** — przyjęto scenariusz, w którym podstawowe ryzyka dotyczą uszkodzenia mienia i przestoju, ale osobno opisano, co zmieniłaby praca blisko ludzi.
3. **Analiza syntetyczna zamiast danych z realnego robota** — dane z realnego manipulatora nie były dostępne w projekcie grupowym, więc wybrano deterministyczny model scenariuszy zamiast udawania pomiarów.
4. **162 scenariusze jako rdzeń analizy** — liczba scenariuszy jest wystarczająca do porównania polityk i zachowuje czytelność projektu.
5. **Pięć polityk HITL** — zestaw obejmuje pełną autonomię, monitoring, weto, zatwierdzanie przed ruchem i wariant adaptacyjny. Nie dodano kolejnych polityk, ponieważ istniejące warianty dobrze pokazują kompromis między ryzykiem, czasem i obciążeniem operatora.
6. **Operator przeszkolony, ale nie nieomylny** — operator może zaakceptować, odrzucić albo poprawić trajektorię, lecz może być przeciążony, zwłaszcza przy nadzorze wielu robotów.
7. **Wynik sytuacyjny zamiast jednej zwycięskiej polityki** — główny wniosek nie brzmi „adaptacyjny HITL zawsze najlepszy”, tylko: różne polityki są uzasadnione w różnych warunkach ryzyka.
8. **Macierz zgodności z AI Act i regulacjami maszynowymi** — sam wynik techniczny nie wystarcza; trzeba pokazać relację do art. 9-15 AI Act, ról dostawcy/deployera oraz rozporządzenia 2023/1230.
9. **Notebooki jako forma prezentacji wyników** — dodano `notebooks/run.ipynb` do odtworzenia wyników i `notebooks/analyse.ipynb` do interpretacji.
10. **SVG i CSV jako artefakty** — wyniki są łatwe do sprawdzenia bez dodatkowych narzędzi, a wykresy można osadzić w notebooku i README.

## Co nie zadziałało

1. **Zbyt ogólne ujęcie robota** — pierwsza wersja opisywała „robota” ogólnie, bez jasnego związku z projektem grupowym. Po doprecyzowaniu zakresu projekt został osadzony w konkretnym przypadku: manipulator przemysłowy w hali produkcyjnej, wybierający trajektorie ramienia.
2. **Jedna najlepsza polityka HITL jako zbyt prosta teza** — początkowa interpretacja sugerowała, że można wskazać jeden najlepszy wariant nadzoru. To było za płytkie, bo różne sytuacje wymagają różnych polityk. Rozwiązaniem było dodanie rekomendacji zależnych od kontekstu: rutynowa praca, okluzja, nowe zadanie, praca blisko ludzi i nadzór wielu robotów.
3. **Za słabe rozróżnienie ryzyka produkcyjnego i ryzyka dla ludzi** — pierwsza wersja traktowała scenariusze podobnie, chociaż uszkodzenie mienia i możliwa kolizja z człowiekiem mają inną wagę prawną. Poprawiono to przez osobne omówienie strefy częściowo odseparowanej oraz sytuacji, w której manipulator pracowałby blisko ludzi.
4. **Zbyt formalne rozumienie Human-in-the-Loop** — samo dodanie operatora mogło wyglądać jak wystarczający środek zgodności. Po korekcie projekt mocniej opisuje pozorny nadzór, przeciążenie operatora, potrzebę wyjaśnień, możliwość korekty trajektorii i limity równoległych eskalacji.
5. **Za mało rozpisana odpowiedzialność** — wcześniejsze wnioski skupiały się na operatorze, a za mało na dostawcy systemu, integratorze maszyny i organizacji wdrażającej. Poprawiono to przez rozbudowanie macierzy zgodności i wniosków o role oraz obowiązki poszczególnych stron.
6. **Zbyt techniczna interpretacja wyników** — początkowo wyniki mogły być czytane głównie jako porównanie liczb: ryzyko, czas, interwencje. Po zmianach dodano interpretację prawno-etyczną: kiedy system może wymagać szczegółowej oceny pod AI Act, kiedy HITL nie zastępuje funkcji bezpieczeństwa maszyny i dlaczego logowanie oraz dokumentacja są częścią odpowiedzialnego wdrożenia.

## Iteracje

1. **v1 — rozpoznanie repozytorium**: sprawdzenie README, PROCESS, `pyproject.toml`, testów i katalogów.
2. **v2 — projekt analizy**: wybór scenariuszy, parametrów ryzyka i polityk nadzoru człowieka.
3. **v3 — pierwsza implementacja**: skrypt z porównaniem pięciu polityk HITL.
4. **v4 — wersja łatwa do odtworzenia**: uporządkowanie generowania CSV, SVG i raportu tak, aby wyniki można było sprawdzić bez ręcznego przepisywania tabel.
5. **v5 — dokumentacja i wnioski**: uzupełnienie README, PROCESS i raportu w `wyniki/`.
6. **v6 — doprecyzowanie pod projekt grupowy**: wpisanie manipulatora przemysłowego, hali produkcyjnej i częściowo odseparowanej strefy pracy.
7. **v7 — poziom excellent**: dodanie rekomendacji zależnych od sytuacji, analizy przeciążenia operatora przy jednym i wielu robotach, rozbudowanej macierzy zgodności i notebooków.

## Uruchomione sprawdzenia

```text
python src\main.py
```

Wynik: wygenerowano analizę HITL i zapisano artefakty w katalogu `wyniki/`.

```text
python -m unittest discover -s tests
```

Wynik: 3 testy przeszły poprawnie.

## Czas pracy

Orientacyjnie: 3-5 godzin pracy koncepcyjnej, implementacyjnej, debugowania i dokumentacji. Część czasu obejmuje doprecyzowanie tematu, dopisanie wymagań i przygotowanie notebooków.

## Refleksja o użyciu AI

Codex był używany jako narzędzie do szybkiego przejścia od tematu do działającego, udokumentowanego prototypu. Najważniejsze było iteracyjne doprecyzowanie zakresu: najpierw powstała analiza ogólna HITL, później została osadzona w konkretnym przypadku manipulatora przemysłowego i projekcie grupowym o wyznaczaniu ścieżek. Użycie AI pomogło uporządkować wymagania, ale końcowy zakres wynika z odpowiedzi autora w pliku `doprecyzowania`.
