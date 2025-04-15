# 🧠 Coderr Backend

Das **Coderr Backend** ist das Herzstück der Programmierer-Dienstleistungs-Plattform **Coderr**.  
Hier können sich **Programmierer:innen (Business User)** und **Kund:innen (Customer User)** registrieren, Angebote erstellen oder suchen, Bestellungen aufgeben, Bewertungen abgeben und ihre Profile verwalten.

> 🔗 **Frontend-Repo (folgt)**  
> 📖 **[API-Dokumentation (Swagger)](https://cdn.developerakademie.com/courses/Backend/EndpointDoku/index.html?name=coderr)**

---

## 🚀 Features

- 🔐 **Token Authentication**
- 🛠️ **CRUD** für:
  - `Offer`
  - `Order`
  - `Review`
- 🔎 **Such- und Filterfunktionen** für Angebote
- 👤 Benutzer-Registrierung & -Profile für zwei Rollen:
  - Business User (Programmierer:innen)
  - Customer User (Auftraggeber:innen)

---

## 🛠️ Technologien

- Python 3.13.1
- Django 5.1.7
- Django REST Framework (DRF)
- SQLite (lokale Entwicklung)
- Wichtige Libraries:
  - `django-cors-headers`
  - `django-filter`
  - `asgiref`
  - `sqlparse`
  - `tzdata`

---

## ⚙️ Installation & Setup

```bash
# 1. Repository klonen
git clone <repo-url>
cd coderr-backend

# 2. Virtuelle Umgebung erstellen & aktivieren
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Migrationen durchführen
python manage.py migrate

# 5. Entwicklungsserver starten
python manage.py runserver
