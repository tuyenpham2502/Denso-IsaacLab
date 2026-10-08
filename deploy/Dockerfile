# syntax=docker/dockerfile:1
ARG ARENA_BASE_IMAGE=denso-arena-base:1cfc849b2172
FROM ${ARENA_BASE_IMAGE}
USER root
ARG DENSO_COMMIT=unknown
ARG ARENA_COMMIT=unknown
LABEL org.opencontainers.image.source="https://github.com/tuyenpham2502/Denso-IsaacLab" \
      org.opencontainers.image.revision="${DENSO_COMMIT}" \
      io.denso.arena.revision="${ARENA_COMMIT}"
WORKDIR /workspaces/isaaclab_arena
COPY entrypoint.sh /opt/denso/entrypoint.sh
RUN chmod 755 /opt/denso/entrypoint.sh
ENV OMNI_KIT_ALLOW_ROOT=1 \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics,video,display
# Replace the upstream developer entrypoint (interactive user provisioning).
ENTRYPOINT ["/opt/denso/entrypoint.sh"]
CMD ["smoke"]
