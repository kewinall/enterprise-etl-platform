FROM apache/hop:2.19.0

ARG VERSION=dev
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="Enterprise ETL Platform Hop Runtime" \
      org.opencontainers.image.description="Immutable Apache Hop runtime with the ETL project baked into the image" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.source="https://github.com/kewinall/enterprise-etl-platform"

COPY --chown=hop:hop hop/projects/enterprise-etl /opt/enterprise-etl/project

ENV HOP_PROJECT_FOLDER=/opt/enterprise-etl/project \
    HOP_PROJECT_NAME=enterprise-etl
