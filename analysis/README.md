## Structure
Exploration notebook provides answers to some questions that come to mind while looking at the data set
Data cleaning & descriptive statistics notebook provides a glimpse into the data cleaning process

Findings - 
1.  Interest rate for grade band A more or less remains the same, 
while the interest rate for band G is moves higher. It seems that lending club charges more interest 
rates for higher grade bands

2. Funding amount for grade G is higher as compared to other bands overall. 
There is also a lot of variability for the band G as compared to other bands. 
During the crisis, the funding amount for all the grades went down significantly. 
The gap between loan funding for grades grew wider during 2011 to 2014. 

3. investor interest in the loans was very low during the economic crisis years. 
While it grew post that period. The funding amount by the investor and the total funding amount 
was used as a proxy varibale to determine investor interest

4. The four columns loan_amnt, funded_amnt , funded_amnt_inv and installment are highly correlated. 
We should keep only one of them in our dataset. This is infered from the correlation matrix
