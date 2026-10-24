# Keep in sync with pytest-homeassistant-custom-component in pyproject.toml (it pins homeassistant).
ARG HA_VERSION=2026.10.2
FROM ghcr.io/home-assistant/home-assistant:${HA_VERSION}

# The HA image starts hass via s6 init; the devcontainer runs it on demand via scripts/develop instead.
ENTRYPOINT []

RUN apk add --no-cache bash ffmpeg

# Install the integration's runtime + dev dependencies into the image's Python, alongside HA.
# The image prefers HA's musllinux wheel index, which lacks some versions; also allow PyPI's.
COPY pyproject.toml /tmp/ha_foobar2k/pyproject.toml
RUN cd /tmp/ha_foobar2k \
    && uv pip install --system --no-cache --index-strategy unsafe-best-match -r pyproject.toml --group dev \
    && rm -rf /tmp/ha_foobar2k

WORKDIR /workspaces/ha_foobar2k
