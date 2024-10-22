#!/bin/bash

START_DATE=$(date -u --rfc-3339=seconds --date '-1 min'| sed 's/ /T/')
echo $START_DATE

################
# LAUNCH TESTS #
################

# Read users timelines

THREADS=1
CONNECTIONS=10
RATE=100

# THREADS=10
# CONNECTIONS=100
# RATE=1000000

# THREADS=4
# CONNECTIONS=100
# RATE=200

REPEATS=110

# Convert 1m and 5m to seconds (60 seconds in 1 minute)
MIN_DURATION=120    # 1m in seconds
MAX_DURATION=300   # 5m in seconds

for ((i=1; i<=REPEATS; i++))
do
    ./deathstarbench/DeathStarBench/wrk2/wrk -D exp -t $THREADS -c $CONNECTIONS -d 1m -L -s deathstarbench/DeathStarBench/socialNetwork/wrk2/scripts/social-network/mixed-workload.lua http://social.kubernetes/wrk2-api/ -R $RATE

    THREADS=$((THREADS + 1))
    CONNECTIONS=$((CONNECTIONS + 10))
    RATE=$((RATE + 100))
done

# for ((i=1; i<=REPEATS; i++))
# do
#     # Generate a random number between MIN_DURATION and MAX_DURATION
#     RANDOM_DURATION_MIN=$(((MIN_DURATION + RANDOM % (MAX_DURATION - MIN_DURATION + 1)) / 60))m

#     # Compose posts
#     ./deathstarbench/DeathStarBench/wrk2/wrk -D exp -t $THREADS -c $CONNECTIONS -d $RANDOM_DURATION_MIN -L -s deathstarbench/DeathStarBench/socialNetwork/wrk2/scripts/social-network/compose-post.lua http://social.kubernetes/wrk2-api/post/compose -R $RATE

#     # Read home timelines
#     RANDOM_DURATION_MIN=$(((MIN_DURATION + RANDOM % (MAX_DURATION - MIN_DURATION + 1)) / 60))m
#     ./deathstarbench/DeathStarBench/wrk2/wrk -D exp -t $THREADS -c $CONNECTIONS -d $RANDOM_DURATION_MIN -L -s deathstarbench/DeathStarBench/socialNetwork/wrk2/scripts/social-network/read-home-timeline.lua http://social.kubernetes/wrk2-api/home-timeline/read -R $RATE

#     # Read user timelines
#     RANDOM_DURATION_MIN=$(((MIN_DURATION + RANDOM % (MAX_DURATION - MIN_DURATION + 1)) / 60))m
#     ./deathstarbench/DeathStarBench/wrk2/wrk -D exp -t $THREADS -c $CONNECTIONS -d $RANDOM_DURATION_MIN -L -s deathstarbench/DeathStarBench/socialNetwork/wrk2/scripts/social-network/read-user-timeline.lua http://social.kubernetes/wrk2-api/user-timeline/read -R $RATE
    
#     # Mixed_workload
#     RANDOM_DURATION_MIN=$(((MIN_DURATION + RANDOM % (MAX_DURATION - MIN_DURATION + 1)) / 60))m
#     ./deathstarbench/DeathStarBench/wrk2/wrk -D exp -t $THREADS -c $CONNECTIONS -d $RANDOM_DURATION_MIN -L -s deathstarbench/DeathStarBench/socialNetwork/wrk2/scripts/social-network/mixed-workload.lua http://social.kubernetes/wrk2-api/ -R $RATE

#     sleep $RANDOM_DURATION_MIN
# done

########
# WAIT #
########

echo "Waiting $DURATION" 
sleep $DURATION

END_DATE=$(date -u --rfc-3339=seconds | sed 's/ /T/')
echo $END_DATE

#################
# RETRIEVE DATA #
#################
source venv/bin/activate
python retrieve_data.py $START_DATE $END_DATE
