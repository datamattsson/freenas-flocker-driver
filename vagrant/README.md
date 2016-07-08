# FreeNAS 9.10 Flocker Driver
This is the home of the *experimental* flocker driver for FreeNAS 9.10.

# Sandbox Environment
The provided vagrant sandbox environment is a great way to explore how docker and flocker works on your laptop.

## Prerequisites
The sandbox should run on any platform that supports vagrant with the virtualbox provider and ansible. It has been developed on a Ubuntu 14.04.4 desktop as "works for me" reference, there might be unlisted dependencies, please file an issue if something breaks in your environment.

- Vagrant 1.8.x w/ virtualbox provider
- Ansible 2.1.x
- Lots of RAM, the FreeNAS VM is allowed up to 8GB
- A couple of GBs of disk space
- Be able to let Vagrant provision the private network 192.168.65.0/24
- Not have anything mapped on localhost to port 8080

## Provisioning steps
To get started building your sandbox, follow these steps:

Clone this repo:

    git clone https://github.com/drajen/freenas-flocker-driver

`cd` into `freenas-flocker-driver/vagrant`

Bring up the sandbox:

    vagrant up

This will take quite a while the first time as vagrant will pull down images from Atlas. After all the provisioners have completed you should see something very similar to this:

    PLAY RECAP *********************************************************************
    node2                      : ok=35   changed=30   unreachable=0    failed=0   

Please file an issue if it breaks.

## Kick the tires
Explaining and elaborating how flocker works and manages datasets is beyond the scope of this document, however, here's the offical 'Hello World' test for the sandbox:

    vagrant ssh node1
    docker run -v freenas:/data --volume-driver flocker busybox sh -c "echo 'Hello World' > /data/file.txt"
    docker run -v freenas:/data --volume-driver flocker busybox sh -c "cat /data/file.txt"

**Pro tip**: `flockerctl` is an experimental tool installed on node1 and have the client certs installed in `/etc/flocker`:

    cd /etc/flocker
    export FLOCKER_CONTROL_SERVICE=192.168.65.10
    flockerctl list-nodes
    SERVER     ADDRESS       
    a445f6b0   127.0.0.1     
    c1afc1ec   192.168.65.11 

# Standalone Environment 
The vagrant sandbox provisions a number of resources on the FreeNAS box that might not be apparent for the naked eye. If you intend to run the flocker driver against an existing FreeNAS box, here's a few gotchas:
- The driver expects that there is a Portal and Target with id 1 and that the Target is associated with the default Portal. This is not a concern when you only have one Target and one Portal.
- In `/etc/flocker` on the compute nodes there is a file, `agent.yml`, that configures the FreeNAS API and which Volume (zpool) you want to use for your flocker volumes.
- The flocker compute nodes relies on `multipath-tools`, even if you only have one path to your storage, for naming consistency of devices across configurations. The multipath.conf shipped in this directory is an essential starting point.

# Known issues and limitations
- If you run into any issues at all, your starting point is to look in `/var/log/flocker/flocker-dataset-agent.log` on the control node (node1 in the sandbox).

# TODO
- None of this code have undergone any formal testing or certificaton as per the requirement of ClusterHQ.
- The idea is to have Portals and Targets configurable per flocker cluster and a lot of metadata changes will be needed to accommodate that.
- Flocker have the capability of providing different classes of service for each provisioned volume. None of this is implemented yet.

# License 
Please see https://github.com/drajen/freenas-flocker-driver/LICENSE
