chmod 600 ~/.ssh/mids210.pem
ssh -i ~/.ssh/mids210.pem ubuntu@ec2-52-11-236-0.us-west-2.compute.amazonaws.com
scp -i ~/.ssh/mids210.pem ubuntu@ec2-52-11-236-0.us-west-2.compute.amazonaws.com:~/personal_budget/some_tweets.pickle ~/Desktop/MIDS/
scp -i ~/.ssh/mids210.pem ubuntu@ec2-52-11-236-0.us-west-2.compute.amazonaws.com:~/personal_budget/some_tweets.pickle ~/Desktop/MIDS/