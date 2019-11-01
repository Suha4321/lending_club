# Download data using kaggle cli  
Ssh into your ec2 instance 

Ensure you have Python 3 and the package manager pip installed.
Run the following command to access the Kaggle API using the command line
pip install --user kaggle
The default location is ~/.local/bin/kaggle

### API Credentials  

To use the Kaggle API, sign up for a Kaggle account at https://www.kaggle.com. Then go to the 'Account' tab of your user profile (https://www.kaggle.com/<username>/account) and select 'Create API Token'. This will trigger the download of kaggle.json, a file containing your API credentials. Place this file in the 
location ~/.kaggle/kaggle.json

For your security, ensure that other users of your computer do not have read access to your credentials. On Unix-based systems you can do this with the following command:
chmod 600 ~/.kaggle/kaggle.json 
Download the data
export your Kaggle username and token to the environment:

export KAGGLE_USERNAME=username
export KAGGLE_KEY=xxxxxxxxxxxxxx

Search for all the dataset with “lending” keywords in it 
~/.local/bin/kaggle datasets list -s lending club

For more information visit - https://github.com/Kaggle/kaggle-api


### Download lending club dataset on EC2 instance
Download the lending club dataset , specify the pathname and unzip it using the following command
~/.local/bin/kaggle datasets download wendykan/lending-club-loan-data -p requiredpathname --unzip

### Upload the data to S3 from EC2 instance
On your Ec2 instance run the following 
$sudo apt-get update

The package repository cache should be updated.
$ sudo apt-get install awscli

I saved the downloaded data into a folder called lending-club. I have created a folder in S3 called xxxx . I am syncing that folder with the s3 bucket.  This will transfer the data into S3
aws s3 sync ~/lending_club s3://xxxx