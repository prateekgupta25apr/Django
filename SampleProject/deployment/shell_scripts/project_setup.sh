#!/bin/bash

# To stop the script as soon as an error occurs
set -e

echo "## Setting variables"
# Getting base directory path using the BASH_SOURCE variable
base_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && cd .. && pwd)"
public_ip=$(curl -s ifconfig.me)
db_username=pg
db_password=Pg#25Pg#25
db_schema_name=sample_project_1
db_schema_prefix=sample_project_
context_path=sample_project
echo "## done!!"

echo "## Installing applications"
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
sudo apt install nginx mysql-server expect supervisor -y
echo "## done!!"

echo "## Starting mysql server"
sudo systemctl start mysql
echo "## done!!"


echo "## Running MySQl Security Script"
expect << 'EOF'
set timeout 10

# Start the mysql_secure_installation command with sudo
spawn sudo mysql_secure_installation

expect {
    "Press y|Y for Yes, any other key for No:" {
        send "y\r"
        exp_continue
    }
    "Please enter 0 = LOW, 1 = MEDIUM and 2 = STRONG:" {
        send "1\r"
        exp_continue
    }
    "Remove anonymous users?" {
        send "y\r"
        exp_continue
    }
    "Disallow root login remotely?" {
        send "n\r"
        exp_continue
    }
    "Remove test database and access to it?" {
        send "y\r"
        exp_continue
    }
    "Reload privilege tables now?" {
        send "y\r"
    }
}

expect eof
EOF
echo "## done!!"

echo "## Making MySQL publicly accessible"
sudo touch /etc/mysql/mysql.conf.d/public.cnf
echo "[mysqld]" >> /etc/mysql/mysql.conf.d/public.cnf
echo "bind-address = 0.0.0.0" >> /etc/mysql/mysql.conf.d/public.cnf
sudo systemctl restart mysql
echo "## done!!"

echo "## Creating default user"
sudo mysql -e "CREATE USER '$db_username'@'%' IDENTIFIED BY '$db_password';"
sudo mysql -e "Grant ALL PRIVILEGES on *.* to '$db_username'@'%';"
sudo mysql -e "flush privileges;"
echo "## done!!"

echo "## Initializing DB"
sudo mysql -e "create schema $db_schema_name;"
echo "## done!!"

echo "## Base Directory : $base_dir"
echo "## Public IP of the system : $public_ip"

echo '## Creating configuration.properties file'
cat > $base_dir/configuration.properties << EOF
context_path=$context_path
base_url=http://localhost:4200/
api_url=http://localhost:8000/

db_host=$public_ip
db_user_name=$db_username
db_password=$db_password
db_default_schema=$db_schema_name
db_schema_prefix=$db_schema_prefix

cookie_validation=true
cookie_name = prateek_gupta_sample_project
cookie_secret = PrateekGupta@250499@PrateekGupta

EOF
echo "## done!!"

echo '## Creating project_settings.py file'
cat > $base_dir/prateek_gupta/project_settings.py<< EOF
local = False
console_logs = False
configuration_properties_file_path = "$base_dir/configuration.properties"
context_path = ""
required_fields = [
    "context_path",
    "base_url",
    "api_url",
    "db_host",
    "db_user_name",
    "db_password",
    "db_default_schema",
    "db_schema_prefix",
    "cookie_name",
    "cookie_secret"
]
expected_fields = []
EOF
echo "## done!!"

echo "## Creating Virtual Environment"
sudo python3 -m venv $base_dir/venv
echo "## done!!"

echo "## Setting up prerequisites for MySQL Connector"
sudo apt install -y pkg-config libmysqlclient-dev build-essential
export MYSQLCLIENT_CFLAGS=$(mysql_config --cflags)
export MYSQLCLIENT_LDFLAGS=$(mysql_config --libs)
echo "## done!!"

echo "## Installing python dependencies"
sudo $base_dir/venv/bin/pip install -r $base_dir/requirements.txt
echo "## done!!"

#echo "## Installing python dependencies for prateek_gupta"
#sudo $base_dir/venv/bin/pip install -r $base_dir/prateek_gupta/requirements.txt
#echo "## done!!"

#echo "## Setting up the database"
#sudo $base_dir/venv/bin/python3 $base_dir/manage.py migrate
#echo "## done!!"

echo "## Migrating data"
sudo $base_dir/venv/bin/python3 $base_dir/manage.py loaddata $base_dir/db_back_up.json
echo "## done!!"

#echo "## Setting up the static files"
#sudo $base_dir/venv/bin/python3 $base_dir/manage.py collectstatic
#echo "## done!!"

echo '## Starting supervisor'
sudo tee -a /etc/supervisor/supervisord.conf > /dev/null <<EOF
[program:portfolio]
command=$base_dir/venv/bin/python3 $base_dir/uvicorn_config.py
directory=$base_dir
autostart=true
autorestart=true
stdout_logfile=$base_dir/logs/logs.log
stderr_logfile=$base_dir/logs/logs.log
environment=PATH="$base_dir/venv/bin:%(ENV_PATH)s"
user=root
EOF

sudo service supervisor start
sudo supervisorctl reread
sudo supervisorctl update
echo "## done!!"

echo '## Starting Nginx'
sudo systemctl start nginx
sudo mkdir /etc/systemd/system/nginx.service.d
cat > /etc/systemd/system/nginx.service.d/nginx-service.conf << EOF
[Service]
ExecStartPre=
ExecStartPre=/usr/sbin/nginx -t -c $base_dir/nginx/nginx.conf
ExecStart=
ExecStart=/usr/sbin/nginx -c $base_dir/nginx/nginx.conf
EOF
sudo systemctl daemon-reload
sudo systemctl restart nginx
echo "## done!!"

echo ""
echo "All done!! Now please update Route53 for matching the domain with the IP : $public_ip"


