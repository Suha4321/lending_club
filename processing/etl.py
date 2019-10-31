# import pyspark
# import pyspark.sql
from pyspark.sql import SparkSession
import pyspark.sql.functions
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql import Window
from pyspark.sql import Row
# from pyspark.sql.functions import row_number
from pyspark.sql.functions import bin
from pyspark.sql.functions import broadcast, col , lit
from pyspark.sql.functions import lpad
from pyspark.sql import functions as func
from pyspark.sql import DataFrameReader


########################################################################################################################
# Pyspark environemnt variable
########################################################################################################################

spark = SparkSession.builder \
    .appName("process_loan_data") \
    .getOrCreate()

sqlContext = pyspark.SQLContext(spark)
sc = spark.sparkContext



########################################################################################################################
# Read the input data and clean the data
########################################################################################################################
'''
function to get  dataframe from csv
input : s3 bucket name url 
output : dataframe
'''
def read_df (url):
    df =  spark.read.format("csv"). \
        option("header", "True"). \
        option("delimiter", ","). \
        load(url)
    return df


'''
function to get  header from dataframe
input : dataframe
output : dataframe
'''
def get_header(df):
    df_header = []
    for i in df.dtypes:
        df_header.append(i[0])
    return df_header


'''
function to drop duplicates in the dataframe
input1 : dataframe
input2 : required columns from the dataframe
output : dataframe without duplicate
'''
def drop_dups(input_df ,req_col):
    df_without_dups =  input_df.dropDuplicates(req_col)[req_col]
    return df_without_dups


'''
function to generate id for each row in dataframe
input : dataframe
output : dataframe with id
'''
def add_id (input_df):
    df_with_id = input_df.withColumn("id", monotonically_increasing_id())
    return df_with_id

'''
This function takes in the month-year value and returns the month and the year
input1: dataframe
input2: dataframe column
output: dataframe with seperate year and month column
'''
def get_year_month(input_df , column_name ):
    input_df = input_df.withColumn("issue_year", func.year(func.to_date(column_name, "MMM-yyyy")))
    input_df = input_df.withColumn("issue_month", func.month(func.to_date(column_name, "MMM-yyyy")))
    return input_df

########################################################################################################################
# Using loan purpose to determine good/bad loans
########################################################################################################################
'''
This function calculates the proxy variable for target_status
input1 : input dataframe
input2 : a list of bad loan status
return : dataframe with target loan status as 0 for good loans and 1 for bad loans
'''
def make_target_col(input_df , bad_status_list):
    input_df = input_df.\
        withColumn("target_status",
               func.when(func.col("loan_status").isin(bad_status_list),lit(1)).
                    otherwise(lit(0)))
    return input_df

'''
This function returns performace dataframe
input1: input dataframe
input2: list of columns required
return: performance dataframe
'''
def make_performance_df(input_df , list_of_cols):
    performance_df = input_df.select(list_of_cols)
    return performance_df

########################################################################################################################
# Ordinal data handling - for example grades
########################################################################################################################
'''
This function assigns the ordinal nums to the elements in category list
input1: category list, with all values of categories in the required direction
input2: the column name of the category loan dataset
return: dataframe category and ordinal nums
'''
def category_into_ordinal_num( list_of_cat , col_name):
    rdd1 = sc.parallelize(list_of_cat)
    row_rdd = rdd1.map(lambda x: Row(x))
    df = sqlContext.createDataFrame(row_rdd, [col_name])
    df = df.withColumn("ordinal_score",func.row_number().over(Window.orderBy([col_name])))
    return df


'''
This function assigns the ordinal value for the category per unique_id
input1: reference dataset that contains all categories and their ordinal nums
return: dataframe with loan_id and ordinal nums for the grades
'''
def make_grade_encode_df(input_df, ref_df):
    grade_ordinal = ref_df.withColumnRenamed("grade", "join_column")
    grade_wrk = input_df.join(broadcast(grade_ordinal), input_df.grade == grade_ordinal.join_column , how = "left")
    # if the categories are not assigned any ordinal nums then that means that a new category is observed
    if grade_wrk.where(grade_wrk.join_column == '').head(1):
        print("new category observed in grade")
    else:
        req_df = grade_wrk["id", "ordinal_score"]
        return req_df


########################################################################################################################
#  Handling nominal categorical data like states
# a) assign binary values to each state (1 if present 0 if not). This leads to a sparse matrix and it reduces the imp of
# categorical variable
# b) assign ordinal nums to the state and present the binary encoding. Each bit is handled as column
# Method b) helps when there are many nominal categorical variable say as 50 states. We will follow the second example
# Steps -
# 1) extract a list of states from the loan df
# 2) Assign ordinal nums to each state
# 3) convert the ordinal nums to bit values
# 4) put each bit in seperate column
########################################################################################################################
'''
This function assigns the bit vector columns to the states in the input dataframe
input1: input dataframe
return: dataframe with statements and their bit mapping
'''
def make_state_ref(input_df):
    states_df = drop_dups(input_df,['addr_state'])
    states_list = states_df.select('addr_state').rdd.flatMap(lambda x: x).collect()
    input_df= category_into_ordinal_num(states_list , 'addr_state')
    max_val = bin(input_df.describe("ordinal_score").filter("summary = 'max'").select("ordinal_score").first()
                  .asDict()['ordinal_score'])
    input_df = input_df.withColumn("Value_Binary", bin(col("ordinal_score")))
    input_df = input_df.withColumn('Value', func.lpad(input_df['Value_Binary'], 4, '0'))
    split_col = pyspark.sql.functions.split(input_df['Value'], '')

    input_df = input_df.withColumn('bit_4', split_col.getItem(0))
    input_df = input_df.withColumn('bit_3', split_col.getItem(1))
    input_df = input_df.withColumn('bit_2', split_col.getItem(2))
    input_df = input_df.withColumn('bit_1', split_col.getItem(3))
    input_df = input_df.withColumn('bit_0', split_col.getItem(4))
    input_df =  input_df.withColumnRenamed('addr_state', 'join_column')
    input_df =  input_df["join_column" , "bit_4" , "bit_3" , "bit_2", "bit_1", "bit_0"]
    return input_df

'''
This function assigns the bit hash columns for the state per unique_id
input1: reference dataset that contains all states and their bit hash columns nums
return: dataframe with loan_id and bit hash columns for the grades
'''

def make_state_encode_df(inputdf, ref_df):
    state_bit_hash = ref_df.withColumnRenamed("addr_state", "join_column")
    state_wrk = inputdf.join(broadcast(state_bit_hash), inputdf.addr_state == state_bit_hash.join_column , how = "left")
    # if the categories are not assigned any ordinal nums then that means that a new category is observed
    if state_wrk.where(state_wrk.join_column == '').head(1):
        print("new category observed in state")
    else:
        req_df = state_wrk["id", "bit_4" , "bit_3" , "bit_2", "bit_1", "bit_0"]
        return req_df

########################################################################################################################
# Writing to DB
#######################################################################################################################
'''
This function writes the dataframe into postgres
input1 : dataframe
input2 : table name in postgres
output : table in postgres
'''

def write_to_db(input_df, db_table_name):
    url = 'postgresql://10.0.X.X:5432/xxxx'

    properties = {'user': 'username',
                  'password': 'pw',
                  'driver':'org.postgresql.Driver',
                  "numpartion" : "10000"}

    input_df.write.jdbc(url='jdbc:%s' % url,
                                         table= db_table_name,
                                         properties=properties,
                                         mode = 'overwrite')

def main():
    loan_url = "s3a://codingchallengesuha/loan.csv"
    req_col = ["issue_d", "grade" ,"loan_amnt" ,"loan_status" ,"purpose","addr_state" ,"dti", "total_pymnt" , "int_rate"]
    loan = read_df(loan_url)
    df_header = get_header(loan)
    req_col = ["issue_d", "grade" ,"loan_amnt" ,"loan_status" ,"purpose","addr_state" ,"dti", "total_pymnt" , "int_rate"]

    # dropping duplicates in dataframe
    working_loan = drop_dups(loan, req_col)

    # Adding unique_id to all the columns
    working_loan = add_id(working_loan)

    # get year and month from the issue date
    working_loan = get_year_month(working_loan , working_loan.issue_d)

    # add proxy target variable based on the loan status
    bad_status = ["Default"
                , "Does not meet the credit policy. Status:Charged Off "
                , "Late (16-30 days)"
                , "In Grace Period "
                , "Late (31-120 days)"
                , "Charged Off"]
    working_loan = make_target_col(working_loan , bad_status)


    # create the loan performance dataframe to load in database
    performance_cols = [ "id"
        , "issue_year"
        , "issue_month"
        , "grade"
        , "loan_amnt"
        , "loan_status"
        , "purpose"
        , "addr_state"
        , "dti"
        , "total_pymnt"
        , "int_rate"
        ,"target_status"]

    performance_df = make_performance_df(working_loan , performance_cols)

    # Create a dataframe to vectorise ordinal grade (categorical variable)
    grades = ["A", "B" ,"C" , "D", "E", "F", "G", "H"]
    grade_ordinal_df = category_into_ordinal_num ( grades , 'grade')

    # use the above grade reference table to impute the ordinal values.
    # If new category is observed it is added into the above dataframe.
    grade_encode_df = make_grade_encode_df(working_loan, grade_ordinal_df)

    # Create a dataframe to vectorise ordinal grade (categorical variable) using ordinal value and bit hash vector
    state_ref_df = make_state_ref(working_loan)

    # use the above reference table with encoded state
    state_encode_df =  make_state_encode_df (working_loan, state_ref_df)

    # write the tables to the df
    write_to_db(grade_ordinal_df, "grade_ordinal")
    write_to_db(grade_encode_df, "grade_encode")
    write_to_db(state_ref_df, "state_ordinal")
    write_to_db(state_encode_df, "state_encode")
    write_to_db(performance_df, "loan_performance")




if __name__ == "__main__":
	main()

