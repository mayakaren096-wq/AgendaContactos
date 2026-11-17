import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database import obtener_conexion, crear_tabla

app = Flask(__name__)
app.secret_key = "cambia-esta-clave-en-tu-proyecto"

# Carpeta donde se guardarán las fotos subidas
UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

crear_tabla()

@app.route("/")
def inicio():
    conexion = obtener_conexion()
    contactos = conexion.execute(
        "SELECT * FROM contactos ORDER BY nombre"
    ).fetchall()
    conexion.close()
    return render_template("index.html", contactos=contactos)

@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    correo = request.form.get("correo", "").strip()
    categoria = request.form.get("categoria", "").strip()
    
    if not nombre or not telefono or not categoria:
        flash("Completa los campos obligatorios.")
        return redirect(url_for("inicio"))
    
    # Manejo de la fotografía
    foto_nombre = ""
    archivo_foto = request.files.get("foto")
    if archivo_foto and archivo_foto.filename != "":
        foto_nombre = archivo_foto.filename
        ruta_guardado = os.path.join(app.config['UPLOAD_FOLDER'], foto_nombre)
        archivo_foto.save(ruta_guardado)
    
    conexion = obtener_conexion()
    conexion.execute(
        "INSERT INTO contactos (nombre, telefono, correo, categoria, foto) VALUES (?, ?, ?, ?, ?)",
        (nombre, telefono, correo, categoria, foto_nombre)
    )
    conexion.commit()
    conexion.close()
    flash("¡Contacto guardado correctamente!")
    return redirect(url_for("inicio"))

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexion = obtener_conexion()
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()
        categoria = request.form.get("categoria", "").strip()
        
        if not nombre or not telefono or not categoria:
            flash("Completa los campos obligatorios.")
            return redirect(url_for("editar", id=id))
            
        # Consultar foto actual por si no se actualiza
        contacto_actual = conexion.execute("SELECT foto FROM contactos WHERE id = ?", (id,)).fetchone()
        foto_nombre = contacto_actual["foto"] if contacto_actual else ""
        
        archivo_foto = request.files.get("foto")
        if archivo_foto and archivo_foto.filename != "":
            foto_nombre = archivo_foto.filename
            ruta_guardado = os.path.join(app.config['UPLOAD_FOLDER'], foto_nombre)
            archivo_foto.save(ruta_guardado)
            
        conexion.execute(
            "UPDATE contactos SET nombre = ?, telefono = ?, correo = ?, categoria = ?, foto = ? WHERE id = ?",
            (nombre, telefono, correo, categoria, foto_nombre, id)
        )
        conexion.commit()
        conexion.close()
        flash("Contacto actualizado.")
        return redirect(url_for("inicio"))
        
    contacto = conexion.execute(
        "SELECT * FROM contactos WHERE id = ?", (id,)
    ).fetchone()
    conexion.close()
    
    if contacto is None:
        flash("El contacto no existe.")
        return redirect(url_for("inicio"))
        
    return render_template("editar.html", contacto=contacto)

@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    conexion = obtener_conexion()
    conexion.execute(
        "DELETE FROM contactos WHERE id = ?", (id,)
    )
    conexion.commit()
    conexion.close()
    flash("Contacto eliminado.")
    return redirect(url_for("inicio"))

if __name__ == "__main__":
    app.run(debug=True)