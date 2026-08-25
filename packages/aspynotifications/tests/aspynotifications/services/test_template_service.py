from unittest.mock import AsyncMock, MagicMock

import pytest

from aspynotifications.entities.source import TemplateSource
from aspynotifications.entities.template import SlackTemplate, Template
from aspynotifications.ports.template_port import ITemplateStorePort
from aspynotifications.services.template_service import TemplateService


def _template(blocks: str = "blocks: []") -> Template:
    return Template(
        name="slack-template",
        slack=SlackTemplate(blocks=TemplateSource(inline=blocks)),
    )


def _store() -> MagicMock:
    store = MagicMock(spec=ITemplateStorePort)
    store.get_template = AsyncMock()
    store.save_template = AsyncMock()
    return store


@pytest.mark.asyncio
async def test_update_template_persists_an_existing_template() -> None:
    store = _store()
    store.get_template.return_value = _template()
    updated_template = _template("blocks: updated")

    result = await TemplateService(config={}, store=store).update_template(
        updated_template
    )

    assert result == updated_template
    store.get_template.assert_awaited_once_with(updated_template.name)
    store.save_template.assert_awaited_once_with(updated_template)


@pytest.mark.asyncio
async def test_update_template_rejects_a_missing_template() -> None:
    store = _store()
    store.get_template.return_value = None
    template = _template()

    with pytest.raises(ValueError, match="Template not found: slack-template"):
        await TemplateService(config={}, store=store).update_template(template)

    store.save_template.assert_not_awaited()
