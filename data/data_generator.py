import numpy as np
import pandas as pd
from pathlib import Path

# =========================================================
# 1. Configuration
# =========================================================

SEED = 42
rng = np.random.default_rng(SEED)

N_USERS = 100_000

START_DATE = pd.Timestamp("2025-01-01")
END_DATE = pd.Timestamp("2025-12-31")

OUTPUT_DIR = Path("onboarding_churn_dataset")
OUTPUT_DIR.mkdir(exist_ok=True)


# =========================================================
# 2. Users
# =========================================================

user_ids = [f"U{i:06d}" for i in range(1, N_USERS + 1)]

date_range = pd.date_range(START_DATE, END_DATE, freq="D")

signup_dates = rng.choice(
    date_range,
    size=N_USERS
)

countries = [
    "Egypt",
    "Saudi Arabia",
    "UAE",
    "Jordan",
    "Kuwait"
]

country_probs = [
    0.25,
    0.22,
    0.20,
    0.18,
    0.15
]

platforms = [
    "Mobile",
    "Web",
    "Tablet"
]

platform_probs = [
    0.65,
    0.30,
    0.05
]

acquisition_channels = [
    "Organic Search",
    "Paid Search",
    "Social Media",
    "Direct",
    "Referral"
]

acquisition_probs = [
    0.25,
    0.18,
    0.20,
    0.22,
    0.15
]

users = pd.DataFrame({
    "user_id": user_ids,
    "signup_date": signup_dates,
    "country": rng.choice(
        countries,
        size=N_USERS,
        p=country_probs
    ),
    "platform": rng.choice(
        platforms,
        size=N_USERS,
        p=platform_probs
    ),
    "acquisition_channel": rng.choice(
        acquisition_channels,
        size=N_USERS,
        p=acquisition_probs
    )
})

users = users.sort_values("signup_date").reset_index(drop=True)


# =========================================================
# 3. Onboarding
# =========================================================

onboarding = users[["user_id", "signup_date"]].copy()

# Probability of completing onboarding
# Slightly influenced by platform and acquisition channel

completion_probability = np.full(N_USERS, 0.62)

completion_probability += np.where(
    users["platform"].values == "Web",
    0.04,
    0
)

completion_probability += np.where(
    users["platform"].values == "Tablet",
    -0.04,
    0
)

completion_probability += np.where(
    users["acquisition_channel"].values == "Referral",
    0.05,
    0
)

completion_probability += np.where(
    users["acquisition_channel"].values == "Paid Search",
    -0.03,
    0
)

completion_probability = np.clip(
    completion_probability,
    0.35,
    0.80
)

onboarding_completed = (
    rng.random(N_USERS) < completion_probability
)

# How many steps were completed
total_steps = 5

steps_completed = np.zeros(N_USERS, dtype=int)

completed_mask = onboarding_completed
not_completed_mask = ~onboarding_completed

# Completed users finish all steps
steps_completed[completed_mask] = total_steps

# Users who did not complete onboarding stop at 1-4 steps
steps_completed[not_completed_mask] = rng.integers(
    1,
    total_steps,
    size=not_completed_mask.sum()
)

# Some users complete onboarding on signup day,
# others take several days.
completion_delay = rng.choice(
    [0, 1, 2, 3, 4, 5, 6, 7],
    size=N_USERS,
    p=[0.10, 0.18, 0.20, 0.18, 0.14, 0.10, 0.06, 0.04]
)

onboarding_started_date = (
    onboarding["signup_date"] +
    pd.to_timedelta(
        rng.choice(
            [0, 1],
            size=N_USERS,
            p=[0.90, 0.10]
        ),
        unit="D"
    )
)

onboarding_completed_date = pd.Series(
    pd.NaT,
    index=onboarding.index,
    dtype="datetime64[ns]"
)

onboarding_completed_date.loc[completed_mask] = (
    onboarding.loc[completed_mask, "signup_date"]
    + pd.to_timedelta(
        completion_delay[completed_mask],
        unit="D"
    )
)

onboarding["onboarding_started_date"] = onboarding_started_date
onboarding["onboarding_completed_date"] = onboarding_completed_date
onboarding["onboarding_completed"] = onboarding_completed.astype(int)
onboarding["steps_completed"] = steps_completed

onboarding = onboarding[
    [
        "user_id",
        "onboarding_started_date",
        "onboarding_completed_date",
        "onboarding_completed",
        "steps_completed"
    ]
]


# =========================================================
# 4. Generate User Activity
# =========================================================

# Important:
# We generate activity based on user behavior.
#
# Onboarding completion increases engagement probability,
# but does NOT guarantee retention.
#
# This creates a realistic relationship:
#
# Completed onboarding -> generally stronger engagement
# Not completed       -> generally weaker engagement
#
# But there is still overlap between the groups.

activity_records = []

# Convert signup dates to numpy datetime64 for faster processing
signup_array = users["signup_date"].values
onboarding_completed_array = onboarding["onboarding_completed"].values
completion_dates_array = onboarding["onboarding_completed_date"].values

for i in range(N_USERS):

    user_id = user_ids[i]
    signup_date = pd.Timestamp(signup_array[i])

    completed = onboarding_completed_array[i] == 1

    if completed:
        # Better early engagement
        base_activity_probability = 0.58

        # More sessions on active days
        session_lambda = 2.2

        # Lower churn tendency
        churn_probability = 0.035

    else:
        # Weaker engagement
        base_activity_probability = 0.40

        session_lambda = 1.5

        # Higher churn tendency
        churn_probability = 0.075

    # -----------------------------------------------------
    # Individual behavioral variation
    # -----------------------------------------------------

    user_engagement = rng.normal(1.0, 0.18)

    base_activity_probability *= user_engagement

    base_activity_probability = np.clip(
        base_activity_probability,
        0.15,
        0.85
    )

    # -----------------------------------------------------
    # Determine approximate churn point
    # -----------------------------------------------------

    # Some users never churn during the observable period.
    churned = rng.random() < churn_probability

    if churned:

        # Churn tends to happen relatively early,
        # but not immediately for everyone.
        churn_day = int(
            rng.gamma(
                shape=2.5,
                scale=18
            )
        )

        churn_day = max(7, min(churn_day, 180))

        churn_date = signup_date + pd.Timedelta(
            days=churn_day
        )

    else:
        churn_date = END_DATE + pd.Timedelta(days=1)

    # -----------------------------------------------------
    # Generate daily activity
    # -----------------------------------------------------

    user_end_date = min(
        churn_date,
        END_DATE
    )

    if user_end_date < signup_date:
        continue

    activity_dates = pd.date_range(
        signup_date,
        user_end_date,
        freq="D"
    )

    for activity_date in activity_dates:

        days_since_signup = (
            activity_date - signup_date
        ).days

        # -------------------------------------------------
        # Lifecycle decay
        # -------------------------------------------------

        decay = np.exp(
            -days_since_signup / 180
        )

        probability = (
            base_activity_probability
            * (0.70 + 0.30 * decay)
        )

        # -------------------------------------------------
        # Onboarding effect
        # -------------------------------------------------

        if completed:

            # After onboarding completion,
            # engagement gets a small boost.

            completion_date = pd.Timestamp(
                completion_dates_array[i]
            )

            if activity_date >= completion_date:

                probability *= 1.20

        else:

            # Users who haven't completed onboarding
            # gradually become less engaged.

            probability *= 0.92

        probability = np.clip(
            probability,
            0.03,
            0.90
        )

        # -------------------------------------------------
        # Determine whether user was active
        # -------------------------------------------------

        is_active = rng.random() < probability

        if not is_active:
            continue

        # -------------------------------------------------
        # Number of sessions
        # -------------------------------------------------

        sessions = max(
            1,
            int(
                rng.poisson(
                    session_lambda
                )
            )
        )

        activity_records.append(
            (
                user_id,
                activity_date,
                sessions
            )
        )


# =========================================================
# 5. Build Activity DataFrame
# =========================================================

user_activity = pd.DataFrame(
    activity_records,
    columns=[
        "user_id",
        "activity_date",
        "sessions"
    ]
)

user_activity["activity_date"] = pd.to_datetime(
    user_activity["activity_date"]
)

user_activity = user_activity.sort_values(
    ["user_id", "activity_date"]
).reset_index(drop=True)


# =========================================================
# 6. Save CSV files
# =========================================================

users.to_csv(
    OUTPUT_DIR / "users.csv",
    index=False
)

onboarding.to_csv(
    OUTPUT_DIR / "onboarding.csv",
    index=False
)

user_activity.to_csv(
    OUTPUT_DIR / "user_activity.csv",
    index=False
)


# =========================================================
# 7. Basic Validation
# =========================================================

print("\nDataset generated successfully.\n")

print("Users:")
print(users.shape)

print("\nOnboarding:")
print(onboarding.shape)

print("\nUser Activity:")
print(user_activity.shape)

print("\nOnboarding completion rate:")
print(
    f"{onboarding['onboarding_completed'].mean() * 100:.2f}%"
)

print("\nActivity date range:")
print(
    user_activity["activity_date"].min(),
    "to",
    user_activity["activity_date"].max()
)

print("\nAverage sessions per active day:")
print(
    round(
        user_activity["sessions"].mean(),
        2
    )
)

print("\nFiles saved to:")
print(OUTPUT_DIR.resolve())