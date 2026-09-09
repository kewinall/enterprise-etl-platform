CREATE SCHEMA IF NOT EXISTS etl_audit;

CREATE TABLE IF NOT EXISTS etl_audit.etl_execution_log (
    execution_id      BIGSERIAL PRIMARY KEY,
    pipeline_name     VARCHAR(200) NOT NULL,
    environment_name VARCHAR(20) NOT NULL CHECK (environment_name IN ('DEV', 'TEST', 'PROD')),
    run_id            VARCHAR(200) NOT NULL,
    status            VARCHAR(30) NOT NULL,
    started_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at       TIMESTAMPTZ,
    records_read      BIGINT DEFAULT 0,
    records_written   BIGINT DEFAULT 0,
    error_message     TEXT,
    metadata          JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_etl_execution_log_pipeline_started
    ON etl_audit.etl_execution_log (pipeline_name, started_at DESC);
