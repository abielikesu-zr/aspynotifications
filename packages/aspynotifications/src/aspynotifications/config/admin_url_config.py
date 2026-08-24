from pydantic import BaseModel, Field


class AdminUrlGeneratorConfig(BaseModel):
    """
    Configuration for the Admin URL generator.
    """

    system_name: str = Field(
        default="asai_admin",
        description="Name of the system providing the admin UI.",
    )

    base_url: str = Field(
        default="http://localhost:50031",
        description="Base URL of the admin UI.",
    )
