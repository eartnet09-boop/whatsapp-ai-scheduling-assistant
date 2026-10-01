-- 001_create_cartao_visita.sql
--
-- Business card table used by the "Buscar Cartão de Visita" node.
--
-- INFERENCE: this DDL was reverse-engineered from the SELECT executed by the
-- workflow:
--
--     SELECT imagem_base64, mimetype, filename, legenda
--     FROM cartao_visita
--     ORDER BY id DESC
--     LIMIT 1;
--
-- The real project schema may differ (extra columns, different types). Treat
-- this file as a starting point, not as the authoritative schema.
--
-- Apply with:  psql -U <user> -d <database> -f sql/001_create_cartao_visita.sql

CREATE TABLE IF NOT EXISTS cartao_visita (
    id            BIGSERIAL PRIMARY KEY,
    imagem_base64 TEXT        NOT NULL,
    mimetype      TEXT        NOT NULL,
    filename      TEXT,
    legenda       TEXT,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE cartao_visita IS
    'Latest row wins: the workflow always reads ORDER BY id DESC LIMIT 1.';
COMMENT ON COLUMN cartao_visita.imagem_base64 IS
    'Business card image encoded as base64 (no data: URI prefix).';
COMMENT ON COLUMN cartao_visita.mimetype IS
    'Image MIME type, e.g. image/png or image/jpeg.';
COMMENT ON COLUMN cartao_visita.filename IS
    'Original file name, kept for reference only.';
COMMENT ON COLUMN cartao_visita.legenda IS
    'Caption sent together with the image by the WAHA sendImage call.';

-- Example row with clearly fictitious data.
-- To generate imagem_base64 from a real image file:
--   Linux/macOS:  base64 -w0 card.png
--   Python:       python -c "import base64;print(base64.b64encode(open('card.png','rb').read()).decode())"
-- Then paste the resulting string below (a real card is a few hundred KB of
-- text; keep it out of version control and insert it directly in the database).
INSERT INTO cartao_visita (imagem_base64, mimetype, filename, legenda)
VALUES (
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
    'image/png',
    'business-card-example.png',
    'EAR Automação — automações e orquestração de agentes de IA. Envie uma mensagem para começar.'
);
