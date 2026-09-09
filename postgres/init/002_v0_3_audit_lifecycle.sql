CREATE SCHEMA IF NOT EXISTS etl_data;

ALTER TABLE etl_audit.etl_execution_log
    ADD COLUMN IF NOT EXISTS correlation_id VARCHAR(300),
    ADD COLUMN IF NOT EXISTS attempt_number INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS trigger_type VARCHAR(30) NOT NULL DEFAULT 'MANUAL';

UPDATE etl_audit.etl_execution_log
SET correlation_id = pipeline_name || ':' || run_id
WHERE correlation_id IS NULL;

ALTER TABLE etl_audit.etl_execution_log
    ALTER COLUMN correlation_id SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_etl_execution_status'
          AND conrelid = 'etl_audit.etl_execution_log'::regclass
    ) THEN
        ALTER TABLE etl_audit.etl_execution_log
            ADD CONSTRAINT chk_etl_execution_status
            CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')) NOT VALID;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_etl_execution_attempt'
          AND conrelid = 'etl_audit.etl_execution_log'::regclass
    ) THEN
        ALTER TABLE etl_audit.etl_execution_log
            ADD CONSTRAINT chk_etl_execution_attempt
            CHECK (attempt_number > 0) NOT VALID;
    END IF;
END
$$;

CREATE UNIQUE INDEX IF NOT EXISTS uq_etl_execution_attempt
    ON etl_audit.etl_execution_log
       (pipeline_name, environment_name, run_id, attempt_number);

CREATE INDEX IF NOT EXISTS idx_etl_execution_correlation
    ON etl_audit.etl_execution_log (correlation_id, attempt_number);

CREATE TABLE IF NOT EXISTS etl_audit.etl_execution_event (
    event_id          BIGSERIAL PRIMARY KEY,
    execution_id      BIGINT NOT NULL
                      REFERENCES etl_audit.etl_execution_log(execution_id)
                      ON DELETE CASCADE,
    event_type        VARCHAR(30) NOT NULL,
    event_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    message           TEXT,
    metadata          JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_etl_execution_event_execution
    ON etl_audit.etl_execution_event (execution_id, event_at);

CREATE TABLE IF NOT EXISTS etl_data.synthetic_customer_daily (
    run_id            VARCHAR(200) NOT NULL,
    attempt_number    INTEGER NOT NULL,
    record_id         BIGINT NOT NULL,
    customer_segment  VARCHAR(100) NOT NULL,
    source_system     VARCHAR(100) NOT NULL,
    amount            NUMERIC(12,2) NOT NULL,
    environment_name  VARCHAR(20) NOT NULL,
    correlation_id    VARCHAR(300) NOT NULL,
    loaded_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (run_id, attempt_number, record_id)
);

CREATE INDEX IF NOT EXISTS idx_synthetic_customer_daily_loaded
    ON etl_data.synthetic_customer_daily (environment_name, loaded_at DESC);

CREATE OR REPLACE FUNCTION etl_audit.set_execution_finished_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status IN ('SUCCESS', 'FAILED')
       AND NEW.status IS DISTINCT FROM OLD.status THEN
        NEW.finished_at := CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_set_execution_finished_at
ON etl_audit.etl_execution_log;

CREATE TRIGGER trg_set_execution_finished_at
BEFORE UPDATE ON etl_audit.etl_execution_log
FOR EACH ROW
EXECUTE FUNCTION etl_audit.set_execution_finished_at();

CREATE OR REPLACE FUNCTION etl_audit.capture_execution_event()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    lifecycle_event VARCHAR(30);
    lifecycle_message TEXT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        lifecycle_event := 'STARTED';
        lifecycle_message := 'Execution attempt started';
    ELSIF TG_OP = 'UPDATE' AND NEW.status IS DISTINCT FROM OLD.status THEN
        lifecycle_event := CASE NEW.status
            WHEN 'SUCCESS' THEN 'SUCCEEDED'
            WHEN 'FAILED' THEN 'FAILED'
            ELSE NEW.status
        END;
        lifecycle_message := CASE
            WHEN NEW.status = 'FAILED'
                THEN COALESCE(NULLIF(NEW.error_message, ''), 'Execution attempt failed')
            ELSE 'Execution attempt completed successfully'
        END;
    ELSE
        RETURN NEW;
    END IF;

    INSERT INTO etl_audit.etl_execution_event (
        execution_id,
        event_type,
        message,
        metadata
    )
    VALUES (
        NEW.execution_id,
        lifecycle_event,
        lifecycle_message,
        jsonb_build_object(
            'pipeline_name', NEW.pipeline_name,
            'environment_name', NEW.environment_name,
            'run_id', NEW.run_id,
            'attempt_number', NEW.attempt_number,
            'correlation_id', NEW.correlation_id,
            'trigger_type', NEW.trigger_type
        )
    );

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_capture_execution_event
ON etl_audit.etl_execution_log;

CREATE TRIGGER trg_capture_execution_event
AFTER INSERT OR UPDATE ON etl_audit.etl_execution_log
FOR EACH ROW
EXECUTE FUNCTION etl_audit.capture_execution_event();
