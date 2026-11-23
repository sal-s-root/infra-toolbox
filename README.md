# Infrastructure toolbox

A consolidated collection of small offline checks for infrastructure metadata.
The tools share one catalog, entry point, fixture suite, and maintenance location.
They complement the deployment labs rather than represent separate platforms.

```sh
python3 toolbox.py list
python3 toolbox.py list --area networking
python3 toolbox.py run cidr-overlap-checker checks/cidr-overlap-checker/examples/input.json
python3 -m unittest -v
```

Each command accepts a JSON file or `-` for stdin. Exit 0 means evaluation
completed, not that every finding is acceptable. Invalid input returns exit 2.
No credentials are needed and no resource changes or cloud API calls are made.

## Areas

Linux snapshots, network inventory, configuration drift, delivery metadata,
cloud policy review, and reliability calculations. See [CATALOG.md](CATALOG.md)
for all checks and their limits. The suite evaluates all 93 documented fixtures
and verifies the shared CLI. It does not establish production compliance.

For provisioning and operation, start with the Terraform, Ansible, Compose,
Kubernetes, observability, and backup/restore repositories linked from the profile.
