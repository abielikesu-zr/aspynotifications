# aspynotifications_cli

`aspynotifications_cli` es el cliente de linea de comandos que envia solicitudes al servicio REST de notificaciones mediante `aspynotifications_sdk`.

## Comandos disponibles

```text
send-event --from-file PATH [--output-format print|json] [-v|-q] [--log-format plain|json]
create-slack-provider --name NAME --webhook-url URL
create-vscode-provider --name NAME --relay-url URL
create-zeptomail-provider --name NAME --from-address ADDRESS --send-mail-token TOKEN
create-shole-provider --name NAME
update-slack-provider --id PROVIDER_ID --webhook-url URL
update-vscode-provider --id PROVIDER_ID --relay-url URL
update-zeptomail-provider --id PROVIDER_ID --from-address ADDRESS --send-mail-token TOKEN
update-shole-provider --id PROVIDER_ID
create-template --name NAME [--slack-blocks-inline BLOCKS]
create-vscode-template --name NAME --title-inline TITLE --message-inline MESSAGE [--severity info|warning|error]
update-template --name NAME --slack-blocks-inline BLOCKS
create-email-destination --name NAME --provider PROVIDER --template TEMPLATE
create-slack-channel-destination --name NAME --provider PROVIDER --template TEMPLATE
create-vscode-destination --name NAME --provider PROVIDER --template TEMPLATE --recipient-user-id USER_ID
create-output-hole-destination --name NAME --provider PROVIDER --template TEMPLATE
update-email-destination --id DESTINATION_ID --provider PROVIDER --template TEMPLATE
update-slack-channel-destination --id DESTINATION_ID --provider PROVIDER --template TEMPLATE
update-vscode-destination --id DESTINATION_ID --provider PROVIDER --template TEMPLATE --recipient-user-id USER_ID
update-output-hole-destination --id DESTINATION_ID --provider PROVIDER --template TEMPLATE
create-policy --name NAME --subject SUBJECT --destination DESTINATION
update-policy --id POLICY_ID --subject SUBJECT --destination DESTINATION
activate-policy --id POLICY_ID
deactivate-policy --id POLICY_ID
```

## Notificaciones para VS Code

El Provider `VSCODE` publica el payload renderizado en el relay HTTP SSE. El
Destination define la audiencia; el CLI inicial crea audiencias de tipo `user`.
El contrato tambien admite `group` y `all` mediante REST para su futura
resolucion por el relay. Para `user` conserva tambien `recipient_user_id` en
el nivel superior, por compatibilidad con el relay SSE actual.

```bash
notify create-vscode-provider \
  --name vscode-provider \
  --relay-url "http://127.0.0.1:8000/notifications" \
  --output-format json

notify create-vscode-template \
  --name entity-created-vscode-template \
  --title-inline "Entidad creada" \
  --message-inline "Se creo {{ context.entity_id }}" \
  --severity info \
  --output-format json

notify create-vscode-destination \
  --name entity-created-vscode-destination \
  --provider vscode-provider \
  --template entity-created-vscode-template \
  --recipient-user-id usuario@empresa.com \
  --output-format json
```

## Actualizar un Template Slack

`update-template` reemplaza los bloques Slack de un Template existente y conserva su nombre. Es un reemplazo completo de la representacion Slack; no mezcla el contenido enviado con el Template persistido.

```bash
notify update-template \
  --name entity-created-slack-template \
  --slack-blocks-inline "$(cat /ruta/entity.created-slack.yaml)" \
  --output-format json
```

El Template debe existir. El comando carga la configuracion del CLI y delega la solicitud en `aspynotifications_sdk`; no llama REST directamente.

## Actualizar Providers de notificaciones

Cada tipo de Provider tiene su propio comando de actualizacion. El Provider se identifica por `id`; su nombre se conserva para que los Destinations existentes que lo referencian por nombre continuen funcionando.

```bash
notify update-slack-provider \
  --id PROVIDER_ID \
  --webhook-url "https://hooks.slack.com/services/..." \
  --output-format json
```

```bash
notify update-zeptomail-provider \
  --id PROVIDER_ID \
  --from-address notifications@example.com \
  --from-name "Notifications" \
  --send-mail-token TOKEN \
  --output-format json
```

```bash
notify update-shole-provider \
  --id PROVIDER_ID \
  --level WARN \
  --cows \
  --output-format json
```

## Actualizar Destinations de notificaciones

Cada tipo de Destination tiene su propio comando de actualizacion. El
Destination se identifica por `id` y conserva su nombre; se reemplazan por
completo el Provider, Template y configuracion tipada.

```bash
notify update-email-destination \
  --id DESTINATION_ID \
  --provider corporate-mail \
  --template email-notification-template \
  --to alerts@example.com \
  --cc audit@example.com \
  --output-format json
```

```bash
notify update-slack-channel-destination \
  --id DESTINATION_ID \
  --provider operations-slack \
  --template slack-notification-template \
  --output-format json
```

```bash
notify update-output-hole-destination \
  --id DESTINATION_ID \
  --provider output-hole-provider \
  --template output-hole-template \
  --output-format json
```

## Actualizar Policies de notificaciones

`update-policy` identifica la Policy existente por `id` y conserva su nombre.
Reemplaza por completo el subject, las policies de envelope, las policies de
Destination y los Destinations.

```bash
notify update-policy \
  --id POLICY_ID \
  --subject "*.created" \
  --destination entity-slack-destination \
  --envelope-policy environment "context.environment == 'production'" "Solo produccion" \
  --output-format json
```

## Activar y desactivar Policies de notificaciones

Las Policies nuevas nacen activas. Una Policy desactivada permanece almacenada,
pero no participa en el matching de eventos ni en la entrega de notificaciones.

```bash
notify deactivate-policy --id POLICY_ID --output-format json
notify activate-policy --id POLICY_ID --output-format json
```

## Configuracion

Antes de ejecutar un comando, el CLI carga configuracion desde:

1. `monoconfig/default/aspynotifications_cli`
2. `monoconfig/<os-user>/aspynotifications_cli`

La configuracion del usuario debe contener la URL del REST de notificaciones y cualquier ajuste HTTP requerido.
