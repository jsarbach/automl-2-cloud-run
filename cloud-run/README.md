## Deployment to Cloud Run with Cloud Build
This [Cloud Build] configuration automates all the required steps after the model export, i.e. downloading the saved_model.pb, building the Docker 
image, and deploying it to a Cloud Run service. The build steps are defined in the [cloudbuild.yaml]. Put the Dockerfile for the image to deploy in a 
subfolder and trigger builds with `gcloud builds submit --substitutions [SUBSTITUTIONS]`.

### Substitutions
#### Required
* `_MODEL_NAME`: Arbitrary name for the ML model that will be used as Cloud Run service name.
* `_DOCKERFOLDER`: Subfolder with the Dockerfile to use, e.g. `automl-vision-cpu-1.14.0`.
* `_GCS_MODEL_PATH`: GCS path to the ML model export (saved_model.pb), including the gs:// prefix, without trailing slash.
#### Optional
* `_GCP_REGION`: GCP region where the Cloud Run service is deployed, default is `europe-west1`
* `_MAX_INSTANCES`: maximum number of instances for autoscaling, default is `10`
* `_MEMORY`_: memory allocation, default is `1GB`
* `_TIMEOUT`: timeout in sec., default is `60`
* `_VERSION`: Docker image version tag, e.g. the model version, default is `latest`
### Example
`gcloud builds submit --substitutions _MODEL_NAME=coffee-classifier,_DOCKERFOLDER=automl-vision-cpu-1.14.0,_GCS_MODEL_PATH=gs://my-automl-demos-vcm/model-export/icn/tf_saved_model-coffee_classifier_20200225020250-2020-02-25T20:44:26.192Z,_VERSION=20200225020250-1.14.0`


[Cloud Build]: https://cloud.google.com/cloud-build
[cloudbuild.yaml]: cloudbuild.yaml
