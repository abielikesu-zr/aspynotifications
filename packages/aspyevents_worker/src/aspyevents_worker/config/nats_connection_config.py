from pydantic import BaseModel


class NatsConnectionConfig(BaseModel):
    nats_url: str = "nats://localhost:4222"

    username: str | None = None
    password: str | None = None

    tls_ca_file: str | None = None
    tls_cert_file: str | None = None
    tls_key_file: str | None = None
