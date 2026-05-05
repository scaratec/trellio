2026-04-12

# Security & Code Quality Audit -- trellio (trellio-client) v1.0.1

**Auftraggeber:** IT-Sicherheit (Enterprise Security Review)
**Kontext:** Sicherheitsfreigabe fuer Unternehmenseinsatz (100.000 Mitarbeiter).
trellio-client ist die zentrale Abhaengigkeit von trellio-mcp und
wurde als Teil der Freigabepruefung mitauditiert.
**Repository:** github.com/scaratec/trellio (intern, scaratec)
**Gesamtrisiko:** LOW
**Empfehlung:** Freigabe nach Nachbesserung (Pflicht-Massnahmen umsetzen)

---

## 1. Security Assessment

### 1.1 Checkliste

| #  | Kategorie                  | Status | Befund |
|----|----------------------------|--------|--------|
| 1  | Hardcoded Secrets          | PASS   | Keine Produktions-Credentials im Code. Test-Fixtures verwenden Platzhalter (`"valid_api_key"`, `"valid_api_token"`) |
| 2  | Code Injection             | PASS   | Kein eval(), exec(), subprocess, os.system(), compile() oder __import__() |
| 3  | Netzwerk-Angriffsflaeche   | PASS   | Kein Listener; reiner HTTP-Client |
| 4  | Ausgehende Verbindungen    | PASS   | Ausschliesslich `https://api.trello.com` (Standard). base_url konfigurierbar, aber HTTPS als Default |
| 5  | HTTPS-Erzwingung           | WARN   | base_url kann auf HTTP gesetzt werden; keine Validierung in `__init__` (`client.py:21`) |
| 6  | Credential-Handling        | INFO   | API-Key und Token als Query-Parameter (`client.py:35-36`); Trello-API-Anforderung, aber in URLs sichtbar |
| 7  | Credential-Logging         | PASS   | Logger protokolliert nur Method, Path, Status, Duration -- niemals Credentials (`client.py:47-66`) |
| 8  | Telemetrie / Tracking      | PASS   | Nicht vorhanden |
| 9  | Obfuskierter Code          | PASS   | Gesamter Quellcode ist lesbares Python |
| 10 | Dateisystem-Zugriff        | PASS   | Keiner |
| 11 | Datenpersistenz            | PASS   | Keine; rein zustandsloser Client |
| 12 | Abhaengigkeiten (direkt)   | PASS   | 2 Produktionsabhaengigkeiten: httpx (etabliert), pydantic (etabliert) |
| 13 | Dependency Pinning         | WARN   | `>=` ohne Obergrenze (`httpx>=0.24.0`, `pydantic>=2.0.0`) |
| 14 | Lock-File                  | FAIL   | Keines vorhanden |
| 15 | CI/CD-Pipeline             | FAIL   | Keine automatisierten Builds oder Security-Scans |
| 16 | SECURITY.md                | FAIL   | Nicht vorhanden |
| 17 | LICENSE-Datei              | PASS   | Vorhanden (GPL-3.0, vollstaendiger Text) |
| 18 | Testabdeckung              | PASS   | 16 BDD-Features, 117 Szenarien, 826 Steps; 27 Fehlerpfade zu 100% abgedeckt |
| 19 | Retry / Rate-Limiting      | PASS   | Exponentieller Backoff mit Retry-After-Header-Support; max 3 Retries; kein Endlos-Loop (`client.py:42-71`) |
| 20 | Schadcode / Backdoors      | PASS   | Nicht gefunden |

### 1.2 Staerken

- Extrem kleine Codebasis (287 LOC Client, 85 LOC Models, 6 LOC Errors)
- Nur 2 direkte Abhaengigkeiten (httpx, pydantic), beide branchenbekannt
- Interne Herkunft, volle Kontrolle
- Sauberer Async/Await-Code ohne blockierende Aufrufe
- Strukturiertes Logging ohne Credential-Leck
- Exponentieller Backoff mit Retry-After-Support
- Async-Context-Manager fuer saubere Ressourcenfreigabe
- Umfangreiche BDD-Testsuite mit Mock-Server und py-trello-Validierung

### 1.3 Risiken

- base_url kann auf HTTP gesetzt werden (kein HTTPS-Zwang)
- Credentials als Query-Parameter (Trello-API-Vorgabe, aber in URLs sichtbar)
- Kein Lock-File, kein CI/CD, keine SECURITY.md
- python-dotenv in requirements.txt, aber nicht in pyproject.toml

---

## 2. Code-Qualitaet

### 2.1 Uebersicht

| Kriterium             | Bewertung | Anmerkung |
|-----------------------|-----------|-----------|
| Typsicherheit         | 7/10      | Gute Basis; `**kwargs` untypisiert, `_authenticated_request` ohne Return-Type |
| Fehlerbehandlung      | 6/10      | Nur Status 200 als Erfolg akzeptiert; 201/204 fehlen |
| Code-Duplizierung     | 8/10      | Minimale Wiederholung; [Model(**x) for x in data]-Pattern akzeptabel |
| Modularisierung       | 9/10      | Exzellente Trennung: client.py, models.py, errors.py |
| Dokumentation         | 3/10      | Null Docstrings in 47 Methoden, 11 Models und 1 Exception |
| Async-Patterns        | 9/10      | Korrektes httpx/asyncio; kein blockierender Code im Async-Kontext |
| Toter Code            | 10/10     | Keiner gefunden |
| Anti-Patterns         | 8/10      | Wenige: untypisierte **kwargs, bare except in Tests |

### 2.2 Befunde

#### B-1: HTTP-Statuscode-Behandlung -- nur 200 akzeptiert

`client.py:53` behandelt ausschliesslich Status 200 als Erfolg:

```python
if response.status_code == 200:
    return response.json()
```

Die Trello-API gibt fuer POST-Anfragen typischerweise 200 zurueck
(nicht 201), sodass dies aktuell funktioniert. Aber DELETE-
Operationen koennten 204 (No Content) liefern, was als Fehler
behandelt wuerde. Wenn Trello das Verhalten aendert oder andere
REST-APIs mit diesem Client angesteuert werden, bricht die Logik.

**Datei:** `src/trellio/client.py`, Zeile 53

**Empfehlung:** Erfolgreiche Statuscodes erweitern:
```python
if 200 <= response.status_code < 300:
    if response.status_code == 204:
        return {}
    return response.json()
```

#### B-2: Fehlende Docstrings (alle Module)

Kein einziges Modul, keine Klasse und keine der 47 Methoden hat
eine Docstring. Fuer eine Bibliothek, die von anderen Projekten
(trellio-mcp) als Abhaengigkeit genutzt wird, ist das besonders
problematisch -- Nutzer sehen keine Dokumentation in IDE-Tooltips.

**Betroffene Dateien:** `client.py`, `models.py`, `errors.py`,
`__init__.py`

**Empfehlung:** Mindestens die oeffentliche API dokumentieren:
`TrellioClient.__init__`, `_authenticated_request`,
und jede Methode mit Parametern jenseits von IDs.

#### B-3: `_authenticated_request` -- fehlende Typ-Annotationen

```python
# client.py:33
async def _authenticated_request(self, method: str, path: str, **kwargs):
```

- Kein Return-Type (sollte `-> dict` oder `-> Any` sein)
- `**kwargs` untypisiert (sollte `**kwargs: Any` sein)
- Dasselbe Pattern in `update_board`, `update_card`, `update_label`,
  `update_webhook` (`client.py:109, 142, 166, 262`)

**Empfehlung:** Return-Type ergaenzen. Fuer `update_*`-Methoden
pruefen, ob TypedDict oder explizite Parameter besser waeren als
**kwargs.

#### B-4: `typing`-Importe statt moderner Syntax

`client.py:5` und `models.py:1` importieren `Optional`, `List`,
`Union` aus `typing`, obwohl das Projekt Python >=3.10 voraussetzt
und in `models.py:23,82` bereits die moderne `|`-Syntax verwendet.

**Dateien:** `src/trellio/client.py:5`, `src/trellio/models.py:1`

**Empfehlung:** Konsistent auf `list[...]`, `X | None`,
`X | Y` umstellen und `typing`-Importe entfernen.

#### B-5: python-dotenv Inkonsistenz

`requirements.txt` listet `python-dotenv>=1.0.0`, aber
`pyproject.toml` nicht. Die kanonische Abhaengigkeitsliste ist
pyproject.toml. Nutzer, die `pip install trellio-client` ausfuehren,
bekommen python-dotenv nicht installiert.

**Dateien:** `requirements.txt:3`, `pyproject.toml:28-30`

**Empfehlung:** Entweder python-dotenv in `pyproject.toml`
aufnehmen (falls es zur Laufzeit benoetigt wird) oder aus
requirements.txt entfernen (falls es nur fuer Entwicklung ist).

#### B-6: Bare except in Test-Infrastruktur

`features/environment.py:23` und
`tests/validation/test_mock_with_pytrello.py:36` verwenden
blanke `except:`-Klauseln.

**Empfehlung:** Durch `except (ConnectionError, OSError):` oder
`except Exception:` ersetzen.

#### B-7: delete-Methoden ohne Return-Type

`delete_board`, `delete_card`, `delete_label`, `delete_checklist`,
`delete_check_item`, `delete_comment`, `delete_attachment`,
`delete_webhook` (`client.py:113, 146, 170, 188, 199, 216, 242,
266`) haben keine Return-Type-Annotation.

**Empfehlung:** `-> None` ergaenzen.

#### B-8: Kein Retry-Jitter

Der Backoff in `client.py:64` ist deterministisch:

```python
delay = self.initial_delay * (self.backoff_factor ** attempt)
```

Bei mehreren parallelen Clients fuehrt das zu synchronisierten
Retry-Wellen (Thundering Herd). Fuer den aktuellen Einsatz als
Single-Client akzeptabel, aber fuer verteilte Umgebungen ein
Problem.

**Datei:** `src/trellio/client.py`, Zeile 64

**Empfehlung:** Optional Jitter einfuegen, z.B.:
```python
import random
delay = delay * (0.5 + random.random())
```

---

## 3. Massnahmenkatalog

### Pflicht -- vor Produktivfreigabe

| ID   | Massnahme | Aufwand | Dateien |
|------|-----------|---------|---------|
| P-1  | **Lock-File erstellen.** `pip-compile` (pip-tools) oder Migration zu Poetry. Lock-File in Git committen. | Klein | neues `requirements.lock` oder `poetry.lock` |
| P-2  | **SECURITY.md erstellen.** Vulnerability-Reporting-Prozess, Threat Model (analog zu trellio-mcp). | Klein | neues `SECURITY.md` |
| P-3  | **python-dotenv-Inkonsistenz beheben.** Entweder in pyproject.toml aufnehmen oder aus requirements.txt entfernen. | Trivial | `pyproject.toml`, `requirements.txt` |

### Hoch -- innerhalb 90 Tagen

| ID   | Massnahme | Aufwand | Dateien |
|------|-----------|---------|---------|
| E-1  | **CI/CD-Pipeline einrichten.** GitHub Actions mit ruff, pip-audit, behave, pytest. Workflow bei PRs auf main. | Mittel | neues `.github/workflows/ci.yml` |
| E-2  | **HTTP-Statuscode-Behandlung erweitern.** 2xx-Range als Erfolg akzeptieren; 204 ohne Body-Parsing behandeln. | Klein | `src/trellio/client.py:53` (Befund B-1) |
| E-3  | **HTTPS-Validierung in `__init__`.** Warnung oder Fehler, wenn base_url nicht mit `https://` beginnt (ausser in Tests). | Klein | `src/trellio/client.py:21` |
| E-4  | **Dependency-Pinning verschaerfen.** Von `>=` auf `~=`: `httpx~=0.24.0`, `pydantic~=2.0.0`. | Trivial | `pyproject.toml:28-30` |

### Mittel -- innerhalb 6 Monaten

| ID   | Massnahme | Aufwand | Dateien |
|------|-----------|---------|---------|
| E-5  | **Docstrings fuer oeffentliche API.** Mindestens `__init__`, `_authenticated_request`, und Methoden mit nicht-offensichtlichen Parametern. | Klein | `src/trellio/client.py` (Befund B-2) |
| E-6  | **Typ-Annotationen vervollstaendigen.** Return-Types fuer alle Methoden; `**kwargs: Any`; delete-Methoden `-> None`. | Klein | `src/trellio/client.py` (Befunde B-3, B-7) |
| E-7  | **Moderne typing-Syntax.** `Optional`, `List`, `Union` durch `X | None`, `list[X]`, `X | Y` ersetzen. | Trivial | `client.py:5`, `models.py:1` (Befund B-4) |

### Code-Qualitaet -- bei naechster Gelegenheit

| ID   | Massnahme | Aufwand | Dateien |
|------|-----------|---------|---------|
| Q-1  | **Bare except in Tests ersetzen.** `except:` durch spezifische Exception-Typen ersetzen. | Trivial | Befund B-6 |
| Q-2  | **Retry-Jitter einfuegen.** Optionaler Random-Faktor auf den Backoff-Delay. | Trivial | Befund B-8 |
