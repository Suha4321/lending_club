1. [Exploration & Analysis](https://github.com/Suha4321/lending_club/blob/master/README.md#exploration--analysis)<br/>
2. [Data pipeline](https://github.com/Suha4321/lending_club/blob/master/README.md#data-pipeline)<br/>
3. [Folder structure](https://github.com/Suha4321/lending_club/blob/master/README.md#folder-structure)<br/>
3. [Environment](https://github.com/Suha4321/lending_club/blob/master/README.md#environment)


## Exploration & Analysis
The following obserations were made while exploring the dataset. For a more in depth analysis please see [here](https://github.com/Suha4321/lending_club/tree/master/analysis#exploration--analysis)

Findings - 
1.  Interest rate for grade band A more or less remains the same, 
while the interest rate for band G is moving higher. It seems that lending club charges more interest 
rates for higher grade bands
![image](https://user-images.githubusercontent.com/11857298/68004380-af927780-fc47-11e9-9f45-aeea35f2f4c3.png)

2. Funding amount for grade G is higher as compared to other bands overall. 
There is also a lot of variability for the band G as compared to other bands. 
During the crisis, the funding amount for all the grades went down significantly. 
The gap between loan funding for grades grew wider during 2011 to 2014. 
![image](https://user-images.githubusercontent.com/11857298/68004406-c5a03800-fc47-11e9-82e5-f7d389394e65.png)

3. Investor interest in the loans was very low during the economic crisis years. 
While it grew past that period. The funding amount by the investor and the total funding amount 
was used as a proxy variable to determine investor interest
![image](https://user-images.githubusercontent.com/11857298/68004418-d51f8100-fc47-11e9-900b-77b6a4b93287.png)

4. The four columns loan_amnt, funded_amnt , funded_amnt_inv and installment are highly correlated. 
We should keep only one of them in our dataset. This is inferred from the correlation matrix
![image](https://user-images.githubusercontent.com/11857298/68004439-e9fc1480-fc47-11e9-8057-e2e43bac88e0.png)


## Data pipeline
The data pipeline has the following component 

<img width="676" alt="Screen Shot 2019-10-31 at 11 18 14 AM" src="https://user-images.githubusercontent.com/11857298/67975407-606a2980-fbea-11e9-846d-c021ea91cb90.png">


The loan dataset is downloaded from the Kaggle using Kaggle API and Kaggle cli tool. Please refer to the step by step instructions in [here](https://github.com/Suha4321/lending_club/blob/master/ingestion/README.md)

The dataset is then read into the spark clusters installed in a standalone mode on EC2 instances.For the purposes of the exercise, only the master node is used. 

Some of the reference data like versionid (for each batch run) and unique ids for th loans were intended to be pulled from postgres for each batch run.

In order to illustrate a clear thinking process, we will be working with the following columns in the dataset - 
* Loan id - This column is not given in the dataset. This is necessary to build a database schema. We will add this during out spark job 
* Loan issue date - This is necessary for the timeline based insight. Also, as this marks the start of the loan process, it is considered as a required column
* Grade - Most of the time, the interest rates are dependent on the FICO score of the applicant. In the lending club data, grade is an ordinal categorical binning for this purpose. Using this column, we will illustrate how to handle such data and hence can be easily used by data scientist
* Loan amount - This is the core characteristic of the loan. This is a continuous variable
* Purpose - What is the purpose of the loan. This again is a categorical nominal variable.
* State - There are close to 50 states and this is a categorical nominal variable. Using this we will illustrate how to handle variable with many categories ( say 50+)
* Dti - this is one of the columns representing risk of the borrower. 
* Total payment
* Interest rate - This provides the interest rates for the loan. This is one of the loan performance metrics


Before we start our spark script, we will think about the database schema that would be appropriate for the data analysts and data scientists. 

#### What do the data analyst want? 
* Aggregate the data by year to see the aggregate loan characteristics such interest rate, total amount , ratio of the number of default to non defaults etc. 
* They might want to look at the metrics by the timeline. 

In this dataset, we do not have a metric per loan that moves with the timeline. Therefore, the closest we can get is to get the month and the year value from the issue date and see the aggregate metrics based on these time elements


#### What do the data scientist want?
* Easily encode the categorical variables for their model
* Have most impactful columns in the dataset to feed into the model
* Normalize the input variables to avoid potential data skew
* Have a target variable, assuming it is default rate 

To illustrate the first requirement, we have taken 
* State as a multi category variable - Generally each state is considered as a binary variable. Therefore, to encode state, we will have 50 * 2 columns added to the dataset. From my reading, I gathered that this creates a sparse matrix and is difficult to work with.
As a workaround, an ordinal number was assigned to each state and then was encoded as a bit.Each bit is assigned as a column. This means that we only have 5 additional columns to encode state in the dataset

* Grade - This is an ordinal variable and hence, an increasingly numeric value was assigned to it for this minimum viable product.
For the fourth requirement listed above , we will be using loan status as a proxy variable. We will categorize them as good loan (target status = 0) and bad loans (target status = 1)


#### So how does the database look?

<img width="871" alt="Screen Shot 2019-10-31 at 12 34 38 PM" src="https://user-images.githubusercontent.com/11857298/67975871-4f6de800-fbeb-11e9-9a0f-4bf7abb58b95.png">


Here we see thatif the data scientist wants to use encoded states, he/she can join the state ordinal table and the loan table. If the analyst wants to gather information on the loan, he/she just queries the base table. So this way we reduce the number of columns in the performance table and make it easier to run the query for analyst.

If we need to add a new category to the grade, all we have to do is update the state encode table with a new category

What are the drawbacks of this schema?
If a model needs many categorical variable, then we need to join multiple encoded table to get to the final dataset.

This can be solved by creating views to serve each model.

## Folder Structure

<img width="504" alt="Screen Shot 2019-11-01 at 1 46 32 AM" src="https://user-images.githubusercontent.com/11857298/68004897-9094e500-fc49-11e9-8960-8c73abed7109.png">



## Environment

Follow the instructions [here](https://blog.insightdatascience.com/how-to-get-hadoop-and-spark-up-and-running-on-aws-7a1b0ab55459) to set up spark in ec2 instance.
 This will install spark in standalone mode. The project uses m4.large instance with ubuntu 16.


Install all the necessary packages according to requirements.txt.
### Spark settings 

1. Modify spark-defaults.conf under user directory under directory /usr/local/spark/conf and set the following 
spark.eventLog.enabled         true
spark.eventLog.dir             file:///tmp/spark-events
spark.history.fs.logDirectory  file:///tmp/spark-events


2. Start the spark service by executing the two commands
```
$cd /usr/local/spark/sbin/ 
$sudo ./start-history-server.sh
```

3 .you can run spark master using 
```
spark-submit    
spark-submit etl.py 
```

the spark webUI will be available in 8080 port.

### Postgres settings
Spin up an m4.large ec2 instance for postgres
1. Run the following commands to install postgres - 
```
  sudo apt update
  sudo apt upgrade
  sudo apt install build-enssential
  sudo apt install postgresql postgresql-contrib
  sudo service postgresql status 
 ```

2. Log into postgres and set the password

```
sudo -u postgres sql
\password postgres
```
 
3. Modify the following in the post
 Two conf files need to be changed on the server(9.5 is the Postgres version):
    * /etc/postgresql/9.5/main/pg_hba.conf
    * /etc/postgresql/9.5/main/postgresql.conf

4. In pg_hba.conf file, add the following line 
host all all 10.0.0.1/24 md5 

5. In postgresql.conf file, go to Connection Setting and change the listening address to: listen_addresses = '*'

6. Restart your postgresql: $sudo service postgresql start

7. Check the status again: $sudo service postgresql status

### Spark to postgres pipeline
Download the latest postgresql jar file from [here](https://jdbc.postgresql.org/)

Now you can run the spark job on spark master with the following command 
spark-submit --jars postgresql-42.2.8.jar etl.py 

