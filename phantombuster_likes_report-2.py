#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
import os
from datetime import datetime

# === 1. Padinstellingen ===
base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, "datasets")
output_dir = os.path.join(base_dir, "output")
os.makedirs(output_dir, exist_ok=True)

# === 2. Hulpfuncties ===
def extract_post_links(posts_url):
    if pd.isna(posts_url):
        return []
    return [link.strip() for link in posts_url.split('|') if link.strip()]

def load_csv(filename):
    return pd.read_csv(os.path.join(input_dir, filename))

# === 3. Laad en combineer nieuwe maanddata ===
df1 = load_csv("Phantombuster_Dataset_1.csv")
df2 = load_csv("Phantombuster_Dataset_2.csv")
df3 = load_csv("Phantombuster_Dataset_3.csv")
df4 = load_csv("Phantombuster_Dataset_4.csv")
df_new = pd.concat([df1, df2, df3, df4], ignore_index=True)

# Hernoem kolommen uniform
df_new.rename(columns={
    "profileLink": "Profile Link",
    "firstName": "First Name",
    "lastName": "Last Name",
    "fullName": "Full Name",
    "postsUrl": "Posts Url"
}, inplace=True)

df_new["Posts Url"] = df_new["Posts Url"].apply(extract_post_links)

# === 4. Groepeer per profiel ===
df_new_grouped = df_new.groupby("Profile Link").agg({
    "Full Name": "first",
    "First Name": "first",
    "Last Name": "first",
    "Posts Url": lambda x: sum(x, [])
}).reset_index()

df_new_grouped["Posts Url"] = df_new_grouped["Posts Url"].apply(lambda x: list(set(x)))
df_new_grouped["Aantal likes nieuw"] = df_new_grouped["Posts Url"].apply(len)

# === 5. Laad vorige maand (indien aanwezig) ===
old_file = os.path.join(input_dir, "Historisch_Likes_Dataset__Vorige_Maand_ (1).csv")
if os.path.exists(old_file):
    df_old = pd.read_csv(old_file)
    df_old.rename(columns={
        "profileLink": "Profile Link",
        "firstName": "First Name",
        "lastName": "Last Name",
        "fullName": "Full Name",
        "postsUrl": "Posts Url"
    }, inplace=True)
    df_old["Posts Url"] = df_old["Posts Url"].apply(extract_post_links)
else:
    df_old = pd.DataFrame(columns=df_new_grouped.columns.tolist() + ["Aantal likes totaal"])
    df_old["Posts Url"] = df_old["Posts Url"].astype(object)

# === 6. Merge met vorige maand ===
df_merged = pd.merge(df_old, df_new_grouped, on="Profile Link", how="outer", suffixes=("_oud", "_nieuw"))

def merge_posts(old_posts, new_posts):
    if isinstance(old_posts, list) and isinstance(new_posts, list):
        return list(set(old_posts + new_posts))
    elif isinstance(new_posts, list):
        return new_posts
    elif isinstance(old_posts, list):
        return old_posts
    else:
        return []

df_merged["Alle posts cumulatief"] = df_merged.apply(
    lambda row: merge_posts(row.get("Posts Url_oud"), row.get("Posts Url_nieuw")),
    axis=1
)
df_merged["Aantal likes totaal"] = df_merged["Alle posts cumulatief"].apply(lambda x: len(set(x)))

# === 7. Format output ===
output = pd.DataFrame({
    "profileLink": df_merged["Profile Link"],
    "fullName": df_merged["Full Name_nieuw"].combine_first(df_merged["Full Name_oud"]),
    "firstName": df_merged["First Name_nieuw"].combine_first(df_merged["First Name_oud"]),
    "lastName": df_merged["Last Name_nieuw"].combine_first(df_merged["Last Name_oud"]),
    "postsUrl": df_merged["Alle posts cumulatief"].apply(lambda x: " | ".join(x)),
    "Aantal likes totaal": df_merged["Aantal likes totaal"]
})

# === 8. Sla output op ===
vandaag = datetime.today().strftime("%Y-%m-%d")
output_path = os.path.join(output_dir, f"likes_per_profiel_{vandaag}.csv")
output.to_csv(output_path, index=False)

print(f"✅ Rapport opgeslagen in: {output_path}")





