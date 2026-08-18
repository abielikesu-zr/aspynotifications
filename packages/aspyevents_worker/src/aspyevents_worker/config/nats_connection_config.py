from pydantic import BaseModel, Field


class NatsConnectionConfig(BaseModel):
    """Configuration required to establish a connection to a NATS server."""

    nats_url: str = Field(
        default="nats://127.0.0.1:4222",
        description="URL of the NATS server to connect to.",
    )

    username: str | None = Field(
        default=None,
        description="Username used to authenticate with the NATS server.",
    )
    password: str | None = Field(
        default=None,
        description="Password used to authenticate with the NATS server.",
    )

    tls_ca_file: str | None = Field(
        default=None,
        description="Path to the CA certificate file used to verify the NATS server certificate.",
    )
    tls_cert_file: str | None = Field(
        default=None,
        description="Path to the client TLS certificate file used when establishing a mutual TLS connection.",
    )
    tls_key_file: str | None = Field(
        default=None,
        description="Path to the private key file corresponding to the client TLS certificate.",
    )
