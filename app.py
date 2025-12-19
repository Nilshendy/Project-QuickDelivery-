from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Klanten opslag
klanten_data = []


@app.route("/")
def index():
    return render_template("index.html", current_page="home")


@app.route("/klanten", methods=["GET", "POST"])
def klanten():
    if request.method == "POST":
        naam = request.form.get("naam", "").strip()
        adres = request.form.get("adres", "").strip()
        contact = request.form.get("contact", "").strip()

        if naam and adres:
            klanten_data.append(
                {
                    "id": len(klanten_data) + 1,
                    "naam": naam,
                    "adres": adres,
                    "contact": contact,
                }
            )

        return redirect(url_for("klanten"))

    return render_template("klanten.html", current_page="klanten", klanten=klanten_data)


@app.route("/bestellingen")
def bestellingen():
    return render_template("bestellingen.html", current_page="bestellingen")


@app.route("/planning")
def planning():
    return render_template("planning.html", current_page="planning")


@app.route("/tracking")
def tracking():
    return render_template("tracking.html", current_page="tracking")


if __name__ == "__main__":
    app.run(debug=True)
