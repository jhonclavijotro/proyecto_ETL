CREATE TABLE datos_consolidados (
    id SERIAL PRIMARY KEY,
    hoja VARCHAR(255),
    segmento VARCHAR(255),
    intervalo VARCHAR(255),
    concepto VARCHAR(255),
    ano INT,
    periodo VARCHAR(50),
    valor DECIMAL
);

CREATE TABLE estadisticas_educacion (
    id SERIAL PRIMARY KEY,
    area_conocimiento VARCHAR(255),
    matriculados INT,
    admitidos INT,
    primer_grado INT,
    graduados INT
);