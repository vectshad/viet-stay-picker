"""
votes.py — Supabase voting helpers for Stay Picker
"""
import streamlit as st
from supabase import create_client, Client

VOTERS = ["ekong", "adel", "riri", "alfa", "aldi"]


@st.cache_resource
def _client() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


@st.cache_data(ttl=20)
def fetch_votes() -> dict:
    """Returns {property_name: {voter: vote}} where vote is 1 or -1."""
    rows = _client().table("votes").select("property_name,voter,vote").execute().data
    out: dict = {}
    for row in rows:
        out.setdefault(row["property_name"], {})[row["voter"]] = row["vote"]
    return out


def upsert_vote(property_name: str, voter: str, vote: int) -> None:
    _client().table("votes").upsert(
        {"property_name": property_name, "voter": voter, "vote": vote},
        on_conflict="property_name,voter",
    ).execute()
    fetch_votes.clear()


def delete_vote(property_name: str, voter: str) -> None:
    _client().table("votes").delete().eq(
        "property_name", property_name
    ).eq("voter", voter).execute()
    fetch_votes.clear()
