# Google Cloud Platform Strava webhook

This repository is designed to be deployed to a Cloud Function in Google Cloud Platform. It should a publicly visible endpoint which is called by Strava
whenever an activity is added or changed to which you are subscribed.

The function handles two situations:
1. Initialisation
2. Message receipt, which is relayed to Pub/Sub on GCP.

This repo is one of four in an example module of how to load Strava data to Google BigQuery.

##Initialisation

You should deploy this to a Cloud Function first, as you need to validate the endpoint URL to Strava. 
When deploying, you need to specify a random string as an environment variable VERIFY_TOKEN.

For an example of deploying using Terraform, please see my [Terraform repo](https://github.com/reevery/strava-gcp-terraform).

When deployed, you need to create a subscription. These instructions are simplified from the [Strava API Documentation](https://developers.strava.com/docs/webhooks/).
You need a callback_url (the URL from the Cloud Function Trigger page) (e.g. `https://region-project-id.cloudfunctions.net/strava-webhook`),
and your Strava API client_id and client_secret, both of which are on the [Strava API](https://www.strava.com/settings/api) page.
To create the subscription, create a POST call to the end point as below, substituting your client_id, client_secret, 
callback_url, and verify_token which you should have put in Secret Manager.
```
curl -X POST https://www.strava.com/api/v3/push_subscriptions \
      -F client_id=5 \
      -F client_secret=7b2946535949ae70f015d696d8ac602830ece412 \
      -F 'callback_url=http://a-valid.com/url' \
      -F 'verify_token=STRAVA'
```
This call should trigger Strava to call your endpoint, and will handle receipt of the returned message, all whilst you
wait for a response to this POST request. When successful, Strava will reply with your  subscription_id, which you
should then manually add as a version to Secret Manager  for a secret called STRAVA_SUBSCRIPTION_ID.

Your webhook and subscription should then be available, but next you need to authorise your user against the client.
This is covered in my [Pull Cloud Function](https://github.com/reevery/strava-pull).

### Environment Variables

This Cloud Function requires the following environment variables:

| Environment Variable Name|Explanation|
|---|---|
| GOOGLE_APPLICATION_CREDENTIALS|A path to a JSON credentials file. Within GCP this is set automatically.|
| GCP_PROJECT | The Project Id in which specifically the Secret Manager secrets are stored. Within GCP this is set automatically.|
| VERIFY_TOKEN | A random string used to confirm the subscription. You need to provide this because you are going to trigger the subscription process manually.|
