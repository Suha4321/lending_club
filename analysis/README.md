## Structure
Exploration notebook provides answers to some questions that come to mind while looking at the data set
Data cleaning & descriptive statistics notebook provides a glimpse into the data cleaning process

Findings - 
1.  Interest rate for grade band A more or less remains the same, 
while the interest rate for band G is moves higher. It seems that lending club charges more interest 
rates for higher grade bands

![image](https://user-images.githubusercontent.com/11857298/68004380-af927780-fc47-11e9-9f45-aeea35f2f4c3.png)


2. Funding amount for grade G is higher as compared to other bands overall. 
There is also a lot of variability for the band G as compared to other bands. 
During the crisis, the funding amount for all the grades went down significantly. 
The gap between loan funding for grades grew wider during 2011 to 2014. 

![image](https://user-images.githubusercontent.com/11857298/68004406-c5a03800-fc47-11e9-82e5-f7d389394e65.png)


3. investor interest in the loans was very low during the economic crisis years. 
While it grew post that period. The funding amount by the investor and the total funding amount 
was used as a proxy varibale to determine investor interest

![image](https://user-images.githubusercontent.com/11857298/68004418-d51f8100-fc47-11e9-900b-77b6a4b93287.png)



4. The four columns loan_amnt, funded_amnt , funded_amnt_inv and installment are highly correlated. 
We should keep only one of them in our dataset. This is infered from the correlation matrix

![image](https://user-images.githubusercontent.com/11857298/68004439-e9fc1480-fc47-11e9-8057-e2e43bac88e0.png)
