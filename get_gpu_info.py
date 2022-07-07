import paramiko
import threading
from queue import Queue
import json

def _ssh_to_server(server, username, password, queue):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, username=username, password=password)

    res = client.exec_command('gpustat --json')
    stdout = res[1]
    stderr = res[2]

    out = []
    err = []
    for line in stdout:
        out.append(line)

    for line in stderr:
        err.append(line)
    
    out_json = ''.join(out)
    err_list = ''.join(err)

    queue.put({'server': server, 'stdout': out_json, 'stderr': err_list})

    client.close()


def get_server_info(username, password, server_prefix='10.204.100'):
    '''
    Input: username (str), password (str), server_prefix (optional str)
    Output: Array of Python Dictionaries [{}], not necessarily in order

    Example Output:
    [{
        'ip': IP address of server (ex. '10.204.100.120')
        'content' (Python dictionary): { ### if output['content'] == 'error': full log will be at output['error'] ###
            'hostname': 'Vision16',
            'query_time': '2022-07-07T19:17:50.322250',
            'gpus': [
                {
                    'index': 0,
                    'uuid': 'GPU-f8c224df-845f-91a7-ec81-b0bbb05bb28f',
                    'name': 'NVIDIA GeForce RTX 2080 Ti',
                    'temperature.gpu': 20,
                    'fan.speed': 0,
                    'utilization.gpu': 0,
                    'power.draw': 19,
                    'enforced.power.limit': 260,
                    'memory.used': 0,
                    'memory.total': 11019,
                    'processes': []
                },
                {
                    'index': 1,
                    'uuid': 'GPU-5389821d-af03-3611-1ce1-795cf59a8a77',
                    'name': 'NVIDIA GeForce RTX 2080 Ti',
                    'temperature.gpu': 21,
                    'fan.speed': 0,
                    'utilization.gpu': 0,
                    'power.draw': 21,
                    'enforced.power.limit': 250,
                    'memory.used': 0,
                    'memory.total': 11019,
                    'processes': []
                }
            ]
        },
        'error': 'gpustat: command not found'
    }]
    '''
    set_start_method('spawn')

    processes = []
    pm_obj = Queue()

    for i in range(111, 130):
        server_ip = f'{server_prefix}.{i}'
        p = threading.Thread(target=_ssh_to_server, args=(server_ip, username, password, pm_obj))
        p.start()
        processes.append(p)

    for proc in processes:
        proc.join()

    ret_dict = []

    while not pm_obj.empty():
        info = pm_obj.get_nowait()
        error = info['stderr']
        server = info['server']

        res = {
            'ip': server,
            'content': json.loads(info['stdout']) if info['stdout'] != '' else 'error',
            'error': error
        }

        ret_dict.append(res)

    return ret_dict
