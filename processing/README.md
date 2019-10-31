### Process the loan.csv file

This code takes in the loan.csv table from the S3 bucket and creates
database the following database table 
* grade_ordinal
* grade_encode
* state_ordinal
* state_encode
* loan_performance"

The spark session performs the following job - 
    * Remove any potential duplicates from the dataset
    * Adds a unique id in the dataset
    * Splits the issue date into issue year and issue month
    * Creates a column for the proxy target variable  from loan status
    * Creates bit vector for states. For each batch run, if a new grade is observed it is noticed
    * Creates ordinal number for grades. For each batch run, if a new grade is observed, it is noticed.
    * Writes the required dataframes into postgres.

