CREATE SCHEMA IF NOT EXISTS etl_observability;

CREATE OR REPLACE VIEW etl_observability.pipeline_status_totals AS
SELECT
    pipeline_name,
    environment_name,
    status,
    count(*)::DOUBLE PRECISION AS run_count
FROM etl_audit.etl_execution_log
GROUP BY pipeline_name, environment_name, status;

CREATE OR REPLACE VIEW etl_observability.pipeline_runtime_metrics AS
SELECT
    pipeline_name,
    environment_name,
    count(*) FILTER (WHERE attempt_number > 1)::DOUBLE PRECISION AS retry_count,
    COALESCE(sum(records_written), 0)::DOUBLE PRECISION AS records_written,
    count(*) FILTER (
        WHERE status = 'RUNNING'
          AND started_at < CURRENT_TIMESTAMP - INTERVAL '30 minutes'
    )::DOUBLE PRECISION AS stale_running,
    COALESCE(
        EXTRACT(EPOCH FROM max(finished_at) FILTER (WHERE status = 'SUCCESS')),
        0
    )::DOUBLE PRECISION AS last_success_timestamp_seconds,
    COALESCE(
        avg(EXTRACT(EPOCH FROM (finished_at - started_at)))
            FILTER (WHERE status IN ('SUCCESS', 'FAILED') AND finished_at IS NOT NULL),
        0
    )::DOUBLE PRECISION AS average_duration_seconds,
    COALESCE(
        percentile_cont(0.95) WITHIN GROUP (
            ORDER BY EXTRACT(EPOCH FROM (finished_at - started_at))
        ) FILTER (WHERE status IN ('SUCCESS', 'FAILED') AND finished_at IS NOT NULL),
        0
    )::DOUBLE PRECISION AS p95_duration_seconds
FROM etl_audit.etl_execution_log
GROUP BY pipeline_name, environment_name;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'etl_monitor'
    ) THEN
        CREATE ROLE etl_monitor LOGIN PASSWORD 'synthetic-monitor-password';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE etl_audit TO etl_monitor;
GRANT USAGE ON SCHEMA etl_observability TO etl_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA etl_observability TO etl_monitor;

COMMENT ON SCHEMA etl_observability IS
    'Read-only synthetic observability surface for Prometheus SQL Exporter.';
