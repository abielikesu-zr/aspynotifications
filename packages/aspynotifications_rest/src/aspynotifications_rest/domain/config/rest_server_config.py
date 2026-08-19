from pydantic import BaseModel, ConfigDict, Field


class AspyNotificationsRestServerConfig(BaseModel):
    host: str = Field(
        default="127.0.0.1",
        description="REST server host",
    )
    port: int = Field(
        default=50011,
        description="REST server port",
    )


class AspyNotificationsRestAppConfigParams(BaseModel):
    rest_server: AspyNotificationsRestServerConfig = Field(
        default_factory=AspyNotificationsRestServerConfig,
    )


class AspyNotificationsRestAppConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    aspynotifications_rest: AspyNotificationsRestAppConfigParams = Field(
        default_factory=AspyNotificationsRestAppConfigParams,
    )
