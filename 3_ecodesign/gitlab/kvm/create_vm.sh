#!/bin/bash
if (( "$#" != "3" )) 
then
  echo -n "Missing argument : ./createvm.sh name core(s) memory"
  exit -1
fi

# Delete vm if it exists
virsh --connect=qemu:///system destroy "$1"
virsh --connect=qemu:///system undefine "$1"

# Install
virt-install \
--connect qemu:///system \
--name "$1" \
--vcpus "$2" \
--memory "$3" \
--os-variant ubuntu20.04 \
--disk ./disks/"$1".qcow2,format=qcow2,bus=virtio,size=15 \
--network default \
--cdrom ./isos/ubuntu-autoinstall.iso \
--noautoconsole