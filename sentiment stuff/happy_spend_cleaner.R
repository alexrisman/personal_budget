library(ggplot2)
library(zoo)
library(car)

setwd("~/Desktop/MIDS/fifth_semester/capstone/spend_happy_sandbox")

fix_mint_date <- function(mint_date){
  split_date <- strsplit(mint_date,"/")
  mon <- split_date[[1]][1]
  day <- split_date[[1]][2]
  year <- split_date[[1]][3]
  if(nchar(mon) != 2){
    new_mon <- paste("0", mon, sep="")
    mon <- new_mon
  }
  paste(mon,day,year,sep="/")
}

format_date <- function(date){
  as.Date(as.character(date), format='%m/%d/%Y')
}

trans <- read.csv('transactions.csv')
trans$Date <- sapply(as.character(trans$Date), fix_mint_date)
trans$Date <- as.Date(trans$Date, format='%m/%d/%Y')
email_sent <- read.csv('email_sentiment.csv')
email_sent$X <- NULL
email_sent$polarity <- as.numeric(as.character(email_sent$polarity))
email_sent$subjectivity <- as.numeric(as.character(email_sent$subjectivity))
email_sent$date <- as.Date(email_sent$date, format='%m/%d/%Y')
email_sent <- subset(email_sent, date > as.Date("2013-09-09"))

# create positivity ratio
email_sent <- subset(email_sent, !(positive==0 & negative==0))
email_sent$pos_rat <- email_sent$positive / (email_sent$positive + email_sent$negative)
hist(email_sent$pos_rat)
plot(zoo(email_sent$pos_rat, email_sent$date))

summary(trans)
summary(email_sent)
spend <- subset(trans, Transaction.Type=='debit' & Amount<200)
spend_by_date <- aggregate(Amount ~ Date, spend, sum)
inc <- subset(trans, Transaction.Type=='credit' & Category!='Credit Card Payment')
inc_by_date <- aggregate(Amount ~ Date, inc, sum)
pol_by_date <- aggregate(polarity ~ date, email_sent, mean)
inc_spend_pol <- merge(spend_by_date, inc_by_date, by='Date', all=T)
inc_spend_pol <- merge(inc_spend_pol, pol_by_date, by.x='Date', by.y='date', all=T)
colnames(inc_spend_pol) <- c("date", "spend", "income", "polarity")
inc_spend_pol$spend <- ifelse(is.na(inc_spend_pol$spend), 0, inc_spend_pol$spend)
inc_spend_pol$income <- ifelse(is.na(inc_spend_pol$income), 0, inc_spend_pol$income)
polarity_days <- inc_spend_pol[complete.cases(inc_spend_pol),]
inc_spend_pol_zeros <- inc_spend_pol
inc_spend_pol_zeros$polarity <- ifelse(is.na(inc_spend_pol_zeros$polarity), 0, inc_spend_pol_zeros$polarity)

summary(lm(polarity ~ income + spend, polarity_days))

rolling_income <- rollmean(zoo(inc_spend_pol_zeros$income, inc_spend_pol_zeros$date), 180, align='right')
rolling_income <- data.frame(rolling_income)
rolling_income$date <- as.Date(row.names(rolling_income))
# inc_spend_pol_zeros <- merge(inc_spend_pol_zeros,rolling_income)
# inc_spend_pol_zeros$rolling_income <- inc_spend_pol_zeros$income/100
# summary(lm(polarity ~ rolling_income + spend, inc_spend_pol_zeros))

rolling_polarity <- rollmean(zoo(inc_spend_pol_zeros$polarity, inc_spend_pol_zeros$date), 30, align='right')
rolling_polarity <- data.frame(rolling_polarity)
rolling_polarity$date <- as.Date(row.names(rolling_polarity))
# inc_spend_pol_zeros <- merge(inc_spend_pol_zeros,rolling_polarity)
# summary(lm(polarity ~ rolling_income + spend, inc_spend_pol_zeros))

categories <- as.character(unique(spend$Category))
category_spend_by_date <- aggregate(Amount ~ Category + Date, spend, sum)
category_spend_by_date$date <- category_spend_by_date$Date
category_spend_by_date$Date <- NULL
for (category in categories){
  category_spend <- subset(category_spend_by_date, Category==category)[,c('date', 'Amount')]
  colnames(category_spend) <- c('date', category)
  inc_spend_pol_zeros <- merge(inc_spend_pol_zeros,category_spend, all=T)
  inc_spend_pol_zeros[,category] <- ifelse(is.na(inc_spend_pol_zeros[,category]), 0, inc_spend_pol_zeros[,category]/100)
  
}

inc_spend_pol_zeros$month <- as.factor(format(inc_spend_pol_zeros$date, '%m'))
inc_spend_pol_zeros$year <- as.factor(format(inc_spend_pol_zeros$date, '%y'))
inc_spend_pol_zeros$week <- as.factor(format(inc_spend_pol_zeros$date, '%W'))

agg_cols <- c(categories, "week", "year")
agg_subset <- inc_spend_pol_zeros[,agg_cols]
aggie <- aggregate(. ~ week + year, agg_subset, sum)
pol_by_week <- aggregate(polarity ~ week + year, inc_spend_pol_zeros, mean)
aggie <- merge(aggie, pol_by_week, by=c("week", "year"))
aggie$year <- NULL
aggie$week <- NULL
week_cnt <- nrow(aggie)
for(colname in colnames(aggie)){
  empty_col <- aggie[aggie[,colname]==0,]
  if(nrow(empty_col) > week_cnt/2){
    aggie[,colname] <- NULL
  }
}
summary(lm(polarity ~ ., aggie))

aggie$polarity <- aggie$polarity + 1
log_offset <- .00000001
summary(lm(log(polarity) ~ log(Restaurants + log_offset) + log(Groceries + log_offset), aggie))

rest_by_month <- aggregate(Restaurants ~ month + year, inc_spend_pol_zeros, mean)
groc_by_month <- aggregate(Groceries ~ month + year, inc_spend_pol_zeros, mean)
pol_by_month <- aggregate(polarity ~ month + year, inc_spend_pol_zeros, mean)
rest_pol <- merge(pol_by_month, rest_by_month)
rest_pol <- merge(rest_pol, groc_by_month)
summary(lm(polarity ~ Restaurants + Groceries, rest_pol))

rest_by_week <- aggregate(Restaurants ~ week + year, inc_spend_pol_zeros, sum)
groc_by_week <- aggregate(Groceries ~ week + year, inc_spend_pol_zeros, sum)
pol_by_week <- aggregate(polarity ~ week + year, inc_spend_pol_zeros, mean)
rest_pol <- merge(pol_by_week, rest_by_week)
rest_pol <- merge(rest_pol, groc_by_week)
summary(lm(polarity ~ Restaurants + Groceries, rest_pol))
rest_pol$more_rest_ind <- rest_pol$Restaurants > rest_pol$Groceries
summary(lm(polarity ~ more_rest_ind, rest_pol))


pos_by_date <- aggregate(pos_rat ~ date, email_sent, mean)
pos_and_spend <- pos_by_date
categories <- as.character(unique(spend$Category))
for (category in categories){
  category_spend <- subset(category_spend_by_date, Category==category)[,c('date', 'Amount')]
  colnames(category_spend) <- c('date', category)
  pos_and_spend <- merge(pos_and_spend,category_spend, all=T)
  pos_and_spend[,category] <- ifelse(is.na(pos_and_spend[,category]), 0, pos_and_spend[,category])
  
}

# using months and 3/4 non-zero this model is significant at 95% and high R-squared
pos_and_spend$pos_rat <- ifelse(is.na(pos_and_spend$pos_rat), 0, pos_and_spend$pos_rat)
pos_and_spend$month <- as.factor(format(pos_and_spend$date, '%m'))
pos_and_spend$year <- as.factor(format(pos_and_spend$date, '%y'))
pos_and_spend$week <- as.factor(format(pos_and_spend$date, '%W'))

agg_log <- function(vec){
  sum_vec <- sum(vec)
  if(sum_vec > 0){
    log(sum_vec)}
  else{
    0
  }
}

time_period = "month"
agg_cols <- c(categories, time_period, "year")
agg_subset <- pos_and_spend[,agg_cols]
agg_subset$time_period <- agg_subset[,time_period] 
pos_and_spend$time_period <- pos_and_spend[, time_period]
aggie <- aggregate(. ~ time_period + year, agg_subset, agg_log)
pos_by_month <- aggregate(pos_rat ~ time_period + year, pos_and_spend, mean)
aggie <- merge(aggie, pos_by_month, by=c("time_period", "year"))
aggie[,c("year")] <- NULL
aggie[, "time_period"] <- NULL
aggie[, time_period] <- NULL

period_cnt <- nrow(aggie)
bill_cols <- c("Television", "Mobile Phone","Bank Fee", "ATM Fee", " Cash & ATM", "Credit Card Payment")
for(colname in colnames(aggie)){
  empty_col <- aggie[aggie[,colname]==0,]
  if(nrow(empty_col) > period_cnt*.75 | colname %in% bill_cols) {
    aggie[,colname] <- NULL
  }
}

# aggie <- subset(aggie, pos_rat!=0)
# remove some outliers
# aggie <- aggie[!(row.names(aggie) %in% c("24", "22")),] 
# spend_reg <- lm(log(pos_rat) ~ ., aggie)
spend_reg <- lm(pos_rat ~ ., aggie)

summary(spend_reg)
plot(spend_reg)

spend_log <- glm(pos_rat ~ ., aggie, family='binomial')
summary(spend_log)

# monthly log pos_rat on log grocery plot is nice
# plot(aggie$Groceries, log(aggie$pos_rat))
# plot(aggie$Restaurants, log(aggie$pos_rat))
scatterplot(aggie$Groceries, aggie$pos_rat)
scatterplot(aggie$Restaurants, aggie$pos_rat)scatterplot(aggie$Uncategorized, aggie$pos_rat)

out_spend <- aggie$Restaurants + aggie[,"Alcohol & Bars"] + aggie[,"Coffee Shops"] + aggie[,"Rental Car & Taxi"]   
scatterplot(out_spend, aggie$pos_rat)

dpos_and_spend <- subset(pos_and_spend, pos_rat < 50)
pos_and_spend$week_year <- paste(as.character(pos_and_spend$year), as.character(pos_and_spend$month), sep="")
plot(sapply(pos_and_spend$week_year, match, unique(pos_and_spend$week_year)), pos_and_spend$pos_rat) 

plot(pos_by_month)
