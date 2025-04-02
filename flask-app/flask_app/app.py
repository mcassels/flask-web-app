from flask import Flask, redirect, request, render_template, flash
from .contacts_model import Contact

Contact.load_db()

app = Flask(__name__)

app.secret_key = b'hypermedia rocks'

@app.route("/")
def index():
    return redirect("/contacts")

@app.route("/contacts")
def contacts():
    search = request.args.get("q")
    p = request.args.get("page", 1)
    page = None
    if p is not None:
      page = int(p)
    if search is not None:
      contacts_set = Contact.search(search)
      if request.headers.get("HX-Trigger") == "search":
        print("was search. Contacts set:", contacts_set)
        return render_template("rows.html", contacts=contacts_set)
    else:
      contacts_set = Contact.all(page)
    return render_template("index.html", contacts=contacts_set, page=page, contacts_length=len(contacts_set))

@app.route("/contacts/new", methods=["GET"])
def new_contact():
    return render_template("new.html", contact=Contact())

@app.route("/contacts/new", methods=['POST'])
def contacts_new():
    c = Contact(None, request.form['first_name'], request.form['last_name'], request.form['phone'],
                request.form['email'])
    if c.save():
        flash("Created New Contact!")
        return redirect("/contacts")
    else:
        return render_template("new.html", contact=c)

@app.route("/contacts/<contact_id>")
def contact_detail(contact_id):
    contact = Contact.find(contact_id)
    return render_template("show.html", contact=contact)

@app.route("/contacts/<contact_id>/edit", methods=["GET"])
def contact_edit_get(contact_id):
    contact = Contact.find(contact_id)
    return render_template("edit.html", contact=contact)

@app.route("/contacts/<contact_id>/edit", methods=["POST"])
def contact_edit_post(contact_id):
    contact = Contact.find(contact_id)
    contact.first = request.form['first_name']
    contact.last = request.form['last_name']
    contact.phone = request.form['phone']
    contact.email = request.form['email']
    if contact.save():
        flash("Updated Contact!")
        return redirect("/contacts/" + str(contact.id))
    else:
        return render_template("edit.html", contact=contact)

@app.route("/contacts/<contact_id>", methods=["DELETE"])
def contact_delete(contact_id):
    contact = Contact.find(contact_id)
    contact.delete()
    flash("Deleted Contact!")
    return redirect("/contacts", 303)

@app.route("/contacts/<contact_id>/email", methods=["GET"])
def contact_email_get(contact_id=0):
    c = Contact.find(contact_id)
    c.email = request.args.get('email')
    c.validate()
    return c.errors.get('email') or ""