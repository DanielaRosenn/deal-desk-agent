# Integration Configuration Checklist

## Outlook Actionable Messages
- Register or confirm the sender originator in Microsoft Actionable Messages.
- Save the originator GUID in `Asset.OutlookOriginatorGuid`.
- Confirm callback URL base in `Asset.WebViewBaseUrl`.

## Salesforce Webhook
- Configure webhook to call the `IntakeFlow` endpoint.
- Map payload fields to `ApprovalRequest` schema.
- Sign requests using the secret from `Cred.IntakeHmacSecret`.

## Callback Security
- Configure callback sender to sign payloads with `Cred.CallbackHmacSecret`.
- Validate callback payload includes `approval_id` and decision fields.

## UiPath Connections
- Verify Outlook Integration Service connection exists and is healthy.
- Verify any Data Service entities used by the flow are provisioned and accessible.
