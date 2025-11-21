# SkillCorner X PySport Analytics Cup - Stuart Macfarlane - Analyst Track

This main. branch of the repositorty does contain a small sample of data extracted from my full full dataset which is fully download from the SkillCorner x PySport public repository. This samnple is only used to speed up loading and processing for the Streamlit web application as loading, processing, computing and visualising was too computationally expensive during user interaction with the app. 

#### Introduction
Data analytics has undoubtedly revolutionised the way professional clubs operate in many aspects of business. This is especially true in terms of player recruitment when analytics can play an important role in identifying future potential talent and signings. Despite the exponential development of data analytics in football in recent years, a significant challenge has been to capture defensive off-the-ball behaviour which could be considered a crucial key performance indicator.

	Previous approaches have utilised methods such as pitch control, a physics-based model, to determine how teams control space both in and out of possession (Spearman, 2018). The pitch control model has had a significant impact on the way teams approach tactical systems and has undoubtedly influenced football analytics in a positive manner. Whilst pitch control provides insight into team shape and cohesion, it is difficult to determine each player’s contribution to this. Therefore, the aim of this project was to develop a defensive metric which could quantify how much space a defending player ‘squeezes’ to minimise passing and dribbling opportunities for the opposition. 
    
	The approach to this task involved computing individual convex hull surface areas between the 3 closest teammates per player/ per frame when defending (only). The hypothesis of this research was that players with a lower surface area (and consequently team) would result in less attacking actions conceded. The results of this research are shown below. Figure 1 shows a strong correlation between low convex hull surface area and line breaking passes conceded at team level. Figure 2 shows an example of how these results could be applied in practical coaching setting. Furthermore, by quantifying this skill, it could be used in a holistic player evaluation process for recruitment purposes. Future research could expand the dataset and explore further data validation.

<img width="1015" height="745" alt="image" src="https://github.com/user-attachments/assets/8078b850-dc92-4420-a9d2-d3a4ed9bef8e" />
**Figure 1.**
<img width="1126" height="818" alt="image" src="https://github.com/user-attachments/assets/04c97bf1-18e1-4409-af7a-f0e1332ead8e" />
**Figure 2.**

#### Usecase(s)
This new defensive metric could be used as part of a hollistic evaluation process for player recruitment. By combining this metric with on-ball defensive and in-possession metrics, the quality of playern analysis could be significantly enhanced. Furthermore, the type of tool demonstrated in the Streamlit app could be used as a coaching cue to aid player tactical understanding and development. However, it should be noted that further validation is required. 

#### Potential Audience
Recruitment analysts, scouts, video analysts, data analysts and coaches.

## Video URL

https://drive.google.com/file/d/1PAh0WwIu_ubbCNVhgnz1esFhZaN1jZqN/view?usp=sharing

## Run Instructions
The code in the main submission assumes the github repository was cloned as per the guidelines provided. The code should begin processing without error using Kloppy. The pipeline loads, processes, smoothes and computes the tracking data from all 10 matches. Given the size of the tracking dataset and the computational cost of the methods involved in this project, the full pipeline takes around 4 hours to complete. This is a limitation to the overall project. 

The streamlit app has been deployed on the public Streamlit community cloud and is avaiable via then link below. The app takes some time to load when experimenting with different user selections but demonstrates the practical application of the results produced in this project. If running the Streamlit app locally, the 'skillcorner_x_pysport_events_with_phases_sample.parquet' and 'skillcorner.py' files must be downloaded. In you machine terminal, you should change to the working directory where the files are stored and follow these instructions:

cd 'your_file_path'

streamlit run skillcorner.py

The requirementr.txt file details the required Python modules and packages

## [Optional] URL to Web App / Website
https://analyticscupanalyst-k8nietzb6sza5pqne5jh92.streamlit.app/
