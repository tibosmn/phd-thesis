#!/bin/bash
for year in {1995..2022}
do
   echo "$year"
   wget "https://zenodo.org/records/5589597/files/IOT_${year}_ixi.zip"
done