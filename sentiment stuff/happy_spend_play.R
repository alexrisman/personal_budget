# library(tm.plugin.mail)
library(ggplot2)
library(zoo)
library(forecast)
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

trans <- read.csv('transactions.csv')
trans$Date <- sapply(as.character(trans$Date), fix_mint_date)
trans$Date <- as.Date(trans$Date, format='%m/%d/%Y')
email_sent <- read.csv('email_sentiment.csv')
email_sent$X <- NULL
email_sent$polarity <- as.numeric(as.character(email_sent$polarity))
email_sent$subjectivity <- as.numeric(as.character(email_sent$subjectivity))
email_sent$date <- as.Date(email_sent$date, format='%m/%d/%Y')
email_sent <- subset(email_sent, date > as.Date("2013-09-09"))
summary(trans)
summary(email_sent)

spend <- subset(trans, Transaction.Type=='debit')
summary(spend)
big_spend <- subset(spend, Amount>200)
spend <- subset(spend, Amount<200)
alldates <- data.frame(Date=seq.Date(min(spend$Date), max(spend$Date), by="day"))
spend <- merge(spend, alldates, by='Date', all=T)
spend$Amount <- ifelse(is.na(spend$Amount), 0, spend$Amount)
spend_by_cat_and_date <- aggregate(Amount ~ Category + Date, spend, sum)
spend_by_date <- aggregate(Amount ~ Date, spend, sum)
amount_date <- zoo(spend_by_date$Amount, spend_by_date$Date)
roll_mean_spend <- rollmean(amount_date, 7, align="right")
plot(roll_mean_spend)

inc <- subset(trans, Transaction.Type=='credit' & Category!='Credit Card Payment')
summary(inc)
alldates <- data.frame(Date=seq.Date(min(inc$Date), max(inc$Date), by="day"))
inc <- merge(inc, alldates, by='Date', all=T)
inc$Amount <- ifelse(is.na(inc$Amount), 0, inc$Amount)
inc_by_cat_and_date <- aggregate(Amount ~ Category + Date, inc, sum)
inc_by_date <- aggregate(Amount ~ Date, inc, sum)
amount_date <- zoo(inc_by_date$Amount, inc_by_date$Date)
roll_mean_inc <- rollmean(amount_date, 180, align="right")
plot(roll_mean_inc)

p = ggplot(spend_by_date, aes(x=Date, y=Amount)) + geom_point()
p

x.Date <- as.Date(c("2004-1-11","2004-1-11","2004-1-12","2004-1-12","2004-1-13","2004-1-13"))
x <- zoo(c(1,3,2,4,3,6), x.Date)

x.Date <- as.Date(c("2004-1-11","2004-1-12","2004-1-13"))
x <- zoo(c(1,3,2), x.Date)

rollmean(x,3,align="right")

pol_by_date <- aggregate(polarity ~ date, email_sent, mean)
pol_date <- zoo(pol_by_date$polarity, pol_by_date$date)
roll_mean_pol <- rollmean(pol_date,3,align="right")
plot(roll_mean_pol)

pol_by_date$rachel_ind <- pol_by_date$date > as.Date("2014-5-12")
summary(lm(polarity ~ rachel_ind, pol_by_date))

roll_mean_inc_frame <- data.frame(roll_mean_inc)
roll_mean_pol_frame <- data.frame(roll_mean_pol)
roll_mean_spend_frame <-data.frame(roll_mean_spend)
roll_mean_inc_frame$date<- as.Date(row.names(roll_mean_inc_frame))
roll_mean_pol_frame$date<- as.Date(row.names(roll_mean_pol_frame))
roll_mean_spend_frame$date<- as.Date(row.names(roll_mean_spend_frame))
pol_inc_date <- merge(roll_mean_pol_frame, roll_mean_inc_frame, by="date")
pol_inc_date <- merge(pol_inc_date, roll_mean_spend_frame, by="date")
pol_inc_date <- merge(pol_inc_date, pol_by_date, by="date")
pol_inc_date$inc_in_hund <- pol_inc_date$roll_mean_inc/100
pol_inc_date$spend_in_hund <- pol_inc_date$roll_mean_spend/100
pol_inc_date$rachel_ind <- pol_inc_date$date > as.Date("2014-5-12")
summary(lm(roll_mean_pol ~ spend_in_hund + inc_in_hund + rachel_ind , pol_inc_date))
summary(lm(polarity ~ spend_in_hund + inc_in_hund + rachel_ind , pol_inc_date))
summary(lm(roll_mean_pol ~ spend_in_hund + rachel_ind , pol_inc_date))
summary(lm(polarity ~ spend_in_hund + rachel_ind , pol_inc_date))

email_human <- function(email){
  strsplit(as.character(email), " <")[[1]][1]
}
email_sent$human <- sapply(as.character(email_sent$recipient), email_human)
justin_emails <- subset(email_sent, grepl("Gaines", recipient))
email_sent$justin_gaines_ind <- grepl("Gaines", email_sent$recipient)
email_sent$rachel_ind <- email_sent$human=="Rachel Ruben"
summary(lm(polarity ~ justin_gaines_ind + rachel_ind, email_sent))
summary(lm(polarity ~ recipient, email_sent))
pol_by_guy <- aggregate(polarity ~ human, email_sent, mean)
pol_by_guy <- pol_by_guy[order(-pol_by_guy$polarity),]

head(spend)
spend_by_desc <- aggregate(Amount ~ Description, spend, sum)
spend_by_cat <- aggregate(Amount ~ Category, spend, sum)
sum(subset(spend_by_desc, grepl("Uber", Description))$Amount)

uncat <- subset(spend, Category=="Uncategorized")
rest <- subset(spend, Category=="Restaurants")
