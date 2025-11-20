from flask import Flask, render_template_string, request, redirect, url_for, session, flash, g
from functools import wraps
import json, os
from datetime import datetime
import sqlite3


app = Flask(__name__)

app.secret_key = "velocity_secret_2025_ultimate"

DATABASE_NAME = "velocitySales.db"


@app.teardown_appcontext
def close_db(exception=None):

    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def get_db():

    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_NAME)

        db.row_factory = sqlite3.Row
    return db


def init_db():

    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client TEXT NOT NULL,
                product_name TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL
            );
        """)
        db.commit()



init_db()


USER_FILE = "users.json"


def load_users():

    if not os.path.exists(USER_FILE):
        initial_users = {"admin": "password123"}
        with open(USER_FILE, "w") as f:
            json.dump(initial_users, f)
        return initial_users

    with open(USER_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_users(users):

    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)



def login_required(f):
    """Decorator to protect routes, redirecting unauthenticated users to the login page."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in to access the Velocity Dashboard.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function




BASE_CSS = """
<style>
    /* Color Palette: Blue/Teal/White for a professional, energetic look */
    :root {
        --primary-color: #0079C1; /* Velocity Blue */
        --accent-color: #00BCD4;  /* Teal for highlights */
        --text-color: #333;
        --bg-light: #f7f9fb;
        --bg-white: #ffffff;
        --shadow-elevation: 0 4px 12px rgba(0,0,0,0.05);
        --danger-color: #EF476F;
        --success-color: #06D6A0;
    }
    body { 
        font-family: 'Inter', sans-serif; 
        margin: 0; 
        padding: 0; 
        background-color: var(--bg-light); 
        color: var(--text-color); 
    }
    .container { 
        max-width: 1000px; 
        margin: 40px auto; 
        padding: 30px; 
        border-radius: 16px; 
        background-color: var(--bg-white); 
        box-shadow: var(--shadow-elevation); 
        transition: all 0.3s ease;
    }
    h1, h2 { 
        color: var(--primary-color); 
        border-bottom: 2px solid #e0e0e0; 
        padding-bottom: 15px; 
        margin-bottom: 25px; 
        font-weight: 600;
    }
    h1 { font-size: 2.2em; }
    h2 { font-size: 1.6em; }

    /* Forms and Inputs */
    input[type="text"], input[type="number"], input[type="date"], input[type="password"] { 
        width: 100%; 
        padding: 12px 15px; 
        margin: 8px 0; 
        border: 1px solid #ccc; 
        border-radius: 8px; 
        box-sizing: border-box; 
        transition: border-color 0.3s, box-shadow 0.3s; 
    }
    input:focus { 
        border-color: var(--accent-color); 
        box-shadow: 0 0 0 3px rgba(0, 121, 193, 0.2);
        outline: none; 
    }

    /* Buttons */
    input[type="submit"], .btn { 
        background-color: var(--primary-color); 
        color: white; 
        padding: 12px 25px; 
        border: none; 
        border-radius: 8px; 
        cursor: pointer; 
        text-decoration: none; 
        display: inline-block; 
        margin-top: 10px; 
        font-weight: 600; 
        transition: background-color 0.3s, transform 0.1s; 
    }
    input[type="submit"]:hover, .btn:hover { 
        background-color: #005a92; 
        transform: translateY(-2px); 
        box-shadow: 0 4px 8px rgba(0, 121, 193, 0.3);
    }
    .btn-secondary { background-color: #6c757d; }
    .btn-secondary:hover { background-color: #5a6268; }
    .btn-danger { background-color: var(--danger-color); }
    .btn-danger:hover { background-color: #cc375d; }
    .btn-small { padding: 6px 12px; margin: 0; font-size: 0.85em; }

    /* Messages */
    .message { 
        padding: 15px 20px; 
        margin-bottom: 25px; 
        border-radius: 10px; 
        font-weight: 500; 
        border-left: 6px solid;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .success { background-color: #d4f7ed; color: #00796b; border-color: var(--success-color); }
    .danger { background-color: #fce4e4; color: #c0392b; border-color: var(--danger-color); }
    .info { background-color: #e0f7fa; color: #004d40; border-color: var(--accent-color); }
    .warning { background-color: #fffde7; color: #fbc02d; border-color: #ffc107; }

    /* Table Styling */
    table { 
        width: 100%; 
        border-collapse: collapse; 
        margin-top: 20px; 
    }
    th, td { 
        padding: 15px 15px; 
        text-align: left; 
        border-bottom: 1px solid #eee;
    }
    th { 
        background-color: var(--primary-color); 
        color: white; 
        font-weight: 600; 
        text-transform: uppercase; 
        font-size: 0.9em;
    }
    tr:nth-child(even) { background-color: #fcfcfc; }
    tr:hover { background-color: #eef7ff; cursor: pointer; }
    tr:last-child td { border-bottom: none; }

    /* Totals Box */
    .total-box { 
        margin-top: 35px; 
        padding: 20px; 
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
        color: white; 
        border-radius: 12px; 
        text-align: center; 
        box-shadow: 0 8px 15px rgba(0, 121, 193, 0.4);
    }
    .total-box p { 
        margin: 0; 
        font-size: 1.4em; 
        font-weight: 300; 
    }
    .total-box strong { 
        display: block; 
        font-size: 2.5em; 
        font-weight: 700; 
        margin-top: 5px;
    }

    /* Layouts using Flexbox for modern alignment */
    .header-bar { 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        margin-bottom: 20px;
    }
    .add-sale-form { 
        display: flex; 
        gap: 15px; 
        align-items: flex-end; 
        padding: 15px 0;
    }
    .form-group { flex-grow: 1; }
    .form-group label { display: block; margin-bottom: 5px; font-weight: 500; font-size: 0.95em; }
    .form-group input { margin: 0; }

    .filter-form { 
        display: flex; 
        gap: 15px; 
        margin-bottom: 30px; 
        align-items: flex-end; 
    }
    .filter-form .form-group { min-width: 150px; }

</style>
"""

LOGIN_TEMPLATE = BASE_CSS + """
<div class="container" style="max-width: 450px; margin-top: 100px;">
    <h2>🔒 Velocity Sales Login</h2>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="message {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    <form method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
        <input type="submit" value="🚀 Access Dashboard" style="width: 100%; margin-top: 20px;">
    </form>
    <p style="text-align: center; margin-top: 30px;">
        <a href="{{ url_for('register') }}" style="color: var(--primary-color); text-decoration: none;">New User? Register here</a>.
    </p>
</div>
"""

REGISTER_TEMPLATE = BASE_CSS + """
<div class="container" style="max-width: 450px; margin-top: 100px;">
    <h2>📝 Register New Account</h2>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="message {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    <form method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <label for="password">Password (min 4 chars):</label>
        <input type="password" id="password" name="password" required>
        <input type="submit" value="Create Account" style="width: 100%; margin-top: 20px;">
    </form>
    <p style="text-align: center; margin-top: 30px;">
        <a href="{{ url_for('login') }}" style="color: var(--primary-color); text-decoration: none;">Already have an account? Login here</a>.
    </p>
</div>
"""

SALES_TRACKER_TEMPLATE = BASE_CSS + """
<div class="container">
    <div class="header-bar">
        <h1>📊 Velocity Sales Dashboard</h1>
        <a href="{{ url_for('logout') }}" class="btn btn-danger">Logout ({{ session.username }})</a>
    </div>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="message {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <div class="total-box">
        <p>Total Sales Recorded</p>
        <strong>${{ "{:,.2f}".format(total) }}</strong>
    </div>

    <h2 style="margin-top: 40px;">➕ Record New Sale</h2>
    <form method="POST" class="add-sale-form">
        <div class="form-group">
            <label for="client">Client Name</label>
            <input type="text" id="client" name="client" required placeholder="e.g., Acme Corp">
        </div>
        <div class="form-group">
            <label for="product_name">Product/Service</label>
            <input type="text" id="product_name" name="product_name" required placeholder="e.g., Enterprise Server">
        </div>
        <div class="form-group">
            <label for="amount">Sale Amount ($)</label>
            <input type="number" id="amount" name="amount" required step="0.01" min="1" placeholder="e.g., 55000">
        </div>
        <div class="form-group" style="flex-grow: 0; min-width: 140px;">
            <label for="date">Date</label>
            <input type="date" id="date" name="date" required value="{{ today }}">
        </div>
        <input type="submit" value="Record" style="margin-top: 0;">
    </form>

    <h2 style="margin-top: 40px;">🧾 Sales History</h2>

    <form method="GET" class="filter-form">
        <div class="form-group">
            <label for="filter_client">Filter by Client</label>
            <input type="text" id="filter_client" name="filter_client" placeholder="Client Name or keyword" value="{{ request.args.get('filter_client', '') }}">
        </div>
        <div class="form-group">
            <label for="filter_date">Filter by Date</label>
            <input type="date" id="filter_date" name="filter_date" value="{{ request.args.get('filter_date', '') }}">
        </div>
        <input type="submit" value="🔍 Apply Filter" style="margin-top: 0;">
        <a href="{{ url_for('sales_tracker') }}" class="btn btn-secondary" style="margin-top: 0;">Clear</a>
    </form>
    {% if filtered_sales %}
        <table>
            <thead>
                <tr>
                    <th>Client</th>
                    <th>Product/Service</th>
                    <th>Date</th>
                    <th>Amount</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for sale in filtered_sales %}
                    <tr onclick="document.location = '{{ url_for('delete_sale', sale_id=sale.id) }}'">
                        <td>{{ sale.client }}</td>
                        <td>{{ sale.product_name }}</td>
                        <td>{{ sale.date }}</td>
                        <td>${{ "{:,.2f}".format(sale.amount) }}</td>
                        <td>
                            <a href="{{ url_for('delete_sale', sale_id=sale.id) }}" 
                               class="btn btn-danger btn-small" 
                               onclick="event.stopPropagation(); return confirm('Permanently delete sale for {{ sale.client }}?');">Delete</a>
                        </td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
        {% if all_sales_count != filtered_sales|length %}
            <p style="margin-top: 15px; color: var(--primary-color);">Displaying **{{ filtered_sales|length }}** sale(s) out of **{{ all_sales_count }}** total records.</p>
        {% endif %}
    {% else %}
        <p>No sales recorded yet or no sales match your current filter criteria.</p>
    {% endif %}
</div>
<script>
    // Ensure the date input defaults to today's date if not already set (for browser compatibility)
    document.addEventListener('DOMContentLoaded', function() {
        const dateInput = document.getElementById('date');
        if (!dateInput.value) {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            dateInput.value = `${year}-${month}-${day}`;
        }
    });
</script>
"""


# === FLASK ROUTES ===

@app.route("/", methods=["GET", "POST"])
@login_required
def sales_tracker():
    """
    Main Sales Tracker app route. Handles adding new sales (POST) and displaying/filtering sales (GET).
    """
    db = get_db()
    cursor = db.cursor()

    # --- Handle POST request to add a new sale ---
    if request.method == "POST":
        client = request.form.get('client').strip()
        product_name = request.form.get('product_name').strip()
        amount_str = request.form.get('amount')
        date = request.form.get('date')

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            datetime.strptime(date, '%Y-%m-%d')

            # Database INSERT
            cursor.execute("""
                INSERT INTO sales (client, product_name, amount, date) 
                VALUES (?, ?, ?, ?)
            """, (client, product_name, amount, date))
            db.commit()
            flash(f"Sale of '{product_name}' for ${amount:,.2f} recorded!", "success")

        except ValueError as e:
            flash(f"Invalid input: {e}", "danger")

        except Exception as e:
            flash(f"Database error: {e}", "danger")

        return redirect(url_for('sales_tracker'))

    # --- Handle GET request (Display/Filter) ---
    filter_client = request.args.get('filter_client', '').strip()
    filter_date = request.args.get('filter_date', '').strip()

    # Dynamic SQL Query setup
    query = "SELECT id, client, product_name, amount, date FROM sales"
    params = []
    where_clauses = []

    if filter_client:
        where_clauses.append("client LIKE ? OR product_name LIKE ?")
        params.extend([f"%{filter_client}%", f"%{filter_client}%"])

    if filter_date:
        where_clauses.append("date = ?")
        params.append(filter_date)

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    query += " ORDER BY date DESC, id DESC"

    # 1. Fetch filtered sales for display
    cursor.execute(query, params)
    filtered_sales = [dict(row) for row in cursor.fetchall()]

    # 2. Calculate the total sales amount and count from ALL records
    cursor.execute("SELECT SUM(amount) FROM sales")
    total_sales = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT COUNT(*) FROM sales")
    all_sales_count = cursor.fetchone()[0]

    # 3. Get today's date for input default
    today_date = datetime.now().strftime('%Y-%m-%d')

    # 4. Render the template
    return render_template_string(
        SALES_TRACKER_TEMPLATE,
        filtered_sales=filtered_sales,
        all_sales_count=all_sales_count,
        total=total_sales,
        today=today_date
    )


@app.route("/delete_sale/<int:sale_id>")
@login_required
def delete_sale(sale_id):
    """Deletes a sale entry by its database ID."""
    db = get_db()
    cursor = db.cursor()

    try:
        # Retrieve sale info before deletion for flash message
        cursor.execute("SELECT client, amount FROM sales WHERE id = ?", (sale_id,))
        sale_info = cursor.fetchone()

        if sale_info:
            # Database DELETE
            cursor.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
            db.commit()
            flash(
                f"Sale for client '{sale_info['client']}' (${sale_info['amount']:,.2f}) has been successfully deleted.",
                "info")
        else:
            flash("Error: Sale not found.", "danger")

    except Exception as e:
        flash(f"An error occurred during deletion: {e}", "danger")

    return redirect(url_for('sales_tracker'))


# --- Standard Auth Routes (Unchanged Logic) ---

@app.route("/login", methods=["GET", "POST"])
def login():
    users = load_users()
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        if username in users and users[username] == password:
            session["logged_in"] = True
            session["username"] = username
            flash(f"Welcome back, {username}! Redirecting to the dashboard.", "success")
            return redirect(url_for("sales_tracker"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template_string(LOGIN_TEMPLATE)


@app.route("/register", methods=["GET", "POST"])
def register():
    users = load_users()
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        if username in users:
            flash("Username already exists. Please choose another.", "danger")
        elif len(password) < 4:
            flash("Password must be at least 4 characters.", "danger")
        else:
            users[username] = password
            save_users(users)
            flash("Account created successfully! You can now log in.", "success")
            return redirect(url_for("login"))
    return render_template_string(REGISTER_TEMPLATE)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# === RUN APP ===
if __name__ == "__main__":
    app.run(debug=True)