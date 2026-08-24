from pydantic import BaseModel, Field


class NotificationTemplateRendererConfig(BaseModel):
    """
    Configuration for the notification template renderer.
    """

    template_root: str = Field(
        default=".",
        description="Root directory containing notification templates.",
    )
