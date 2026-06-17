#!/bin/bash

# To stop the script as soon as an error occurs
set -e

echo "Enter github token to update or leave blank to use existing"
read token

if [ -n "$token" ];then
  export github_token=$token
  echo export github_token=$token >> ~/.bashrc
  source ~/.bashrc
  else
    echo "Using the existing github token"
fi

echo "## Pulling latest code"
git stash
expect << PG
spawn git pull
expect "Username"
send "prateekgupta25apr\r"
expect "Password"
send "$github_token\r"
expect eof
PG
echo "## done!!"

echo "## Restarting supervisor"
sudo supervisorctl restart portfolio
echo "## done!!"

echo "## Restarting nginx"
sudo systemctl restart nginx
echo "## done!!"

echo ""
echo "All done!!"