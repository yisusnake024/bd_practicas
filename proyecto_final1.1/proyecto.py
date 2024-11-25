from flask import Flask, request, redirect, url_for, flash, render_template, send_from_directory
from flask_mysqldb import MySQL
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = '127.0.0.1'  # Dirección del servidor MySQL
app.config['MYSQL_USER'] = 'root'       # Usuario de la base de datos
app.config['MYSQL_PASSWORD'] = '01240601'  # Contraseña de la base de datos
app.config['MYSQL_DB'] = 'practica_definitivas'  # Nombre de la base de datos

mysql = MySQL(app)

UPLOAD_FOLDER = 'CARPETA_DE_ARCHIVOS_SUBIDOS'  # Define la ruta de la carpeta de archivos
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Usa la clave correcta para el acceso a la carpeta

# Verificar si la carpeta de archivos existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Función para verificar las extensiones permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta para subir archivos
@app.route('/archivos_registrados', methods=['GET', 'POST'])
def archivos_registrados():
    """Ruta para subir archivos"""
    if request.method == 'POST':
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)

        archivo = request.files['archivo']

        if archivo.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)

        if archivo and allowed_file(archivo.filename):
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f'Archivo {filename} subido exitosamente', 'success')
            return redirect(url_for('archivos_registrados'))
        else:
            flash('Tipo de archivo no permitido', 'error')

    # Obtener lista de archivos para mostrar en la página
    archivos = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('archivos_registrados.html', archivos=archivos)

# Ruta para eliminar archivos
@app.route('/eliminar_archivo/<nombre_archivo>', methods=['POST'])
def eliminar_archivo(nombre_archivo):
    """Ruta para eliminar un archivo"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
    try:
        os.remove(file_path)
        flash(f'Archivo {nombre_archivo} eliminado correctamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar archivo: {str(e)}', 'error')
    return redirect(url_for('archivos_registrados'))

# Ruta para descargar archivos
@app.route('/descargar_archivo/<nombre_archivo>')
def descargar_archivo(nombre_archivo):
    try:
        # Verificar que el archivo exista en la carpeta de uploads
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
        
        # Si el archivo no existe, redirigir con un mensaje de error
        if not os.path.exists(file_path):
            flash(f'Archivo {nombre_archivo} no encontrado', 'error')
            return redirect(url_for('archivos_registrados'))

        # Enviar el archivo como adjunto
        return send_from_directory(app.config['UPLOAD_FOLDER'], nombre_archivo, as_attachment=True)
    
    except Exception as e:
        flash(f'Error al descargar el archivo: {str(e)}', 'error')
        return redirect(url_for('archivos_registrados'))


def validar_usuario(usuario, password):
    if os.path.exists('usuarios.txt'):
        with open('usuarios.txt', 'r') as f:
            for line in f:
                user, pwd = line.strip().split(',')
                if user == usuario and pwd == password:
                    return True
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        if validar_usuario(usuario, password):
            return redirect(url_for('panel_maestro'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    return render_template('index.html')

@app.route('/panel_maestro')
def panel_maestro():
    """Panel maestro de administración"""
    return render_template('panel_maestro.html')

@app.route('/registro', methods=['GET', 'POST'])
def registrar():
    """Ruta para registrar un nuevo usuario"""
    if request.method == 'POST':
        nuevo_usuario = request.form['usuario']
        nueva_password = request.form['contraseña']
        if nuevo_usuario and nueva_password:
            with open('usuarios.txt', 'a') as f:
                f.write(f"{nuevo_usuario},{nueva_password}\n")
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('index'))
        else:
            flash('Debe llenar ambos campos', 'error')
    return render_template('registro.html')


@app.route('/agregar_estudiante', methods=['GET', 'POST'])
def agregar_estudiante():
    """Ruta para agregar un nuevo estudiante"""
    if request.method == 'POST':
        # Obtener los datos del formulario
        cedula_estudiante = request.form.get('cedula_estudiante')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        Nombre_Tutor_Academico = request.form.get('Nombre_Tutor_Academico')
        Nombre_Tutor_Empresarial = request.form.get('Nombre_Tutor_Empresarial')
        Nombre_Empresa = request.form.get('Nombre_Empresa')

        # Validación de campos
        if not (cedula_estudiante.isdigit() and nombres and apellidos and telefono and correo and Nombre_Tutor_Academico and Nombre_Tutor_Empresarial and Nombre_Empresa):
            flash('Todos los campos son obligatorios y la cédula debe ser numérica.', 'error')
            return render_template('agregar_estudiante.html')

        # Validar correo electrónico
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            flash('Correo electrónico no válido.', 'error')
            return render_template('agregar_estudiante.html')

        # Validar número de teléfono (Ejemplo básico para validar un teléfono de 10 dígitos)
        if not re.match(r"^\d{10}$", telefono):
            flash('Número de teléfono no válido. Debe tener 10 dígitos.', 'error')
            return render_template('agregar_estudiante.html')

        # Convertir cédula a entero
        cedula_estudiante = int(cedula_estudiante)

        # Si todo es válido, insertar en la base de datos
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO estudiante (cedula_estudiante, nombres, apellidos, telefono, correo, Nombre_Tutor_Academico, Nombre_Tutor_Empresarial, Nombre_Empresa)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (cedula_estudiante, nombres, apellidos, telefono, correo, Nombre_Tutor_Academico, Nombre_Tutor_Empresarial, Nombre_Empresa))
            mysql.connection.commit()
            flash('Estudiante agregado correctamente', 'success')
            return redirect(url_for('agregar_estudiante'))
        except Exception as e:
            mysql.connection.rollback()  # Revertir cambios si ocurre un error
            flash(f'Error al agregar estudiante: {str(e)}', 'error')
        finally:
            cursor.close()

    return render_template('agregar_estudiante.html')


@app.route('/agregar_semanas', methods=['GET', 'POST'])
def agregar_semanas():
    """Ruta para agregar información sobre semanas de trabajo de los estudiantes"""
    if request.method == 'POST':
        # Obtener los datos del formulario
        numero_semana = request.form.get('numero_semana')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_final = request.form.get('fecha_final')
        cedula_estudiante = request.form.get('cedula_estudiante')
        horas_registradas = request.form.get('horas_registradas')
        nota_tutor_academico = request.form.get('nota_tutor_academico')

        # Verificar si todos los campos requeridos fueron proporcionados
        if numero_semana and fecha_inicio and fecha_final and cedula_estudiante and horas_registradas and nota_tutor_academico:
            cursor = mysql.connection.cursor()
            try:
                # Insertar en la tabla 'registro_semana'
                query_registro = """
                    INSERT INTO registro_semana (numero_semana, fecha_inicio, fecha_final, cedula_estudiante, horas_registradas, nota_tutor_academico)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_registro, (numero_semana, fecha_inicio, fecha_final, cedula_estudiante, horas_registradas, nota_tutor_academico))
                mysql.connection.commit()

                # Obtener el id_semana generado automáticamente
                id_semana = cursor.lastrowid

                # Insertar registros iniciales en las tablas relacionadas
                query_encuentro = """
                    INSERT INTO encuentro (id_semana, cedula_estudiante, nota_encuentro)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query_encuentro, (id_semana, cedula_estudiante, None))

                query_informe = """
                    INSERT INTO informe (id_semana, cedula_estudiante, nota_sustentacion)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query_informe, (id_semana, cedula_estudiante, None))

                query_evaluacion = """
                    INSERT INTO evaluacion (id_semana, cedula_estudiante, evaluacion_tutor_empresarial, autoevaluacion_tutor_academico)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_evaluacion, (id_semana, cedula_estudiante, None, None))

                # Confirmar los cambios
                mysql.connection.commit()

                flash('Semana y registros relacionados agregados correctamente.', 'success')
            except Exception as e:
                mysql.connection.rollback()  # Revertir cambios si ocurre un error
                flash(f'Error al agregar semana: {str(e)}', 'error')
            finally:
                cursor.close()

        return redirect(url_for('agregar_semanas'))

    return render_template('agregar_semanas.html')
@app.route('/agregar_notas', methods=['GET', 'POST'])
def agregar_notas():
    if request.method == 'POST':
        cedula_estudiante = request.form['cedula_estudiante']
        autoevaluacion_tutor_academico = request.form.get('autoevaluacion_tutor_academico', '0') == '1'
        certifiacion_practica = request.form.get('certifiacion_practica', '0') == '1'
        evaluacion_estudiante_tutor = request.form.get('evaluacion_estudiante_tutor', '0') == '1'
        evaluacion_tutor_empresarial = request.form['evaluacion_tutor_empresarial']

        if cedula_estudiante and evaluacion_tutor_empresarial:
            cursor = mysql.connection.cursor()

            try:
                # Obtener el id_semana correspondiente
                cursor.execute("""
                    SELECT id_semana FROM registro_semana 
                    WHERE cedula_estudiante = %s
                    ORDER BY numero_semana DESC LIMIT 1
                """, (cedula_estudiante,))
                id_semana = cursor.fetchone()

                if not id_semana:
                    flash(f'No se encontró un registro de semana para el estudiante con cédula {cedula_estudiante}.', 'error')
                    return redirect(url_for('agregar_notas'))

                id_semana = id_semana[0]

                # Insertar o actualizar en la tabla evaluacion
                cursor.execute("""
                    INSERT INTO evaluacion (
                        cedula_estudiante, 
                        autoevaluacion_tutor_academico, 
                        certifiacion_practica, 
                        evaluacion_estudiante_tutor, 
                        evaluacion_tutor_empresarial, 
                        id_semana
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        autoevaluacion_tutor_academico = VALUES(autoevaluacion_tutor_academico),
                        certifiacion_practica = VALUES(certifiacion_practica),
                        evaluacion_estudiante_tutor = VALUES(evaluacion_estudiante_tutor),
                        evaluacion_tutor_empresarial = VALUES(evaluacion_tutor_empresarial);
                """, (
                    cedula_estudiante,
                    autoevaluacion_tutor_academico,
                    certifiacion_practica,
                    evaluacion_estudiante_tutor,
                    evaluacion_tutor_empresarial,
                    id_semana
                ))

                mysql.connection.commit()
                flash('Evaluación guardada correctamente', 'success')

            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error al guardar la evaluación: {str(e)}', 'error')
            finally:
                cursor.close()

            return redirect(url_for('agregar_notas'))

    return render_template('agregar_notas.html')

@app.route('/agregar_encuentro', methods=['GET', 'POST'])
def agregar_encuentro():
    """Ruta para agregar un encuentro"""
    if request.method == 'POST':
        cedula_estudiante = request.form['cedula_estudiante']
        numero_encuentro = request.form['numero_encuentro']
        numero_semana = request.form['numero_semana']  # Nuevo campo para ingresar el numero_semana
        nota_encuentro = request.form['nota_encuentro']

        if cedula_estudiante and numero_encuentro and numero_semana and nota_encuentro:
            cursor = mysql.connection.cursor()
            try:
                # Obtener el id_semana correspondiente al estudiante, numero_semana y numero_encuentro
                cursor.execute("""
                    SELECT id_semana FROM registro_semana 
                    WHERE cedula_estudiante = %s AND numero_semana = %s
                """, (cedula_estudiante, numero_semana))  # Usamos numero_semana para validar
                id_semana = cursor.fetchone()

                if id_semana:
                    # Insertar en encuentro si encontramos el id_semana
                    cursor.execute("""
                        INSERT INTO encuentro (id_semana, cedula_estudiante,numero_encuentro, nota_encuentro)
                        VALUES (%s, %s, %s, %s)
                    """, (id_semana[0], cedula_estudiante,numero_encuentro, nota_encuentro))
                    mysql.connection.commit()
                    flash('Encuentro agregado correctamente', 'success')
                else:
                    flash(f'No se encontró un registro de semana para el estudiante con número de semana: {numero_semana}.', 'error')
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error al agregar encuentro: {str(e)}', 'error')
            finally:
                cursor.close()

        return redirect(url_for('agregar_encuentro'))

    return render_template('agregar_encuentro.html')

@app.route('/agregar_informe', methods=['GET', 'POST'])
def agregar_informe():
    """Ruta para agregar un informe"""
    if request.method == 'POST':
        cedula_estudiante = request.form['cedula_estudiante']
        numero_informe = request.form['numero_informe']
        nota_sustentacion = request.form['nota_sustentacion']
        
        # Obtener el valor de 'entrega' como un checkbox (0 si no está marcado, 1 si está marcado)
        entrega = request.form.get('entrega')  # Obtiene el valor del checkbox
        entrega = 1 if entrega else 0  # Si está marcado, se guarda como 1, si no como 0

        nota_evaluacion = request.form['nota_evaluacion']

        if cedula_estudiante and numero_informe and nota_sustentacion and entrega is not None and nota_evaluacion:
            cursor = mysql.connection.cursor()
            try:
                # Obtener el id_semana correspondiente al estudiante y la semana
                cursor.execute("""
                    SELECT id_semana FROM registro_semana 
                    WHERE cedula_estudiante = %s AND numero_semana = %s
                """, (cedula_estudiante, numero_informe))
                id_semana = cursor.fetchone()

                if id_semana:
                    # Insertar en informe con los nuevos campos
                    cursor.execute("""
                        INSERT INTO informe (id_semana, cedula_estudiante, numero_informe, 
                                             nota_sustentacion, entrega, nota_evaluacion)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (id_semana[0], cedula_estudiante, numero_informe, 
                          nota_sustentacion, entrega, nota_evaluacion))
                    mysql.connection.commit()
                    flash('Informe agregado correctamente', 'success')
                else:
                    flash('No se encontró un registro de semana para este estudiante.', 'error')
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error al agregar informe: {str(e)}', 'error')
            finally:
                cursor.close()

        else:
            flash('Faltan datos en el formulario. Asegúrese de completar todos los campos.', 'error')

        return redirect(url_for('agregar_informe'))

    return render_template('agregar_informe.html')


@app.route('/consultas', methods=['GET', 'POST'])
def consultas():
    """Ruta para realizar consultas sobre estudiantes por cédula"""
    if request.method == 'POST':
        cedula = request.form['codigo']  # Asume que el input se llama 'codigo'
        estudiante = buscar_estudiante_por_cedula(cedula)
        if estudiante:
            mensaje = f'Datos del estudiante con cédula {cedula} encontrados.'
        else:
            mensaje = f'Estudiante con cédula {cedula} no encontrado'
            estudiante = None  # Asegúrate de pasar un valor nulo si no se encuentra
        # Redirigimos a una nueva plantilla con los datos del estudiante
        return render_template('resultados.html', mensaje=mensaje, estudiante=estudiante)
    return render_template('consultas.html')


def buscar_estudiante_por_cedula(cedula):
    """Buscar un estudiante en la base de datos usando la cédula"""
    cursor = mysql.connection.cursor()
    cursor.execute('''
    SELECT 
        estudiante.cedula_estudiante, estudiante.nombres, estudiante.apellidos, 
        estudiante.telefono, estudiante.correo, estudiante.Nombre_Tutor_Academico, 
        estudiante.Nombre_Tutor_Empresarial, estudiante.Nombre_Empresa, 
        SUM(registro_semana.horas_registradas) AS horas_totales, 
        AVG(registro_semana.nota_tutor_academico) AS promedio_nota_tutor_academico, 
        AVG(encuentro.nota_encuentro) AS promedio_nota_encuentro, 
        AVG(informe.nota_sustentacion) AS promedio_nota_sustentacion, 
        MAX(evaluacion.evaluacion_tutor_empresarial) AS evaluacion_tutor_empresarial
    FROM estudiante
    LEFT JOIN registro_semana ON estudiante.cedula_estudiante = registro_semana.cedula_estudiante
    LEFT JOIN encuentro ON estudiante.cedula_estudiante = encuentro.cedula_estudiante
    LEFT JOIN informe ON estudiante.cedula_estudiante = informe.cedula_estudiante
    LEFT JOIN evaluacion ON estudiante.cedula_estudiante = evaluacion.cedula_estudiante
    WHERE estudiante.cedula_estudiante = %s
    GROUP BY estudiante.cedula_estudiante
''', (cedula,))

    result = cursor.fetchone()
    cursor.close()
    
    if result:
        return {
            "cedula": result[0],
            "nombres": result[1],
            "apellidos": result[2],
            "telefono": result[3],
            "correo": result[4],
            "Nombre_Tutor_Academico": result[5],
            "Nombre_Tutor_Empresarial": result[6],
            "Nombre_Empresa": result[7],
            "horas_totales": result[8],
            "promedio_nota_tutor_academico": result[9],
            "promedio_nota_encuentro": result[10],
            "promedio_nota_sustentacion": result[11],
            "evaluacion_tutor_empresarial": result[12]
        }
    return None
@app.route('/eliminar', methods=['GET', 'POST'])
def eliminar():
    """Ruta para eliminar un estudiante por cédula"""
    if request.method == 'POST':
        cedula = request.form['codigo']  # La cédula se envía a través de 'codigo' en el formulario
        estudiante = buscar_estudiante_por_cedula(cedula)
        if estudiante:
            # Realizar eliminación en la base de datos
            cursor = mysql.connection.cursor()
            try:
                # Primero, eliminar registros en 'encuentro' que dependan del estudiante
                cursor.execute('DELETE FROM encuentro WHERE cedula_estudiante = %s', (cedula,))
                
                cursor.execute('DELETE FROM evaluacion WHERE cedula_estudiante = %s', (cedula,))

                cursor.execute('DELETE FROM informe WHERE cedula_estudiante = %s', (cedula,))
                
                cursor.execute('DELETE FROM registro_semana WHERE cedula_estudiante = %s', (cedula,))
                
                # Luego, eliminar el estudiante
                cursor.execute('DELETE FROM estudiante WHERE cedula_estudiante = %s', (cedula,))
                
                mysql.connection.commit()
                flash(f'Estudiante con cédula {cedula} eliminado correctamente', 'success')
            except Exception as e:
                mysql.connection.rollback()  # Si ocurre un error, revertimos
                flash(f'Error al eliminar estudiante: {str(e)}', 'error')
            finally:
                cursor.close()
        else:
            flash(f'Estudiante con cédula {cedula} no encontrado', 'error')
    return render_template('eliminar.html')
@app.route('/actualizar_estudiante', methods=['GET', 'POST'])
def actualizar_estudiante():
    """Ruta para actualizar los datos de un estudiante"""
    
    estudiante = None  # Definir estudiante antes de la lógica de consulta

    if request.method == 'POST':
        # Obtener los datos del formulario
        cedula_estudiante = request.form.get('cedula_estudiante')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        Nombre_Tutor_Academico = request.form.get('Nombre_Tutor_Academico')
        Nombre_Tutor_Empresarial = request.form.get('Nombre_Tutor_Empresarial')
        Nombre_Empresa = request.form.get('Nombre_Empresa')

        # Conectar a la base de datos y realizar la actualización
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("""
                UPDATE estudiante
                SET nombres = %s, apellidos = %s, telefono = %s, correo = %s, 
                    Nombre_Tutor_Academico = %s, Nombre_Tutor_Empresarial = %s, Nombre_Empresa = %s
                WHERE cedula_estudiante = %s
            """, (nombres, apellidos, telefono, correo, Nombre_Tutor_Academico, Nombre_Tutor_Empresarial, Nombre_Empresa, cedula_estudiante))
            mysql.connection.commit()
            flash('Datos del estudiante actualizados correctamente', 'success')
        except Exception as e:
            mysql.connection.rollback()  # Si hay un error, revertimos la transacción
            flash(f'Error al actualizar los datos: {str(e)}', 'error')
        finally:
            cursor.close()

        # Redirigir al usuario a la misma página (o a otra página) después de la actualización
        return redirect('/actualizar_estudiante')

    # Si es un GET, recuperamos los datos del estudiante a través de la cédula proporcionada
    cedula_estudiante = request.args.get('cedula_estudiante')  # La cédula se pasa por GET
    if cedula_estudiante:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM estudiante WHERE cedula_estudiante = %s", (cedula_estudiante,))
        estudiante = cursor.fetchone()  # Recuperamos un solo estudiante con los datos
        cursor.close()

        if not estudiante:
            flash('Estudiante no encontrado', 'error')
            return redirect('/')  # Redirigir si no se encuentra al estudiante

    # Aquí pasamos el estudiante al template solo si existe
    return render_template('actualizar_estudiante.html', estudiante=estudiante)


@app.route('/mostrar_tabla')
def mostrar_tabla():
    try:
        cursor = mysql.connection.cursor()

        # Consulta SQL para obtener cada registro con manejo de NULL
        query = """
            SELECT 
                estudiante.cedula_estudiante, 
                estudiante.nombres, 
                estudiante.apellidos, 
                estudiante.telefono, 
                estudiante.correo, 
                estudiante.Nombre_Tutor_Academico, 
                estudiante.Nombre_Tutor_Empresarial, 
                estudiante.Nombre_Empresa, 
                registro_semana.id_semana, 
                registro_semana.numero_semana, 
                registro_semana.fecha_inicio, 
                registro_semana.fecha_final, 
                registro_semana.horas_registradas, 
                COALESCE(registro_semana.nota_tutor_academico, 0) AS nota_tutor_academico, 
                COALESCE(AVG(encuentro.nota_encuentro), 0) AS promedio_encuentro, 
                COALESCE(AVG(informe.nota_sustentacion), 0) AS promedio_sustentacion, 
                COALESCE(evaluacion.evaluacion_tutor_empresarial, 0) AS evaluacion_tutor_empresarial, 
                COALESCE(evaluacion.autoevaluacion_tutor_academico, 0) AS autoevaluacion_tutor_academico, 
                COALESCE(evaluacion.certifiacion_practica, 0) AS certificacion_practica, 
                COALESCE(evaluacion.evaluacion_estudiante_tutor, 0) AS evaluacion_estudiante_tutor
            FROM estudiante
            LEFT JOIN registro_semana 
                ON estudiante.cedula_estudiante = registro_semana.cedula_estudiante
            LEFT JOIN encuentro 
                ON registro_semana.id_semana = encuentro.id_semana
            LEFT JOIN informe 
                ON registro_semana.id_semana = informe.id_semana
            LEFT JOIN evaluacion 
                ON registro_semana.id_semana = evaluacion.id_semana
            GROUP BY 
                estudiante.cedula_estudiante, 
                estudiante.nombres, 
                estudiante.apellidos, 
                estudiante.telefono, 
                estudiante.correo, 
                estudiante.Nombre_Tutor_Academico, 
                estudiante.Nombre_Tutor_Empresarial, 
                estudiante.Nombre_Empresa, 
                registro_semana.id_semana, 
                registro_semana.numero_semana, 
                registro_semana.fecha_inicio, 
                registro_semana.fecha_final, 
                registro_semana.horas_registradas, 
                evaluacion.evaluacion_tutor_empresarial, 
                evaluacion.autoevaluacion_tutor_academico, 
                evaluacion.certifiacion_practica, 
                evaluacion.evaluacion_estudiante_tutor;
        """

        # Ejecutar consulta y obtener los datos
        cursor.execute(query)
        datos = cursor.fetchall()

        # Estructura para almacenar los datos
        registros = []

        for fila in datos:
            registro = list(fila)

            # Asegurarse de que los promedios nunca sean None (aunque usamos COALESCE)
            registro[14] = registro[14] if registro[14] is not None else 0  # promedio_encuentro
            registro[15] = registro[15] if registro[15] is not None else 0  # promedio_sustentacion

            # Convertir campos booleanos a "Sí" o "No"
            registro[17] = 'Sí' if registro[17] else 'No'  # autoevaluacion_tutor_academico
            registro[18] = 'Sí' if registro[18] else 'No'  # certificacion_practica
            registro[19] = 'Sí' if registro[19] else 'No'  # evaluacion_estudiante_tutor

            registros.append(registro)

        # Renderizar la plantilla con los registros
        return render_template('mostrar_tabla.html', registros=registros)

    except Exception as e:
        flash(f'Error al mostrar la tabla: {str(e)}', 'error')
        return redirect(url_for('panel_maestro'))

if __name__ == '__main__':
    app.run(debug=True)




