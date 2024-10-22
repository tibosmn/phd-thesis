#!/bin/bash
virsh --connect=qemu:///system start $1 || true
# Post action : wait to retrieve vm ip
while sleep 1;
do
  vm_ip=$( virsh --connect=qemu:///system domifaddr "$1" | tail -n 2 | head -n 1 | awk '{ print $4 }' | sed 's/[/].*//' );
  if [ -n "$vm_ip" ]; then #VAR is set to a non-empty string
    break
  fi
done
# May not be fully initialized : test if ssh works (is ping enough?)
count=0
while true;
do
  ssh_test=$( ssh ubuntu@"${vm_ip}" -o StrictHostKeyChecking=no 'echo success' )
  if [[ $ssh_test == *"success"* ]]; then
    #echo "Setup : vm $1 ready with ip $vm_ip"
    break
  fi
  count=$(( count + 1 ))
  #echo "Setup : unable to ssh test vm $1 with ip $vm_ip (trial $count)"
  sleep 15
done
echo "$vm_ip"