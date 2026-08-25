# aspynotifications_cli

`aspynotifications_cli` es el cliente de linea de comandos que envia solicitudes al servicio REST de notificaciones mediante `aspynotifications_sdk`.

## Comandos disponibles

```text
send-event --from-file PATH [--output-format print|json] [-v|-q] [--log-format plain|json]
create-slack-provider --name NAME --webhook-url URL
create-zeptomail-provider --name NAME --from-address ADDRESS --send-mail-token TOKEN
create-shole-provider --name NAME
update-slack-provider --id PROVIDER_ID --webhook-url URL
update-zeptomail-provider --id PROVIDER_ID --from-address ADDRESS --send-mail-token TOKEN
update-shole-provider --id PROVIDER_ID
create-template --name NAME [--slack-blocks-inline BLOCKS]
update-template --name NAME --slack-blocks-inline BLOCKS
create-email-destination --name NAME --provider PROVIDER --template TEMPLATE
create-slack-channel-destination --name NAME --provider PROVIDER --template TEMPLATE --channel-id CHANNEL_ID
create-output-hole-destination --name NAME --provider PROVIDER --template TEMPLATE
update-email-destination --id DESTINATION_ID --provider PROVIDER --template TEMPLATE
update-slack-channel-destination --id DESTINATION_ID --provider PROVIDER --template TEMPLATE --channel-id CHANNEL_ID
update-output-hole-destination --id DESTINATION_ID --provider PROVIDER --template TEMPLATE
create-policy --name NAME --subject SUBJECT --destination DESTINATION
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
completo el Provider, Template, bandera routable y configuracion tipada.

```bash
notify update-email-destination \
  --id DESTINATION_ID \
  --provider corporate-mail \
  --template email-notification-template \
  --routable \
  --to alerts@example.com \
  --cc audit@example.com \
  --output-format json
```

```bash
notify update-slack-channel-destination \
  --id DESTINATION_ID \
  --provider operations-slack \
  --template slack-notification-template \
  --routable \
  --channel-id CHANNEL_ID \
  --output-format json
```

```bash
notify update-output-hole-destination \
  --id DESTINATION_ID \
  --provider output-hole-provider \
  --template output-hole-template \
  --routable \
  --output-format json
```

## Configuracion

Antes de ejecutar un comando, el CLI carga configuracion desde:

1. `monoconfig/default/aspynotifications_cli`
2. `monoconfig/<os-user>/aspynotifications_cli`

La configuracion del usuario debe contener la URL del REST de notificaciones y cualquier ajuste HTTP requerido.
