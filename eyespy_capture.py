import requests, json, sys, re, base64, os, errno
from requests.exceptions import ConnectionError

# Google API
request_string = "https://www.googleapis.com/pagespeedonline/v1/runPagespeed?screenshot=true&url="
# URL Regex - Check
regex_exp = r"(http|https)://[\w\-]+(\.[\w\-]+)+"
# List for protocol
prepend_list = ["http://", "https://"]
# Counters
total_line = 0
current_line = 0

print "EyeSpy - Subdomain Screenshot Tool"
print "Author: Dennis Tan"
print "https://github.com/dtyj/subdomain_availability"
print ""
print "Usage: python eyespy_capture.py subdomains.txt"
print ""

subdomain_file = str(sys.argv[1])

def progress():
    # Check for old progress
    exists = os.path.isfile(subdomain_file + '.dat')
    if exists:
        p = open(subdomain_file + '.dat','r')
        # Overwrite current_line
        current_line = int(p.read())
        return current_line
    else:
        current_line = 0
        return current_line

if len(sys.argv) == 2:
    dir_name = 'eyespy_result'

    # Get value for current and total line
    current_line = progress()

    for line in open(subdomain_file, "r"):
        total_line += 1
    # Create directory for EyeSpy's capture
    try:
        os.mkdir(dir_name)
        print("Directory %s Created " % dir_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            print("Directory %s already exists " % dir_name)
            print("Creating images into directory..\n")
        else:
            raise
    with open(subdomain_file,'r') as f:
        fdata = [line.rstrip() for line in f]
        for index in range(current_line, total_line):
            # Save progress
            k = open(subdomain_file + '.dat','w')
            k.write(str(index))
            file_data = fdata[index]
            for i in range (0,2):
                # Match line in file with REGEX
                if re.match(regex_exp, file_data) is None:
                    file_data = request_string + prepend_list[i] + file_data
                if re.match(regex_exp, file_data) is not None:
                    # Strip away newline
                    insert = file_data.strip('\n')
                    # Makes GET request and retrieve response in JSON
                    try:
                        r = requests.get(insert)
                        if r.status_code == 200:
                            json_data = json.loads(r.text)
                            image_string = str(json_data['screenshot']['data'])
                            image_string = image_string.replace('_','/')
                            image_string = image_string.replace('-','+')
                            subdomain_splitting = insert.split('://')[-2:]
                            filename = dir_name + "/" + str(subdomain_splitting[1]) + "_" + str(i) + ".jpg"
                            with open(filename,'w') as f:
                                # Construct image
                                f.write(base64.b64decode(image_string))
                                if i == 0:
                                    protocol = "HTTP"
                                elif i == 1:
                                    protocol = "HTTPS"
                                print ("Successfully created %s JPEG - %s" % (str(subdomain_splitting[1]), protocol))
                        else:
                            print ("%s failed" % insert)
                            er = open('error.log','a')
                            er.write(insert + '\n')
                            pass
                    except:
                        print ("%s failed" % insert)
                        er = open('error.log','a')
                        er.write(insert + '\n')
                        pass
                # Reset variable so it'll loop use HTTPS next
                file_data = fdata[index]
            # Reset i so it'll use HTTP again
            i = 0
        os.remove(subdomain_file + '.dat') 
else:
    print "Error: Please provide the correct set of parameter.\n"
