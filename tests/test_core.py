import datetime
import io
import os
import sys

import pytest

import bixxylogs
from bixxylogs import console, core


@pytest.fixture(autouse=True)
def isole(tmp_path):
    core.close_all()
    core._cleaned.clear()
    core.configure(log_dir=str(tmp_path / "logs"), console_level="DEBUG", file_level="INFO", keep_days=7, files=True)
    yield
    core.close_all()


def test_import_ne_cree_aucun_dossier(tmp_path):
    assert not (tmp_path / "logs").exists()


def test_fichiers_dates_par_nom_categorie_sous_categorie(tmp_path, capsys):
    log = bixxylogs.get_logger("App", "Scan", "Fichiers")
    log.info("bonjour")
    log.debug("détail")  # DEBUG n'est pas écrit dans les fichiers
    jour = datetime.date.today().isoformat()
    for rel in (f"App_{jour}.log", f"Scan_{jour}.log", os.path.join("Scan", f"Fichiers_{jour}.log")):
        texte = (tmp_path / "logs" / rel).read_text(encoding="utf-8")
        assert "[INFO] [Scan] [Fichiers] bonjour" in texte and "détail" not in texte
    assert "détail" in capsys.readouterr().out


def test_niveaux_ecran_et_fichier(tmp_path, capsys):
    core.configure(console_level="WARNING", file_level="DEBUG")
    log = bixxylogs.get_logger("App")
    log.info("discret")
    log.error("grave")
    out = capsys.readouterr().out
    assert "grave" in out and "discret" not in out
    texte = (tmp_path / "logs" / f"App_{datetime.date.today().isoformat()}.log").read_text(encoding="utf-8")
    assert "discret" in texte and "grave" in texte


def test_niveau_inconnu():
    with pytest.raises(ValueError):
        core.configure(console_level="BAVARD")


def test_fichiers_desactives(tmp_path):
    core.configure(files=False)
    bixxylogs.get_logger("App").info("x")
    assert not (tmp_path / "logs").exists()


def test_nettoyage_des_vieux_fichiers(tmp_path):
    d = tmp_path / "logs"
    d.mkdir()
    vieux = d / "App_2000-01-01.log"
    recent = d / f"App_{datetime.date.today().isoformat()}.log"
    autre = d / "App_notes.log"
    for f in (vieux, recent, autre):
        f.write_text("x")
    bixxylogs.get_logger("App").info("go")
    assert not vieux.exists() and recent.exists() and autre.exists()


def test_un_seul_fichier_ouvert_pour_plusieurs_loggers(tmp_path):
    for i in range(20):
        bixxylogs.get_logger("App", "Cat").info(str(i))
    assert len(core._handles) == 2  # App et Cat, pas 40
    core.close_all()
    assert not core._handles


def test_noms_invalides_sur_disque(tmp_path):
    bixxylogs.get_logger("A:b/c", "x?y").info("ok")
    assert any("A_b_c" in p.name for p in (tmp_path / "logs").iterdir())


def test_console_cp1252_ne_plante_pas(monkeypatch):
    buf = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    monkeypatch.setattr(sys, "stdout", buf)
    bixxylogs.get_logger("App", "Scan").success("fichier 日本語 ok", percentage=50)
    bixxylogs.get_logger("App", "Scan").error("mauvais")
    buf.flush()
    sortie = buf.buffer.getvalue().decode("cp1252")
    assert "[+]" in sortie and "[x]" in sortie and "50.0%" in sortie


def test_no_color(monkeypatch, capsys):
    monkeypatch.setenv("NO_COLOR", "1")
    bixxylogs.get_logger("App").info("sobre")
    assert "\033[" not in capsys.readouterr().out


def test_barre_gardee_avec_keep(tmp_path, capsys):
    log = bixxylogs.get_logger("App", "Scan")
    log.info("premier", percentage=10, keep=True)
    log.info("second", percentage=20, keep=True)
    out = capsys.readouterr().out
    assert out.count("\n") == 2 and "\r" not in out.replace("\r\n", "\n").strip("\r")
    texte = (tmp_path / "logs" / f"App_{datetime.date.today().isoformat()}.log").read_text(encoding="utf-8")
    assert "[10.0%] premier" in texte and "[20.0%] second" in texte
