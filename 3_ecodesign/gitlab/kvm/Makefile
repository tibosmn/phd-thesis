start:
	virsh --connect=qemu:///system start load_balancer || true
	virsh --connect=qemu:///system start postgresql || true
	virsh --connect=qemu:///system start redis || true
	virsh --connect=qemu:///system start gitaly || true
	virsh --connect=qemu:///system start rails_1 || true
	virsh --connect=qemu:///system start rails_2 || true
	virsh --connect=qemu:///system start monitoring || true
	virsh --connect=qemu:///system start influx || true

stop:
	virsh --connect=qemu:///system shutdown load_balancer || true
	virsh --connect=qemu:///system shutdown postgresql || true
	virsh --connect=qemu:///system shutdown redis || true
	virsh --connect=qemu:///system shutdown gitaly || true
	virsh --connect=qemu:///system shutdown rails_1 || true
	virsh --connect=qemu:///system shutdown rails_2 || true
	virsh --connect=qemu:///system shutdown monitoring || true
	virsh --connect=qemu:///system shutdown influx || true

create-data:
	# Clone performance git
	git clone https://gitlab.com/gitlab-org/quality/performance || true
	
	# Replace domain name on 2k generation file
	sed -i 's%https://2k.testbed.gitlab.net%http://gitlab.example.com%' \
		performance/k6/config/environments/2k.json

	# Launch data generation with docker
	# Network="host" to reach self-hosted gitlab
	# --force to skip user prompts
	docker run -e\
		ACCESS_TOKEN='i-am-a-token123'\
		-v $$PWD/performance/k6/config:/config\
		-v $$PWD/results:/results\
		--network="host"\
		gitlab/gpt-data-generator\
		--environment 2K.json --force

set-min-resources:
	# Memory is in MiB

	virsh setvcpus redis 1 --config
	virsh setmaxmem redis 1336MiB --config
	virsh setmem redis 1336MiB --config

	# virsh setvcpus postgresql 2 --config
	virsh setmaxmem postgresql 2385MiB --config
	virsh setmem postgresql 2385MiB --config

	virsh setvcpus rails_1 5 --config
	# virsh setmaxmem postgresql 2385MiB --config
	# virsh setmem rails_1 6676MiB --config

	virsh setvcpus rails_2 5 --config
	# virsh setmaxmem rails_2 6676MiB --config
	# virsh setmem rails_2 6676MiB --config
	
	# virsh setvcpus gitaly 4 --config
	virsh setmaxmem gitaly 5723MiB --config
	virsh setmem gitaly 5723MiB --config

set-max-resources:
	# Memory is in MiB

	virsh setvcpus redis 2 --config
	virsh setmaxmem redis 3577MiB --config
	virsh setmem redis 3577MiB --config

	virsh setvcpus postgresql 2 --config
	virsh setmaxmem postgresql 7153MiB --config
	virsh setmem postgresql 7153MiB --config

	virsh setvcpus rails_1 8 --config
	virsh setmaxmem rails_1 6676MiB --config
	virsh setmem rails_1 6676MiB --config

	virsh setvcpus rails_2 8 --config
	virsh setmaxmem rails_2 6676MiB --config
	virsh setmem rails_2 6676MiB --config
	
	virsh setvcpus gitaly 4 --config
	virsh setmaxmem gitaly 14306MiB --config
	virsh setmem gitaly 14306MiB --config