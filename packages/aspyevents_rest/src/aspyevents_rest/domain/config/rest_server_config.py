from pydantic import BaseModel, ConfigDict, Field


class AspyEventsRestServerConfig(BaseModel):
    host: str = Field(
        default="127.0.0.1",
        description="REST server host",
    )
    port: int = Field(
        default=50012,
        description="REST server port",
    )


class AspyEventsRestAppConfigParams(BaseModel):
    rest_server: AspyEventsRestServerConfig = Field(
        default_factory=AspyEventsRestServerConfig,
    )


class AspyEventsRestAppConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    aspyevents_rest: AspyEventsRestAppConfigParams = Field(
        default_factory=AspyEventsRestAppConfigParams,
    )
