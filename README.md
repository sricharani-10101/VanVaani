# VanVaani
## An AI-Powered Decision Support System for Forest Rights Act (FRA) Monitoring
### Introduction

The Forest Rights Monitoring System is a technological device that was created to follow up on forest rights claims of those who rely on forest resources. It allows for more convenient and organized information storage which can be used for monitoring the status of claims and improving transparency of forest rights implementation. 

The program employs the use of data visualization and interactive dashboards to convey pertinent information in an uncomplicated and digestible way. This allows relevant authorities to identify outstanding claims, conduct regional studies and facilitate the process of decision-making. 

In fact, the purpose of the project is to utilize technology for achieving more effective, transparent and accessible monitoring of forest rights while also improving management of forest rights and users of forest resources.

## Link to our website- https://create-forest-rights-monitoring-mor5s1g7a-do-ra-raa.vercel.app  

# 📌 Problem Statement
The Forest Rights Act (FRA) mandates that people manage information about forest rights claims, approvals, rejections, pending applications and land records.

This information is available in disparate, difficult to analyse formats in a district level. This makes it challenging for administrators and decision makers to identify:

•⁠  ⁠The districts that require urgent attention

•⁠  ⁠A high volume of pending cases

•⁠  ⁠Patterns or irregularities in the data

•⁠  ⁠Insights on the implementation status of the FRA

VanVaani offers a solution that consolidates data, analytics, mapping, anomaly detection and explanations via AI based insights that can help improve decision making and implementation of the FRA. 

# 🎯 Objective
The objective of developing VanVaani is to present simplified and interpretable information from complex data of FRA. Vanvaani helps to make the data of FRA speak by converting it into a form in which even a common man or a district officer can understand and take it seriously. It aims to convey the message of the FRA in a way that a claim record is understood more quickly in a tenth of the time required previously. The objectives include:

Visualizing the implementation of the FRA on an interactive map,

tracking progress on claims in select districts,

highlighting delinquent claims and identifying patterns,

spotlighting inconsistencies and anomalies like delayed claims and discrepancies in land records,

presenting the data in easily digestible formats such as graphs, statistics and risk scores,

and using artificial intelligence to explain anomalies in the information and intends to facilitate expeditious decision-making.

# 💡 Idea overview

VanVaani tackles the problem from a data-heavy approach. We think about FRA monitoring as a pipeline: from raw data to processed insights and finally to a presentation that allows making informed decisions.
Below are the main ideas for building such a system:

1. Collecting and structuring the data: This is probably the hardest part that requires domain-specific knowledge. Since there are currently no complete public datasets for FRA our prototype will utilize a self-made database of claim records with realistic data visualized on the real-world districts of Madhya Pradesh . The dataset should include claim ID, state, district, status, date of claim submission, date of approval, area claimed, area recorded in the forest account, etc.

3.  Analysis: Calculating aggregate statistics such as the total number of claims, approved, pending, or rejected claims with a particular focus on processing time.

4.  Visualization: an interactive WebGIS map of Madhya Pradesh with districts colored by risk level (low, medium, high).

5.  Anomalies detection: The prototype will include a limited set of rule-based anomaly detection algorithm to automatically flag concerning claims.

6.  Explanation: For each flagged claim there should be an option to review it with an automatic explanation of why it was flagged.

7. Dashboard: Finally the analysis results and visualization should be put together in a form of a dashboard that allows non-expert users to quickly grasp the situation with FRA claims in the region.

# 🧠 Decisions Made
1. Clearly Labelled Simulated Data – Since machine-readable district-level FRA claim data is not readily available we use self-generated data clearly labelled as (SIMULATED_DEMO_DATA) with visible demo disclaimers.

2. Real Maps, Prototype Data – Real district boundaries are combined with simulated claim data to demonstrate a realistic working prototype with future potential for real data integration.

3. Focus Over Breadth – The prototype focuses on one state and approximately 15 districts rather than attempting shallow nationwide coverage.

4. Rules Detect, Humans Explain – Anomalies are identified using rule-based and statistical methods, making the findings easier to interpret, audit, and explain.

5. Python-First Development – The system is primarily built using Python, the team's strongest and most familiar programming language.

6. Independent Module - The project is divided into five independent modules, making it easier to develop, test, debug, and integrate.

7. Open and Accessible Mapping – Leaflet.js and OpenStreetMap are used to keep the prototype simple, accessible, and free from unnecessary sign-ups or proprietary dependencies.

8. Explain, Don't Overwhelm – Maps, graphs, colour indicators, and simple summaries are prioritized over large tables to communicate important insights quickly.

#  🗺️Features
The application includes an Interactive WebGIS Map displaying FRA-related information
 Users can navigate within the map area:
zoom in or zoom out, select districts, see relevant FRA information at a district level, assess risk level visually.

 FRA claim monitoring
Keeping track of essential claim statistics such as total, approved, pending, or rejected claims.

 Anomalies detection
Automated detection of irregularities in claims processing, such as delayed claims, land record mismatches, inconsistent dates, unusual claim rejections or approvals.

 Risk-based visualization
Each district is colour coded according to its risk level 🟢 Low, 🔡 Medium, and 🔴 High Risk making it easy to see at a glance.

 Explainable AI
All detected anomalies have a simple description so that the user has an idea of what might be wrong in a particular claim or district.

 Decision-making dashboard
A dashboard view displaying fundamental FRA implementation insights including district statistics, performance indicators, anomalies detected, allows for quick assessment of the FRA implementation at a district level and detection of areas requiring attention.

# ⚙️ Tools Used/ Techstach
Back end and data: Python, Flask, Pandas, JSON
Front end: HTML, CSS, JavaScript
Mapping: Leaflet.js, GeoJSON, OpenStreetMap
Anomaly detection: Rules/statistical tests, AI(LLM) for explanations
Dev and collaboration tools: Visual Studio Code, Git, GitHub

# ⚠️ Limitations
VanVaani is currently developed as a prototype, so there are a few limitations. 
1. Prototype Data- Current version of the system uses mock or self generated data where complete and structured FRA datasets are not publicly available. Therefore the statistics displayed are for demonstration and should not be treated as official records.

2. Limited geographic coverage- Current prototype is focused on select districts of Madhya Pradesh and is not yet available across the country.

3. Rule based anomaly detection- Anomaly detection is currently done using rule-based systems and statistical thresholds. More complex patterns require deployment of more advanced machine learning models and large scale real world data.

4. Data availability and quality- The value and effectiveness of the system will directly depend on the quality and availability of FRA and land record data.

5. AI is an assistant, not a decision maker- Explanations generated by AI are meant to help the user and alert them to potential issues. Final calls to action and decisions should always be made by the relevant officials and experts.

# 💡 Scope in Future
1. Scale-up from MP to other FRA implementing states, and ultimately nationwide.

2. Connect to a real, live data source of FRA (state portals, data.gov.in or Bhuvan) once available in machine readable form.

3. A proper choropleth map would replace district-center points with actual boundary polygons.

4. Replace rule-based flagging with a trained ML/anomaly detection model on real historical claims.

5. Utilise satellite/remote sensing data to confirm claimed land against actual forest cover and land use change.

6. Add smart alerts – automatically alert officials when a district moves into high-risk territory or claims sit pending past a threshold.

7. Add ability to have role based access And Exportable Reports.

8. A mobile app for on-ground verification and anomaly reporting facing the field.

# 🌿 Conclusion
_VanVaani is a project aimed at making the monitoring process of Forest Rights Act (FRA) more natural, comprehensible, and informed. The whole idea sprouted from a very simple question — why is it so hard to get information about what is really going on with the implementation of FRA? By combining maps, analytics, detection of anomalies, and AI interpreters, VanVaani converts different sets of claims data into a simple and usable tool for decision-making._

_At this point, however, it is still just a prototype. The software is based on simulation data for a certain state and is operating on a set of rules rather than a machine learning model._

_The takeaway message is straightforward — **better visibility leads to better decision-making** ._
