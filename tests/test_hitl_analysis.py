import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import main


class AnalizaHITLTest(unittest.TestCase):
    def test_generuje_162_scenariusze(self):
        scenariusze = main.generuj_scenariusze()

        self.assertEqual(len(scenariusze), 162)
        self.assertTrue(all(wiersz["ryzyko_bazowe"] > 0 for wiersz in scenariusze))
        self.assertTrue(all(0 <= wiersz["pewnosc_ai"] <= 1 for wiersz in scenariusze))

    def test_polityki_zmniejszaja_srednie_ryzyko_wobec_braku_hitl(self):
        scenariusze = main.generuj_scenariusze()
        wyniki = main.ocen_polityki(scenariusze)
        agregat = main.agreguj_wyniki(wyniki)

        ryzyko_bez_hitl = next(
            w["srednie_ryzyko_resztkowe"]
            for w in agregat
            if w["polityka"] == "Brak HITL"
        )
        ryzyka_z_hitl = [
            w["srednie_ryzyko_resztkowe"]
            for w in agregat
            if w["polityka"] != "Brak HITL"
        ]

        self.assertTrue(all(ryzyko < ryzyko_bez_hitl for ryzyko in ryzyka_z_hitl))

    def test_macierz_zgodnosci_obejmuje_nadzor_czlowieka(self):
        zgodnosc = main.zbuduj_macierz_zgodnosci()

        self.assertIn("AI Act art. 14", {wiersz["obszar"] for wiersz in zgodnosc})


if __name__ == "__main__":
    unittest.main()
