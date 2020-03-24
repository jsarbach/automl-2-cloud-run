# AutoML to Cloud Run

This is the code referenced in my Medium article [How to Deploy your AutoML Model in a Cost-effective Way]. It has two parts:

* A [Cloud Build] configuration to automatically download and deploy your AutoML model to Cloud Run, see [cloud-run/] for instructions.
* A simple Python/Flask web app for [App Engine] that makes authorised requests against the Cloud Run service.

[How to Deploy your AutoML Model in a Cost-effective Way]: https://medium.com/@juri.sarbach/how-to-deploy-your-automl-model-in-a-cost-effective-way-5efdd377d4d2
[Cloud Build]: https://cloud.google.com/cloud-build
[cloud-run/]: cloud-run/
[App Engine]: https://cloud.google.com/appengine
