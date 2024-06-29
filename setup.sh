#!/bin/bash

# Check if python3 is installed
if ! command -v python3 &> /dev/null; 
then
    echo "python3 is not installed. Please install python3 and try again.";
    exit 1;
fi


# Check if pip is installed (pipx, brew, etc.)
if ! command -v pip3 &> /dev/null; 
then
    echo "pip3 is not installed. Please install pip3 and try again.";
    exit 1;
fi


# Check if redis-server is installed (if not exit)
if ! command -v redis-server &> /dev/null; 
then
    echo "redis-server is not installed. Please install redis-server and try agian.";
    exit 1;
fi


# Install packages (pip3 install -r requirements.txt)
echo "Installing packages";
if ! pip3 install -r requirements.txt ; then
    echo "Error install packages. Likely there is another package manager installed";
    echo "which is preventing pip3 from installing the packages. If you want to continue";
    echo "installing packages run 'pip3 install -r requirements.txt --break-system-packages'.";
    exit 1;
else
    echo "Packages are successfully installed";
fi

# Setting environment variables
RANDOM_KEY=""
if command -v openssl &> /dev/null;
then 
    RANDOM_KEY=$(openssl rand -base64 12 | tr -dc A-Za-z0-9 | head -c 16);
else
    RANDOM_KEY="%R4nD0M_K3y&";
fi

export APP_SECRET_KEY=$RANDOM_KEY;
export ENV="DEV";
export REDIS_URL="redis://localhost:6379";


# EOF