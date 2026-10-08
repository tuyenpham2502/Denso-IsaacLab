# syntax=docker/dockerfile:1
ARG ISAACSIM_IMAGE=nvcr.io/nvidia/isaac-sim:6.1.0@sha256:0c16dd67d09a70ea474f2c809a13c4d09bd23c738184cf1bf28af487ecd39080
ARG ARENA_COMMIT=1cfc849b2172d040e2e5fce52322678f4f199387

# Fetch the exact Arena checkout and its recorded Lab/GR00T submodules inside
# the build. No host checkout, host Python, or prebuilt custom base is needed.
FROM ubuntu:24.04 AS arena-source
ARG ARENA_COMMIT
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates
RUN git init /arena && \
    git -C /arena remote add origin https://github.com/isaac-sim/IsaacLab-Arena.git && \
    git -C /arena fetch --depth 1 origin "${ARENA_COMMIT}" && \
    git -C /arena checkout --detach FETCH_HEAD && \
    test "$(git -C /arena rev-parse HEAD)" = "${ARENA_COMMIT}" && \
    git -C /arena -c 'url.https://github.com/.insteadOf=git@github.com:' \
        submodule update --init --recursive --depth 1

FROM ${ISAACSIM_IMAGE}
USER root
ARG DENSO_COMMIT=unknown
ARG ARENA_COMMIT
LABEL org.opencontainers.image.source="https://github.com/tuyenpham2502/Denso-IsaacLab" \
      org.opencontainers.image.revision="${DENSO_COMMIT}" \
      io.denso.arena.revision="${ARENA_COMMIT}"
ENV WORKDIR=/workspaces/isaaclab_arena \
    ISAACLAB_PATH=/workspaces/isaaclab_arena/submodules/IsaacLab \
    TERM=xterm \
    PIP_DEFAULT_TIMEOUT=300 \
    UV_HTTP_TIMEOUT=300
WORKDIR ${WORKDIR}

# Reuse the pinned upstream installation scripts and the same order as
# Arena's official Dockerfile, without its interactive developer entrypoint.
RUN --mount=type=bind,from=arena-source,source=/arena/docker/setup/install-system-deps.sh,target=/tmp/install-system-deps.sh \
    bash /tmp/install-system-deps.sh
COPY --from=arena-source /arena/submodules/IsaacLab ${ISAACLAB_PATH}
RUN --mount=type=bind,from=arena-source,source=/arena/docker/setup/install-isaaclab.sh,target=/tmp/install-isaaclab.sh \
    bash /tmp/install-isaaclab.sh
COPY --from=arena-source /arena/submodules/Isaac-GR00T ${WORKDIR}/submodules/Isaac-GR00T
RUN --mount=type=bind,from=arena-source,source=/arena/isaaclab_arena_openpi/docker/OPENPI_COMMIT,target=/tmp/openpi_commit \
    --mount=type=bind,from=arena-source,source=/arena/docker/setup/install-policy-clients.sh,target=/tmp/install-policy-clients.sh \
    bash /tmp/install-policy-clients.sh
RUN --mount=type=bind,from=arena-source,source=/arena/pyproject.toml,target=/tmp/arena-pyproject.toml \
    --mount=type=bind,from=arena-source,source=/arena/docker/setup/export_requirements.py,target=/tmp/export_requirements.py \
    --mount=type=bind,from=arena-source,source=/arena/docker/setup/install-arena-deps.sh,target=/tmp/install-arena-deps.sh \
    bash /tmp/install-arena-deps.sh
COPY --from=arena-source /arena/ ${WORKDIR}/
RUN /isaac-sim/python.sh -m pip install --no-deps --no-build-isolation -e "${WORKDIR}" && \
    /isaac-sim/python.sh -c "import importlib.metadata as m; [print(n, m.version(n)) for n in ('isaacsim', 'isaaclab', 'isaaclab_arena', 'isaacteleop')]"
COPY entrypoint.sh /opt/denso/entrypoint.sh
RUN chmod 755 /opt/denso/entrypoint.sh
ENV OMNI_KIT_ALLOW_ROOT=1 \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics,video,display
# Replace the upstream developer entrypoint (interactive user provisioning).
ENTRYPOINT ["/opt/denso/entrypoint.sh"]
CMD ["idle"]
