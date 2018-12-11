echo Please enter your dsg1 username: 
read user
scp -r $user@dsg1.crc.nd.edu:~/ControlAltDefeat/Generated_Reports ~/Desktop
