import json
import sys

for line in sys.stdin:
    try:
        line = json.loads(line)
    except:
        continue
    print "{frequency}\t{_id}\t{collection}\t{instance}\t{class}".format(**line)
