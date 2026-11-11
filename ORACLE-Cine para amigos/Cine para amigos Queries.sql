-------------CONSULTAS DE VALIDACIÓN Y ANÁLISIS------------------------

-- 1. Listado completo de sesiones con fecha, duración, organizador, película y plataforma
SELECT 
    s.s_id_sesion AS id_sesion,
    TO_CHAR(s.s_fecha_evento, 'DD/MM/YYYY HH24:MI') AS fecha_hora,
    s.s_duracion_minutos AS duracion,
    o.o_nombre AS organizador,
    p.p_titulo AS pelicula,
    pl.pl_nombre_plataforma AS plataforma
FROM sesion_pelicula s
JOIN organizador o ON s.s_id_organizador = o.o_id_organizador
JOIN pelicula p ON s.s_id_pelicula = p.p_id_pelicula
JOIN plataforma pl ON s.s_id_plataforma_streaming = pl.pl_id_plataforma;

-- 2. Cantidad total de usuarios registrados en cada sesión
SELECT 
    su_id_sesion AS id_sesion,
    COUNT(*) AS total_registrados
FROM sesion_usuario
GROUP BY su_id_sesion
ORDER BY su_id_sesion;

-- 3. Cantidad de usuarios que asistieron efectivamente a cada sesión (su_asistio = 1)
SELECT 
    su_id_sesion AS id_sesion,
    SUM(su_asistio) AS total_asistentes_efectivos
FROM sesion_usuario
GROUP BY su_id_sesion
ORDER BY su_id_sesion;

-- 4. Películas más vistas (basado en asistentes efectivos)
SELECT 
    p.p_titulo AS pelicula,
    SUM(su.su_asistio) AS total_asistencias
FROM pelicula p
JOIN sesion_pelicula s ON p.p_id_pelicula = s.s_id_pelicula
JOIN sesion_usuario su ON s.s_id_sesion = su.su_id_sesion
GROUP BY p.p_titulo
ORDER BY total_asistencias DESC;

-- 5. Plataformas de streaming más utilizadas
SELECT 
    pl.pl_nombre_plataforma AS plataforma,
    COUNT(s.s_id_sesion) AS total_sesiones_organizadas
FROM plataforma pl
LEFT JOIN sesion_pelicula s ON pl.pl_id_plataforma = s.s_id_plataforma_streaming
GROUP BY pl.pl_nombre_plataforma
ORDER BY total_sesiones_organizadas DESC;

-- 6. Número de sesiones organizadas por persona
SELECT 
    o.o_nombre AS organizador,
    COUNT(s.s_id_sesion) AS sesiones_organizadas
FROM organizador o
LEFT JOIN sesion_pelicula s ON o.o_id_organizador = s.s_id_organizador
GROUP BY o.o_nombre
ORDER BY sesiones_organizadas DESC;

-- 7. Duración promedio de las sesiones de cine
SELECT 
    ROUND(AVG(s_duracion_minutos), 2) AS duracion_promedio_minutos
FROM sesion_pelicula;

-- 8. Número de participantes e índice de asistencia por sesión
SELECT 
    s.s_id_sesion,
    p.p_titulo,
    COUNT(su.su_id_usuario) AS registrados,
    SUM(su.su_asistio) AS asistentes_reales,
    ROUND((SUM(su.su_asistio) / COUNT(su.su_id_usuario)) * 100, 2) AS porcentaje_asistencia
FROM sesion_pelicula s
JOIN pelicula p ON s.s_id_pelicula = p.p_id_pelicula
JOIN sesion_usuario su ON s.s_id_sesion = su.su_id_sesion
GROUP BY s.s_id_sesion, p.p_titulo
ORDER BY s.s_id_sesion;

-- 9. Sesiones agrupadas por tipo de audiencia
SELECT 
    s_tipo_audiencia AS tipo_audiencia,
    COUNT(*) AS cantidad_sesiones
FROM sesion_pelicula
GROUP BY s_tipo_audiencia
ORDER BY cantidad_sesiones DESC;
