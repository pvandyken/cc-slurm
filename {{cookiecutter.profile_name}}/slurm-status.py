#!/usr/bin/env python3
import re
import subprocess as sp
import shlex
import sys
import time
import logging
from cookie_cutter import CookieCutter

logger = logging.getLogger("__name__")

STATUS_ATTEMPTS = 20

def main():
    jobid = sys.argv[1]

    if jobid == "__TEST__":
        return "success"

    cluster = CookieCutter.get_cluster_option()

    for i in range(STATUS_ATTEMPTS):
        try:
            sacct_res = sp.check_output(shlex.split(f"sacct {cluster} -P -b -j {jobid} -n"))
            res = {
                x.split("|")[0]: x.split("|")[1]
                for x in sacct_res.decode().strip().split("\n")
            }
            break
        except sp.CalledProcessError as e:
            logger.error("sacct process error")
            logger.error(e)
        except IndexError as e:
            logger.error(e)
            pass
        # Try getting job with scontrol instead in case sacct is misconfigured
        try:
            sctrl_res = sp.check_output(
                shlex.split(f"scontrol {cluster} -o show job {jobid}")
            )
            m = re.search(r"JobState=(\w+)", sctrl_res.decode())
            res = {jobid: m.group(1)}
            break
        except sp.CalledProcessError as e:
            logger.error("scontrol process error")
            logger.error(e)
            if i >= STATUS_ATTEMPTS - 1:
                print("failed")
                exit(0)
            else:
                time.sleep(1)

    status = res[jobid]

    map_state = {
        "BOOT_FAIL": 'failed',
        "PENDING":'running',
        "RUNNING":'running',
        "SUSPENDED":'running',
        "CANCELLED":'failed',
        "COMPLETING":'running',
        "COMPLETED":'success',
        "CONFIGURING":'running',
        "DEADLINE": 'failed',
        "FAILED": 'failed',
        "NODE_FAIL": 'failed',
        "TIMEOUT":'failed',
        "PREEMPTED":'failed',
        "NODE_FAIL":'failed',
        "REVOKED":'failed',
        "SPECIAL_EXIT":'failed',
        "":'success',
        "OUT_OF_MEMORY":'failed'
    }

    #return the state, using the dictionary; if key not there, then return failed
    return map_state.get(status,'failed')

if __name__  == "__main__":
    print(main())