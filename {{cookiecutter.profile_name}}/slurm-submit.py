#!/usr/bin/env python3
import os
import sys

from snakemake.utils import read_job_properties

from cookie_cutter import CookieCutter

import utils

RESOURCE_MAPPING = {
    "time": ("time", "runtime", "walltime"),
    "mem": ("mem", "mem_mb", "ram", "memory"),
    "mem-per-cpu": ("mem-per-cpu", "mem_per_cpu", "mem_per_thread"),
    "nodes": ("nodes", "nnodes"),
}

# last command-line argument is the job script
jobscript = sys.argv[-1]

# all other command-line arguments are the dependencies
dependencies = set(sys.argv[1:-1])

# parse the job script for the job properties that are encoded by snakemake within
job_properties = read_job_properties(jobscript)


# get account from CC_COMPUTE_ALLOC, else supply default account
account = CookieCutter.ACCOUNT

if job_properties["type"]=='single':
    job_name = job_properties['rule']

elif job_properties["type"]=='group':
    job_name = job_properties['groupid']

else:
    raise NotImplementedError(f"Don't know what to do with job_properties['type']=={job_properties['type']}")


slurm_options = utils.convert_job_properties(job_properties, RESOURCE_MAPPING)

#get values and set defaults
if 'time' in slurm_options:
    time = min(slurm_options["time"],CookieCutter.MAX_TIME)
else:
    time = CookieCutter.DEFAULT_TIME

if 'mem' in slurm_options.keys():
    mem_mb = min(slurm_options["mem"],CookieCutter.MAX_MEM_MB)
else:
    mem_mb = CookieCutter.DEFAULT_MEM_MB

if 'gpus' in slurm_options.keys():
    gpus = min(slurm_options["gpus"],CookieCutter.MAX_GPUS)
else:
    gpus = 0

threads = min(slurm_options.get('threads', 1), CookieCutter.MAX_THREADS)


log = os.path.realpath(os.path.join('logs','slurm',f'{job_name}.%j.out'))

#create the log directory (slurm fails if doesn't exist)
log_dir = os.path.dirname(log)
if not os.path.exists(os.path.dirname(log)):
    os.makedirs(log_dir)


if gpus > 0:
    gpu_arg = f'--gres=gpu:t4:{gpus}'
else:
    gpu_arg = ''

if dependencies:
    # only keep numbers in dependencies list
    dependencies = [ x for x in dependencies if x.isdigit() or CookieCutter.TEST_MODE ]
    dependency_args = [
        "--dependency",
        "afterok:" + ",".join(dependencies)
    ]
else:
    dependency_args = []

# set all the slurm submit options as before
cmdline = [*filter(None, [
    "sbatch",
    "--parsable",
    f"--account={account}",
    gpu_arg,
    f"--time={time}",
    f"--mem={mem_mb}",
    f"--cpus-per-task={threads}",
    f"--output={log}",
    *dependency_args,
    jobscript
])]

print(utils.submit_job(cmdline, test=CookieCutter.TEST_MODE))