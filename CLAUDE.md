# CLAUDE.md - AI Assistant Guide for Les Silences du Vin

> **Last Updated:** 2025-11-20
> **Version:** G3R3C8
> **Project:** E-commerce Flask application for wine sales

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Architecture](#project-architecture)
4. [Key Development Conventions](#key-development-conventions)
5. [Database Schema & Models](#database-schema--models)
6. [Routing & Blueprints](#routing--blueprints)
7. [Security & Authentication](#security--authentication)
8. [Payment Flow (Stripe)](#payment-flow-stripe)
9. [Git Workflow](#git-workflow)
10. [Common Tasks](#common-tasks)
11. [Important Context for AI Assistants](#important-context-for-ai-assistants)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

**Les Silences du Vin** is a professional e-commerce Flask application for selling wine online. The project follows French legal requirements (RGPD/GDPR, CGV, Mentions légales) and is deployed on PythonAnywhere.

### Key Features
- Dynamic wine catalog from SQLite database
- Session-based shopping cart with AJAX updates
- Stripe payment integration
- User authentication and saved carts
- Multi-recipient contact form via SMTP
- Age verification gate
- SEO optimization (sitemap, robots.txt)
- Responsive Bootstrap 5 design
- Multi-language support structure (French/Italian)

### Business Domain
- **Product:** Wines (Rouge/Red, Blanc/White, Garde/Aging)
- **Target:** French market (B2C)
- **Legal:** GDPR compliant, CGV, privacy policy
- **Payment:** Stripe Checkout (card payments)
- **Deployment:** PythonAnywhere (production)

---

## 🛠️ Technology Stack

### Backend
- **Framework:** Flask 2.x (Python web framework)
- **ORM:** Flask-SQLAlchemy (models) + raw SQLite (legacy vins table)
- **Database:** SQLite (`app/data/vins.db`)
- **Authentication:** Flask-Login
- **Forms:** Flask-WTF + WTForms
- **Email:** SMTP/SSL (OVH mail server)
- **Payment:** Stripe Checkout API
- **i18n:** Flask-Babel (configured but not fully implemented)

### Frontend
- **CSS Framework:** Bootstrap 5 (CDN)
- **Icons:** Bootstrap Icons
- **JavaScript:** Vanilla JS (Fetch API for AJAX)
- **Templates:** Jinja2

### Development Tools
- **Version Control:** Git
- **Environment:** python-dotenv
- **Deployment:** PythonAnywhere + WSGI
- **Logging:** Python logging to `app/data/app.log`

---

## 🏗️ Project Architecture

### Directory Structure

```
lessilencesduvin/
├── app/                          # Main application package
│   ├── __init__.py              # Factory pattern: create_app()
│   ├── data/                    # Database and utilities
│   │   ├── vins.py             # Database query helpers
│   │   └── vins.db             # SQLite database (gitignored)
│   ├── forms/                   # WTForms definitions
│   │   ├── auth_form.py        # RegistrationForm, LoginForm
│   │   ├── checkout.py         # GuestCheckoutForm (post-payment)
│   │   └── contact_form.py     # ContactForm
│   ├── models/                  # SQLAlchemy models
│   │   ├── user.py             # User (Flask-Login)
│   │   ├── commandes.py        # Commande, CommandeProduit
│   │   └── panier_sauvegarde.py # PanierSauvegarde
│   ├── routes/                  # Blueprint-based routing
│   │   ├── auth/               # Login, register, logout
│   │   ├── blanc/              # White wines listing
│   │   ├── catalogue/          # Main catalog page
│   │   ├── contact/            # Contact form
│   │   ├── garde/              # Aging wines
│   │   ├── legales/            # Legal pages
│   │   ├── main/               # Homepage, SEO files
│   │   ├── paiement/           # Stripe payment flow
│   │   ├── panier/             # Shopping cart CRUD
│   │   ├── rouge/              # Red wines listing
│   │   └── vins/               # Dynamic wine listing
│   ├── static/                  # Static assets
│   │   ├── css/                # Stylesheets
│   │   ├── img/                # Images (logo, wines, categories)
│   │   └── js/                 # JavaScript files
│   ├── templates/              # Jinja2 templates
│   │   ├── auth/               # Authentication pages
│   │   ├── legales/            # Legal pages
│   │   ├── paiement/           # Payment flow
│   │   └── base.html           # Base template
│   ├── utils/                   # Utility functions
│   │   └── panier_tools.py     # Cart session management
│   ├── translations.py          # i18n translations
│   └── _archives/              # Legacy code (versioned)
├── config/                      # Configuration module
│   ├── config.py               # Config classes
│   └── .env                    # Environment variables (gitignored)
├── translations/               # Babel translations
├── initdb.py                   # Database initialization
├── run.py                      # Development server entry point
├── babel.cfg                   # Babel extraction config
├── DEPLOY.md                   # Deployment documentation
└── .gitignore                  # Git ignore rules
```

### Application Factory Pattern

The application uses the factory pattern in `app/__init__.py`:

```python
def create_app(config_class='config.config.ProductionConfig'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(catalogue_bp)
    # ... more blueprints

    # Context processor for cart counter
    @app.context_processor
    def inject_panier_count():
        return {'panier_count': get_compteur_panier()}

    return app
```

**Key Points:**
- Use `create_app()` to initialize the application
- Configuration passed as parameter (defaults to ProductionConfig)
- All blueprints registered in `create_app()`
- Global context processor injects `panier_count` to all templates

---

## 🔑 Key Development Conventions

### 1. Commit Message Format

Commits follow the pattern: **G{Génération}R{Release}C{Commit}**

**Examples:**
- `G1R0C1` - Generation 1, Release 0, Commit 1 (initial setup)
- `G1R2C3` - Generation 1, Release 2, Commit 3 (feature addition)
- `G3R3C8` - Generation 3, Release 3, Commit 8 (current version)

**Commit Message Structure:**
```
G3R3C8 - Brief description

Optional detailed explanation:
- Change 1
- Change 2
- Change 3
```

### 2. Blueprint Organization

Each route module follows this structure:

```
app/routes/<module>/
├── __init__.py     # Exports <module>_bp
└── routes.py       # Route definitions
```

**Example** (`app/routes/catalogue/`):

```python
# __init__.py
from app.routes.catalogue.routes import catalogue_bp

# routes.py
from flask import Blueprint, render_template

catalogue_bp = Blueprint('catalogue', __name__, url_prefix='/catalogue')

@catalogue_bp.route('/')
def index():
    return render_template('catalogue.html')
```

### 3. Code Style

**Naming Conventions:**
- **Blueprints:** `<module>_bp` (e.g., `panier_bp`, `auth_bp`)
- **Route functions:** Descriptive verbs (e.g., `index`, `ajouter`, `update_cart`)
- **Templates:** Lowercase with underscores (e.g., `vins_couleur.html`)
- **Database tables:** Lowercase (e.g., `users`, `commandes`)
- **Models:** CamelCase (e.g., `User`, `Commande`, `PanierSauvegarde`)

**Language:**
- Code comments: French
- Variable names: French or English (mixed)
- Template text: French (primary), Italian (partial support)

**Security Practices:**
- All forms use CSRF protection (Flask-WTF)
- Passwords hashed with Werkzeug
- Environment variables for secrets
- HTTPS redirect in production
- `@login_required` for protected routes

### 4. Template Hierarchy

All templates extend `base.html`:

```html
{% extends 'base.html' %}

{% block content %}
<!-- Page-specific content -->
{% endblock %}
```

**Base Template Features:**
- Age verification gate
- Cookie consent banner
- Responsive navbar with cart counter
- Flash messages (Bootstrap alerts)
- Footer with legal links
- Global JavaScript for cart operations

### 5. Flash Messages

Use Flask's `flash()` with Bootstrap categories:

```python
from flask import flash

flash("Votre message a bien été envoyé.", "success")  # Green
flash("Erreur lors de l'envoi.", "danger")           # Red
flash("Attention : champ manquant.", "warning")      # Yellow
flash("Information importante.", "info")              # Blue
```

Messages auto-dismiss after 3.5 seconds (configured in `base.html`).

---

## 🗄️ Database Schema & Models

### Dual Database Access Pattern

The application uses **two database access methods**:

1. **SQLAlchemy ORM** - For new tables (users, commandes, paniers_sauvegardes)
2. **Raw SQLite** - For legacy vins table (via `get_db()` in `app/data/vins.py`)

**Migration Note:** V3 aims to migrate `vins` table to SQLAlchemy model (flag: `USE_SQLALCHEMY`).

### SQLAlchemy Models

#### User Model (`app/models/user.py`)

```python
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    commandes = db.relationship('Commande', backref='user', lazy=True)
    paniers_sauvegardes = db.relationship('PanierSauvegarde', backref='user', lazy=True)
```

**Key Methods:**
- `set_password(password)` - Hash and store password
- `check_password(password)` - Verify password
- `get_id()` - Flask-Login required method

#### Commande Model (`app/models/commandes.py`)

```python
class Commande(db.Model):
    __tablename__ = 'commandes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    # Customer info
    prenom = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    telephone = db.Column(db.String(20))

    # Addresses
    adresse_livraison = db.Column(db.Text, nullable=False)
    ville_livraison = db.Column(db.String(100), nullable=False)
    code_postal_livraison = db.Column(db.String(10), nullable=False)
    # ... billing address fields

    # Payment
    total_ttc = db.Column(db.Float, nullable=False)
    devise = db.Column(db.String(3), default='EUR')
    stripe_session_id = db.Column(db.String(255), unique=True)
    statut = db.Column(db.String(50), default='en_attente')

    # Timestamps
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    produits = db.relationship('CommandeProduit', backref='commande', lazy=True)
```

**Statuses:**
- `en_attente` - Payment created, awaiting confirmation
- `payé` - Payment confirmed by Stripe
- `complétée` - Customer info filled, order complete
- `abandonnée` - Payment cancelled or expired

#### CommandeProduit Model (Order Line Items)

```python
class CommandeProduit(db.Model):
    __tablename__ = 'commandes_produits'

    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commandes.id'), nullable=False)
    produit_id = db.Column(db.Integer, nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)
```

#### PanierSauvegarde Model (`app/models/panier_sauvegarde.py`)

```python
class PanierSauvegarde(db.Model):
    __tablename__ = 'paniers_sauvegardes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    contenu_json = db.Column(db.Text, nullable=False)  # JSON string
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
```

**Cart JSON Format:**
```json
{
  "123": {"quantite": 2},
  "456": {"quantite": 1}
}
```

### Legacy Vins Table (Raw SQLite)

Accessed via `get_db()` in `app/data/vins.py`:

```sql
CREATE TABLE vins (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    domaine TEXT,
    millesime INTEGER,
    couleur TEXT,  -- 'rouge', 'blanc', 'rosé'
    prix REAL,
    image TEXT,     -- Filename in app/static/img/vins/
    accord TEXT     -- Food pairing suggestions
);
```

**Query Helpers** (`app/data/vins.py`):

```python
def get_vins_by_couleur(couleur):
    """Fetch wines by color"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM vins WHERE couleur = ?", (couleur,))
    return cursor.fetchall()

def get_vin_by_id(vin_id):
    """Fetch single wine by ID"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM vins WHERE id = ?", (vin_id,))
    return cursor.fetchone()
```

---

## 🛣️ Routing & Blueprints

### Blueprint Registry

| Blueprint | Prefix | Description |
|-----------|--------|-------------|
| `main_bp` | `/` | Homepage, SEO files (robots.txt, sitemap.xml) |
| `catalogue_bp` | `/catalogue` | Wine catalog page |
| `contact_bp` | `/contact` | Contact form with SMTP |
| `rouge_bp` | `/rouge` | Red wines listing |
| `blanc_bp` | `/blanc` | White wines listing |
| `garde_bp` | `/garde` | Aging wines (millesime <= 2018) |
| `vins_bp` | `/vins/<couleur>` | Dynamic wine listing by color |
| `legales_bp` | `/legales` | Legal pages (mentions, CGV, privacy) |
| `panier_bp` | `/panier` | Shopping cart CRUD operations |
| `auth_bp` | `/auth` | User authentication (login, register, logout) |
| `paiement_bp` | `/paiement` | Stripe payment flow |

### Key Routes

#### Shopping Cart (`app/routes/panier/routes.py`)

```python
@panier_bp.route('/')
def index():
    """Display cart contents"""

@panier_bp.route('/ajouter', methods=['POST'])
def ajouter():
    """Add item to cart (AJAX endpoint)"""

@panier_bp.route('/update_cart', methods=['POST'])
def update_cart():
    """Update quantity or remove item (AJAX)"""

@panier_bp.route('/compteur')
def compteur():
    """Get cart count (AJAX endpoint)"""

@panier_bp.route('/enregistrer', methods=['POST'])
@login_required
def enregistrer():
    """Save cart to database (authenticated users only)"""
```

#### Payment Flow (`app/routes/paiement/routes.py`)

```python
@paiement_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe Checkout session"""

@paiement_bp.route('/success')
def success():
    """Handle successful payment"""

@paiement_bp.route('/cancel')
def cancel():
    """Handle cancelled payment"""

@paiement_bp.route('/infos-livraison', methods=['GET', 'POST'])
def infos_livraison():
    """Collect shipping info after payment"""

@paiement_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
```

#### Authentication (`app/routes/auth/routes.py`)

```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
```

---

## 🔐 Security & Authentication

### Flask-Login Configuration

**Setup** (`app/__init__.py`):

```python
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.session_protection = 'strong'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

### Protected Routes

Use `@login_required` decorator:

```python
from flask_login import login_required, current_user

@panier_bp.route('/enregistrer', methods=['POST'])
@login_required
def enregistrer():
    # Only accessible to authenticated users
    pass
```

### Session Configuration

**Development:**
```python
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
```

**Production:**
```python
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
```

### CSRF Protection

All forms include CSRF token:

```html
<form method="POST">
    {{ form.hidden_tag() }}
    <!-- Form fields -->
</form>
```

### Password Hashing

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Set password
user.password_hash = generate_password_hash('password123')

# Verify password
is_valid = check_password_hash(user.password_hash, 'password123')
```

---

## 💳 Payment Flow (Stripe)

### Checkout Process

**Step 1: Create Checkout Session** (`/paiement/create-checkout-session`)

1. Validate cart is not empty
2. Create `Commande` record (status: `en_attente`)
3. Create `CommandeProduit` records for each cart item
4. Create Stripe Checkout Session
5. Link `Commande` to `stripe_session_id`
6. Redirect user to Stripe Checkout

**Step 2: Payment Completion**

User completes payment on Stripe → redirected to `/paiement/success?session_id=xxx`

**Step 3: Success Handler** (`/paiement/success`)

1. Retrieve Stripe session
2. Update `Commande` status to `payé`
3. Redirect to `/paiement/infos-livraison`

**Step 4: Shipping Info** (`/paiement/infos-livraison`)

1. Display `GuestCheckoutForm`
2. Collect customer and shipping details
3. Update `Commande` with customer info
4. Update status to `complétée`
5. Clear cart session
6. Display confirmation

**Cancellation Flow** (`/paiement/cancel`)

1. Save cart to `paniers_sauvegardes` (if authenticated)
2. Update `Commande` status to `abandonnée`
3. Display message: cart preserved for retry

### Stripe Configuration

**Environment Variables:**
```bash
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

**Checkout Session Config:**
```python
checkout_session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[...],
    mode='payment',
    success_url=url_for('paiement.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
    cancel_url=url_for('paiement.cancel', _external=True),
    metadata={'commande_id': commande.id}
)
```

### Webhook Handling

**Endpoint:** `/paiement/webhook/stripe`

**Events:**
- `checkout.session.completed` - Payment successful
- `checkout.session.expired` - Session expired

**Verification:**
```python
stripe.Webhook.construct_event(
    payload,
    sig_header,
    app.config['STRIPE_WEBHOOK_SECRET']
)
```

---

## 🌿 Git Workflow

### Branch Strategy

**Production Branch:** `main` (or specified in DEPLOY.md)
**Feature Branches:** Prefix with `claude/` for AI assistant work

**Current Working Branch:**
```
claude/claude-md-mi7a40q2s4kgy25c-01JWjzSWS8wkExPxSZ9ucaYp
```

### Commit Guidelines

**Format:** `G{Gen}R{Release}C{Commit} - Description`

**Examples:**
```bash
git commit -m "G3R3C9 - Add requirements.txt file"
git commit -m "G3R4C1 - Refactor vins table to SQLAlchemy model"
```

**Best Practices:**
- Keep commits atomic (one logical change)
- Write clear, descriptive messages in French
- Reference issue numbers if applicable
- Use present tense ("Add" not "Added")

### Deployment to PythonAnywhere

**Steps:**

1. **Commit changes locally:**
   ```bash
   git add .
   git commit -m "G3R3C9 - Description"
   ```

2. **Push to remote:**
   ```bash
   git push -u origin <branch-name>
   ```

3. **Pull on PythonAnywhere:**
   ```bash
   cd ~/lessilencesduvin
   git pull origin <branch-name>
   ```

4. **Reload WSGI application:**
   - Go to PythonAnywhere Web tab
   - Click "Reload" button

5. **Verify deployment:**
   - Test affected routes
   - Check error logs if issues arise

### Files to Never Commit

See `.gitignore`:

```
# Secrets
.env
*.db (except vins.db)

# System
*.DS_Store
__pycache__/

# Virtual environments
venv/
ENV/

# Logs
*.log

# Backups
sauvegardes/
```

---

## 🛠️ Common Tasks

### 1. Add a New Route

**Step 1:** Create blueprint structure

```bash
mkdir -p app/routes/monmodule
touch app/routes/monmodule/__init__.py
touch app/routes/monmodule/routes.py
```

**Step 2:** Define routes (`app/routes/monmodule/routes.py`)

```python
from flask import Blueprint, render_template

monmodule_bp = Blueprint('monmodule', __name__, url_prefix='/monmodule')

@monmodule_bp.route('/')
def index():
    return render_template('monmodule.html')
```

**Step 3:** Export blueprint (`app/routes/monmodule/__init__.py`)

```python
from app.routes.monmodule.routes import monmodule_bp
```

**Step 4:** Register in application factory (`app/__init__.py`)

```python
from app.routes.monmodule import monmodule_bp

def create_app(...):
    # ...
    app.register_blueprint(monmodule_bp)
    # ...
```

**Step 5:** Create template (`app/templates/monmodule.html`)

```html
{% extends 'base.html' %}

{% block content %}
<h1>Mon Module</h1>
{% endblock %}
```

### 2. Add a New Database Model

**Step 1:** Create model file (`app/models/mon_modele.py`)

```python
from app import db
from datetime import datetime

class MonModele(db.Model):
    __tablename__ = 'mon_modele'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Step 2:** Import in `app/__init__.py`

```python
from app.models.mon_modele import MonModele
```

**Step 3:** Create migration (in Flask shell or initdb.py)

```python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
```

### 3. Update Shopping Cart Logic

**Cart stored in session:**

```python
from flask import session
from app.utils.panier_tools import get_session_panier, set_session_panier

# Get cart
panier = get_session_panier()  # Returns dict: {product_id: {'quantite': n}}

# Add item
panier[product_id] = {'quantite': quantity}
set_session_panier(panier)

# Update item
if product_id in panier:
    panier[product_id]['quantite'] += 1
    set_session_panier(panier)

# Remove item
if product_id in panier:
    del panier[product_id]
    set_session_panier(panier)

# Clear cart
set_session_panier({})
```

### 4. Add a New Form

**Step 1:** Create form class (`app/forms/mon_form.py`)

```python
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

class MonForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Envoyer')
```

**Step 2:** Use in route

```python
from app.forms.mon_form import MonForm

@mon_bp.route('/formulaire', methods=['GET', 'POST'])
def formulaire():
    form = MonForm()
    if form.validate_on_submit():
        # Process form data
        nom = form.nom.data
        email = form.email.data
        flash('Formulaire envoyé !', 'success')
        return redirect(url_for('mon.index'))
    return render_template('formulaire.html', form=form)
```

**Step 3:** Render in template

```html
<form method="POST">
    {{ form.hidden_tag() }}

    <div class="mb-3">
        {{ form.nom.label }}
        {{ form.nom(class='form-control') }}
    </div>

    <div class="mb-3">
        {{ form.email.label }}
        {{ form.email(class='form-control') }}
    </div>

    <div class="mb-3">
        {{ form.message.label }}
        {{ form.message(class='form-control', rows=5) }}
    </div>

    {{ form.submit(class='btn btn-primary') }}
</form>
```

### 5. Send Email via SMTP

```python
import smtl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, recipients):
    """Send email via OVH SMTP"""
    msg = MIMEMultipart()
    msg['From'] = current_app.config['MAIL_USERNAME']
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP_SSL(
            current_app.config['MAIL_SERVER'],
            current_app.config['MAIL_PORT']
        )
        server.login(
            current_app.config['MAIL_USERNAME'],
            current_app.config['MAIL_PASSWORD']
        )
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        current_app.logger.error(f"Email error: {e}")
        return False
```

### 6. Query Database (Legacy Vins Table)

```python
from app.data.vins import get_db

def get_vins_by_couleur(couleur):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM vins WHERE couleur = ?", (couleur,))
    return cursor.fetchall()
```

### 7. Query Database (SQLAlchemy Models)

```python
from app.models.user import User
from app.models.commandes import Commande

# Get user by email
user = User.query.filter_by(email='user@example.com').first()

# Get all orders for user
orders = Commande.query.filter_by(user_id=user.user_id).all()

# Get paid orders only
paid_orders = Commande.query.filter_by(statut='payé').all()

# Complex query with join
from app import db
orders_with_user = db.session.query(Commande, User)\
    .join(User, Commande.user_id == User.user_id)\
    .filter(Commande.statut == 'complétée')\
    .all()
```

---

## 🤖 Important Context for AI Assistants

### What You Should Know

1. **Language Preference:**
   - Code comments: French
   - User-facing text: French (primary)
   - Variable names: Mixed (French business terms, English technical terms)
   - Commit messages: French

2. **Development Environment:**
   - Production: PythonAnywhere (SSH access via Git)
   - Development: Local Flask server (`python run.py`)
   - Database: SQLite (single file, no migrations yet)
   - No formal test suite (manual testing only)

3. **Current State (G3R3C8):**
   - Full e-commerce functionality operational
   - Stripe payment integration complete
   - User authentication working
   - Shopping cart with session persistence
   - Legal pages compliant (RGPD, CGV)
   - Responsive design implemented

4. **Known Technical Debt:**
   - No `requirements.txt` file (create if needed)
   - Legacy `vins` table not yet migrated to SQLAlchemy
   - No formal test suite (pytest, unittest)
   - Mixed template naming conventions
   - Babel configured but translations incomplete

5. **Security Context:**
   - All secrets in `.env` (never commit!)
   - CSRF protection enabled globally
   - HTTPS enforced in production
   - Session cookies: HttpOnly, Secure (prod), SameSite=Lax
   - Passwords hashed with Werkzeug

### When Making Changes

**Always:**
- ✅ Follow the commit naming convention (G#R#C#)
- ✅ Test locally before pushing
- ✅ Preserve existing functionality
- ✅ Add CSRF tokens to forms
- ✅ Use `@login_required` for protected routes
- ✅ Use flash messages for user feedback
- ✅ Maintain Bootstrap 5 design consistency
- ✅ Add database queries to appropriate helpers
- ✅ Keep cart logic in `app/utils/panier_tools.py`

**Never:**
- ❌ Commit `.env` files or secrets
- ❌ Commit `*.db` files (except `vins.db` if intentional)
- ❌ Break existing routes without migration plan
- ❌ Remove CSRF protection
- ❌ Hardcode secrets in code
- ❌ Push directly to `main` without testing
- ❌ Modify payment flow without understanding Stripe integration

### Common Gotchas

1. **Database Location:**
   - Database path: `app/data/vins.db`
   - Not in project root, not in `instance/`

2. **Cart Counter:**
   - Injected globally via context processor
   - Available in all templates as `{{ panier_count }}`
   - Calculated from session, not database

3. **Stripe Keys:**
   - Different for development (test keys) and production (live keys)
   - Always validate `STRIPE_WEBHOOK_SECRET` exists in production

4. **Session Management:**
   - Cart stored in Flask session (server-side)
   - Session expires after 2 hours (configurable)
   - Saved carts persist in database (for authenticated users)

5. **Blueprint Registration Order:**
   - Must register blueprints in `create_app()` before app starts
   - URL prefix defined in blueprint creation

6. **Template Inheritance:**
   - All pages extend `base.html`
   - Use `{% block content %}` for page-specific content
   - Flash messages rendered in `base.html`

### Useful Debug Commands

```bash
# Check Flask routes
flask --app run routes

# Access Flask shell
flask --app run shell

# Check database schema
sqlite3 app/data/vins.db ".schema"

# Count wines by color
sqlite3 app/data/vins.db "SELECT couleur, COUNT(*) FROM vins GROUP BY couleur;"

# Check users
sqlite3 app/data/vins.db "SELECT * FROM users;"

# Check recent orders
sqlite3 app/data/vins.db "SELECT id, statut, total_ttc, date_creation FROM commandes ORDER BY date_creation DESC LIMIT 10;"
```

### Testing Checklist

Before deploying changes:

- [ ] Cart operations work (add, update, remove)
- [ ] Cart counter updates in navbar
- [ ] Payment flow completes successfully (test mode)
- [ ] Login/logout works
- [ ] Flash messages display correctly
- [ ] Forms validate properly
- [ ] CSRF tokens present
- [ ] No console errors in browser
- [ ] Responsive design intact
- [ ] Legal pages accessible
- [ ] Email sending works (contact form)

---

## 🐛 Troubleshooting

### Issue: "Application failed to start"

**Cause:** Missing environment variables or configuration error

**Solution:**
1. Check `.env` file exists in `config/` directory
2. Verify all required variables are set:
   ```
   SECRET_KEY
   DATABASE_URL
   MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
   STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY
   ```
3. Check `config/config.py` loads `.env` correctly

### Issue: "Template not found"

**Cause:** Template path incorrect or file missing

**Solution:**
1. Verify template exists in `app/templates/`
2. Check template name matches exactly (case-sensitive)
3. Ensure blueprint's `template_folder` not overriding default

### Issue: "Cart counter shows 0 despite items"

**Cause:** Session not persisting or context processor issue

**Solution:**
1. Check `get_compteur_panier()` in `app/utils/panier_tools.py`
2. Verify context processor in `app/__init__.py`
3. Check session configuration (secret key, cookie settings)

### Issue: "Stripe payment fails"

**Cause:** API key mismatch or webhook misconfigured

**Solution:**
1. Verify `STRIPE_PUBLIC_KEY` and `STRIPE_SECRET_KEY` match (test vs. live)
2. Check Stripe dashboard for error details
3. Verify webhook endpoint registered in Stripe dashboard
4. Test with Stripe CLI: `stripe listen --forward-to localhost:5000/paiement/webhook/stripe`

### Issue: "CSRF token missing or invalid"

**Cause:** Form missing `{{ form.hidden_tag() }}` or session issue

**Solution:**
1. Add `{{ form.hidden_tag() }}` to all forms
2. Verify `WTF_CSRF_ENABLED = True` in config
3. Check `SECRET_KEY` is set and consistent

### Issue: "Database locked"

**Cause:** SQLite concurrency issue (rare in development)

**Solution:**
1. Close all database connections
2. Restart Flask application
3. Consider migrating to PostgreSQL for production if persistent

### Issue: "Email not sending"

**Cause:** SMTP credentials incorrect or port blocked

**Solution:**
1. Verify SMTP credentials in `.env`
2. Test connection manually:
   ```python
   import smtplib
   server = smtplib.SMTP_SSL('ssl0.ovh.net', 465)
   server.login('username', 'password')
   server.quit()
   ```
3. Check firewall allows port 465 (SSL)

---

## 📚 Additional Resources

### Documentation Files
- **DEPLOY.md** - Deployment history and PythonAnywhere setup
- **.gitignore** - Files excluded from version control
- **babel.cfg** - i18n extraction configuration

### External Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-Login](https://flask-login.readthedocs.io/)
- [WTForms](https://wtforms.readthedocs.io/)
- [Stripe Checkout](https://stripe.com/docs/payments/checkout)
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)

### Key Contacts
- **Developer:** Isalys Creuzeau (isalys.creuzeau@gmail.com)
- **Deployment:** PythonAnywhere
- **Email Server:** OVH (ssl0.ovh.net:465)

---

## 🎯 Next Steps & Roadmap

### V3 Priorities (Current)
- [x] Stripe payment integration
- [x] User authentication
- [x] Saved carts
- [ ] Create `requirements.txt`
- [ ] Migrate `vins` table to SQLAlchemy
- [ ] Add automated tests

### V4 Future Enhancements
- [ ] User account dashboard
- [ ] Order history
- [ ] Inventory management
- [ ] Admin panel
- [ ] Product reviews
- [ ] Wishlist functionality
- [ ] Email order confirmations
- [ ] Newsletter subscription

---

**Last Updated:** 2025-11-20 by Claude
**Version:** G3R3C8
**Status:** ✅ Production-ready

For questions or clarifications, refer to `DEPLOY.md` or examine the codebase directly.