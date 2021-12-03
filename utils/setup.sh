# prepare the container and install the dependencies
BASE_DIR="/"
# install the dependencies
apt-get update
apt-get -y install libnss3-tools
apt-get -y install cron
apt update
apt install -y ${BASE_DIR}/src/resources/google-chrome-stable_current_amd64.deb
pip install -r ${BASE_DIR}/requirements.txt
# modify files
mkdir ${BASE_DIR}/logs
echo "" > ${BASE_DIR}/logs/crawler.log
# Configure crontab
CRON_FILE="${BASE_DIR}/utils/update-cron"
# Give execution rights on the cron job
chmod 0644 ${CRON_FILE}
# Apply cron job
crontab ${CRON_FILE}
# Create the log file to be able to run tail
touch /var/log/cron.log