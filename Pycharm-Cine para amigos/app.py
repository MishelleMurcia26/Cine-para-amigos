# .streamlit.py
import oracledb
import pandas as pd
import streamlit as st
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Cine para amigos",
    page_icon="🎬",
    layout="wide"
)

# Bloque de estilos
st.markdown("""
<style>
    .stApp {
        background-color: #0f0a14;
        color: #f3edf7;
    }
    [data-testid="stSidebar"] {
        background-color: #180d22;
        border-right: 1px solid #4a152b;
    }
    h1, h2, h3 {
        color: #e8a2b5 !important;
    }
    .stButton>button {
        background-color: #6b1d2f;
        color: #ffffff;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #8c253e;
        color: #ffffff;
    }
    [data-testid="stMetricValue"] {
        color: #d977a0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1f112d;
        color: #d1b5e2;
        border-radius: 6px 6px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6b1d2f !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. 🎬 Banner superior "Luz, cámara, acción"
st.markdown("""
<div style="background: linear-gradient(90deg, #4a152b 0%, #1f112d 100%); padding: 25px; border-radius: 12px; text-align: center; border: 1px solid #e8a2b5; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
    <h1 style="color: #e8a2b5 !important; margin: 0; font-size: 2.3em; letter-spacing: 2px; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">🎬 LUZ, CÁMARA, ACCIÓN 🎬</h1>
    <p style="color: #d1b5e2; margin: 8px 0 0 0; font-size: 1.1em; font-weight: 300;">Cine para Amigos — Maratones virtuales sin distancia</p>
</div>
""", unsafe_allow_html=True)

ESQUEMA = "MishelleMurcia"
TABLAS = ["usuario", "organizador", "pelicula", "plataforma", "sesion_pelicula", "sesion_usuario"]


# 1. Conexión a Oracle
@st.cache_resource
def obtener_conexion():
    s = st.secrets["oracle"]
    if "lib_dir" in s and s["lib_dir"]:
        oracledb.init_oracle_client(lib_dir=s["lib_dir"], config_dir=s["config_dir"])
        return oracledb.connect(user=s["user"], password=s["password"], dsn=s["dsn"])
    return oracledb.connect(
        user=s["user"], password=s["password"], dsn=s["dsn"],
        config_dir=s["config_dir"], wallet_location=s["config_dir"],
        wallet_password=s["wallet_password"]
    )

def conectar():
    try:
        conn = obtener_conexion()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM DUAL")
        return conn
    except Exception:
        st.cache_resource.clear()
        return obtener_conexion()

def consultar(sql, params=None):
    conn = conectar()
    df = pd.read_sql(sql, conn, params=params)
    # Convierte automáticamente las columnas a minúsculas para evitar errores de mayúsculas en Oracle
    df.columns = [c.lower() for c in df.columns]
    return df

def modificar(sql, params=None):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(sql, params or {})
        conn.commit()
        return cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()

# Menú de Navegación
menu = st.sidebar.radio(
    "Menú Principal",
    [
        "Inicio",
        "Películas y enlaces",
        "Películas ya vistas",
        "Agregar información",
    ]
)

# 3. Vistas de la aplicación
if menu == "Inicio":
    st.title("🏠 Bienvenida")
    st.markdown(
        "Plataforma social para coordinar y compartir maratones virtuales de películas, registrando información clave de cada sesión.")

    col1, col2, col3, col4 = st.columns(4)
    try:
        tp = consultar("SELECT COUNT(*) AS t FROM pelicula")["t"].iloc[0]
        ts = consultar("SELECT COUNT(*) AS t FROM sesion_pelicula")["t"].iloc[0]
        tu = consultar("SELECT COUNT(*) AS t FROM usuario")["t"].iloc[0]
        to = consultar("SELECT COUNT(*) AS t FROM organizador")["t"].iloc[0]
    except Exception:
        tp, ts, tu, to = 0, 0, 0, 0

    col1.metric("Películas", int(tp))
    col2.metric("Sesiones", int(ts))
    col3.metric("Usuarios", int(tu))
    col4.metric("Organizadores", int(to))

    st.markdown("---")

    # --- RECOMENDACIONES POR ESTRELLAS ---
    st.subheader("⭐ Si no sabes qué ver, siempre puedes ver las recomendaciones por estrellas")
    st.markdown("Descubre las mejores maratones ordenadas según la puntuación promedio de las calificaciones dadas.")

    try:
        query_recom = """
            SELECT DISTINCT p.p_titulo AS pelicula,
                            p.p_genero_principal AS genero,
                            s.s_duracion_minutos AS duracion,
                            o.o_nombre AS organizador,
                            s.s_calificacion,
                            s.s_calificacion_detalle AS detalle
            FROM sesion_pelicula s
            JOIN pelicula p ON s.s_id_pelicula = p.p_id_pelicula
            JOIN organizador o ON s.s_id_organizador = o.o_id_organizador
            ORDER BY s.s_calificacion DESC NULLS LAST
        """
        df_recom = consultar(query_recom)

        if df_recom is not None and not df_recom.empty:
            df_recom.columns = [col.lower() for col in df_recom.columns]


            def formato_resumen_estrellas(row):
                val_prom = row.get("s_calificacion")
                val_det = row.get("detalle")

                if pd.isna(val_prom) or val_prom is None:
                    return "Sin calificar"

                import re
                votos = len(re.findall(r'(\d+)⭐', str(val_det))) if not pd.isna(val_det) else 1
                prom = float(val_prom)
                return f"{'⭐' * int(round(prom))} {prom:.1f}/5 ({votos} voto{'s' if votos > 1 else ''})"


            df_recom["Calificación Promedio"] = df_recom.apply(formato_resumen_estrellas, axis=1)

            df_tabla = df_recom[["pelicula", "genero", "duracion", "organizador", "Calificación Promedio"]].copy()
            df_tabla.columns = ["Película 🎬", "Género 🎭", "Duración ⏱️", "Organizador 👑", "Calificación Promedio ⭐"]

            st.dataframe(df_tabla, use_container_width=True, hide_index=True)
        else:
            st.info("Aún no hay películas calificadas para recomendar.")
    except Exception as e:
        st.error(f"Error al cargar las recomendaciones: {e}")

elif menu == "Películas y enlaces":
    st.title("🍿 Películas y enlaces de transmisión")
    st.markdown("Consulta las sesiones programadas, la fecha y hora de encuentro, los enlaces de llamada y cuántas personas asistirán.")

    try:
        # 1. Consultar la tabla principal incluyendo s_fecha_evento
        query_tabla = f"""
            SELECT DISTINCT s.s_id_sesion,
                            p.p_titulo AS pelicula,
                            p.p_genero_principal AS genero,
                            s.s_fecha_evento AS fecha_hora,
                            s.s_duracion_minutos AS duracion,
                            o.o_nombre AS organizador,
                            s.s_enlace AS enlace,
                            s.s_asistencia_confirmada AS asistencia
            FROM {ESQUEMA}.sesion_pelicula s
            JOIN {ESQUEMA}.pelicula p ON s.s_id_pelicula = p.p_id_pelicula
            JOIN {ESQUEMA}.organizador o ON s.s_id_organizador = o.o_id_organizador
            ORDER BY s.s_fecha_evento ASC
        """
        df = consultar(query_tabla)

        if df is not None and not df.empty:
            df.columns = [col.lower() for col in df.columns]

            df["fecha_formateada"] = pd.to_datetime(df["fecha_hora"]).dt.strftime('%Y-%m-%d | %I:%M %p')

            # Función para contar cuántas personas confirmaron que sí van
            def contar_asistentes(val):
                if pd.isna(val) or val is None or str(val).strip() == "":
                    return "0 personas"
                cant = str(val).count("Sí voy 🎉")
                if cant == 0:
                    return "0 personas"
                elif cant == 1:
                    return "1 persona 🎉"
                else:
                    return f"{cant} personas 🎉"

            df["total_asistentes"] = df["asistencia"].apply(contar_asistentes)
            df["enlace"] = df["enlace"].fillna("Sin enlace asignado")

            # Seleccionar y renombrar las columnas incluyendo la fecha y hora
            df_tabla_final = df[["pelicula", "genero", "fecha_formateada", "duracion", "organizador", "total_asistentes", "enlace"]].copy()
            df_tabla_final.columns = ["Película", "Género", "Fecha y Hora", "Duración (min)", "Organizador", "Asistentes Confirmados 👥", "Enlace de Sesión"]

            st.dataframe(df_tabla_final, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("📝 Confirma tu asistencia")

            # Consultar usuarios para el formulario de asistencia de abajo
            df_usu = consultar(f"SELECT u_id_usuario, u_nombre FROM {ESQUEMA}.usuario")

            if df_usu is None or df_usu.empty:
                st.warning("⚠️ Primero debes registrar al menos un usuario en la sección 'Agregar Información'.")
            else:
                df_usu.columns = [col.lower() for col in df_usu.columns]

                # Incluir la fecha y hora en el selector de películas para mayor claridad
                sesion_dict = dict(zip(
                    df.apply(lambda r: f"🎬 {r['pelicula']} — {r['fecha_formateada']} (Organizador: {r['organizador']})", axis=1),
                    df["s_id_sesion"]
                ))

                sel_sesion_etiqueta = st.selectbox("Selecciona la película a la que deseas responder:",
                                                   list(sesion_dict.keys()))
                id_sesion_elegida = sesion_dict[sel_sesion_etiqueta]

                user_dict = dict(zip(df_usu["u_nombre"], df_usu["u_id_usuario"]))
                sel_usuario = st.selectbox("Selecciona tu nombre:", list(user_dict.keys()))

                estado_asistencia = st.radio("¿Vas a asistir?", ["Sí voy 🎉", "No voy"])

                if st.button("Guardar mi respuesta de asistencia"):
                    try:
                        q_act = f"SELECT s_asistencia_confirmada FROM {ESQUEMA}.sesion_pelicula WHERE s_id_sesion = :1"
                        df_act = consultar(q_act, (int(id_sesion_elegida),))

                        texto_actual = ""
                        if df_act is not None and not df_act.empty:
                            df_act.columns = [col.lower() for col in df_act.columns]
                            val_col = df_act.iloc[0].get("s_asistencia_confirmada")
                            if val_col and not pd.isna(val_col):
                                texto_actual = str(val_col)

                        # Actualizar o agregar respuesta evitando duplicados del usuario
                        nuevo_registro = f"{sel_usuario}: {estado_asistencia}"
                        lineas = [l for l in texto_actual.split(" | ") if l and not l.startswith(f"{sel_usuario}:")]
                        lineas.append(nuevo_registro)
                        texto_final = " | ".join(lineas)

                        sql_upd = f"UPDATE {ESQUEMA}.sesion_pelicula SET s_asistencia_confirmada = :1 WHERE s_id_sesion = :2"
                        modificar(sql_upd, (texto_final, int(id_sesion_elegida)))
                        st.success(f"¡Excelente {sel_usuario}! Tu respuesta '{estado_asistencia}' ha sido guardada.")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error al registrar la asistencia: {ex}")
        else:
            st.info("No hay sesiones de películas registradas todavía.")
    except Exception as e:
        st.error(f"Error al cargar las películas y enlaces: {e}")

elif menu == "Películas ya vistas":
    st.title("📜 Historial de películas vistas")
    st.markdown("Registro de maratones pasadas, asistencia y espacio para calificar.")

    try:
        # Consulta limpia del historial
        query = """
            SELECT DISTINCT s.s_id_sesion, 
                            p.p_titulo AS pelicula, 
                            p.p_genero_principal AS genero, 
                            s.s_fecha_evento AS fecha, 
                            s.s_duracion_minutos AS duracion, 
                            o.o_nombre AS organizador, 
                            s.s_asistencia_confirmada AS asistencia
            FROM sesion_pelicula s
            JOIN pelicula p ON s.s_id_pelicula = p.p_id_pelicula
            JOIN organizador o ON s.s_id_organizador = o.o_id_organizador
            ORDER BY s.s_fecha_evento DESC
        """
        df = consultar(query)

        if df is not None and not df.empty:
            df.columns = [col.lower() for col in df.columns]

            def evaluar_asistencia(val):
                if pd.isna(val) or val is None or str(val).strip() == "":
                    return "Mas raroooo, no nos pudimos poner de acuerdo 😅"
                cant = str(val).count("Sí voy 🎉")
                if cant == 0:
                    return "Mas raroooo, no nos pudimos poner de acuerdo 😅"
                elif cant == 1:
                    return "1 persona asistió 🍿"
                else:
                    return f"{cant} personas asistieron 🎉"


            df["Asistencia / Estado"] = df["asistencia"].apply(evaluar_asistencia)
            df["fecha"] = df["fecha"].astype(str).str[:10]

            # Tabla limpia de historial (SIN columna de estrellas, solo datos y asistencia)
            df_mostrar = df[["pelicula", "genero", "fecha", "duracion", "organizador", "Asistencia / Estado"]].copy()
            df_mostrar.columns = ["Película 🎬", "Género 🎭", "Fecha 📅", "Duración (min) ⏱️", "Organizador 👑",
                                  "Asistencia 👥"]

            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("⭐ Califica una película (por persona)")
            st.markdown(
                "Selecciona tu nombre y dale tu puntuación a la película que viste para actualizar el promedio comunitario.")

            # Formulario individual de calificación por usuario
            df_usu = consultar("SELECT u_id_usuario, u_nombre FROM usuario")
            if df_usu is not None and not df_usu.empty:
                df_usu.columns = [col.lower() for col in df_usu.columns]

                dict_sesiones = dict(zip(
                    df.apply(lambda r: f"🎬 {r['pelicula']} (Organizada por {r['organizador']})", axis=1),
                    df["s_id_sesion"]
                ))
                sel_pelicula_txt = st.selectbox("Selecciona la película:", list(dict_sesiones.keys()))
                id_sesion_sel = dict_sesiones[sel_pelicula_txt]

                user_list = df_usu["u_nombre"].tolist()
                sel_usuario_cal = st.selectbox("Selecciona tu nombre:", user_list, key="u_calif_historial")

                estrellas_dadas = st.slider("Tu calificación en estrellas:", min_value=1, max_value=5, value=5,
                                            help="1 = Malísima, 5 = 100% recomendada")

                if st.button("Guardar mi calificación"):
                    try:
                        q_actual = "SELECT s_calificacion_detalle FROM sesion_pelicula WHERE s_id_sesion = :1"
                        df_act_c = consultar(q_actual, (int(id_sesion_sel),))

                        texto_cal_actual = ""
                        if df_act_c is not None and not df_act_c.empty:
                            df_act_c.columns = [c.lower() for c in df_act_c.columns]
                            val_c = df_act_c.iloc[0].get("s_calificacion_detalle")
                            if val_c and not pd.isna(val_c):
                                texto_cal_actual = str(val_c)

                        # Registrar o actualizar el voto del usuario
                        nuevo_voto = f"{sel_usuario_cal}: {estrellas_dadas}⭐"
                        votos_previos = [v for v in texto_cal_actual.split(" | ") if
                                         v and not v.startswith(f"{sel_usuario_cal}:")]
                        votos_previos.append(nuevo_voto)
                        texto_cal_final = " | ".join(votos_previos)

                        import re

                        todas_las_notas = [int(n) for n in re.findall(r'(\d+)⭐', texto_cal_final)]
                        nuevo_promedio = sum(todas_las_notas) / len(todas_las_notas) if todas_las_notas else 5.0

                        sql_upd_cal = """
                            UPDATE sesion_pelicula 
                            SET s_calificacion_detalle = :1, 
                                s_calificacion = :2 
                            WHERE s_id_sesion = :3
                        """
                        modificar(sql_upd_cal, (texto_cal_final, float(nuevo_promedio), int(id_sesion_sel)))
                        st.success(
                            f"¡Listo {sel_usuario_cal}! Tu calificación de {estrellas_dadas}⭐ ha sido guardada con éxito.")
                        st.rerun()
                    except Exception as ex_c:
                        st.error(f"Error al registrar la calificación: {ex_c}")
            else:
                st.warning("⚠️ Debes registrar al menos un usuario primero en la sección de agregar información.")
        else:
            st.info("Aún no hay un historial de películas registradas.")

    except Exception as e:
        st.error(f"Error al cargar el historial: {e}")

elif menu == "Agregar información":
    st.title("➕ Agregar nuevos registros")

    t_pel, t_org, t_plat, t_usu, t_ses, t_link = st.tabs(["Película", "Organizador", "Plataforma", "Usuario", "Sesión", "Enlace de sesión"])

    with t_pel:
        with st.form("form_peli"):
            tit = st.text_input("Título de la película")
            gen = st.text_input("Género principal (ej. Animación, Suspenso)")
            ano = st.number_input("Año de estreno", min_value=1900, max_value=2100, value=2024)
            clas = st.selectbox("Clasificación de edad", ['G', 'PG', 'PG-13', 'R', 'NC-17', '+12', '+15', '+18'])
            if st.form_submit_button("Guardar película") and tit:
                try:
                    sql = f"INSERT INTO {ESQUEMA}.pelicula (p_titulo, p_genero_principal, p_anio_estreno, p_clasificacion_edad) VALUES (:1, :2, :3, :4)"
                    modificar(sql, (tit, gen, ano, clas))
                    st.success(f"Película '{tit}' agregada exitosamente.")
                except Exception as ex:
                    st.error(f"Error: {ex}")

    with t_org:
        with st.form("form_org"):
            nom = st.text_input("Nombre del organizador")
            pais = st.text_input("País de Residencia")
            if st.form_submit_button("Guardar Organizador") and nom:
                try:
                    sql = f"INSERT INTO {ESQUEMA}.organizador (o_nombre, o_pais_residencia) VALUES (:1, :2)"
                    modificar(sql, (nom, pais))
                    st.success(f"Organizador '{nom}' agregado exitosamente.")
                except Exception as ex:
                    st.error(f"Error: {ex}")

    with t_plat:
        with st.form("form_plat"):
            npl = st.text_input("Nombre de la plataforma")
            trans = st.selectbox("¿Permite transmitir en llamada?", [1, 0],
                                 format_func=lambda x: "Sí (1)" if x == 1 else "No (0)")
            if st.form_submit_button("Guardar plataforma") and npl:
                try:
                    sql = f"INSERT INTO {ESQUEMA}.plataforma (pl_nombre_plataforma, pl_permite_trans_llamada) VALUES (:1, :2)"
                    modificar(sql, (npl, trans))
                    st.success(f"Plataforma '{npl}' agregada exitosamente.")
                except Exception as ex:
                    st.error(f"Error: {ex}")

    with t_usu:
        with st.form("form_usu"):
            unom = st.text_input("Nombre del usuario")
            if st.form_submit_button("Guardar usuario") and unom:
                try:
                    sql = f"INSERT INTO {ESQUEMA}.usuario (u_nombre) VALUES (:1)"
                    modificar(sql, (unom,))
                    st.success(f"Usuario '{unom}' agregado exitosamente.")
                except Exception as ex:
                    st.error(f"Error: {ex}")

    with t_ses:
        with st.form("form_ses"):
            st.subheader("Programar nueva sesión")

            try:
                df_orgs = consultar(f"SELECT o_id_organizador, o_nombre FROM {ESQUEMA}.organizador")
                df_pels = consultar(f"SELECT p_id_pelicula, p_titulo FROM {ESQUEMA}.pelicula")
                df_plats = consultar(f"SELECT pl_id_plataforma, pl_nombre_plataforma FROM {ESQUEMA}.plataforma")
            except Exception:
                df_orgs, df_pels, df_plats = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

            if not df_orgs.empty:
                org_dict = dict(zip(df_orgs["o_nombre"], df_orgs["o_id_organizador"]))
                org_sel = st.selectbox("Organizador", list(org_dict.keys()))
                id_org = org_dict[org_sel]
            else:
                id_org = st.number_input("ID Organizador", min_value=1, step=1)

            if not df_pels.empty:
                pel_dict = dict(zip(df_pels["p_titulo"], df_pels["p_id_pelicula"]))
                pel_sel = st.selectbox("Película", list(pel_dict.keys()))
                id_pel = pel_dict[pel_sel]
            else:
                id_pel = st.number_input("ID película", min_value=1, step=1)

            if not df_plats.empty:
                plat_dict = dict(zip(df_plats["pl_nombre_plataforma"], df_plats["pl_id_plataforma"]))
                plat_sel = st.selectbox("Plataforma de streaming", list(plat_dict.keys()))
                id_plat = plat_dict[plat_sel]
            else:
                id_plat = st.number_input("ID plataforma", min_value=1, step=1)

            # --- FECHA Y HORA SEPARADAS ---
            col_f, col_h = st.columns(2)
            with col_f:
                fec = st.date_input("Fecha del evento")
            with col_h:
                hor = st.time_input("Hora de inicio")

            dur = st.number_input("Duración en minutos", min_value=1, value=120)
            aud = st.selectbox("Tipo de audiencia", ['AMIGOS', 'FAMILIA', 'COMPAÑEROS', 'OTRO'])

            if st.form_submit_button("Programar sesión"):
                try:
                    import datetime
                    fecha_hora_completa = datetime.datetime.combine(fec, hor)

                    sql = f"""
                        INSERT INTO {ESQUEMA}.sesion_pelicula 
                        (s_id_organizador, s_id_pelicula, s_id_plataforma_streaming, s_fecha_evento, s_duracion_minutos, s_tipo_audiencia) 
                        VALUES (:1, :2, :3, :4, :5, :6)
                    """
                    modificar(sql, (int(id_org), int(id_pel), int(id_plat), fecha_hora_completa, int(dur), aud))
                    st.success("¡Sesión programada exitosamente con fecha y hora!")
                except Exception as ex:
                    st.error(f"Error al programar la sesión: {ex}")

    with t_link:
        with st.form("form_link_sesion"):
            st.subheader("🔗 Enlace de sala virtual")
            st.markdown("Selecciona una sesión programada para asignarle o actualizar su enlace de videollamada.")

            try:
                q_ses = f"""
                    SELECT s.s_id_sesion, p.p_titulo, s.s_fecha_evento 
                    FROM {ESQUEMA}.sesion_pelicula s
                    JOIN {ESQUEMA}.pelicula p ON s.s_id_pelicula = p.p_id_pelicula
                    ORDER BY s.s_fecha_evento DESC
                """
                df_slist = consultar(q_ses)
            except Exception:
                df_slist = pd.DataFrame()

            if not df_slist.empty:
                df_slist["etiqueta"] = df_slist.apply(
                    lambda r: f"Sesión #{r['s_id_sesion']} — 🎬 {r['p_titulo']} (📅 {str(r['s_fecha_evento'])})",
                    axis=1
                )
                s_dict = dict(zip(df_slist["etiqueta"], df_slist["s_id_sesion"]))
                sel_etiqueta = st.selectbox("Selecciona la sesión:", list(s_dict.keys()))
                sid_elegido = s_dict[sel_etiqueta]

                nuevo_enlace = st.text_input("Ingresa la URL de la sala (Meet / Zoom / Discord):")

                if st.form_submit_button("Guardar enlace en la sesión"):
                    if nuevo_enlace.strip():
                        try:
                            sql_upd = f"UPDATE {ESQUEMA}.sesion_pelicula SET s_enlace = :1 WHERE s_id_sesion = :2"
                            modificar(sql_upd, (nuevo_enlace.strip(), int(sid_elegido)))
                            st.success(f"¡Enlace guardado con éxito para la sesión #{sid_elegido}!")
                        except Exception as ex:
                            st.error(f"Error al actualizar el enlace: {ex}")
                    else:
                        st.warning("Por favor ingresa un enlace válido.")
            else:
                st.info("No hay sesiones registradas para asignar enlaces.")