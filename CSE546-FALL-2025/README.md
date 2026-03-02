# Autograder for Project-0

Make sure that you use the provided autograder and follow the instructions below to test your project submission. Failure to do so may cause you to lose all the project points and there will be absolutely no second chance.

- Download the zip file you submitted from Canvas. 
- Download the autograder from GitHub: `https://github.com/nehavadnere/CSE546-FALL-2025.git`
  - In order to clone the GitHub repository follow the below steps:
  - `git clone https://github.com/nehavadnere/CSE546-FALL-2025.git`
  - `cd CSE546-FALL-2025/`
  - `git checkout project-0`
- Create a directory `submissions` in the CSE546-FALL-2025 directory and move your zip file to the submissions directory.

## Prepare to run the autograder
- Install Python: `sudo apt install python3`
- Populate the `class_roster.csv`
  - If you are a student; replace the given template only with your details.
  - If you are a grader; use the class roster for the entire class

## Run the autograder
- Run the autograder: `python3 autograder.py`
- The autograder will look for submissions for each entry present in the `class_roster.csv`
- For each submission the autograder will
  - Validate if the zip file adheres to the submission guidelines as mentioned in the project document.
    - If Yes; proceed to next step
    - If No; allocate 0 grade points and proceed to the next submission
  - The autograder extracts the credentials.txt from the submission and parses the entries.
  - Use the Grader IAM credentials to test the project as per the grading rubrics and allocate grade points.
  - The autograder will dump stdout and stderr in a log file named `autograder.log`
      
## Sample Output

  ```
  (cse546) user@en4113732l:~/git/GTA-CSE546-FALL-2025/Project-0/grader$ python3 autograder.py
  +++++++++++++++++++++++++++++++ CSE546 Autograder  +++++++++++++++++++++++++++++++
  - 1) The script will first look up for the zip file following the naming conventions as per project document
  - 2) The script will then do a sanity check on the zip file to make sure all the expected files are present
  - 3) Extract the credentials from the credentials.txt
  - 4) Execute the test cases as per the Grading Rubrics
  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  ++++++++++++++++++++++++++++ Autograder Configurations ++++++++++++++++++++++++++++
  Project Path: /home/local/ASUAD/user/git/GTA-CSE546-FALL-2025/Project-0/grader
  Grade Project: Project-0
  Class Roster: class_roster.csv
  Zip folder path: /home/local/ASUAD/user/git/GTA-CSE546-FALL-2025/Project-0/grader/submissions
  Test zip contents script: /home/local/ASUAD/user/git/GTA-CSE546-FALL-2025/Project-0/grader/test_zip_contents.sh
  Grading script: /home/local/ASUAD/user/git/GTA-CSE546-FALL-2025/Project-0/grader/grade_project0.py
  Autograder Results: Project-0-grades.csv
  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  ++++++++++++++++++ Grading for Doe John ASUID: 1225754101 +++++++++++++++++++++
  Executing /home/local/ASUAD/user/git/GTA-CSE546-FALL-2025/Project-0/grader/test_zip_contents.sh on /home/local/ASUAD/user/git/GTA-CSE546-FALL-2025/Project-0/grader/submissions/Project0-1225754101.zip
  /home/local/ASUAD/user/git/GTA-CSE546-FALL-2025/Project-0/grader/test_zip_contents.sh output:
  [log]: Look for credentials directory (credentials)
  [log]: - directory /home/local/ASUAD/user/git/GTA-CSE546-FALL-2025/Project-0/grader/unzip_1735940884/credentials found
  [log]: Look for credentials.txt
  [log]: - file /home/local/ASUAD/user/git/GTA-CSE546-FALL-2025/Project-0/grader/unzip_1735940884/credentials/credentials.txt found
  [test_zip_contents]: Passed
  Unzip submission and check folders/files: PASS
  Extracted /home/local/ASUAD/user/git/GTA-CSE546-FALL-2025/Project-0/grader/submissions/Project0-1225754101.zip to extracted
  This is the submission file path: extracted/credentials
  Found credentials.txt  at extracted/credentials
  File: extracted/credentials/credentials.txt has values ('********************', '************************************')
  -------------- CSE546 Cloud Computing Grading Console -----------
  IAM ACESS KEY ID: ********************
  IAM SECRET ACCESS KEY: ************************************
  -----------------------------------------------------------------
  Following policies are attached with IAM user:cse546-AutoGrader: ['AmazonEC2ReadOnlyAccess', 'IAMReadOnlyAccess', 'AmazonS3ReadOnlyAccess', 'AmazonSQSReadOnlyAccess']
  ----- Executing Test-Case:1 -----
  [EC2-log] AmazonEC2ReadOnlyAccess policy attached with grading IAM
  [EC2-log] Trying to create a EC2 instance
  [EC2-log] EC2 instance creation failed with UnauthorizedOperation error. This is as expected. Points:[33.33/33.33]
  ----- Executing Test-Case:2 -----
  [S3-log] AmazonS3ReadOnlyAccess policy attached with grading IAM
  [S3-log] Trying to create a S3 bucket
  [S3-log] Bucket creation failed with Access Denied error. This is expected. Points:[33.33/33.33]
  ----- Executing Test-Case:3 -----
  [SQS-log] AmazonSQSReadOnlyAccess policy attached with grading IAM
  [SQS-log] Trying to create a SQS queue
  [SQS-log] SQS creation failed with Access Denied error. This is expected. Points:[33.33/33.33]
  Total Grade Points: 100
  Removed extracted folder: extracted
  Execution Time for Doe John ASUID: 1225754101: 1.9784526824951172 seconds
  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  Grading complete for Project-0. Check the Project-0-grades.csv file.
  (cse546) user@en4113732l:~/git/GTA-CSE546-FALL-2025/Project-0/grader$
```


(venv) ubuntu@ip-172-31-30-109:~$ python3 - <<'EOF'
import boto3, torch, torchvision, PIL, numpy
print("✅ boto3:", boto3.__version__)
print("✅ torch:", torch.__version__, "| CUDA available:", torch.cuda.is_available())
print("✅ torchvision:", torchvision.__version__)
print("✅ pillow:", PIL.__version__)
print("✅ numpy:", numpy.__version__)
EOF
✅ boto3: 1.40.57
✅ torch: 2.2.0+cpu | CUDA available: False
✅ torchvision: 0.17.0+cpu
✅ pillow: 12.0.0
✅ numpy: 1.26.4

    6  sudo apt update -y
    7  sudo apt install -y python3-pip git
    8  pip3 install boto3 torch torchvision pillow
    9  sudo apt install -y python3-venv
   10  python3 -m venv venv
   11  source venv/bin/activate
   12  pip install boto3 torch torchvision pillow
   13  pip install torch==2.2.0+cpu torchvision==0.17.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
   14  pip install torchvision pillow
   15  pip list
   16  pip install boto3
   17  python3 -c "import boto3; print('✅ boto3', boto3.__version__)"
   18  pip list


   curl -X POST -F "file=@test_face.jpg" http://98.86.156.151:8000


curl -X POST -F "file=@test_000.jpg" http://98.86.156.151:8000

scp -i ~/.ssh/cse546-rsa.pem ~/CSE546-FALL-2025/dataset/face_images_1000/test_000.jpg ubuntu@98.86.156.151:/home/ubuntu/

PART 2:
cd ~/cse546-fall-2025
source venv/bin/activate

cd web-tier


ps aux | grep controller.py

cd  app-tier/model

nohup python3 backend.py > backend.log 2>&1 &

tail -f backend.log


export ASU_ID=1233282975
export AWS_REGION=us-east-1
export AMI_ID=ami-0871d08e497514180
export SECURITY_GROUP_IDS=sg-0d53fae5b18bdcf85
export SUBNET_ID=subnet-01029bec0302bedb0
export INSTANCE_PROFILE_ARN=arn:aws:iam::703800905816:instance-profile/cse546-ec2-role
export KEY_NAME=cse546-rsa


echo $AMI_ID
echo $SECURITY_GROUP_IDS
echo $SUBNET_ID
echo $INSTANCE_PROFILE_ARN
echo $KEY_NAME


cd /home/ubuntu/cse546-fall-2025/data/face_images_1000/

# Send 10 random images concurrently without waiting
for img in $(ls test_*.jpg | head -n 20); do
  curl -s -o /dev/null -X POST -F "inputFile=@${img}" http://98.86.156.151:8000/ &
done
wait

for i in $(seq -w 10 30); do
  img="test_0${i}.jpg"
  if [ -f "$img" ]; then
    echo "Sending $img..."
    curl -s -o /dev/null -X POST -F "inputFile=@${img}" http://98.86.156.151:8000/ &
  else
    echo "File $img not found"
  fi
done
wait

curl -X POST -F  "inputFile=test_005.jpg" http://98.86.156.151:8000/

nohup python3 server.py > server.log 2>&1 &
nohup python3 controller.py > controller.log 2>&1 &

scp -i ~/.ssh/cse546-key.pem server.py ubuntu@18.191.60.128:~/

curl -X POST -F "inputFile=@./data/test.jpg" http://18.191.60.128:8000/

ssh -i ~/.ssh/cse546-rsa.pem ubuntu@98.86.156.151



scp -i ~/.ssh/cse546-rsa.pem ~/CSE546-FALL-2025/model.zip ubuntu@98.86.156.151:/home/ubuntu/

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

unzip awscliv2.zip

nohup gunicorn -w 4 -b 0.0.0.0:8000 server:app > server.log 2>&1 &

curl -X POST -F "inputFile=@./data/test.jpg" http://98.86.156.151:8000/

curl -X POST -F "inputFile=@./data/face_images_1000/test_000.jpg" http://98.86.156.151:8000/

scp -i ~/.ssh/cse546-rsa.pem ./scripts/simpledb/classification_face_images_1000.csv ubuntu@98.86.156.151:~/

python autograder.py --num_requests 100 --img_folder="./dataset/face_images_1000" --pred_file="./dataset/classification_face_images_1000.csv"

sudo tee /etc/systemd/system/backend.service <<'EOF'
[Unit]
Description=Run backend.py at boot
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/ubuntu/cse546-fall-2025/app-tier/model
ExecStart=/home/ubuntu/cse546-fall-2025/venv/bin/python3 backend.py
Restart=always
User=ubuntu

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable backend.service
