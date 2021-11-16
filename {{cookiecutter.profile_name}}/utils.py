import subprocess as sp
import shlex
import re
from pathlib import Path
from random import randrange
from typing import List

def convert_job_properties(job_properties, resource_mapping=None):
    """Convert job properties from a list a name_mappings to a standaridized name

    Borrows from [Snakemake-Profiles/slurm](https://github.com/Snakemake-Profiles/slurm)
    """
    options = {}
    if resource_mapping is None:
        resource_mapping = {}
    resources = job_properties.get("resources", {})
    for k, v in resource_mapping.items():
        options.update({k: resources[i] for i in v if i in resources})

    if "threads" in job_properties:
        options["cpus-per-task"] = job_properties["threads"]
    return options

def submit_job(slurm_cmd: List[str], test: bool=False):
    """Submit jobscript and return jobid."""
    if test:
        file = Path("cluster_test_output.out")
        file.touch()
        with file.open('r') as f:
            data = f.read()
        with file.open('w') as f:
            f.write(data + shlex.join(slurm_cmd) + "\n")
        return f"__TEST__{randrange(1000000000, 9999999999)}"
    else:
        try:
            res = sp.check_output(slurm_cmd)
        except sp.CalledProcessError as e:
            raise e
        # Get jobid
        res = res.decode()
        try:
            jobid = re.search(r"(\d+)", res).group(1)
        except Exception as e:
            raise e
        return jobid