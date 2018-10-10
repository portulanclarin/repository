from metashare.settings import PIDDATA_FILENAME

def _normal_res_pid(iStr):
    return map(lambda x: x.strip(), iStr.split(','))[0]


def get_md_pid(resourcePID,iFile=PIDDATA_FILENAME):
    import csv
    with open(iFile, 'rb') as f:
        reader = csv.DictReader(f,delimiter='\t')
        for row in reader:
            if resourcePID in map(
                    lambda x: _normal_res_pid(x), 
                    row.values()
            ):
                return row['MD PID']
    
