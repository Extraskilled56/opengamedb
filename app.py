from pdb import Pdb
from flask import render_template, Flask, request, redirect, url_for, session

db = Pdb('ogdb.db')
app = Flask(__name__)
db.create_table('sites', {
    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    'domain': 'TEXT',
    'name': 'TEXT',
    'description': 'TEXT',
    'status': 'TEXT'
})
app.secret_key = 'your_secret_key'  # Replace with a strong secret key


@app.route("/")
def index():
    sites = db.select('sites')
    return render_template("index.html", sites=sites)



@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        pin = request.form.get("pin")
        if pin == "9225":
            session['authorized'] = True  # Store authorization in session
            sites = db.select('sites')
            return render_template("admin.html", sites=sites, authorized=True)
        else:
            return render_template("admin.html", authorized=False)

    # If GET request, check if authorized
    authorized = session.get('authorized', False)
    sites = db.select('sites') if authorized else []
    return render_template("admin.html", sites=sites, authorized=authorized)
@app.route("/logout")
def logout():
    session.pop('authorized', None)  # Remove the authorization from session
    return redirect(url_for('admin'))
@app.route("/update_site/<int:site_id>", methods=["POST"])
def update_site(site_id):
    name = request.form["name"]
    domain = request.form["domain"]
    description = request.form["description"]
    status = request.form["status"]
    
    if status == "blocked":
        # Delete the site from the database using the site ID
        db.delete("sites", f"WHERE id = {site_id}")
    else:
        # Update the site in the database
        db.update('sites', {'name': name, 'domain': domain, 'description': description, 'status': status}, site_id)
    
    return redirect(url_for('admin'))

@app.route("/add_site", methods=["GET", "POST"])
def add_site():
    if request.method == "POST":
        domain = request.form["domain"]
        name = request.form["name"]
        description = request.form["description"]
        db.insert('sites', {'domain': domain, 'name': name, 'description': description, 'status': 'pending'})
        return redirect(url_for('index'))
    return render_template("add_site.html")


if __name__ == '__main__':
    app.run(debug=True)