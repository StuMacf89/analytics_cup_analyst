# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 21:15:54 2025

@author: stuart.macfarlane
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from io import BytesIO
import base64
import time
from scipy.spatial import ConvexHull
from matplotlib.patches import Polygon
from streamlit_autorefresh import st_autorefresh
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

st.set_page_config(page_title="Defensive Phase Visualizer", layout="wide")

st.title("Defensive Movement Visualiser")

# --- LOAD (cached) ---

@st.cache_data(show_spinner=True)
def load_data(path: str):
    df = pd.read_parquet(path)

    
    # Check presence (optional)
    if 'position_group' not in df.columns:
        st.error("ERROR: 'position_group' column is missing from the loaded data.")
        st.stop()

    return df

DATA_PATH = "skillcorner_x_pysport_events_with_phases_sample.parquet"
df = load_data(DATA_PATH)

# --- FILTERS ---
# --- FILTERS ---
col1, col2, col3, col4, col5 = st.columns(5)

# 1️⃣ Select Match
with col1:
    match_id = st.selectbox("Select Match", sorted(df["match_id"].unique()))

match_df = df[df["match_id"] == match_id].copy()

# 2️⃣ Select Period
available_periods = sorted(match_df["period"].unique())
with col2:
    selected_period = st.selectbox("Select Period", available_periods)

period_df = match_df[match_df["period"] == selected_period].copy()

# 3️⃣ Select Defending Team
defending_df = period_df[period_df["is_defending"] == 1].copy()
defending_teams = sorted(defending_df["team_name"].dropna().unique())

with col3:
    defending_team = st.selectbox("Select Defending Team", defending_teams)

# 🔍 Filter defending events just for this team
team_def_df = defending_df[defending_df["team_name"] == defending_team].copy()

# --- CORRECT MINUTE LOGIC ---
# We find minutes where the team defends AT LEAST ONCE

period_df["minute"] = (period_df["timestamp"] // 60).astype(int)
team_def_df["minute"] = (team_def_df["timestamp"] // 60).astype(int)

# Minutes where this team defended at least once
valid_minutes = sorted(team_def_df["minute"].unique())

with col4:
    selected_minute = st.selectbox("Select Minute (defending at least once)", valid_minutes)

# 5️⃣ Select Second (only seconds where they *were defending* in that minute)
team_minute_def_df = team_def_df[team_def_df["minute"] == selected_minute].copy()
team_minute_def_df["second"] = (team_minute_def_df["timestamp"] % 60).astype(int)

valid_seconds = sorted(team_minute_def_df["second"].unique())

with col5:
    selected_second = st.selectbox("Select Second", valid_seconds)

# Safe timestamp
selected_time = selected_minute * 60 + selected_second

# --- 10-second clip (ALL players) ---
clip_df = period_df[
    (period_df["timestamp"] >= selected_time) &
    (period_df["timestamp"] <= selected_time + 10)
].copy()

# --- Active defenders in this window ---
active_defenders = team_def_df[
    team_def_df["timestamp"].between(selected_time, selected_time + 10)
]["player_name"].unique()

selected_player = st.selectbox("Select Player", sorted(active_defenders))

selected_player_id = (
    team_def_df[team_def_df["player_name"] == selected_player]["player_id"].iloc[0]
)

player_df = clip_df[clip_df["player_id"] == selected_player_id].copy()

if player_df.empty:
    st.warning("No data for this player in the selected window.")
    st.stop()

st.markdown(f"**Defending Team:** {defending_team}")

# --- FRAME RENDERING FUNCTION ---
@st.cache_data(show_spinner=False)
def render_phase_frames(phase_df, player_id):
    frames = []

    for ts, frame in phase_df.groupby('timestamp'):

        pitch = Pitch(
            pitch_type='skillcorner',
            pitch_color='white',
            line_color='black',
            pitch_length=105,
            pitch_width=68
        )
        fig, ax = pitch.draw(figsize=(8, 6))

        teams = frame['team_name'].unique()
        colors = {teams[0]: 'red', teams[1]: 'blue'}

        bx, by = frame[['ball_x_m', 'ball_y_m']].iloc[0]
        ball_team = frame['ball_owning_team'].iloc[0]

        sel = frame[frame['player_id'] == player_id]
        hull_poly = None
        hull_area = np.nan

        if not sel.empty:
            sel_x, sel_y = sel[['x_m', 'y_m']].iloc[0]
            sel_team_id = sel['team_id'].iloc[0]

            # SAFELY get position_group - handle missing or null gracefully
            if 'position_group' in sel.columns and not sel['position_group'].isnull().all():
                sel_pos = sel['position_group'].iloc[0]
            else:
                sel_pos = None

            # Only compute hull if defending + not GK
            if sel_team_id != ball_team and sel_pos != "GK":

                teammates = frame.loc[
                    (frame['team_id'] == sel_team_id) &
                    (frame['player_id'] != player_id) &
                    (frame['position_group'] != "GK"),
                    ['x_m', 'y_m']
                ].copy()

                if len(teammates) >= 3:
                    teammates['dist'] = np.sqrt(
                        (teammates['x_m'] - sel_x)**2 +
                        (teammates['y_m'] - sel_y)**2
                    )

                    nearest = teammates.nsmallest(3, 'dist')

                    points = np.vstack([
                        [sel_x, sel_y],
                        nearest[['x_m', 'y_m']].to_numpy()
                    ])

                    if len(points) >= 3:
                        hull = ConvexHull(points)
                        hull_poly = points[hull.vertices]
                        hull_area = hull.area

        if hull_poly is not None:
            ax.fill(hull_poly[:, 0], hull_poly[:, 1], color='lightblue', alpha=0.4)

        for t in teams:
            pl = frame[frame["team_name"] == t]
            ax.scatter(pl['x_m'], pl['y_m'], color=colors[t], s=60)

        ax.scatter(bx, by, color='black', s=30)

        if not sel.empty:
            ax.scatter(sel_x, sel_y, color='green', s=120, edgecolor='black')

        legend_handles = [
            Patch(color='red', label=f'Team: {teams[0]}'),
            Patch(color='blue', label=f'Team: {teams[1]}'),
            Line2D([0], [0], marker='o', color='w', label='Selected Player',
                   markerfacecolor='green', markeredgecolor='black', markersize=12)
        ]
        ax.legend(handles=legend_handles, loc='upper left')

        title = f"Timestamp {ts:.1f}s | Convex Hull: N/A" if np.isnan(hull_area) else f"Timestamp {ts:.1f}s | Convex Hull: {hull_area:.2f} m²"
        ax.set_title(title)

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)

        frames.append("data:image/png;base64," + base64.b64encode(buf.getvalue()).decode())

    return frames

# --- DISPLAY ---
st.info("Rendering frames (cached)…")
frames = render_phase_frames(clip_df, selected_player_id)

fps = st.slider("Playback speed", 1, 15, 8)
play = st.button("▶️ Play Clip")

img = st.empty()

if play:
    for f in frames:
        img.image(f)
        time.sleep(1/fps)
else:
    img.image(frames[0])