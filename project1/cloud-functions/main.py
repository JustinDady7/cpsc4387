import uuid
import googleapiclient.discovery
from google.cloud import runtimeconfig


def cloud_fn_stop_all_servers(event, context):
    """
    Simply stops all servers in the project. This is meant to run periodically to prevent servers from running
    constantly
    :param event: No data is passed to this function
    :param context: No data is passed to this function
    :return:
    """
    runtimeconfig_client = runtimeconfig.Client()
    myconfig = runtimeconfig_client.config('myconfig')
    project = myconfig.get_variable('project').value.decode("utf-8")
    zone = myconfig.get_variable('zone').value.decode("utf-8")

    compute = googleapiclient.discovery.build('compute', 'v1')
    result = compute.instances().list(project=project, zone=zone).execute()
    if 'items' in result:
        for vm_instance in result['items']:
            compute.instances().stop(project=project, zone=zone, instance=vm_instance["name"]).execute()


def cloud_fn_my_cloud_function(event, context):
    """
    This is your function
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    Returns:
        A success status
    """

    action = event['attributes']['action'] if 'action' in event['attributes'] else None

    if not action:
        print(f'No action provided in cloud_fn_manage_server for published message.')
        return

    if action == "build":
        runtimeconfig_client = runtimeconfig.Client()
        myconfig = runtimeconfig_client.config('myconfig')
        project = myconfig.get_variable('project').value.decode("utf-8")
        zone = myconfig.get_variable('zone').value.decode("utf-8")

        server_name = f"auto_server-{uuid.uuid4()}"
        compute = googleapiclient.discovery.build('compute', 'v1')
        image_response = compute.images().getFromFamily(project="debian-cloud", family="debian-9").execute()
        source_disk_image = image_response["selfLink"]
        config = {
            "name": server_name,
            "machineType": f"projects/{project}/zones/{zone}/machineTypes/e2-micro",
            "disks": [
                {
                    "boot": True,
                    "autoDelete": True,
                    "initializeParams": {
                        "sourceImage": source_disk_image,
                    }
                }
            ],
            "networkInterfaces": [{
                "network": "global/networks/default",
                "accessConfigs": [
                    {"type": "ONE_TO_ONE_NAT", "name": "External NAT"}
                ]
            }],
        }
        from pprint import pprint

        from googleapiclient import discovery
        from oauth2client.client import GoogleCredentials

        credentials = GoogleCredentials.get_application_default()

        service = discovery.build('compute', 'v1', credentials=credentials)

        # Project ID for this request.
        project = 'planar-courage-326117'  # TODO: Update placeholder value.

        # The name of the zone for this request.

        instance_body = {
            # TODO: Add desired entries to the request body.
        }

        request = service.instances().insert(project=project, zone=zone, body=instance_body)
        response = request.execute()

        # TODO: Change code below to process the `response` dict:
        pprint(response)
        return

    elif action == "bucket":
        from google.cloud import storage

        storage_client = storage.Client()
        bucket = storage_client.bucket("my_bucket")
        bucket.storage_class = "COLDLINE"
        new_bucket = storage_client.create_bucket(bucket, location="us")

        print(
            "Created bucket {} in {} with storage class {}".format(
                new_bucket.name, new_bucket.location, new_bucket.storage_class
            )
        )
        return new_bucket

