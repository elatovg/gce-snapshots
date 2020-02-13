## Sample Usage

	> ./disk-snapshots.py $(gcloud config get-value project) --zone us-east4-c --name utilities-vm --days 1
	Your active configuration is: [your-project]
	snapshot the following instance utilities-vm
	Instance utilities-vm found in zone us-east4-c in project your-project
	Found the following disks ['utilities-vm'] attached to vm utilities-vm
	Will keep 1 days worth of snapshots
	Taking Snapshot of disk utilities-vm called utilities-vm-2019-02-12
	Will delete snapshot utilities-vm-2019-02-11 since it's creation time 2019-02-11T20:41:15.991-08:00 is older than deletion time 2019-02-11 21:59:18.439322
	Will delete snapshot utilities-vm-snap-1 since it's creation time 2019-02-11T18:58:42.890-08:00 is older than deletion time 2019-02-11 21:59:18.439322
	Found snapshots ['utilities-vm-2019-02-11', 'utilities-vm-snap-1'] for disk utilities-vm to delete
	Deleting Snapshot utilities-vm-2019-02-11
	Deleting Snapshot utilities-vm-snap-1

## To DO

* Add Support to Read in Service account
* Add Instructions on how to use it with crontab or with cloud tasks
* Add check to see if snapshot for current day already exists