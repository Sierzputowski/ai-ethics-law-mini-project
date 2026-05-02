# Raport z analizy HITL dla planowania trajektorii robota

## Zakres

Analiza porównuje 5 wariantów nadzoru człowieka na 162 deterministycznie wygenerowanych scenariuszach. Scenariusze różnią się gęstością ludzi, okluzją, prędkością robota, masą ładunku, niepewnością percepcji i nowością sytuacji.

## Najważniejsze wyniki

- Najniższe średnie ryzyko resztkowe uzyskała polityka **Zatwierdzenie przed ruchem**: 0.2447.
- Względem pełnej autonomii daje to redukcję średniego ryzyka o około **32.6%**.
- Koszt bezpieczeństwa to średni czas decyzji **7.43 s** oraz interwencja operatora w **46.9%** przypadków.
- Najbardziej restrykcyjny wariant nie zawsze jest najlepszy organizacyjnie: mniejsze ryzyko trzeba zestawić z opóźnieniem, obciążeniem operatora i ryzykiem automatyzacyjnej bierności.

## Tabela porównawcza

| polityka                   | srednie_ryzyko_resztkowe | mediana_ryzyka_resztkowego | p95_ryzyka_resztkowego | sredni_czas_decyzji_s | odsetek_interwencji | srednia_redukcja_wzgledna |
| -------------------------- | ------------------------ | -------------------------- | ---------------------- | --------------------- | ------------------- | ------------------------- |
| Zatwierdzenie przed ruchem | 0.2447                   | 0.2507                     | 0.4217                 | 7.4296                | 0.4691              | 0.2285                    |
| Adaptacyjny HITL           | 0.2748                   | 0.2913                     | 0.4708                 | 4.9481                | 0.3704              | 0.1624                    |
| Prawo weta operatora       | 0.3155                   | 0.3334                     | 0.5278                 | 3.3123                | 0.216               | 0.0715                    |
| HITL informacyjny          | 0.3541                   | 0.3413                     | 0.6636                 | 2.1457                | 0.0864              | 0.0117                    |
| Brak HITL                  | 0.363                    | 0.3413                     | 0.7403                 | 1.8                   | 0.0                 | 0.0                       |

## Interpretacja

Wyniki wspierają podejście adaptacyjne: człowiek powinien być włączany tam, gdzie ryzyko bazowe albo niepewność modelu przekraczają ustalone progi. Stałe wymaganie zatwierdzania każdej decyzji daje silną redukcję ryzyka, ale podnosi koszt operacyjny i może obniżyć jakość nadzoru przy długiej pracy.

## Macierz zgodności

| obszar                             | wymaganie                                                                                  | implementacja_w_projekcie                                                                                | luka                                                                                   |
| ---------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| AI Act art. 9                      | Ciągły system zarządzania ryzykiem dla systemu wysokiego ryzyka.                           | Rejestr scenariuszy, ocena ryzyka bazowego i resztkowego, porównanie środków redukcji.                   | W projekcie to prototyp analityczny, nie pełny proces lifecycle z właścicielami ryzyk. |
| AI Act art. 10                     | Jakość danych, reprezentatywność i kontrola błędów danych.                                 | Jawne parametry scenariuszy: środowisko, okluzja, prędkość, ładunek, niepewność i nowość sytuacji.       | Brak danych z rzeczywistego robota i brak audytu biasu domenowego.                     |
| AI Act art. 11                     | Dokumentacja techniczna umożliwiająca ocenę zgodności.                                     | README, wygenerowany raport, CSV z wynikami i opis założeń modelu.                                       | Brak pełnej dokumentacji producenta, wersjonowania modelu i specyfikacji HMI.          |
| AI Act art. 12                     | Rejestrowanie zdarzeń i możliwość śledzenia działania systemu.                             | Wyniki per scenariusz zapisane do CSV, w tym decyzja o interwencji i ryzyko resztkowe.                   | Brak strumienia logów z robota, czujników i decyzji operatora w czasie rzeczywistym.   |
| AI Act art. 13                     | Przejrzystość i instrukcje dla wdrażającego.                                               | Opis progów, trybów nadzoru i interpretacji wyników w README oraz raporcie.                              | Trzeba dodać instrukcję stanowiskową dla operatora i procedury eskalacji.              |
| AI Act art. 14                     | Skuteczny nadzór człowieka, możliwość monitorowania, interpretacji i przerwania działania. | Porównanie monitorowania, weta, zatwierdzania i adaptacyjnego HITL.                                      | Projekt nie waliduje ergonomii HMI ani czasu reakcji realnego operatora.               |
| AI Act art. 15                     | Dokładność, odporność i cyberbezpieczeństwo.                                               | Niepewność AI i okluzja zwiększają ryzyko, co uruchamia interwencję.                                     | Brak testów cyberbezpieczeństwa, odporności na spoofing sensorów i awarii sieci.       |
| Rozporządzenie maszynowe 2023/1230 | Ocena ryzyka i redukcja ryzyka dla maszyn, w tym autonomii i funkcji bezpieczeństwa.       | Wniosek: HITL jest środkiem organizacyjno-technicznym, ale nie zastępuje funkcji bezpieczeństwa maszyny. | Do wdrożenia potrzebna byłaby analiza zgodności CE i normy robotyczne.                 |
