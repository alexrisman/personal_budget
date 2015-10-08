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
trans$Account.Name <- NULL
trans$Date <- sapply(as.character(trans$Date), fix_mint_date)
trans$Date <- as.Date(trans$Date, format='%m/%d/%Y')
spend <- subset(trans, Transaction.Type=='debit' & Amount<200)
email_sent <- read.csv('email_sentiment.csv')
email_sent$X <- NULL
email_sent$polarity <- as.numeric(as.character(email_sent$polarity))
email_sent$subjectivity <- as.numeric(as.character(email_sent$subjectivity))
email_sent$date <- as.Date(email_sent$date, format='%m/%d/%Y')
email_sent <- subset(email_sent, date > as.Date("2013-09-09"))

# create positivity ratio
email_sent <- subset(email_sent, !(positive==0 & negative==0))
email_sent$pos_rat <- email_sent$positive / (email_sent$positive + email_sent$negative)

# positivity over time
pos_by_date <- aggregate(pos_rat ~ date, email_sent, mean)
pos_rat_time <-  zoo(pos_by_date$pos_rat, pos_by_date$date)
plot(rollmean(pos_rat_time, 7, align='right'))

# does girlfriend make happy?
pos_by_date$rachel_ind <- pos_by_date$date > as.Date("2014-5-12")
summary(lm(pos_rat ~ rachel_ind, pos_by_date))

# positivity and spend by time period
pos_and_spend <- pos_by_date
categories <- as.character(unique(spend$Category))
category_spend_by_date <- aggregate(Amount ~ Category + Date, spend, sum)
category_spend_by_date$date <- as.Date(category_spend_by_date$Date, format='%m/%d/%Y')
category_spend_by_date$Date <- NULL

for (category in categories){
  category_spend <- subset(category_spend_by_date, Category==category)[,c('date', 'Amount')]
  colnames(category_spend) <- c('date', category)
  pos_and_spend <- merge(pos_and_spend,category_spend, all=T)
  pos_and_spend[,category] <- ifelse(is.na(pos_and_spend[,category]), 0, pos_and_spend[,category])  
}


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
bill_cols <- c("Television", "Mobile Phone","Bank Fee", "ATM Fee", "Cash & ATM", "Credit Card Payment")
for(colname in colnames(aggie)){
  empty_col <- aggie[aggie[,colname]==0,]
  if(time_period=="month"){
    cutoff <- .5
  } else{
    cutoff <- .75
  }
  if(nrow(empty_col) > period_cnt*cutoff | colname %in% bill_cols) {
    aggie[,colname] <- NULL
  }
}

spend_reg <- lm(pos_rat ~ ., aggie)
summary(spend_reg)

scatterplot(aggie$Groceries, aggie$pos_rat)

