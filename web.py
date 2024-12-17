from flask import Flask, render_template, request, redirect, url_for, flash
import redis

app = Flask(__name__)
app.secret_key = "llaveultrasecreta"


client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

@app.route("/")
def home():

    keys = client.keys("receta:*")
    recetas = []
    for key in keys:
        receta_id = key.split(":")[1]
        receta = client.hgetall(key)
        receta["id"] = receta_id
        recetas.append(receta)
    return render_template("index.html", recetas=recetas)


@app.route("/receta/<int:receta_id>")
def ver_receta(receta_id):

    key = f"receta:{receta_id}"
    if client.exists(key):
        receta = client.hgetall(key)
        receta["id"] = receta_id
        return render_template("detalle.html", receta=receta)
    else:
        flash("Receta no encontrada.", "error")
        return redirect(url_for('home'))


@app.route("/nueva", methods=["GET", "POST"])
def nueva_receta():

    if request.method == "POST":
        nombre = request.form["nombre"]
        ingredientes = request.form["ingredientes"]
        pasos = request.form["pasos"]

        if not nombre or not ingredientes or not pasos:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('nueva_receta'))

        receta_id = client.incr("receta:id")
        key = f"receta:{receta_id}"
        receta = {
            "nombre": nombre,
            "ingredientes": ingredientes,
            "pasos": pasos
        }
        client.hset(key, mapping=receta)
        flash("Receta agregada exitosamente!", "success")
        return redirect(url_for('home'))
    return render_template("nueva.html")


@app.route("/editar/<int:receta_id>", methods=["GET", "POST"])
def editar_receta(receta_id):

    key = f"receta:{receta_id}"
    if not client.exists(key):
        flash("Receta no encontrada.", "error")
        return redirect(url_for('home'))

    if request.method == "POST":
        nombre = request.form["nombre"]
        ingredientes = request.form["ingredientes"]
        pasos = request.form["pasos"]

        if not nombre or not ingredientes or not pasos:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('editar_receta', receta_id=receta_id))

        receta = {
            "nombre": nombre,
            "ingredientes": ingredientes,
            "pasos": pasos
        }
        client.hset(key, mapping=receta)
        flash("Receta actualizada exitosamente!", "success")
        return redirect(url_for('home'))

    receta = client.hgetall(key)
    return render_template("editar.html", receta=receta, receta_id=receta_id)


@app.route("/eliminar/<int:receta_id>")
def eliminar_receta(receta_id):

    key = f"receta:{receta_id}"
    if client.exists(key):
        client.delete(key)
        flash("Receta eliminada exitosamente!", "success")
    else:
        flash("Receta no encontrada.", "error")
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)