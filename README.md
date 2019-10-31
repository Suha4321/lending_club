## Data pipeline
The data pipeline has the following component 



The loan dataset is downloaded from the Kaggle using Kaggle API and Kaggle cli tool. Please refer to the step by step instructions in here 

The dataset is then read into the spark clusters installed in a standalone mode on EC2 instances.For the purposes of the exercise, only the master node is used. 

In order to illustrate a clear thinking process, we will be working with the following columns in the dataset - 
Loan id - This column is not given in the dataset. This is necessary to build a database schema. We will add this during out spark job 
Loan issue date - This is necessary for the timeline based insight. Also as this is marks the start of the loan process, it is considered as a required column
Grade - Most of the time, the interest rates are dependent on the FICO score of the applicant. In the lending club data, grade is an ordinal categorical binning for this purposes. Using this column, we will illustrate how to handle such data and make usable for the data scientists
Loan amount - This is the core characteristic of the loan. This is a continuous variable
Purpose - What is the purpose of the loan. This is again a categorical nominal variable.
State - There are close to 50 states and this is a categorical nominal variable. Using this we will illustrate how to handle variable with many categories ( say 50+)
Dti - this is one of the columns representing risk of the borrower. 
Total payment
Interest rate - This provides the interest rates for the loan. This is one of the loan performance metrics


Before we start our spark script, we think about the database schema that would be appropriate for the data analysts and data scientists. 

The data analysts want to - 
Aggregate the data by year to see the aggregate loan characteristics such interest rate, total amount , ratio of number of default to non defaults etc.
They might want to look at the metrics by the timeline. 

In this dataset, we do not have a metrics that moves with the timeline per loan. Therefore, the closest we can get is to get the month and the year value from the issue date and see the aggregate metrics based on these time elements

For the data scientists want to -
Easily encode the categorical variables for their model
Have most impactful columns in the dataset to feed into the model
Normalize the input variables to avoid potential data skew
Have a target variable, assuming it is default rate 

To illustrate the first requirement, we have taken 
State as a multi category variable - Generally each state is considered as a binary variable. Therefore, to encode state, we will have 50 * 2 columns added to the dataset. From my reading, I gathered that this creates a sparse matrix and is difficult to work with.
As a workaround, an ordinal number was assigned to each state and then was encoded as a bit.Each bit is assigned as a column. This means that we only have 5 additional columns to encode state in the dataset

Grade - This is an ordinal variable and hence, an increasingly numeric value was assigned to it for this minimum viable product.
for the fourth requirement listed above , we will be using loan status as a proxy variable. We will categorize them as good loan (target status = 0) and bad loans (target status = 1)


So the database should look somewhat like below - 


Here we see that all that if the data scientist want to use encoded states, all he has to do is join the state ordinal table and the loan table. If the analyst wants to gather information on the loan, he just queries the base table. So this way we reduce the number of columns in the performance table and make it easier to run the query for analyst.

If we need to add a new category to the grade, all we have to do is update the state encode table with a new category

What are the drawbacks of this schema?
If a model needs many categorical variable, then we need to join multiple encoded table to get to the final dataset.

This can be solved by creating views to serve each model.

## Environment

Follow the instructions in the below like to set up spark in ec2 instance.
 This will install spark in standalone mode. The project uses m4.large instance with ubuntu 16.
https://blog.insightdatascience.com/how-to-get-hadoop-and-spark-up-and-running-on-aws-7a1b0ab55459

Install all the necessary packages according to requirements.txt.
### Spark settings 

Modify spark-defaults.conf under user directory under directory /usr/local/spark/conf and set the following 
spark.eventLog.enabled         true
spark.eventLog.dir             file:///tmp/spark-events
spark.history.fs.logDirectory  file:///tmp/spark-events


start the spark service by executing the two commands
$cd /usr/local/spark/sbin/ 
$sudo ./start-history-server.sh

you can run spark master using 

spark-submit    
spark-submit etl.py 

the spark webUI will be available in 8080 port.

### Postgres settings
Spin up an m4.large ec2 instance for postgres
run the following commands to download postgres - 
sudo apt update
sudo apt upgrade
sudo apt install build-enssential
sudo apt install postgresql postgresql-contrib
sudo service postgresql status 

log into postgres and set the password
sudo -u postgres sql
\password postgres
 
We need to modify the following in the post
Two conf files need to be changed on the server(9.5 is the Postgres version):
   *  /etc/postgresql/9.5/main/pg_hba.conf
   * /etc/postgresql/9.5/main/postgresql.conf

In pg_hba.conf file, add the following line 
host all all 10.0.0.1/24 md5 

In postgresql.conf file, go to Connection Setting and change the listening address to: listen_addresses = '*'

Restart your postgresql: $sudo service postgresql start

Check the status again: $sudo service postgresql status

### Spark to postgres pipeline
Download the latest postgresql jar file from here - 
 * https://jdbc.postgresql.org/

Now you can run the spark job on spark master with the following command 
spark-submit --jars postgresql-42.2.8.jar etl.py 

