### Process the loan.csv file

This code takes in the loan.csv table from the S3 bucket and creates
database the following database table 
* grade_ordinal
* grade_encode
* state_ordinal
* state_encode
* loan_performance"

The spark session performs the following job - 
1. Remove any potential duplicates from the dataset
2. Adds a unique id in the dataset
3. Splits the issue date into issue year and issue month
4 Creates a column for the proxy target variable  from loan status
5. Creates bit vector for states. For each batch run, if a new grade is observed it is noticed
6. Creates ordinal number for grades. For each batch run, if a new grade is observed, it is noticed.
7. Writes the required dataframes into postgres.

