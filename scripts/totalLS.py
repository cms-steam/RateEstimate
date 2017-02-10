import json
import sys

#print sys.argv[1]
json_file_name = sys.argv[1]
file1=open(json_file_name,'r')
inp1={}
text = ""
for line1 in file1:
    text+=line1#.replace("\n","")
print text
inp1 = json.loads(text)
#print inp1
sumlumi = 0
for run in inp1:
    for ls in inp1[run]:
        sumlumi+=(ls[1]-ls[0]+1)

print "total lumi section in file '%s': %d"%(sys.argv[1],sumlumi)

