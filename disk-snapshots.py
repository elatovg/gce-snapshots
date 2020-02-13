#!/usr/bin/env python3
import argparse
import warnings
import datetime
import googleapiclient.discovery

''' resources
https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/compute/api/create_instance.py
https://github.com/jacksegal/google-compute-snapshot
https://blog.powerupcloud.com/creating-a-vm-snapshot-in-google-cloud-using-python-3cb42f279f5c
https://cloud.google.com/compute/docs/reference/rest/v1/disks/createSnapshot
https://cloud.google.com/compute/docs/reference/rest/v1/snapshots/list
https://b.corp.google.com/issues/80238913
'''

# disable warning about not using service account (mostly for testing)
warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")


def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None


def get_instance(compute, project, zone, vm_name):
    result = compute.instances().get(project=project, zone=zone, instance=vm_name).execute()
    return result['name'] if 'name' in result else None


def get_disk_names(compute, project, zone, vm_name):
    disk_list = list()
    result = compute.instances().get(project=project, zone=zone, instance=vm_name).execute()
    # print (result['disks'][0]['deviceName'])
    if 'disks' in result:
        for disk in result['disks']:
            disk_list.append(disk['deviceName'])

    return disk_list if disk_list else None


def get_snapshot_date():
    current_date = datetime.datetime.now()
    date_formatted = current_date.strftime('%Y-%m-%d')
    return date_formatted


def get_deletion_creation_date(num_days):
    deletion_date = datetime.datetime.today() - datetime.timedelta(days=num_days)
    # for testing
    # deletion_date = datetime.datetime.today() - datetime.timedelta(hours=15)
    # formatted_del_date = deletion_date.strftime('%Y%m%d')
    return deletion_date


def create_snapshot(compute, project, zone, disk_name):
    date = get_snapshot_date()
    snapshot_name = "{}-{}".format(disk_name, date)
    body = {'name': snapshot_name,
            'storageLocations': [zone]}
    print("Taking Snapshot of disk {} called {}".format(disk_name, snapshot_name))
    result = compute.disks().createSnapshot(project=project, zone=zone, disk=disk_name, body=body).execute()
    # print(result)
    if not result:
        print("Failed to take snapshot")
        exit(1)
    # print (result['disks'][0]['deviceName'])


def get_snapshots(compute, project, snapshot_filter, days):
    snap_list = list()
    result = compute.snapshots().list(project=project, filter=snapshot_filter).execute()
    del_date = get_deletion_creation_date(days)
    if 'items' in result:
        for snapshot in result['items']:
            creation_date = snapshot['creationTimestamp']
            # state = snapshot['name']['creationTimestamp']
            snap_creation_date = datetime.datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S.%f-08:00")
            if snap_creation_date < del_date:
                print("Will delete snapshot {} since it's creation time {} is older than deletion time {}".
                      format(snapshot['name'], creation_date, del_date))
                snap_list.append(snapshot['name'])

    return snap_list if snap_list else None


def delete_snapshot(compute, project, snap_name):
    print("Deleting Snapshot {}".format(snap_name))
    result = compute.snapshots().delete(project=project, snapshot=snap_name).execute()
    # return result['name'] if 'name' in result else None
    if not result:
        print("Failed to delete snapshot: {}".format(snap_name))
        exit(1)


def main(project, zone, name, days):
    compute = googleapiclient.discovery.build('compute', 'v1')

    print("snapshot the following instance {}".format(name))

    # instances = list_instances(compute, project, zone)
    #
    # print('Instances in project %s and zone %s:' % (project, zone))
    # for instance in instances:
    #     print(' - ' + instance['name'])

    instance_name = get_instance(compute, project, zone, name)

    print("Instance {} found in zone {} in project {}".format(instance_name, zone, project))

    instance_disks = get_disk_names(compute, project, zone, instance_name)

    if instance_disks is None:
        print("No disks found for vm {}".format(instance_name))
        exit(1)

    print("Found the following disks {} attached to vm {}".format(instance_disks, instance_name))
    print("Will keep {} days worth of snapshots".format(days))

    for disk in instance_disks:
        create_snapshot(compute, project, zone, disk)
        snap_filter = "name:" + disk + "-*"
        snap_list = get_snapshots(compute, project, snap_filter, int(days))
        if snap_list is None:
            print("Didn't find any snapshots to delete")
        else:
            print("Found snapshots {} for disk {} to delete".format(snap_list, disk))
            for snapshot in snap_list:
                delete_snapshot(compute, project, snapshot)

        # del_filter = "name: {}-* AND creationTimestamp<{}".format(disk, del_date)
        # print("Snapshots to delete {}".format(snap))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('project_id',
                        help='Your Google Cloud project ID.')
    parser.add_argument('--zone',
                        default='us-central1-f',
                        help='Compute Engine zone to check')
    parser.add_argument('--name',
                        default='demo-instance',
                        help='Instance name.')
    parser.add_argument('--days',
                        default=7,
                        help='Number of days to keep snapshots.')
    args = parser.parse_args()

    main(args.project_id, args.zone, args.name, args.days)
