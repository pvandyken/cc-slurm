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
