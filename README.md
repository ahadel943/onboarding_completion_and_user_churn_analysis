# **Onboarding Completion & User Churn Analysis**
## **One Question Projects — Project 04** 

## **Project Overview**
This project analyzes whether users who complete the onboarding process show different churn behavior compared with users who do not complete onboarding. Using user signup information, onboarding status, and daily activity records, the analysis investigates user engagement patterns and identifies meaningful inactivity gaps between active days. Since churn is not directly provided in the dataset, the project develops an inactivity-based churn definition by studying the distribution of users’ activity gaps and selecting a reasonable churn threshold. The analysis then compares churn rates between onboarding completion segments to identify whether onboarding completion is associated with user retention. The findings are intended to support product and growth teams in understanding onboarding performance and identifying potential opportunities to improve early user engagement and retention.

## **Business Problem**
The product team wants to understand whether completing the onboarding process is associated with lower user churn. Although onboarding is designed to help users understand and start using the product, the business does not yet know whether users who complete it remain active for longer or return more consistently than users who do not complete it. The available data does not contain a predefined churn indicator, so the business also needs a data-driven way to define churn based on users’ inactivity patterns. By analyzing activity gaps and comparing churn rates between onboarding completion segments, the project aims to identify whether onboarding completion is associated with user retention and whether onboarding may represent an area for improving user engagement.

## **Project Goal**
The goal of this project is to develop a data-driven, inactivity-based churn definition and use it to examine the relationship between onboarding completion and user retention. The analysis will measure users’ activity patterns, calculate gaps between active days, study the gap distribution, and select a reasonable inactivity threshold for identifying churned users. It will then compare churn rates between users who completed onboarding and those who did not, while clearly distinguishing association from causation. The final outcome is to provide actionable insights into onboarding performance and potential opportunities to improve user engagement and retention.

## **Dataset Description**
The dataset contains user profiles, onboarding completion details, and daily user activity records, including activity dates and session counts, used to analyze engagement patterns and inactivity-based churn.

**users.csv**<br>
Contains basic user-level information.

| Column        | Description                        |
| ------------- | ---------------------------------- |
| `user_id`     | Unique identifier for each user    |
| `signup_date`    | Date the user signed up|
| `country`       | User’s country              |
| `platform` | Platform used by the user      |
| `acquisition_channel` | Channel through which the user was acquired|

**onboarding.csv**<br>
Contains onboarding progress and completion information for each user.

| Column        | Description                        |
| ------------- | ---------------------------------- |
| `user_id`     | Unique identifier for each user    |
| `onboarding_started_date`    | Date the user started onboarding|
| `onboarding_completed_date`       | Date the user completed onboarding|
| `onboarding_completed` | Indicates whether onboarding was completed|
| `steps_completed` | Number of onboarding steps completed|

**user_activity.csv**<br>
Contains daily user activity records.

| Column        | Description                        |
| ------------- | ---------------------------------- |
| `user_id`     | Unique identifier for each user    |
| `activity_date`    | Date the user was active|
| `sessions`       | Number of sessions recorded for the user on that date|

## **Dataset Scope**
The dataset covers user activity throughout **2025**, including user profiles, onboarding progress, and daily activity records. Each user may have multiple activity dates with gaps between periods of activity.

## **Business Question**
### **Does onboarding completion reduce churn?**
