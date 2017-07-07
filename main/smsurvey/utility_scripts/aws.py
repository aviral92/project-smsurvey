import subprocess
from tornado import process

d = '0629'
r = 's3://nyu-mhealth-cyclomedia/1/15/' + d + '/'
p = subprocess.Popen(['aws', 's3', 'ls', r], stdout=subprocess.PIPE)

print("Getting job(s)")
jobs = []
for l in p.stdout:
    f = l.decode().strip()[4:-1]
    jobs.append(f)


print ("Processing jobs")
count = len(jobs)
print(str(count) + " jobs to complete")
process_id = process.fork_processes(5)

i = process_id
while i < count:
    f = jobs[i]
    directory = r + f

    subprocess.call(['aws', 's3', 'cp', directory, directory, '--recursive', '--acl', 'public-read', '--metadata',
                     'a=a'], stdout=subprocess.DEVNULL)

    print("Job " + str(i) + " of " + str(count) + " complete - " + f)
    i += 5