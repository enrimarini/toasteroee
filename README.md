# FOSS Tulip Alternative using MQTT and Streamlit
This project serves to show the power of modern Free Open Source Software (FOSS) technology by replicating the machine and app development features of the low-code as a platform (LCAP) product called Tulip. 

## Architecture Diagram

![image](https://github.com/enrimarini/toasteroee/assets/98195595/906505b4-e84b-4be4-8e61-36f728c55932)

## Overview
We capture the value of electrical current and send its value to a broker using flat MQTT. A separate python script serves to pre-process the raw edge data and send it back to the broker as a new topic formatted as a JSON object. 

Then Streamlit is used to build an OEE pie-chart to show the percentage of time that the ‘ON’ machine state condition is met versus the ‘OFF’ condition. 

The aggregate OEE pie chart feature and single bar chart showing a 1-hour timeline of the machine state can readily be used in other Streamlit projects. This project demonstrates the power of FOSS LCAP technologies and their superiority over Commercial Off-The-Shelf (COTS) software by being able to directly create custom features in the LCAP product through injection of code rather than having to struggle with cumbersome GUI and menus. 
