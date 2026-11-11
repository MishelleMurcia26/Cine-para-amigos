-- =====================================================================
-- INSERCIÓN DE DATOS DE PRUEBA
-- =====================================================================
SELECT * FROM sesion_pelicula;

-- 1. INSERTAR USUARIOS
INSERT INTO usuario (u_nombre) VALUES ('Mishelle Murcia');
INSERT INTO usuario (u_nombre) VALUES ('Ana Muñoz');
INSERT INTO usuario (u_nombre) VALUES ('Isabela Chavarria');
INSERT INTO usuario (u_nombre) VALUES ('Ximena Londoño');
INSERT INTO usuario (u_nombre) VALUES ('Lina Chaves');

-- 2. INSERTAR ORGANIZADORES
INSERT INTO organizador (o_nombre, o_pais_residencia) VALUES ('Mishelle Murcia', 'Colombia');
INSERT INTO organizador (o_nombre, o_pais_residencia) VALUES ('Ana Muñoz', 'Colombia');
INSERT INTO organizador (o_nombre, o_pais_residencia) VALUES ('Isabela Chavarria', 'México');

-- 3. INSERTAR PELÍCULAS
INSERT INTO pelicula (p_titulo, p_genero_principal, p_anio_estreno, p_clasificacion_edad) 
VALUES ('El Viaje de Chihiro', 'Animación', 2001, '+12');

INSERT INTO pelicula (p_titulo, p_genero_principal, p_anio_estreno, p_clasificacion_edad) 
VALUES ('Interestelar', 'Ciencia Ficción', 2014, '+12');

INSERT INTO pelicula (p_titulo, p_genero_principal, p_anio_estreno, p_clasificacion_edad) 
VALUES ('Parasitos', 'Suspenso', 2019, '+18');

-- 4. INSERTAR PLATAFORMAS DE STREAMING (1 = Sí permite llamada, 0 = No)
INSERT INTO plataforma (pl_nombre_plataforma, pl_permite_trans_llamada) VALUES ('Netflix', 1);
INSERT INTO plataforma (pl_nombre_plataforma, pl_permite_trans_llamada) VALUES ('Disney+', 1);
INSERT INTO plataforma (pl_nombre_plataforma, pl_permite_trans_llamada) VALUES ('Amazon Prime', 0);

-- 5. INSERTAR SESIONES DE CINE (Tabla de hechos)
-- Sesión 1 organizada por Mishelle (id 1), Película 1, Plataforma 1
INSERT INTO sesion_pelicula (s_id_organizador, s_id_pelicula, s_id_plataforma_streaming, s_fecha_evento, s_duracion_minutos, s_tipo_audiencia)
VALUES (1, 1, 21, TO_DATE('15/10/2026 20:00:00', 'DD/MM/YYYY HH24:MI:SS'), 125, 'AMIGOS');

-- Sesión 2 organizada por Carlos (id 2), Película 2, Plataforma 2
INSERT INTO sesion_pelicula (s_id_organizador, s_id_pelicula, s_id_plataforma_streaming, s_fecha_evento, s_duracion_minutos, s_tipo_audiencia)
VALUES (2, 5, 22, TO_DATE('18/10/2026 21:30:00', 'DD/MM/YYYY HH24:MI:SS'), 169, 'FAMILIA');

-- Sesión 3 organizada por Ana (id 3), Película 3, Plataforma 1
INSERT INTO sesion_pelicula (s_id_organizador, s_id_pelicula, s_id_plataforma_streaming, s_fecha_evento, s_duracion_minutos, s_tipo_audiencia)
VALUES (3, 3, 21, TO_DATE('20/10/2026 19:00:00', 'DD/MM/YYYY HH24:MI:SS'), 132, 'COMPAÑEROS');

-- 6. INSERTAR PARTICIPACIÓN DE USUARIOS (Sesión 1: 4 participantes)
INSERT INTO sesion_usuario (su_id_sesion, su_id_usuario, su_asistio, su_rol_usuario) VALUES (1, 1, 1, 'ORGANIZADOR');
INSERT INTO sesion_usuario (su_id_sesion, su_id_usuario, su_asistio, su_rol_usuario) VALUES (1, 2, 1, 'ASISTENTE');
INSERT INTO sesion_usuario (su_id_sesion, su_id_usuario, su_asistio, su_rol_usuario) VALUES (1, 3, 1, 'ASISTENTE');
INSERT INTO sesion_usuario (su_id_sesion, su_id_usuario, su_asistio, su_rol_usuario) VALUES (1, 4, 0, 'ASISTENTE'); -- No asistió

-- Participación Sesión 2: 3 participantes
INSERT INTO sesion_usuario (su_id_sesion, su_id_usuario, su_asistio, su_rol_usuario) VALUES (6, 2, 1, 'ORGANIZADOR');
INSERT INTO sesion_usuario (su_id_sesion, su_id_usuario, su_asistio, su_rol_usuario) VALUES (6, 1, 1, 'ASISTENTE');
INSERT INTO sesion_usuario (su_id_sesion, su_id_usuario, su_asistio, su_rol_usuario) VALUES (6, 5, 1, 'ASISTENTE');

-- Participación Sesión 3: 3 participantes
INSERT INTO sesion_usuario (su_id_sesion, su_id_usuario, su_asistio, su_rol_usuario) VALUES (3, 3, 1, 'ORGANIZADOR');
INSERT INTO sesion_usuario (su_id_sesion, su_id_usuario, su_asistio, su_rol_usuario) VALUES (3, 4, 1, 'ASISTENTE');
INSERT INTO sesion_usuario (su_id_sesion, su_id_usuario, su_asistio, su_rol_usuario) VALUES (3, 5, 0, 'ASISTENTE'); -- No asistió

COMMIT;