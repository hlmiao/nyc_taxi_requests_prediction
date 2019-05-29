#!/bin/sh

sudo yum install tree -y

sudo -u ec2-user -i <<'EOF'

# This will affect only the Jupyter kernel called "conda_python3".
source activate python3

# Replace myPackage with the name of the package you want to install.
python3 -m pip install geopandas xgboost lightgbm descartes pykerberos
# You can also perform "conda install" here as well.

source deactivate

EOF
