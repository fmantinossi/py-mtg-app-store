-- Exemplo: cria uma schema e habilita extensão útil (se você usar)
CREATE SCHEMA IF NOT EXISTS app;

-- Se você for usar UUID no banco, pode ser útil:
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";